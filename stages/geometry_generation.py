import os
import sys
import io
import base64
import platform
import subprocess
import time
import tempfile
import trimesh
import torch
from vtkmodules.vtkFiltersCore import (
    vtkWindowedSincPolyDataFilter,
    vtkQuadricDecimation,
)
from vtkmodules.vtkIOGeometry import vtkOBJWriter
import moderngl
import numpy as np
import rembg_offline as rembg
import trimesh_vtk
from PIL import Image
from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground, scale_tensor
from download_checkpoints import get_checkpoints_dir


class GeometryGenerationStage:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else ("mps" if torch.backends.mps.is_available() else "cpu")
        )
        self.tsr_model = None
        self.rembg_session = None
        self._autoremesher_process = None

    def run(self, worker, inputs):
        if inputs["settingsPreset"] == "retro":
            occupancy_grid_resolution = 256
            decimate_target_reduction = 0.995
            autoremesher_edge_scaling = 0
            texture_resolution = 256
            texture_chart_padding = 8
            texture_dilation = 4
            texture_brute_force = True
        elif inputs["settingsPreset"] == "balanced":
            occupancy_grid_resolution = 256
            decimate_target_reduction = 0.25
            autoremesher_edge_scaling = 2
            texture_resolution = 1024
            texture_chart_padding = 12
            texture_dilation = 8
            texture_brute_force = False
        elif inputs["settingsPreset"] == "extreme":
            occupancy_grid_resolution = 512
            decimate_target_reduction = 0.25
            autoremesher_edge_scaling = 1
            texture_resolution = 2048
            texture_chart_padding = 16
            texture_dilation = 12
            texture_brute_force = False
        else:
            raise Exception("Unknown settingsPreset")

        self._init_models(worker, inputs)

        input_raw_image = Image.open(
            io.BytesIO(base64.b64decode(inputs["imageBase64"]))
        )
        if inputs["removeBackground"]:
            input_image = self._remove_background(worker, input_raw_image)
        else:
            input_image = input_raw_image

        scene_codes = self._generate_scene_codes(worker, input_image)
        occupancy_grid = self._generate_occupancy_grid(
            worker, scene_codes, occupancy_grid_resolution
        )

        occ2trimesh_result = self._occupancy_grid_to_trimesh(worker, occupancy_grid)
        vtk_smoothed_mesh = self._vtk_smooth_and_decimate(
            worker,
            occ2trimesh_result["mesh"],
            decimate_target_reduction,
        )
        self._send_preview_vtk_mesh(worker, vtk_smoothed_mesh)

        obj_text_remeshed_mesh = self._run_autoremesher(
            worker,
            vtk_smoothed_mesh,
            autoremesher_edge_scaling,
            texture_resolution,
            texture_chart_padding,
            texture_brute_force,
        )
        trimesh_remeshed_mesh = trimesh.load(
            file_obj=trimesh.util.wrap_as_stream(obj_text_remeshed_mesh),
            file_type="obj",
            merge_norm=True,
        )
        self._send_preview_trimesh_mesh(worker, trimesh_remeshed_mesh)

        coarse_texture_image = self._generate_texture(
            worker,
            scene_codes,
            trimesh_remeshed_mesh,
            occ2trimesh_result["inverse_transform"],
            occ2trimesh_result["tsr_transform"],
            texture_resolution,
            texture_dilation,
        )
        self._send_preview_texture(worker, coarse_texture_image)

        self._send_exportable_data(
            worker,
            {
                "objText": obj_text_remeshed_mesh,
                "pngBase64": self._image_to_base64(coarse_texture_image),
            },
        )

        # Done!
        worker._push_event(
            "progress",
            None,
        )

    def _remove_background(self, worker, input_raw_image):
        worker._push_event(
            "progress",
            {
                "label": "Removing background",
                "value": 0.1,
            },
        )
        image = remove_background(input_raw_image, self.rembg_session)
        image = resize_foreground(image, 0.8)
        image = np.array(image).astype(np.float32) / 255.0
        image_to_frontend = (image * 255.0).astype(
            np.uint8
        )  # Copy this before we trim to RGB instead of RGBA
        image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
        image = (image * 255.0).astype(np.uint8)
        self._send_preview_rembg(worker, Image.fromarray(image_to_frontend))
        return image

    def _generate_scene_codes(self, worker, input_image):
        worker._push_event(
            "progress",
            {
                "label": "Imagining 3D shape",
                "value": 0.2,
            },
        )
        with torch.no_grad():
            scene_codes = self.tsr_model([input_image], device=self.device)
        return scene_codes

    def _generate_occupancy_grid(self, worker, scene_codes, grid_resolution):
        worker._push_event(
            "progress",
            {
                "label": "Sampling density grid",
                "value": 0.3,
            },
        )
        GRID_CHUNK_SIZE = 256
        DENSITY_THRESHOLD = 15
        with torch.no_grad():
            density_grid = self._sample_density_in_chunks(
                scene_codes, grid_resolution, GRID_CHUNK_SIZE
            )
        return density_grid >= DENSITY_THRESHOLD

    def _sample_density_in_chunks(self, scene_codes, total_size, chunk_size):
        result = np.zeros((total_size, total_size, total_size), dtype=float)

        for lower_k in range(0, total_size, chunk_size):
            for lower_j in range(0, total_size, chunk_size):
                for lower_i in range(0, total_size, chunk_size):
                    upper_i = lower_i + chunk_size
                    upper_j = lower_j + chunk_size
                    upper_k = lower_k + chunk_size

                    # [0, total_size] but only up to chunk_size part of it
                    sampling_range_x = (lower_i / total_size, upper_i / total_size)
                    sampling_range_y = (lower_j / total_size, upper_j / total_size)
                    sampling_range_z = (lower_k / total_size, upper_k / total_size)

                    with torch.no_grad():
                        # [0, 1] but only up to (chunk_size / total_size) part of it
                        x, y, z = (
                            torch.linspace(*sampling_range_x, chunk_size),
                            torch.linspace(*sampling_range_y, chunk_size),
                            torch.linspace(*sampling_range_z, chunk_size),
                        )
                        x, y, z = torch.meshgrid(x, y, z, indexing="ij")
                        verts = torch.cat(
                            [x.reshape(-1, 1), y.reshape(-1, 1), z.reshape(-1, 1)],
                            dim=-1,
                        ).reshape(-1, 3)

                        queried_grid = self.tsr_model.renderer.query_triplane(
                            self.tsr_model.decoder,
                            scale_tensor(
                                verts.to(
                                    self.device,
                                ),
                                (0, 1),  # Scales from our [0, 1]...
                                (
                                    # ..to fit within [-radius, +radius] of TripoSR model
                                    -self.tsr_model.renderer.cfg.radius,
                                    self.tsr_model.renderer.cfg.radius,
                                ),
                            ),
                            scene_codes[0],
                        )

                        result[lower_i:upper_i, lower_j:upper_j, lower_k:upper_k] = (
                            queried_grid["density_act"]
                            .reshape(chunk_size, chunk_size, chunk_size)
                            .cpu()
                            .numpy()
                        )

        return result

    def _occupancy_grid_to_trimesh(self, worker, occupancy_grid):
        worker._push_event(
            "progress",
            {
                "label": "Marching cubes",
                "value": 0.4,
            },
        )
        trimesh_mesh = trimesh.voxel.ops.points_to_marching_cubes(
            np.argwhere(
                (
                    trimesh.voxel.VoxelGrid(
                        trimesh.voxel.base.DenseEncoding(occupancy_grid)
                    )
                    .hollow()
                    .fill()
                ).encoding.data
                == True
            )
        )

        trimesh_centroid = np.mean(trimesh_mesh.bounds, axis=0)
        trimesh_max_bounds_side = np.max(
            trimesh_mesh.bounds[1] - trimesh_mesh.bounds[0]
        )
        trimesh_scale = 2.0 / trimesh_max_bounds_side
        trimesh_transform = np.array(
            [
                [0, trimesh_scale, 0, -trimesh_centroid[1] * trimesh_scale],
                [0, 0, trimesh_scale, -trimesh_centroid[2] * trimesh_scale],
                [trimesh_scale, 0, 0, -trimesh_centroid[0] * trimesh_scale],
                [0, 0, 0, 1],
            ]
        )
        trimesh_mesh.apply_transform(trimesh_transform)

        trimesh_transform_inverse = np.linalg.inv(trimesh_transform)
        tsr_scale_x = 2.0 * self.tsr_model.renderer.cfg.radius / occupancy_grid.shape[0]
        tsr_scale_y = 2.0 * self.tsr_model.renderer.cfg.radius / occupancy_grid.shape[1]
        tsr_scale_z = 2.0 * self.tsr_model.renderer.cfg.radius / occupancy_grid.shape[2]
        tsr_transform = np.array(
            [
                [
                    tsr_scale_x,
                    0,
                    0,
                    -occupancy_grid.shape[0] * 0.5 * tsr_scale_x,
                ],
                [
                    0,
                    tsr_scale_y,
                    0,
                    -occupancy_grid.shape[1] * 0.5 * tsr_scale_y,
                ],
                [
                    0,
                    0,
                    tsr_scale_z,
                    -occupancy_grid.shape[2] * 0.5 * tsr_scale_z,
                ],
                [0, 0, 0, 1],
            ]
        )

        return {
            "mesh": trimesh_mesh,
            "inverse_transform": trimesh_transform_inverse,
            "tsr_transform": tsr_transform,
        }

    def _vtk_smooth_and_decimate(self, worker, trimesh_mesh, decimate_target_reduction):
        worker._push_event(
            "progress",
            {
                "label": "Smoothing",
                "value": 0.5,
            },
        )
        vtk_mesh = trimesh_vtk.trimesh_to_vtk(
            trimesh_mesh.vertices, trimesh_mesh.faces, None
        )
        vtk_smoother = vtkWindowedSincPolyDataFilter()
        vtk_smoother.SetInputData(vtk_mesh)
        vtk_smoother.SetNumberOfIterations(30)
        vtk_smoother.SetPassBand(0.00001)
        vtk_smoother.NormalizeCoordinatesOn()
        vtk_smoother.Update()
        vtk_decimator = vtkQuadricDecimation()
        vtk_decimator.SetInputConnection(vtk_smoother.GetOutputPort())
        vtk_decimator.SetTargetReduction(decimate_target_reduction)
        vtk_decimator.Update()
        return vtk_decimator.GetOutput()

    def _send_preview_rembg(self, worker, rembg_image):
        worker._push_event(
            "previewRembg",
            {"imageBase64": self._image_to_base64(rembg_image)},
        )

    def _send_preview_vtk_mesh(self, worker, vtk_mesh):
        (preview_points, preview_tris) = trimesh_vtk.vtk_to_points_tris(vtk_mesh)
        trimesh_mesh = trimesh.Trimesh(vertices=preview_points, faces=preview_tris)
        self._send_preview_trimesh_mesh(worker, trimesh_mesh)

    def _send_preview_trimesh_mesh(self, worker, trimesh_mesh):
        worker._push_event(
            "previewGeometry",
            {
                "positions": trimesh_mesh.vertices.flatten().tolist(),
                "texCoords": (
                    trimesh_mesh.visual.uv.flatten().tolist()
                    if isinstance(trimesh_mesh.visual, trimesh.visual.TextureVisuals)
                    else None
                ),
                "normals": trimesh_mesh.vertex_normals.flatten().tolist(),
                "indices": trimesh_mesh.faces.flatten().tolist(),
            },
        )

    def _send_preview_texture(self, worker, texture_image):
        worker._push_event(
            "previewTexture",
            {"imageBase64": self._image_to_base64(texture_image)},
        )

    def _run_autoremesher(
        self,
        worker,
        vtk_mesh,
        edge_scaling,
        texture_resolution,
        texture_chart_padding,
        texture_brute_force,
    ):
        with tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True, delete=True
        ) as tmp_dir_path:
            vtk_out_path = os.path.join(tmp_dir_path, "vtk_out.obj")
            vtk_writer = vtkOBJWriter()
            vtk_writer.SetFileName(vtk_out_path)
            vtk_writer.SetInputData(vtk_mesh)
            vtk_writer.Write()

            worker._push_event(
                "progress",
                {
                    "label": "Remeshing",
                    "value": 0.6,
                },
            )

            AUTOREMESHER_TARGET_TRIANGLE_COUNT = 65536
            autoremesher_base_path = (
                os.path.join(os.path.dirname(__file__), "..", "autoremesher")
                if os.getenv("MESHFINITY_ENVIRONMENT") == "development"
                else os.path.join(sys._MEIPASS, "autoremesher")
            )
            if platform.system() == "Darwin":
                autoremesher_exe_path = os.path.join(
                    autoremesher_base_path,
                    "mac",
                    "autoremesher.app",
                    "Contents",
                    "MacOS",
                    "autoremesher",
                )
            elif platform.system() == "Windows":
                autoremesher_exe_path = os.path.join(
                    autoremesher_base_path,
                    "win",
                    "autoremesher.exe",
                )
            else:
                raise NotImplementedError("autoremesher not supported on your platform")

            autoremesher_out_path = os.path.join(tmp_dir_path, "autoremesher_out.obj")

            self._autoremesher_process = subprocess.Popen(
                [
                    autoremesher_exe_path,
                    vtk_out_path,
                    autoremesher_out_path,
                    str(edge_scaling),
                    str(AUTOREMESHER_TARGET_TRIANGLE_COUNT),
                    str(texture_resolution),
                    str(texture_chart_padding),
                    "1" if texture_brute_force else "0",
                ]
            )
            while True:
                return_code = self._autoremesher_process.poll()
                if return_code is None:
                    time.sleep(0.1)
                else:
                    break
            self._autoremesher_process = None

            with open(autoremesher_out_path, "r") as autoremesher_out_file:
                autoremesher_out_contents = autoremesher_out_file.read()

        return autoremesher_out_contents

    def _generate_texture(
        self,
        worker,
        scene_codes,
        trimesh_mesh,
        inverse_transform,
        tsr_transform,
        texture_resolution,
        texture_dilation,
    ):
        worker._push_event(
            "progress",
            {
                "label": "Generating texture",
                "value": 0.7,
            },
        )

        positions_texture = self._rasterize_positions(
            worker,
            trimesh_mesh,
            inverse_transform,
            tsr_transform,
            texture_resolution,
            texture_dilation,
        )
        colors_texture = self._positions_texture_to_colors_texture(
            worker, scene_codes, positions_texture
        )

        return Image.fromarray((colors_texture * 255.0).astype(np.uint8)).transpose(
            Image.FLIP_TOP_BOTTOM
        )

    def _rasterize_positions(
        self,
        worker,
        trimesh_mesh,
        inverse_transform,
        tsr_transform,
        texture_resolution,
        texture_dilation,
    ):
        ctx = moderngl.create_context(standalone=True)
        basic_prog = ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_uv;
                in vec3 in_pos;
                uniform mat4 u_invMat;
                uniform mat4 u_tsrMat;
                out vec3 v_pos;
                void main() {
                    vec4 v4Pos = vec4(in_pos, 1.0);
                    v4Pos = u_invMat * v4Pos;
                    v4Pos = u_tsrMat * v4Pos;
                    v_pos = v4Pos.xyz;
                    gl_Position = vec4(in_uv * 2.0 - 1.0, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                in vec3 v_pos;
                out vec4 o_col;
                void main() {
                    o_col = vec4(v_pos, 1.0);
                }
            """,
        )
        gs_prog = ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_uv;
                in vec3 in_pos;
                uniform mat4 u_invMat;
                uniform mat4 u_tsrMat;
                out vec3 vg_pos;
                void main() {
                    vec4 v4Pos = vec4(in_pos, 1.0);
                    v4Pos = u_invMat * v4Pos;
                    v4Pos = u_tsrMat * v4Pos;
                    vg_pos = v4Pos.xyz;
                    gl_Position = vec4(in_uv * 2.0 - 1.0, 0.0, 1.0);
                }
            """,
            geometry_shader="""
                #version 330
                uniform float u_resolution;
                uniform float u_dilation;
                layout (triangles) in;
                layout (triangle_strip, max_vertices = 12) out;
                in vec3 vg_pos[];
                out vec3 vf_pos;
                void lineSegment(int aidx, int bidx) {
                    vec2 a = gl_in[aidx].gl_Position.xy;
                    vec2 b = gl_in[bidx].gl_Position.xy;
                    vec3 aCol = vg_pos[aidx];
                    vec3 bCol = vg_pos[bidx];

                    vec2 dir = normalize((b - a) * u_resolution);
                    vec2 offset = vec2(-dir.y, dir.x) * u_dilation / u_resolution;

                    gl_Position = vec4(a + offset, 0.0, 1.0);
                    vf_pos = aCol;
                    EmitVertex();
                    gl_Position = vec4(a - offset, 0.0, 1.0);
                    vf_pos = aCol;
                    EmitVertex();
                    gl_Position = vec4(b + offset, 0.0, 1.0);
                    vf_pos = bCol;
                    EmitVertex();
                    gl_Position = vec4(b - offset, 0.0, 1.0);
                    vf_pos = bCol;
                    EmitVertex();
                }
                void main() {
                    lineSegment(0, 1);
                    lineSegment(1, 2);
                    lineSegment(2, 0);
                    EndPrimitive();
                }
            """,
            fragment_shader="""
                #version 330
                in vec3 vf_pos;
                out vec4 o_col;
                void main() {
                    o_col = vec4(vf_pos, 1.0);
                }
            """,
        )
        uvs = trimesh_mesh.visual.uv.flatten().astype("f4")
        pos = trimesh_mesh.vertices.flatten().astype("f4")
        indices = trimesh_mesh.faces.flatten().astype("i4")
        vbo_uvs = ctx.buffer(uvs)
        vbo_pos = ctx.buffer(pos)
        ibo = ctx.buffer(indices)
        vao_content = [
            vbo_uvs.bind("in_uv", layout="2f"),
            vbo_pos.bind("in_pos", layout="3f"),
        ]
        basic_vao = ctx.vertex_array(basic_prog, vao_content, ibo)
        gs_vao = ctx.vertex_array(gs_prog, vao_content, ibo)
        fbo = ctx.framebuffer(
            color_attachments=[
                ctx.texture((texture_resolution, texture_resolution), 4, dtype="f4")
            ]
        )
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 0.0)
        basic_prog["u_invMat"].value = inverse_transform.flatten(order="F").astype("f4")
        basic_prog["u_tsrMat"].value = tsr_transform.flatten(order="F").astype("f4")
        gs_prog["u_invMat"].value = inverse_transform.flatten(order="F").astype("f4")
        gs_prog["u_tsrMat"].value = tsr_transform.flatten(order="F").astype("f4")
        gs_prog["u_resolution"].value = texture_resolution
        gs_prog["u_dilation"].value = texture_dilation
        gs_vao.render()
        basic_vao.render()

        fbo_bytes = fbo.color_attachments[0].read()
        fbo_np = np.frombuffer(fbo_bytes, dtype="f4").reshape(
            texture_resolution, texture_resolution, 4
        )
        return fbo_np

    def _positions_texture_to_colors_texture(
        self, worker, scene_codes, positions_texture
    ):
        positions = torch.tensor(positions_texture.reshape(-1, 4)[:, :-1]).to(
            self.device
        )
        with torch.no_grad():
            queried_grid = self.tsr_model.renderer.query_triplane(
                self.tsr_model.decoder,
                positions,
                scene_codes[0],
            )
        rgb_f = queried_grid["color"].cpu().numpy().reshape(-1, 3)
        rgba_f = np.insert(rgb_f, 3, positions_texture.reshape(-1, 4)[:, -1], axis=1)
        rgba_f[rgba_f[:, -1] == 0.0] = [0, 0, 0, 0]
        return rgba_f.reshape(positions_texture.shape[0], positions_texture.shape[1], 4)

    def _send_exportable_data(self, worker, exportable_data):
        worker._push_event("exportableData", exportable_data)

    def _image_to_base64(self, image):
        png_bytes = io.BytesIO()
        image.save(png_bytes, format="PNG")
        png_bytes.seek(0)
        b64_encoded_image = base64.b64encode(png_bytes.read()).decode("ascii")
        return b64_encoded_image

    def _init_models(self, worker, inputs):
        worker._push_event(
            "progress",
            {
                "label": "Initializing models",
                "value": 0.0,
            },
        )

        if not self.tsr_model:
            self.tsr_model = TSR.from_pretrained(
                os.path.join(get_checkpoints_dir(), "tsr"),
                config_name="config.yaml",
                weight_name="model.ckpt",
            )
            self.tsr_model.renderer.set_chunk_size(8192)
            self.tsr_model.to(self.device)

        if inputs["removeBackground"] and not self.rembg_session:
            self.rembg_session = rembg.new_session(
                model_name="u2net",
                offline_model_path=(
                    os.path.join(
                        get_checkpoints_dir(),
                        "u2net",
                        "u2net.onnx",
                    )
                ),
            )

    def kill_running_processes(self):
        if self._autoremesher_process is not None:
            self._autoremesher_process.terminate()
            self._autoremesher_process = None
