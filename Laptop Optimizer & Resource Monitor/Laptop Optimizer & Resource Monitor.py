import psutil
import platform
import wmi
import subprocess
import time
from datetime import datetime

def get_system_specs():
    """Retrieve detailed system specifications."""
    specs = {
        "OS": platform.system() + " " + platform.release(),
        "Processor": platform.processor(),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Cores": psutil.cpu_count(logical=True),
        "Total Memory (GB)": psutil.virtual_memory().total / (1024 ** 3),
        "Disk Total (GB)": psutil.disk_usage('/').total / (1024 ** 3)
    }
    if platform.system() == "Windows":
        c = wmi.WMI()
        for computer in c.Win32_ComputerSystem():
            specs["Manufacturer"] = computer.Manufacturer
            specs["Model"] = computer.Model
        for os in c.Win32_OperatingSystem():
            specs["OS Build"] = os.BuildNumber
    return specs

def get_cpu_usage():
    """Get current CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Get current memory usage percentage and details."""
    memory = psutil.virtual_memory()
    total_gb = memory.total / (1024 ** 3)
    used_gb = memory.used / (1024 ** 3)
    percent = memory.percent
    return percent, used_gb, total_gb

def get_disk_usage():
    """Get current disk usage percentage and details for the root drive."""
    disk = psutil.disk_usage('/')
    total_gb = disk.total / (1024 ** 3)
    used_gb = disk.used / (1024 ** 3)
    percent = disk.percent
    return percent, used_gb, total_gb

def get_high_resource_processes(threshold_cpu=20.0, threshold_memory=100.0):
    """Identify processes consuming high CPU or memory (memory in MB)."""
    high_resource_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            cpu = proc.info['cpu_percent']
            memory_mb = proc.info['memory_info'].rss / (1024 ** 2)
            if cpu > threshold_cpu or memory_mb > threshold_memory:
                high_resource_procs.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': cpu,
                    'memory_mb': memory_mb
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(high_resource_procs, key=lambda x: x['cpu_percent'] + x['memory_mb'], reverse=True)

def terminate_process(pid, name):
    """Safely terminate a process by PID with error handling."""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=3)
        return f"Terminated process {name} (PID: {pid})"
    except psutil.NoSuchProcess:
        return f"Process {name} (PID: {pid}) no longer exists"
    except psutil.AccessDenied:
        return f"Access denied to terminate {name} (PID: {pid})"
    except psutil.TimeoutExpired:
        return f"Failed to terminate {name} (PID: {pid}) within timeout"

def disable_startup_programs():
    """Provide command to disable startup programs on Windows (requires manual execution)."""
    if platform.system() == "Windows":
        return "Run 'msconfig' in Command Prompt and uncheck unnecessary programs under the Startup tab."
    return "Startup program management not supported on non-Windows systems."

def check_windows_11_compatibility():
    """Check if system meets basic Windows 11 requirements."""
    if platform.system() != "Windows":
        return "Windows 11 compatibility check only applicable for Windows systems."
    memory = psutil.virtual_memory().total / (1024 ** 3)  # Total RAM in GB
    cores = psutil.cpu_count(logical=False)
    tpm_check = subprocess.run("powershell -Command Get-Tpm", capture_output=True, text=True, shell=True)
    tpm_present = "TpmPresent : True" in tpm_check.stdout
    requirements_met = memory >= 4 and cores >= 2 and tpm_present
    return {
        "RAM (GB)": memory,
        "Physical Cores": cores,
        "TPM 2.0 Present": tpm_present,
        "Meets Windows 11 Requirements": requirements_met
    }

def optimize_laptop():
    """Check system specs, resource usage, and apply optimizations."""
    # Thresholds from provided system information
    CPU_THRESHOLD = 39.9
    MEMORY_THRESHOLD = 84.8
    DISK_THRESHOLD = 58.1

    # Get system specifications
    print("System Specifications:")
    specs = get_system_specs()
    for key, value in specs.items():
        print(f"{key}: {value}")

    # Get resource usage
    cpu_percent = get_cpu_usage()
    memory_percent, memory_used_gb, memory_total_gb = get_memory_usage()
    disk_percent, disk_used_gb, disk_total_gb = get_disk_usage()

    # Print current system information
    print("\nSystem Resource Usage:")
    print(f"CPU Usage: {cpu_percent:.1f}%")
    print(f"Memory Usage: {memory_percent:.1f}% ({memory_used_gb:.2f}/{memory_total_gb:.2f} GB)")
    print(f"Disk Usage: {disk_percent:.1f}% ({disk_used_gb:.2f}/{disk_total_gb:.2f} GB)")

    # Check for high resource usage
    high_usage_detected = False
    messages = []

    if cpu_percent > CPU_THRESHOLD:
        high_usage_detected = True
        messages.append(f"High CPU usage detected: {cpu_percent:.1f}% (Threshold: {CPU_THRESHOLD}%)")

    if memory_percent > MEMORY_THRESHOLD:
        high_usage_detected = True
        messages.append(f"High memory usage detected: {memory_percent:.1f}% ({memory_used_gb:.2f}/{memory_total_gb:.2f} GB) (Threshold: {MEMORY_THRESHOLD}%)")

    if disk_percent > DISK_THRESHOLD:
        high_usage_detected = True
        messages.append(f"High disk usage detected: {disk_percent:.1f}% ({disk_used_gb:.2f}/{disk_total_gb:.2f} GB) (Threshold: {DISK_THRESHOLD}%)")

    # Identify high-resource processes
    print("\nChecking for high-resource processes...")
    high_procs = get_high_resource_processes(threshold_cpu=20.0, threshold_memory=100.0)
    if high_procs:
        print("High-resource processes detected:")
        for proc in high_procs:
            print(f"- {proc['name']} (PID: {proc['pid']}): CPU {proc['cpu_percent']:.1f}%, Memory {proc['memory_mb']:.2f} MB")
        # Ask user to terminate high-resource processes
        for proc in high_procs[:3]:  # Limit to top 3 to avoid overwhelming
            response = input(f"\nTerminate {proc['name']} (PID: {proc['pid']})? [y/N]: ").strip().lower()
            if response == 'y':
                result = terminate_process(proc['pid'], proc['name'])
                print(result)
    else:
        print("No high-resource processes detected (CPU > 20% or Memory > 100 MB).")

    # Check Windows 11 compatibility
    if platform.system() == "Windows":
        print("\nWindows 11 Compatibility Check:")
        compat = check_windows_11_compatibility()
        for key, value in compat.items():
            print(f"{key}: {value}")

    # Provide optimization suggestions
    if high_usage_detected:
        print("\nWarning: High resource usage detected. Optimization suggestions:")
        print("- Disable unnecessary startup programs: " + disable_startup_programs())
        print("- Update drivers via Device Manager or manufacturer’s website.")
        if platform.system() == "Windows":
            print("- If crashes persist, ensure your laptop meets Windows 11 requirements (TPM 2.0, 4GB RAM, etc.).")
            if not check_windows_11_compatibility()['Meets Windows 11 Requirements']:
                print("- Consider reverting to Windows 10 if hardware is underpowered.")
        print("- Close unnecessary applications to reduce CPU and memory usage.")
        print("- Use a disk analyzer tool (e.g., WinDirStat) to identify large files for manual deletion.")
        print("- Consider upgrading RAM (current: 3.44 GB) to at least 8 GB for better performance.")
        print("- For high CPU usage, check for background services (e.g., Windows Update) and disable non-essential ones.")

        print("\nDetailed Issues:")
        for message in messages:
            print(f"- {message}")

if __name__ == "__main__":
    optimize_laptop()