import os
import sys
import traceback
import multiprocessing
import miniaudio
import numpy as np


def looped_sound_stream(filename):
    decoded_file = miniaudio.decode_file(filename)
    decoded_samples = np.array(decoded_file.samples, dtype=np.int16).reshape(
        (-1, decoded_file.nchannels)
    )

    required_frames = yield b""
    current_frame = 0
    while True:
        end_frame = min(len(decoded_samples), current_frame + required_frames)
        required_frames = yield decoded_samples[current_frame:end_frame]
        if end_frame == len(decoded_samples):
            current_frame = 0
        else:
            current_frame = end_frame


class AudioProcessWorker:
    def __init__(self):
        self._in_queue = multiprocessing.Queue()
        self._audio_device = None

    def enqueue(self, item):
        self._in_queue.put(item)

    def run(self):
        while True:
            in_queue_item = self._in_queue.get()

            try:
                item_type = in_queue_item["type"]

                if item_type == "open_playback_device":
                    self.open_playback_device()
                elif item_type == "close_playback_device":
                    self.close_playback_device()
                elif item_type == "play_sound":
                    self.play_sound(in_queue_item["filename"], in_queue_item["loop"])
            except Exception:
                print(traceback.format_exc())

    def open_playback_device(self):
        if not self._has_playback_device():
            self._audio_device = miniaudio.PlaybackDevice()

    def close_playback_device(self):
        if self._has_playback_device():
            self._audio_device.close()

    def play_sound(self, filename, loop):
        if not self._has_playback_device():
            return

        self._stop_current_stream()

        if loop:
            stream = looped_sound_stream(self._get_sound_path(filename))
            next(stream)
        else:
            stream = miniaudio.stream_file(self._get_sound_path(filename))

        # stream = miniaudio.stream_with_callbacks(stream, end_callback=self._stop_audio)
        self._audio_device.start(stream)

    def _stop_current_stream(self):
        if self._has_playback_device():
            self._audio_device.stop()

    def _has_playback_device(self):
        return self._audio_device is not None

    def _get_sound_path(self, sound_filename):
        if os.getenv("MESHFINITY_ENVIRONMENT") == "development":
            return os.path.join(os.path.dirname(__file__), "sounds", sound_filename)
        else:
            return os.path.join(sys._MEIPASS, "sounds", sound_filename)


class AudioProcess:
    def __init__(self):
        self._worker = AudioProcessWorker()
        self._worker_process = multiprocessing.Process(
            target=self._worker.run, daemon=True
        )
        self._worker_process.start()

    def terminate(self):
        self._worker_process.terminate()

    def open_playback_device(self):
        self._worker.enqueue({"type": "open_playback_device"})

    def close_playback_device(self):
        self._worker.enqueue({"type": "close_playback_device"})

    def play_sound(self, filename, loop):
        self._worker.enqueue({"type": "play_sound", "filename": filename, "loop": loop})
