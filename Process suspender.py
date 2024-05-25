import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json
import sys

# Path to configuration file
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def get_pstools_path():
    if getattr(sys, 'frozen', False):
        # If the application is run from a bundle, the files are located in a relative path to the executable
        return os.path.join(sys._MEIPASS, "pstools")
    else:
        # If the script is run normally, the files are in the project directory
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "pstools")

def get_pid_from_name(process_name):
    pstools_path = get_pstools_path()
    pslist_path = os.path.join(pstools_path, "pslist.exe")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        result = subprocess.run([pslist_path, "-t", process_name], capture_output=True, text=True, check=True, startupinfo=startupinfo)
        lines = result.stdout.splitlines()
        process_found = False
        for line in lines:
            if process_found:
                if line.strip().startswith(process_name):
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]  # Return the PID of the main process
            if line.startswith("Name"):
                process_found = True
    except subprocess.CalledProcessError as e:
        print(f"Error running pslist: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def update_status(message, color="black"):
    status_label.config(text=message, fg=color)

def suspend_task():
    input_value = input_entry.get()
    if not input_value:
        update_status("Please enter a PID or process name.", "red")
        return

    pid = input_value if input_value.isdigit() else get_pid_from_name(input_value)
    if not pid:
        update_status(f"Failed to find process with name '{input_value}'.", "red")
        return

    pstools_path = get_pstools_path()
    pssuspend_path = os.path.join(pstools_path, "pssuspend.exe")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        subprocess.run([pssuspend_path, pid], check=True, startupinfo=startupinfo)
        update_status(f"Process with PID '{pid}' suspended successfully.", "green")
    except subprocess.CalledProcessError:
        update_status(f"Failed to suspend process with PID '{pid}'.", "red")

def resume_task():
    input_value = input_entry.get()
    if not input_value:
        update_status("Please enter a PID or process name.", "red")
        return

    pid = input_value if input_value.isdigit() else get_pid_from_name(input_value)
    if not pid:
        update_status(f"Failed to find process with name '{input_value}'.", "red")
        return

    pstools_path = get_pstools_path()
    pssuspend_path = os.path.join(pstools_path, "pssuspend.exe")

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        subprocess.run([pssuspend_path, "-r", pid], check=True, startupinfo=startupinfo)
        update_status(f"Process with PID '{pid}' resumed successfully.", "green")
    except subprocess.CalledProcessError:
        update_status(f"Failed to resume process with PID '{pid}'.", "red")

# Load configuration
config = load_config()

# Create the main window
root = tk.Tk()
root.title("Process Suspend/Resume")

# Create and place the input field
tk.Label(root, text="Enter process PID or name:").pack(pady=5)
input_entry = tk.Entry(root, width=30)
input_entry.pack(pady=5)

# Create and place the Suspend button
suspend_button = tk.Button(root, text="Suspend Task", command=suspend_task)
suspend_button.pack(pady=5)

# Create and place the Resume button
resume_button = tk.Button(root, text="Resume Task", command=resume_task)
resume_button.pack(pady=5)

# Create and place the status label
status_label = tk.Label(root, text="", font=("Helvetica", 10))
status_label.pack(pady=5)

# Run the main event loop
root.mainloop()
