def get_total_memory():
    """
    This function returns the total memory on the system in megabytes.

    Returns:
    int: The total memory on the system in megabytes.
    """
    with open('/proc/meminfo', 'r') as mem:
        total_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) == 'MemTotal:':
                total_memory = int(sline[1])
                break
    return total_memory / 1024  # convert from KiB to MB


print(get_total_memory())
