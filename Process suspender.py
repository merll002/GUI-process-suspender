import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import json
import webbrowser

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

def open_pstools_download_page():
    webbrowser.open("https://docs.microsoft.com/en-us/sysinternals/downloads/pstools")

def prompt_for_pstools_folder():
    dialog = tk.Toplevel(root)
    dialog.title("PSTools Configuration")

    tk.Label(dialog, text="Please select PSTools folder.\nIf it's not installed, click \"Open link\" to open the download page.\nA config file will be created in the current directory.").pack(pady=10)
    
    def on_open_link():
        open_pstools_download_page()

    def on_ok():
        dialog.destroy()
        select_pstools_folder()

    tk.Button(dialog, text="Open link", command=on_open_link).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(dialog, text="Ok", command=on_ok).pack(side=tk.RIGHT, padx=10, pady=10)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

def select_pstools_folder():
    folder_path = filedialog.askdirectory(title="Select PSTools Folder")
    if folder_path:
        config['pstools_path'] = folder_path
        save_config(config)

def get_pid_from_name(process_name):
    pstools_path = config.get('pstools_path')
    pslist_path = os.path.join(pstools_path, "pslist.exe")

    try:
        result = subprocess.run([pslist_path, "-t", process_name], capture_output=True, text=True, check=True)
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

def suspend_task():
    input_value = input_entry.get()
    if not input_value:
        messagebox.showwarning("Input Error", "Please enter a PID or process name.")
        return

    pid = input_value if input_value.isdigit() else get_pid_from_name(input_value)
    if not pid:
        messagebox.showerror("Error", f"Failed to find process with name '{input_value}'.")
        return

    pstools_path = config.get('pstools_path')
    if not pstools_path:
        messagebox.showwarning("Configuration Error", "PSTools folder is not configured.")
        return

    pssuspend_path = os.path.join(pstools_path, "pssuspend.exe")
    try:
        subprocess.run([pssuspend_path, pid], check=True)
        messagebox.showinfo("Success", f"Process with PID '{pid}' suspended successfully.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Failed to suspend process with PID '{pid}'.")

def resume_task():
    input_value = input_entry.get()
    if not input_value:
        messagebox.showwarning("Input Error", "Please enter a PID or process name.")
        return

    pid = input_value if input_value.isdigit() else get_pid_from_name(input_value)
    if not pid:
        messagebox.showerror("Error", f"Failed to find process with name '{input_value}'.")
        return

    pstools_path = config.get('pstools_path')
    if not pstools_path:
        messagebox.showwarning("Configuration Error", "PSTools folder is not configured.")
        return

    pssuspend_path = os.path.join(pstools_path, "pssuspend.exe")
    try:
        subprocess.run([pssuspend_path, "-r", pid], check=True)
        messagebox.showinfo("Success", f"Process with PID '{pid}' resumed successfully.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Failed to resume process with PID '{pid}'.")

# Load configuration
config = load_config()

# Create the main window
root = tk.Tk()
root.title("Process Suspend/Resume")

# PSTools folder configuration
if 'pstools_path' not in config:
    prompt_for_pstools_folder()

# Menu for selecting PSTools folder
menubar = tk.Menu(root)
config_menu = tk.Menu(menubar, tearoff=0)
config_menu.add_command(label="Select PSTools Folder", command=select_pstools_folder)
menubar.add_cascade(label="Configuration", menu=config_menu)
root.config(menu=menubar)

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

# Run the main event loop
root.mainloop()
