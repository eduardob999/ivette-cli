import functools
import sys

from ivette.utils import print_color


def main_process(exit_message):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit) as e:
                print_color(f"{exit_message}", "34")
                sys.exit()
        return wrapper
    return decorator
