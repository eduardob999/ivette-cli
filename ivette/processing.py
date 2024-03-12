# Standard lib imports
import os
import threading
import subprocess

# Local imports
from ivette.classes import CommandRunner
from ivette.decorators import main_process
from ivette.utils import get_total_memory, set_up, trim_file
from ivette.networking import download_file, retrieve_url, update_job, upload_file
from ivette.utils import clean_up, is_nwchem_installed, print_color, waiting_message

# Global variables
job_done = False
job_failed = False
operation = None
exit_status = None
exit_code = None
command_runner = CommandRunner()


def run_nwchem(job_id, nproc, dev):
    """
    Run the calculation
    """

    global job_done
    global job_failed
    global exit_status
    global exit_code
    global command_runner

    if nproc:
        command = [
            f"mpirun -np {nproc} --use-hwthread-cpus --allow-run-as-root /usr/bin/nwchem tmp/{job_id}"]
    else:
        command = [
            f"mpirun -map-by core --use-hwthread-cpus --allow-run-as-root /usr/bin/nwchem tmp/{job_id}"]

    try:
        # Use the instance to run the command
        command_runner.run_command(command, job_id=job_id)
        command_runner.wait_until_done()

        if not exit_status:

            job_done = True

            if operation and operation.upper() == "OPTIMIZE":
                update_job(job_id, "processing", nproc=0)
                trim_file(f"tmp/{job_id}.out", 1)
                upload_file(f"tmp/{job_id}.out", dev=dev)
            else:
                update_job(job_id, "processing", nproc=0)
                trim_file(f"tmp/{job_id}.out", 1)
                upload_file(f"tmp/{job_id}.out", dev=dev)

    except subprocess.CalledProcessError as e:
        if not e.returncode == -2:
            update_job(job_id, "failed", nproc=0)
            upload_file(f"tmp/{job_id}.out", dev=dev)
        job_done = True
        job_failed = True
        exit_code = e.returncode
        raise SystemExit from e


@main_process('\nProcessing module has been stopped.')
def run_job(*, maxproc=None, dev=False):

    global job_done
    global operation
    global job_failed
    global exit_status
    global command_runner

    # Local variables
    job_id = None
    package = None
    operation = None
    maxproc = int(maxproc) if maxproc else None

    # Set number of processors
    if not maxproc:
        maxproc = os.cpu_count()
    print("Running server: - ")
    print("Press Ctrl + C at any time to exit.")

    # Loop over to run the queue
    while True:
        
        # Check if NWChem is installed
        if not is_nwchem_installed():
            print("NWChem is not installed.")
            raise SystemExit
        
        job = set_up(dev, maxproc)
        job_id = job['id']
        package = job['package']
        operation = job['operation']
        if job['nproc'] < maxproc:
            print(f"Using only {job['nproc']} threads due to low memory.")
            nproc = job['nproc']
        else:
            nproc = maxproc
        url = retrieve_url('Inputs', job_id, dev)['url']
        download_file(url, job_id)
        run_thread = threading.Thread(
            target=run_nwchem, args=(job_id, nproc, dev))

        try:

            print(f">  Job Id: {job_id}")
            update_job(job_id, "in progress", nproc if nproc else os.cpu_count(), dev=dev, currentMemory=get_total_memory())
            run_thread.start()
            while not job_done:
                waiting_message(package)
            run_thread.join()
            clean_up(job_id)
            if not job_failed:
                print_color("✓ Job completed successfully.", "32")
            else:
                print(f"\n\n Job failed with exit code {exit_code}.")
            job_done = False
            job_failed = False

        except KeyboardInterrupt as e:

            exit_status = True
            print(' Exit requested.          ', flush=True)
            print('Waiting for all running processes to finish...', flush=True)
            command_runner.stop()  # Probably should be waited too
            if run_thread.is_alive():
                run_thread.join()
            if not job_done:
                update_job(job_id, "interrupted", nproc=0, dev=dev)
            clean_up(job_id)
            print_color("Job interrupted.       ", "34")
            raise SystemExit from e
