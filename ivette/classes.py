import subprocess
import os
import signal

class CommandRunner:
    def __init__(self):
        self.process = None
        self.pid = None
        self.child_pids = []

    def run_command(self, command, job_id):
        with open(f"tmp/{job_id}.out", "w", encoding='utf-8') as output_file:
            self.process = subprocess.Popen(
                command,
                stdout=output_file,
                stderr=subprocess.STDOUT,
                shell=True,
            )
            self.pid = self.process.pid

    def get_child_pids(self):
        ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % self.pid, shell=True, stdout=subprocess.PIPE)
        ps_output = ps_command.stdout.read()
        retcode = ps_command.wait()
        for pid_str in ps_output.decode('utf-8').split("\n")[:-1]:
            self.child_pids.append(int(pid_str.strip()))
        return self.child_pids

    def stop(self):
        if self.process is not None:
            # Terminate and wait for child processes
            for child_pid in self.get_child_pids():
                try:
                    os.kill(child_pid, signal.SIGTERM)
                    os.waitpid(child_pid, 0)  # wait for child process to terminate
                except ChildProcessError:
                    # Ignore the error if the child process has already terminated
                    pass
            # Terminate the main process
            self.process.terminate()
            # Wait for the main process to terminate
            self.process.wait()

    def wait_until_done(self):
        if self.process is not None:
            # Wait for the main process
            self.process.wait()

            # Wait for all child processes
            for child_pid in self.get_child_pids():
                try:
                    os.waitpid(child_pid, 0)
                except ChildProcessError:
                    # The child process has already finished, so we can ignore this error
                    pass
