import base64
import json
import io
import os
import re
import sys
import uuid
import pathlib
import platform
import threading
import traceback
import webbrowser
import requests
import webview
from PIL import Image
from tsr_worker import TsrWorker
from audio_process import AudioProcess
from version import MESHFINITY_CURRENT_VERSION


class TsrWebApi:
    def __init__(self):
        self.worker = TsrWorker(self)
        self.worker_thread = threading.Thread(
            target=self.worker.run, daemon=True
        ).start()

        self._config = None
        self._load_config()

        self._window = None
        self._audio_process = AudioProcess()

    def bind_window(self, window):
        self._window = window

    def setup(self):
        self.worker.push_inputs(
            None,
            {
                "stage": "setup",
            },
        )

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
            if version != MESHFINITY_CURRENT_VERSION:
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

    def enable_audio(self):
        self._audio_process.open_playback_device()
        self._config["audio_enabled"] = True
        self._save_config()

    def disable_audio(self):
        self._config["audio_enabled"] = False
        self._save_config()
        self.kill_audio()

    def get_audio_enabled(self):
        return self._config["audio_enabled"]

    def play_sound(self, filename, loop):
        self._audio_process.play_sound(filename, loop)

    def kill_audio(self):
        self._audio_process.close_playback_device()

    def terminate_audio_process(self):
        try:
            self.kill_audio()
        except Exception:
            print(traceback.format_exc())
        self._audio_process.terminate()
        self._audio_process = None

    def _load_config(self):
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                self._config = json.load(config_file)
        else:
            self._config = self._get_default_config()
            self._save_config()

    def _save_config(self):
        config_path = self._get_config_path()
        with open(config_path, "w") as config_file:
            json.dump(self._config, config_file)

    def _get_config_path(self):
        if os.getenv("MESHFINITY_ENVIRONMENT") == "development":
            folder_path = os.path.join(os.path.dirname(__file__), "config")
        elif platform.system() == "Darwin":
            folder_path = os.path.join(
                pathlib.Path.home(),
                "Library",
                "Application Support",
                "Meshfinity",
                "config",
            )
        elif platform.system() == "Windows":
            folder_path = os.path.join(sys._MEIPASS, "config")
        else:
            raise Exception("Platform not supported")

        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)

        config_path = os.path.join(folder_path, "config.json")
        return config_path

    def _get_default_config(self):
        return {"audio_enabled": True}
