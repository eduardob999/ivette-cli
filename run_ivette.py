"CLI main executable for ivette."
# Standard library imports
import argparse
import os
import json
import site
import sys

# Local imports
from ivette.processing import run_job
from ivette.decorators import main_process
from ivette.utils import print_color


def load_config():
    # Define possible paths for the configuration file
    paths = [
        os.path.join(sys.prefix, 'ivette-client', 'config.json'),
        "config.json",
        os.path.join(site.USER_BASE, 'ivette-client', 'config.json')
    ]

    # Iterate over the possible paths
    for config_path in paths:
        if os.path.exists(config_path):
            # If the file exists, open and load the JSON
            with open(config_path) as f:
                return json.load(f)

    # If no file was found, return a default configuration
    return {'version': "Unable to read version"}


@main_process("Ivette CLI has been terminated gracefully.")
def main():
    "Main program thread."
    dev = False

    # Loading the configuration file
    config = load_config()

    # Creating the parser
    parser = argparse.ArgumentParser(
        description="""Python client for Ivette Computational chemistry and
        Bioinformatics project"""
    )
    # Creating a mutually exclusive group for 'load' and 'run' flags
    group = parser.add_mutually_exclusive_group()
    # Adding flags
    parser.add_argument('--dev', action='store_true', help='Development flag')
    group.add_argument("--load", help="Load a file", metavar="filename")
    group.add_argument("--project", help="Load a Project", metavar="directory")
    group.add_argument("--job", help="Download a job input", metavar="jobId")
    group.add_argument("--calc", help="Download a job output", metavar="jobId")
    group.add_argument("--species", help="Download a species", metavar="species")
    group.add_argument("--np", help="Download a calculation", metavar="nprocess")
    group.add_argument("--cancel", help="Calcel a job", metavar="jobId")
    group.add_argument("--off", help="Turn off a server", metavar="serverId")
    group.add_argument("--version", help="Show version", action="store_true")
    group.add_argument("--skip", help="Skip a job", metavar="jobId")
    args = parser.parse_args()

    # Header
    print_color("-" * 40, "32")
    print_color("IVETTE CLI", "32;1")
    print_color("by Eduardo Bogado (2023) (C)", "34")  # 34 blue
    print_color("-" * 40, "34")
    if args.dev:
        print_color("Running in development mode", "32")
        dev = True

    # Running the main program
    if args.version:
        print_color(f"IVETTE-CLIENT version {config['version']}", "32")
    elif args.np:
        print_color(
            f"A total of {args.np} threads will be used to run jobs", "32")
        run_job(maxproc=args.np, dev=dev)
    else:
        print_color(
            f"A total of {os.cpu_count()} threads will be used to run jobs", "32")
        # Validation loop
        while True:
            response = input("Do you want to continue? [Y/n]: ")
            if response.lower() == "n":
                raise KeyboardInterrupt
            if response.lower() == "y":
                run_job(dev=dev)
                break
            else:
                print("Invalid input. Please enter 'Y' or 'n'.")


if __name__ == "__main__":
    main()
