import os
import sys
import time

try:
    import psutil
except ImportError:
    print("Error: The 'psutil' library is required.")
    print("Please install it using: pip install psutil")
    sys.exit(1)

# --- CONFIGURATION TARGETS ---
CPU_THRESHOLD_PCT = 5.0      # Safe to shutdown if CPU usage is below 5%
LOAD_THRESHOLD = 0.5         # Safe to shutdown if 1-minute load average is below 0.5
CHECK_INTERVAL_SEC = 30      # Time to wait between resource checks
REQUIRED_IDLE_COUTUTES = 3   # Must pass the check 3 consecutive times to shutdown

def is_system_idle():
    """Checks if the system processes are below the consumption thresholds."""
    # 1. Check current CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # 2. Check 1-minute CPU load average
    load_1min, _, _ = os.getloadavg()
    
    # 3. Check active non-root SSH/user connections (optional safety check)
    current_users = len(psutil.users())
    
    print(f"[Check] CPU: {cpu_usage}% | Load Avg: {load_1min} | Active Users: {current_users}")
    
    # Verify if resources are clear
    if cpu_usage < CPU_THRESHOLD_PCT and load_1min < LOAD_THRESHOLD:
        return True
    return False

def safe_shutdown():
    """Monitors the system and executes shutdown when idle targets are met."""
    print("Starting idle monitoring for safe shutdown...")
    idle_strikes = 0
    
    while True:
        if is_system_idle():
            idle_strikes += 1
            print(f"-> System is idle. ({idle_strikes}/{REQUIRED_IDLE_COUTUTES})")
        else:
            idle_strikes = 0
            print("-> System is busy. Resetting idle counter.")
            
        if idle_strikes >= REQUIRED_IDLE_COUTUTES:
            print("System has been consistently idle. Initiating shutdown now...")
            # Execute Linux shutdown command (requires sudo privileges)
            os.system("sudo shutdown -h now")
            break
            
        time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    # Check for root/sudo privileges needed for shutdown
    if os.geteuid() != 0:
        print("Warning: This script must be run with 'sudo' to successfully execute shutdown.")
    
    safe_shutdown()
