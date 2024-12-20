import os
import shutil
import sys
import glob
import pathlib
import platform
import pooch
import traceback
import wakepy


def format_filesize(filesize):
    if filesize > 1000000000:
        return f"{(filesize / 1000000000.0):.2f} GB"
    if filesize > 1000000:
        return f"{round(filesize / 1000000.0)} MB"
    if filesize > 1000:
        return f"{round(filesize / 1000.0)} KB"
    else:
        return f"{filesize} B"


class CustomProgressBar:
    def __init__(
        self,
        worker,
        progress_label,
        elapsed_progress,
        current_item_weight,
    ):
        self.count = 0
        self.total = None
        self._worker = worker
        self._progress_label = progress_label
        self._elapsed_progress = elapsed_progress
        self._current_item_weight = current_item_weight

    # Pooch docs say the `i` argument is the total downloaded so far, but according to the source:
    # https://github.com/fatiando/pooch/blob/main/pooch/downloaders.py#L248
    # it seems that `i` is actually the chunk size when using HTTPDownloader, until the end,
    # at which point it returns the total downloaded size
    def update(self, i):
        self.count += i
        if self.total is None:
            return
        self.count = min(self.count, self.total)
        self._worker._push_event(
            "setupProgress",
            {
                "label": f"{self._progress_label} ({format_filesize(self.count)}/{format_filesize(self.total)})",
                "value": self._elapsed_progress
                + ((self.count / self.total) * self._current_item_weight),
            },
        )

    def reset(self):
        self.count = 0
        self.total = None

    def close(self):
        return None


def get_checkpoints_dir():
    if os.getenv("MESHFINITY_ENVIRONMENT") == "development":
        return os.path.join(os.path.dirname(__file__), "checkpoints")
    elif platform.system() == "Darwin":
        return os.path.join(
            pathlib.Path.home(),
            "Library",
            "Application Support",
            "Meshfinity",
            "checkpoints",
        )
    elif platform.system() == "Windows":
        return os.path.join(sys._MEIPASS, "checkpoints")
    else:
        raise Exception("Platform not supported")


def delete_tmp_downloads():
    combined = [
        *glob.glob(os.path.join(get_checkpoints_dir(), "*tmp*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "*TMP*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "*temp*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "*TEMP*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "**", "*tmp*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "**", "*TMP*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "**", "*temp*")),
        *glob.glob(os.path.join(get_checkpoints_dir(), "**", "*TEMP*")),
    ]

    for item in combined:
        if os.path.exists(item):  # May not exist if we deleted a parent directory
            try:
                if os.path.isdir(item) and not os.path.islink(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
            except Exception:
                print(traceback.format_exc())


def retrieve_checkpoint(
    url,
    known_hash,
    folder_name,
    file_name,
    worker,
    progress_label,
    elapsed_progress,
    current_item_weight,
):
    custom_progress_bar = CustomProgressBar(
        worker, progress_label, elapsed_progress, current_item_weight
    )
    return pooch.retrieve(
        url,
        known_hash,
        path=os.path.join(get_checkpoints_dir(), folder_name),
        fname=file_name,
        downloader=pooch.HTTPDownloader(progressbar=custom_progress_bar),
    )


def _download_checkpoints(worker):
    # We will delete temporary files and pooch verifies SHA hashes before downloading anything...
    # In this `verifying` state, nothing will be displayed
    # If pooch needs to download anything, then CustomProgressBar will update progress accordingly
    worker._push_event(
        "setupProgress",
        {
            "state": "verifying",
            "label": "",
            "value": 0,
        },
    )

    delete_tmp_downloads()

    TSR_WEIGHT = 0.75
    DINO_WEIGHT = 0.15
    U2NET_WEIGHT = 0.08
    JSON_WEIGHT = (1 - (TSR_WEIGHT + DINO_WEIGHT + U2NET_WEIGHT)) / 3

    elapsed_progress = 0

    retrieve_checkpoint(
        "https://huggingface.co/stabilityai/TripoSR/resolve/main/model.ckpt",
        "sha256:429e2c6b22a0923967459de24d67f05962b235f79cde6b032aa7ed2ffcd970ee",
        "tsr",
        "model.ckpt",
        worker,
        "Downloading TripoSR weights",
        elapsed_progress,
        TSR_WEIGHT,
    )
    elapsed_progress += TSR_WEIGHT

    retrieve_checkpoint(
        "https://huggingface.co/stabilityai/TripoSR/resolve/main/config.yaml",
        "sha256:74ca708ce086bf68e97709ea6b3d91f14717921c04691e84043f0eb8fcc68e62",
        "tsr",
        "config.yaml",
        worker,
        "Downloading TripoSR metadata",
        elapsed_progress,
        JSON_WEIGHT,
    )
    elapsed_progress += JSON_WEIGHT

    retrieve_checkpoint(
        "https://huggingface.co/facebook/dino-vitb16/resolve/main/pytorch_model.bin",
        "sha256:a064e36c67289caaa5c949c0b3f7f31a0fcbcba5721f5fa12419933ec1f4fe6e",
        "dino-vitb16",
        "pytorch_model.bin",
        worker,
        "Downloading DINO weights",
        elapsed_progress,
        DINO_WEIGHT,
    )
    elapsed_progress += DINO_WEIGHT

    retrieve_checkpoint(
        "https://huggingface.co/facebook/dino-vitb16/resolve/main/config.json",
        "sha256:b87c0270b97db085fd82cf114a761fd0f62ae7914fbd407c752a2260646b689c",
        "dino-vitb16",
        "config.json",
        worker,
        "Downloading DINO metadata",
        elapsed_progress,
        JSON_WEIGHT,
    )
    elapsed_progress += JSON_WEIGHT

    retrieve_checkpoint(
        "https://huggingface.co/facebook/dino-vitb16/resolve/main/preprocessor_config.json",
        "sha256:44298553bf686c8c3d1b128f24fae01f76235f66bda5516f1c6c0c57bba1b47f",
        "dino-vitb16",
        "preprocessor_config.json",
        worker,
        "Downloading DINO metadata",
        elapsed_progress,
        JSON_WEIGHT,
    )
    elapsed_progress += JSON_WEIGHT

    retrieve_checkpoint(
        "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx",
        "sha256:8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491",
        "u2net",
        "u2net.onnx",
        worker,
        "Downloading u2net weights",
        elapsed_progress,
        U2NET_WEIGHT,
    )
    elapsed_progress += U2NET_WEIGHT

    worker._push_event(
        "setupProgress",
        None,
    )


def download_checkpoints(worker):
    with wakepy.keep.running():
        print("download_checkpoints: Entered wake lock")
        _download_checkpoints(worker)
    print("download_checkpoints: Wake lock released!")
