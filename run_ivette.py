"CLI main executable for ivette."
import argparse
import os

from ivette.processes import run_job
from ivette.decorators import main_process
from ivette.utils import print_color


@main_process("Ivette CLI has been terminated gracefully.")
def main():
    "Main program thread."
    parser = argparse.ArgumentParser(
        description="""Python client for Ivette Computational chemistry and
        Bioinformatics project"""
    )

    # Creating a mutually exclusive group for 'load' and 'run' flags
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--load", help="Load a file", metavar="filename")
    group.add_argument("--project", help="Load a Project", metavar="directory")
    group.add_argument("--job", help="Download a job input", metavar="jobId")
    group.add_argument("--calc", help="Download a job output", metavar="jobId")
    group.add_argument(
        "--species", help="Download a species", metavar="species")
    group.add_argument(
        "--np", help="Download a calculation", metavar="nprocess")
    group.add_argument("--cancel", help="Calcel a job", metavar="jobId")
    group.add_argument("--off", help="Turn off a server", metavar="serverId")
    group.add_argument("--version", help="Show version", action="store_true")
    group.add_argument("--skip", help="Skip a job", metavar="jobId")

    # group.add_argument("--run", help="Run the program", action="store_true")

    args = parser.parse_args()

    # Header
    print_color("-" * 40, "32")
    # 32 is the ANSI code for green, 1 makes it bold
    print_color("IVETTE CLI", "32;1")
    print_color("by Eduardo Bogado (2023) (C)", "34")  # 34 blue
    print_color("-" * 40, "34")

    # Accessing the values of the mutually exclusive flags
    if args.version:

        print_color("IVETTE CLI version 0.3.7", "32")

    elif args.skip:

        print(f"Skipping job {args.skip}...")
        pass
        print_color("Done!", "32")

    elif args.cancel:

        if args.cancel == "all":

            print(f"Warning: Canceling all jobs...")
            pass
            print_color("Done!", "32")

        else:

            print(f"Canceling job {args.cancel}...")
            pass
            print_color("Done!", "32")

    elif args.load:

        pass

    elif args.project:

        pass

    elif args.job:

        print(f"Downloading job {args.job}...")
        pass
        print_color("✓ Done!", "32")

    elif args.calc:

        print(f"Downloading calculation {args.calc}...")
        pass
        print_color("✓ Done!", "32")

    elif args.species:

        print(f"Downloading species {args.species}...")
        pass
        print_color("✓ Done!", "32")

    elif args.off:

        print(f"Requesting {args.off} server turn off...")
        pass
        print_color("✓ Done!", "32")

    elif args.np:

        print_color(
            f"A total of {args.np} threads will be used to run jobs", "32")
        pass

    else:

        print_color(
            f"A total of {os.cpu_count()} threads will be used to run jobs", "32")
        # Validation loop
        while True:
            response = input("Do you want to continue? [Y/n]: ")
            if response.lower() == "n":
                break
            if response.lower() == "y":
                run_job()
            else:
                print("Invalid input. Please enter 'Y' or 'n'.")


if __name__ == "__main__":
    main()
