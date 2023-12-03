#Bring in Relevant Packages for UI
import tkinter as tk
from tkinter import filedialog
import os
import psutil
from tqdm import tqdm
import matplotlib.pyplot as plt

def get_size(bytes, suffix="B"):
    """Convert bytes to human-readable formats (e.g., KB, MB, GB, etc.)."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_file_size_for_extensions(drive, extensions):
    """Get the total size of files with specific extensions in a drive."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(drive):
        for file in filenames:
            if any(file.endswith(ext) for ext in extensions):
                total_size += os.path.getsize(os.path.join(dirpath, file))
    return total_size

def scan_drive():
    drive = path_entry.get()
    if not drive:
        drive = "/"

    partitions = [type('', (), {"mountpoint": drive})()] if drive else psutil.disk_partitions()

    total_space = 0
    total_free_space = 0
    total_ckptsafetensors_size = 0
    log_output = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            log_output.append(f"Skipping {partition.mountpoint} due to permission error\n")
            continue

        ckptsafetensors_size = get_file_size_for_extensions(partition.mountpoint, [".ckpt", ".safetensors"])
        drive_name = partition.device if hasattr(partition, 'device') else drive
        log_output.append(f"\nDrive {drive_name}:")
        log_output.append(f"  Total Space: {get_size(usage.total)}")
        log_output.append(f"  Space taken by .ckpt and .safetensors files: {get_size(ckptsafetensors_size)}")
        log_output.append(f"  Free Space: {get_size(usage.free)}")
        total_space += usage.total
        total_free_space += usage.free
        total_ckptsafetensors_size += ckptsafetensors_size

    log_output.append("\nTOTAL space taken by all drives: {}".format(get_size(total_space)))
    log_output.append("TOTAL free space across all drives: {}".format(get_size(total_free_space)))
    log_output.append("TOTAL space taken by .ckpt and .safetensors files: {}".format(get_size(total_ckptsafetensors_size)))

    # Display results in the text widget
    output_text.delete("1.0", tk.END)  # Clear existing text
    for line in log_output:
        output_text.insert(tk.END, line + "\n")

    # Generate and display the chart
    drives = [partition.device if hasattr(partition, 'device') else drive for partition in partitions]
    total_spaces = [usage.total for usage in [psutil.disk_usage(p.mountpoint) for p in partitions]]
    ckpt_safetensor_sizes = [get_file_size_for_extensions(p.mountpoint, [".ckpt", ".safetensors"]) for p in partitions]
    free_spaces = [usage.free for usage in [psutil.disk_usage(p.mountpoint) for p in partitions]]

    bar_width = 0.25
    r1 = range(len(drives))
    r2 = [x + bar_width for x in r1]
    r3 = [x + bar_width for x in r2]

    plt.bar(r1, total_spaces, color='blue', width=bar_width, edgecolor='grey', label='Total Space')
    plt.bar(r2, ckpt_safetensor_sizes, color='gold', width=bar_width, edgecolor='grey', label='.ckpt & .safetensors Size')
    plt.bar(r3, free_spaces, color='purple', width=bar_width, edgecolor='grey', label='Free Space')

    plt.xlabel('Drives', fontweight='bold')
    plt.xticks([r + bar_width for r in range(len(drives))], drives)
    plt.legend()
    plt.show()

# Create the main window
root = tk.Tk()
root.title("Stable Diffusion Model Space Analyzer")

# Add a label with your name/credit
credit_label = tk.Label(root, text="Made By SixSigmaEngineer", font=("Arial", 10, "italic"))
credit_label.pack(side=tk.BOTTOM)  # You can change 'tk.BOTTOM' to 'tk.TOP' if you prefer it at the top

# Add a label and entry widget for the drive path
path_label = tk.Label(root, text="Enter drive or folder path:")
path_label.pack()

path_entry = tk.Entry(root)
path_entry.pack()

# Add a button to start scanning
scan_button = tk.Button(root, text="Scan", command=scan_drive)
scan_button.pack()

# Text widget to display output
output_text = tk.Text(root, height=10, width=50)
output_text.pack()

# Run the application
root.mainloop()
