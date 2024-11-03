import base64
import json
import io
import os
import re
import uuid
import threading
import traceback
import webbrowser
import requests
import webview
from PIL import Image
from tsr_worker import TsrWorker


class TsrWebApi:
    def __init__(self):
        self.worker = TsrWorker(self)
        self.worker_thread = threading.Thread(
            target=self.worker.run, daemon=True
        ).start()

        self._window = None

    def bind_window(self, window):
        self._window = window

    def push_inputs(self, inputs):
        id = str(uuid.uuid4())
        self.worker.push_inputs(id, inputs)
        return id

    def export_data(self, exportable_data, default_filename):
        obj_path = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=default_filename,
            file_types=("Wavefront OBJ (*.obj)", "All files (*.*)"),
        )
        if obj_path is None:
            return None

        if re.search(r"\s", obj_path) is not None:
            confirm_result = self._window.create_confirmation_dialog(
                "Invalid spaces in filename",
                "The filename you have chosen contains a space. Spaces are invalid in OBJ/MTL filenames and will cause issues with texture loading. Please retry with a different filename.",
            )
            if confirm_result:
                return self.export_data(exportable_data, default_filename)
            else:
                return None

        mtl_path = re.sub(r"\.obj$", "", obj_path, flags=re.IGNORECASE) + ".mtl"
        png_path = re.sub(r"\.obj$", "", obj_path, flags=re.IGNORECASE) + ".png"

        with open(obj_path, "w") as obj_file:
            obj_file.write(
                "mtllib {}\nusemtl Material\n{}\n".format(
                    os.path.basename(mtl_path), exportable_data["objText"]
                )
            )
        with open(mtl_path, "w") as mtl_file:
            mtl_file.write(
                "newmtl Material\nillum 0\nmap_Kd {}\n".format(
                    os.path.basename(png_path)
                )
            )
        texture_image = Image.open(
            io.BytesIO(base64.b64decode(exportable_data["pngBase64"]))
        )
        texture_image.save(png_path)

        return obj_path

    def check_for_updates(self):
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/meshfinity/meshfinity/refs/heads/main/version.json"
            )
            json_data = response.json()
            version = json_data["version"]
            if version != "1.0.0":
                confirm_result = self._window.create_confirmation_dialog(
                    "Update Meshfinity",
                    "An update is available! Would you like to visit meshfinity.com to download it now?",
                )
                if confirm_result:
                    webbrowser.open("https://www.meshfinity.com")
        except Exception:
            print("Error checking for updates: " + traceback.format_exc())

    def webbrowser_open(self, url):
        webbrowser.open(url)

    def kill_running_processes(self):
        self.worker.kill_running_processes()

    def _push_event(self, id, stage, type, event):
        self._window.evaluate_js(
            "window._pywebviewCoreInstance.pushEvent({})".format(
                json.dumps(
                    {
                        "id": id,
                        "stage": stage,
                        "type": type,
                        "event": event,
                    }
                )
            )
        )
