from ivette.networking import get_next_job
from ivette.utils import clean_up
import time
import os


def set_up(dev, server_id=None):
    "returns id and package"
    job = None
    interval = 30  # seconds
    print(
        f"\n>  Checking for jobs...", end="\r", flush=True)

    while True:

        try:

            job = get_next_job(dev)

        except KeyboardInterrupt:
            if job:
                clean_up(job[0])
                # update_job(JOB[0], "interrupted", nproc=0)
                raise SystemExit
            else:
                print("No job to interrupt.            ")
                continue

        if len(job) == 0:
            for remaining in range(interval, 0, -1):
                print(
                    f">  No jobs due. Checking again in {remaining} seconds.",
                    end="\r",
                )
                time.sleep(1)
                # Clear the countdown timer
                print(
                    " "
                    * len(
                        f">  No jobs due. Checking again in {remaining} seconds."
                    ),
                    end="\r",
                )
        else:
            break

    # Create a new folder
    folder_name = "tmp"
    if not os.path.exists(folder_name):
        # If it doesn't exist, create the folder
        os.mkdir(folder_name)

    return job
