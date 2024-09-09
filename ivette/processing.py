# Standard lib imports
import os
import threading
import subprocess
import time
from typing import Optional

# Local imports
from ivette.classes import CommandRunner
from ivette.decorators import main_process
from ivette.utils import get_system_info, get_total_memory, trim_file
from ivette.networking import delete_file, download_file, get_next_job, get_temp_filenames, retrieve_url, update_job, upload_file
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
            update_job(job_id, "processing", nproc=0)
            trim_file(f"tmp/{job_id}.out", 1)
            upload_file(f"tmp/{job_id}.out", dev=dev)
            temp_filenames = get_temp_filenames(
                'Temps', job_id, dev)
            if temp_filenames:
                for filename in temp_filenames:
                    delete_file('Temps', filename, dev)


    except subprocess.CalledProcessError as e:
        if not e.returncode == -2:
            update_job(job_id, "failed", nproc=0)
            trim_file(f"tmp/{job_id}.out", 1)
            upload_file(f"tmp/{job_id}.out", dev=dev)
        job_done = True
        job_failed = True
        exit_code = e.returncode
        raise SystemExit from e


def set_up(dev: str, nproc: int, server_id: Optional[str] = None) -> dict:

    # Local variables
    job = None
    interval = 300  # seconds
    folder_name = "tmp"
    memory = get_total_memory()
    interrupted = False

    print("\n>  Checking for jobs...", end="\r", flush=True)

    while True:

        try:

            job = get_next_job(memory=memory, nproc=nproc, dev=dev)

            if len(job) == 0:
                for remaining in range(interval, 0, -1):
                    minutes, seconds = divmod(remaining, 60)
                    timer = f">  No jobs due. Checking again in {minutes} minutes {seconds} seconds."
                    print(timer, end="\r")
                    time.sleep(1)
                    # Clear the countdown timer
                    print(" " * len(timer), end="\r")

            else:

                if not os.path.exists(folder_name):
                    # If it doesn't exist, create the folder
                    os.mkdir(folder_name)

                job_url = retrieve_url('Inputs', job['id'], dev)['url']
                download_file(job_url, job['id'])
                temp_filenames = get_temp_filenames('Temps', job['id'], dev)

                if temp_filenames:
                    print(">  Downloading saved progress", end="\r", flush=True)
                    for filename in temp_filenames:
                        temp_file_url = retrieve_url(
                            'Temps', filename, dev)['url']
                        download_file(temp_file_url, filename)

                return job

        except KeyboardInterrupt:
            if job and len(job) > 0:
                clean_up(job['id'])
                update_job(job['id'], "interrupted", nproc=0, dev=dev)
                raise SystemExit
            else:
                print("\n Exiting, please wait...")
                #get job with setting up status and update
                raise SystemExit


def upload_from_dir(
        directory: str,
        dev: str,
        *excluded_extensions: str,
        exclude_files_without_extension: bool = True,
        instruction: Optional[str] = None,
) -> None:
    """
    Uploads all files from a given directory except those with specified extensions.

    Parameters:
    directory (str): The directory to search for files.
    dev (str): The device to which the files will be uploaded.
    exclude_files_without_extension (bool): If True, files without an extension will also be excluded.
    *excluded_extensions (str): Extensions of the files to be excluded.
    instruction (str, optional): An instruction for the upload. Defaults to None.

    Returns:
    None

    Example:
    >>> upload_all_except_extensions('/path/to/directory', 'device1', True, '.txt', '.docx')
    This will upload all files in '/path/to/directory' to 'device1', excluding files with '.txt', '.docx' extensions and files without an extension.
    """
    for filename in os.listdir(directory):
        # Check if the file's extension is not in the excluded_extensions
        extension = os.path.splitext(filename)[1]
        if (extension not in excluded_extensions and
                not (exclude_files_without_extension and extension == '')):
            upload_file(os.path.join(directory, filename),
                        instruction=instruction, dev=dev)


@main_process('\nProcessing module has been stopped.')
def run_job(*, maxproc=None, dev=False):

    # Global variables
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
    memory = get_total_memory()

    # Set number of processors
    if not maxproc:
        maxproc = int(os.cpu_count())

    server = get_system_info()
    print(f"Running server: - {server.system_id}")
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
        # Convert nproc to int
        job['nproc'] = int(job['nproc'])
        if job['nproc'] < maxproc:
            print(f"Using only {job['nproc']} threads due to low memory.")
            nproc = job['nproc']
        else:
            nproc = maxproc
        run_thread = threading.Thread(
            target=run_nwchem, args=(job_id, nproc, dev))

        try:

            print(f">  Job Id: {job_id}")
            update_job(job_id, "in progress", nproc if nproc else os.cpu_count(
            ), dev=dev, currentMemory=memory)
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
            print(' Exit requested.          \n', flush=True)
            print('Waiting for all running processes to finish...', flush=True)
            command_runner.stop()  # Probably should be waited too
            if run_thread.is_alive():
                run_thread.join()
            if not job_done:

                # Save the current progress
                output_file = f"tmp/{job_id}.out"
                if os.path.exists(output_file):
                    print('Saving current progress, please do NOT close this terminal...', flush=True)
                    trim_file(output_file, 1)
                    upload_file(output_file, dev=dev)
                    upload_from_dir(
                        "tmp", dev, ".out", exclude_files_without_extension=True, instruction="Temps")
                update_job(job_id, "interrupted", nproc=0, dev=dev)
            
            # Clean up the files
            clean_up(job_id)
            print_color("Job interrupted.       ", "34")
            raise SystemExit from e
