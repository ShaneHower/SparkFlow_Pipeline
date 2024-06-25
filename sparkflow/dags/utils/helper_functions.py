import psutil

def get_half_system_resources():
    total_memory = psutil.virtual_memory().total // (1024 * 1024 * 1024)
    total_cores = psutil.cpu_count()
    return total_memory // 2, total_cores // 2
