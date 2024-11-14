import os
import sys

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import time
import webview
from tsr_web_api import TsrWebApi


def show_after_delay(window):
    time.sleep(1.0)  # Avoid the flash of white background if possible...
    window.show()


if __name__ == "__main__":
    api = TsrWebApi()
    window = webview.create_window(
        "Meshfinity",
        (
            "http://localhost:5173"
            if os.getenv("MESHFINITY_ENVIRONMENT") == "development"
            else os.path.join(sys._MEIPASS, "gui_build", "index.html")
        ),
        js_api=api,
        min_size=(800, 600),
        hidden=True,
    )
    api.bind_window(window)
    webview.start(
        show_after_delay,
        args=(window),
        debug=os.getenv("MESHFINITY_ENVIRONMENT") == "development",
    )
    api.kill_running_processes()
