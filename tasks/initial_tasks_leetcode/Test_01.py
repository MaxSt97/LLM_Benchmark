import psutil
import subprocess
import time


def task_func(process_name):
    # Check if the process is running
    is_running = any([proc for proc in psutil.process_iter() if proc.name() == process_name])

    # If the process is running, terminate it
    if is_running:
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                proc.terminate()
        time.sleep(5)
        subprocess.Popen(process_name)
        return f"Process found. Restarting {process_name}."
    else:
        subprocess.Popen(process_name)
        return f"Process not found. Starting {process_name}."
