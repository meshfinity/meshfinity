import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import atexit
import filelock
import pathlib
import signal
import sys
import tempfile
import traceback
from message_box import message_box_error
from download_checkpoints import delete_tmp_downloads

lock_file_path = None
lock_file = None


def close_splash():
    try:
        import pyi_splash

        pyi_splash.close()
    except Exception:
        # Ignore if we're not running in PyInstaller on Windows
        pass


def acquire_lock_file():
    global lock_file
    global lock_file_path

    lock_file_dir = os.path.join(tempfile.gettempdir(), "Meshfinity")
    pathlib.Path(lock_file_dir).mkdir(parents=True, exist_ok=True)
    lock_file_path = os.path.join(lock_file_dir, "single-instance.lock")

    lock_file = filelock.FileLock(lock_file_path, timeout=1)
    try:
        lock_file.acquire()
    except filelock.Timeout:
        # Set these to None to prevent release_lock_file from deleting another instance's lockfile
        # (This is actually possible for another process to release the lockfile - very strange)
        lock_file = None
        lock_file_path = None

        # Need to close splash before showing dialog, since splash is always on top, nobody could see the dialog
        close_splash()

        # Show error dialog
        message_box_error(
            "Meshfinity is busy",
            "Another instance of Meshfinity is currently busy. Please wait a moment before attempting to launch Meshfinity again, or reboot your device if this problem persists.",
        )

        # Exit immediately
        sys.exit(0)


def release_lock_file():
    global lock_file
    global lock_file_path

    if lock_file is not None:
        try:
            lock_file.release()
        except Exception:
            # Catch this exception so we can at least continue to try to delete the file (probably won't work if still locked)
            print(traceback.format_exc())

        try:
            os.remove(lock_file_path)
        except Exception:
            print(traceback.format_exc())

    lock_file = None
    lock_file_path = None

    sys.exit(0)


def release_lock_file_signal(signum, frame):
    # Prevent exception: release_lock_file takes 0 positional arguments but called with 2
    release_lock_file()


# Register release_lock_file for signals and exit to ensure that the lockfile is deleted when the process exits
# (otherwise it would be impossible to create another instance, even though there is no running process).
# This doesn't work for SIGKILL... there isn't really a good way to clean up if it crashes that badly...
# hopefully the temporary directory will be cleared on reboot.
signal.signal(signal.SIGTERM, release_lock_file_signal)
signal.signal(signal.SIGINT, release_lock_file_signal)
signal.signal(signal.SIGABRT, release_lock_file_signal)
# atexit sends 0 arguments, so register the original release_lock_file() function,
# not release_lock_file_signal
atexit.register(release_lock_file)

# Now try to ensure this is the only running instance
# Will exit if there is another instance
acquire_lock_file()


#
# Success! This is the only instance of meshfinity. Now we can load larger imports and continue with application startup...
#


import time
import webview
from tsr_web_api import TsrWebApi


def on_webview_start(window):
    time.sleep(
        1.0  # Give webview some time to load the page, so we can avoid the flash of white background if possible...
    )
    close_splash()
    window.show()


api = TsrWebApi()


def kill_api_processes():
    global api
    api.kill_running_processes()


atexit.register(delete_tmp_downloads)
atexit.register(kill_api_processes)

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
    on_webview_start,
    args=(window),
    debug=os.getenv("MESHFINITY_ENVIRONMENT") == "development",
)
