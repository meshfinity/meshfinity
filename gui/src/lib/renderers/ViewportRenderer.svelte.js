import Renderer from "$lib/renderers/Renderer.js";
import viewportCameraInstance from "./viewportCameraInstance.js";
import coreInstance from "$lib/core/coreInstance.svelte.js";

const VERTEX_SHADER_SOURCE = `
precision mediump float;

attribute vec3 position;
attribute vec2 texCoord;
attribute vec3 normal;

uniform mat4 projMat;
uniform mat4 viewMat;
uniform mat4 modelMat;
uniform mat3 normalMat;

varying vec2 v_texCoord;
varying float v_diffuse;

void main() {
  v_texCoord = texCoord;

  vec3 transformedNormal = normalize(normalMat * normal);
  vec3 lightDir = vec3(viewMat[0].z, viewMat[1].z, viewMat[2].z);
  v_diffuse = max(dot(transformedNormal, lightDir), 0.0);

  gl_Position = projMat * viewMat * modelMat * vec4(position, 1.0);
}
`;

const FRAGMENT_SHADER_SOURCE = `
precision mediump float;

uniform sampler2D coarseTexture;
uniform bool useTexture;

varying vec2 v_texCoord;
varying float v_diffuse;

void main() {
  vec3 baseCol = useTexture ? texture2D(coarseTexture, v_texCoord).xyz : vec3(1.0);
  gl_FragColor = vec4(baseCol * vec3(0.3 + v_diffuse * 0.7), 1.0);
}
`;

export default class ViewportRenderer extends Renderer {
  constructor(canvas, gl) {
    super(canvas, gl);

    this._positionsBuffer = this._gl.createBuffer();
    this._positionsBufferValid = false;
    this._texCoordsBuffer = this._gl.createBuffer();
    this._texCoordsBufferValid = false;
    this._normalsBuffer = this._gl.createBuffer();
    this._normalsBufferValid = false;
    this._indicesBuffer = this._gl.createBuffer();
    this._numIndices = 0;
    this._indicesBufferValid = false;
    this._coarseTexture = this._gl.createTexture();
    this._coarseTextureValid = false;

    this._shader = this._createShaderProgram(
      VERTEX_SHADER_SOURCE,
      FRAGMENT_SHADER_SOURCE
    );
    this._gl.useProgram(this._shader);
    this._projMatUniform = this._gl.getUniformLocation(this._shader, "projMat");
    this._viewMatUniform = this._gl.getUniformLocation(this._shader, "viewMat");
    this._modelMatUniform = this._gl.getUniformLocation(
      this._shader,
      "modelMat"
    );
    this._normalMatUniform = this._gl.getUniformLocation(
      this._shader,
      "normalMat"
    );
    this._coarseTextureUniform = this._gl.getUniformLocation(
      this._shader,
      "coarseTexture"
    );
    this._useTextureUniform = this._gl.getUniformLocation(
      this._shader,
      "useTexture"
    );
    this._posAttrib = this._gl.getAttribLocation(this._shader, "position");
    this._texCoordAttrib = this._gl.getAttribLocation(this._shader, "texCoord");
    this._normalAttrib = this._gl.getAttribLocation(this._shader, "normal");

    // TODO: Debounce all $effect

    $effect(() => {
      if (this._gl && coreInstance.mesh.positions) {
        this._bufferMeshPositions();
        this._positionsBufferValid = true;
      } else {
        this._positionsBufferValid = false;
      }
    });

    $effect(() => {
      if (this._gl && coreInstance.mesh.texCoords) {
        this._bufferMeshTexCoords();
        this._texCoordsBufferValid = true;
      } else {
        this._texCoordsBufferValid = false;
      }
    });

    $effect(() => {
      if (this._gl && coreInstance.mesh.normals) {
        this._bufferMeshNormals();
        this._normalsBufferValid = true;
      } else {
        this._normalsBufferValid = false;
      }
    });

    $effect(() => {
      if (this._gl && coreInstance.mesh.indices) {
        this._bufferMeshIndices();
        this._numIndices = coreInstance.mesh.indices.length;
        this._indicesBufferValid = true;
      } else {
        this._numIndices = 0;
        this._indicesBufferValid = false;
      }
    });

    $effect(() => {
      if (this._gl && coreInstance.mesh.coarseTextureImage) {
        this._bufferTexture();
        this._coarseTextureValid = true;
      } else {
        this._coarseTextureValid = false;
      }
    });
  }

  render() {
    viewportCameraInstance.update(this._canvas.width, this._canvas.height);
    this._gl.viewport(0, 0, this._canvas.width, this._canvas.height);

    this._gl.clearColor(0.0, 0.0, 0.0, 0.0);
    this._gl.clearDepth(1.0);
    this._gl.enable(this._gl.DEPTH_TEST);
    this._gl.clear(this._gl.COLOR_BUFFER_BIT | this._gl.DEPTH_BUFFER_BIT);

    this._gl.useProgram(this._shader);
    this._gl.uniformMatrix4fv(
      this._projMatUniform,
      false,
      viewportCameraInstance.projMat
    );
    this._gl.uniformMatrix4fv(
      this._viewMatUniform,
      false,
      viewportCameraInstance.viewMat
    );
    this._gl.uniformMatrix4fv(
      this._modelMatUniform,
      false,
      viewportCameraInstance.modelMat
    );
    this._gl.uniformMatrix3fv(
      this._normalMatUniform,
      false,
      viewportCameraInstance.normalMat
    );

    this._gl.activeTexture(this._gl.TEXTURE0);
    this._gl.bindTexture(this._gl.TEXTURE_2D, this._coarseTexture);
    this._gl.uniform1i(this._coarseTextureUniform, 0);

    this._gl.uniform1i(
      this._useTextureUniform,
      this._texCoordsBufferValid && this._coarseTextureValid ? 1 : 0
    );

    if (this._positionsBufferValid) {
      this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._positionsBuffer);
      this._gl.enableVertexAttribArray(this._posAttrib);
      this._gl.vertexAttribPointer(
        this._posAttrib,
        3,
        this._gl.FLOAT,
        false,
        0,
        0
      );
    } else {
      this._gl.disableVertexAttribArray(this._posAttrib);
    }

    if (this._texCoordsBufferValid) {
      this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._texCoordsBuffer);
      this._gl.enableVertexAttribArray(this._texCoordAttrib);
      this._gl.vertexAttribPointer(
        this._texCoordAttrib,
        2,
        this._gl.FLOAT,
        false,
        0,
        0
      );
    } else {
      this._gl.disableVertexAttribArray(this._texCoordAttrib);
    }

    if (this._normalsBufferValid) {
      this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._normalsBuffer);
      this._gl.enableVertexAttribArray(this._normalAttrib);
      this._gl.vertexAttribPointer(
        this._normalAttrib,
        3,
        this._gl.FLOAT,
        false,
        0,
        0
      );
    } else {
      this._gl.disableVertexAttribArray(this._normalAttrib);
    }

    if (this._indicesBufferValid) {
      this._gl.bindBuffer(this._gl.ELEMENT_ARRAY_BUFFER, this._indicesBuffer);
      this._gl.drawElements(
        this._gl.TRIANGLES,
        this._numIndices,
        this._gl.UNSIGNED_INT,
        0
      );
    }
  }

  onPointerMove(event) {
    viewportCameraInstance.onPointerMove(event);
  }

  onWheel(event) {
    viewportCameraInstance.onWheel(event);
  }

  _bufferMeshPositions() {
    this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._positionsBuffer);
    this._gl.bufferData(
      this._gl.ARRAY_BUFFER,
      coreInstance.mesh.positions,
      this._gl.STATIC_DRAW
    );
  }

  _bufferMeshTexCoords() {
    this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._texCoordsBuffer);
    this._gl.bufferData(
      this._gl.ARRAY_BUFFER,
      coreInstance.mesh.texCoords,
      this._gl.STATIC_DRAW
    );
  }

  _bufferMeshNormals() {
    this._gl.bindBuffer(this._gl.ARRAY_BUFFER, this._normalsBuffer);
    this._gl.bufferData(
      this._gl.ARRAY_BUFFER,
      coreInstance.mesh.normals,
      this._gl.STATIC_DRAW
    );
  }

  _bufferMeshIndices() {
    this._gl.bindBuffer(this._gl.ELEMENT_ARRAY_BUFFER, this._indicesBuffer);
    this._gl.bufferData(
      this._gl.ELEMENT_ARRAY_BUFFER,
      coreInstance.mesh.indices,
      this._gl.STATIC_DRAW
    );
  }

  _bufferTexture() {
    this._gl.bindTexture(this._gl.TEXTURE_2D, this._coarseTexture);
    this._gl.pixelStorei(this._gl.UNPACK_FLIP_Y_WEBGL, true);
    this._gl.texImage2D(
      this._gl.TEXTURE_2D,
      0,
      this._gl.RGB,
      this._gl.RGB,
      this._gl.UNSIGNED_BYTE,
      coreInstance.mesh.coarseTextureImage
    );
    this._gl.generateMipmap(this._gl.TEXTURE_2D);
    this._gl.texParameteri(
      this._gl.TEXTURE_2D,
      this._gl.TEXTURE_MIN_FILTER,
      coreInstance.geometryGenerationInputs.settingsPreset === "retro"
        ? this._gl.NEAREST
        : this._gl.LINEAR_MIPMAP_NEAREST
    );
    this._gl.texParameteri(
      this._gl.TEXTURE_2D,
      this._gl.TEXTURE_MAG_FILTER,
      coreInstance.geometryGenerationInputs.settingsPreset === "retro"
        ? this._gl.NEAREST
        : this._gl.LINEAR
    );
  }
}
