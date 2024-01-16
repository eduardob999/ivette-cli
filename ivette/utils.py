import os


def print_color(text, color_code):
    """
    Function to print colored text using ANSI escape codes
    """
    print(f"\033[{color_code}m{text}\033[0m")


def trim_file(filename, desired_size_mb):
    # Calculate the number of lines in the file
    with open(filename, 'r') as file:
        lines = file.readlines()
    total_lines = len(lines)

    # Calculate the current size of the file in MB
    current_size_mb = os.path.getsize(filename) / (1024 * 1024)

    # If the current size is less than or equal to the desired size, do nothing
    if current_size_mb <= desired_size_mb:
        return

    # Calculate the number of lines to keep based on the desired size
    lines_to_keep = int(total_lines * desired_size_mb / current_size_mb)

    # Calculate the number of lines to keep from the beginning and the end
    start_lines = lines_to_keep // 2
    end_lines = lines_to_keep - start_lines

    # Get the lines to keep
    new_lines = lines[
        :start_lines
    ] + [
        '\n\n... this file was trimmed to reduce size\n\n'
    ] + lines[
        -end_lines:
    ]

    # Write the new lines back to the file
    with open(filename, 'w') as file:
        file.writelines(new_lines)
