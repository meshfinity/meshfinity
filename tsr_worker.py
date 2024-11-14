import queue
import traceback
import stages
from download_checkpoints import download_checkpoints


class TsrWorker:
    def __init__(self, api):
        self.in_queue = queue.Queue()

        self._current_inputs_id = None
        self._current_stage_name = None

        self._warm_stage_instance = None
        self._warm_stage_name = None

        self._api = api

    def run(self):
        while True:
            in_queue_item = self.in_queue.get()
            id = in_queue_item["id"]
            inputs = in_queue_item["inputs"]

            self._current_inputs_id = id
            self._current_stage_name = inputs["stage"]

            try:
                if inputs["stage"] == "setup":
                    download_checkpoints(self)
                else:
                    if self._warm_stage_name != inputs["stage"]:
                        self._warm_stage_name = inputs["stage"]
                        self._warm_stage_instance = getattr(stages, inputs["stage"])()
                    self._warm_stage_instance.run(self, inputs)
            except Exception:
                print(traceback.format_exc())
                self._push_event(
                    "error",
                    {"traceback": traceback.format_exc()},
                )

            self._current_inputs_id = None

    def push_inputs(self, id, inputs):
        self.in_queue.put(
            {
                "id": id,
                "inputs": inputs,
            }
        )

    def kill_running_processes(self):
        if self._warm_stage_instance is not None:
            self._warm_stage_instance.kill_running_processes()

    def _push_event(self, type, event):
        self._api._push_event(
            self._current_inputs_id, self._current_stage_name, type, event
        )
