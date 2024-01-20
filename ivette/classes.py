import subprocess
import threading


class CommandRunner:
    def __init__(self):
        self.process = None

    def run_command(self, command, job_id):
        with open(f"tmp/{job_id}.out", "w", encoding='utf-8') as output_file:
            self.process = subprocess.Popen(
                command,
                stdout=output_file,
                stderr=subprocess.STDOUT,
                shell=True,
            )

    def stop(self):
        if self.process is not None:
            self.process.terminate()

    def wait_until_done(self):
        if self.process is not None:
            self.process.wait()


class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
