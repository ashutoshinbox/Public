import subprocess


def run_powershell(command: str):

    print(f"\n[WINDOWS] {command}")

    result = subprocess.run(

        [
            "powershell",
            "-NoProfile",
            "-Command",
            command
        ],

        capture_output=True,

        text=True,

        timeout=30
    )

    if result.returncode != 0:

        return (
            "COMMAND FAILED\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout.strip()


def check_cpu():

    return run_powershell(
        """
        Get-CimInstance Win32_Processor |
        Select-Object Name,LoadPercentage |
        Format-Table -AutoSize
        """
    )


def check_memory():

    return run_powershell(
        """
        Get-CimInstance Win32_OperatingSystem |
        Select-Object
        @{Name='TotalGB';Expression={
            [math]::Round($_.TotalVisibleMemorySize/1MB,2)
        }},
        @{Name='FreeGB';Expression={
            [math]::Round($_.FreePhysicalMemory/1MB,2)
        }}
        """
    )


def check_disk():

    return run_powershell(
        """
        Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" |
        Select-Object
        DeviceID,
        @{Name='SizeGB';Expression={
            [math]::Round($_.Size/1GB,2)
        }},
        @{Name='FreeGB';Expression={
            [math]::Round($_.FreeSpace/1GB,2)
        }}
        """
    )


def check_uptime():

    return run_powershell(
        """
        (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
        """
    )


def cleanup_tmp():

    print(
        "\n[WINDOWS] Cleaning Windows temporary files"
    )

    command = r"""
    $temp = $env:TEMP

    Get-ChildItem `
        -Path $temp `
        -File `
        -Recurse `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.LastWriteTime -lt (Get-Date).AddDays(-7)
    } |
    Remove-Item `
        -Force `
        -ErrorAction SilentlyContinue

    Write-Output "Temporary file cleanup completed."
    """

    return run_powershell(command)


def verify_disk():

    return check_disk()


TOOLS = {

    "check_cpu": check_cpu,

    "check_memory": check_memory,

    "check_disk": check_disk,

    "check_uptime": check_uptime,

    "cleanup_tmp": cleanup_tmp,

    "verify_disk": verify_disk,
}