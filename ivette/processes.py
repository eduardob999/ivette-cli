from ivette.decorators import main_process
from ivette.networking import download_file, get_next_job


@main_process('\nRun module has been stooped.')
def run_job(nproc=None):
    job = get_next_job()
    download_file(job['url'], job['job_id'])