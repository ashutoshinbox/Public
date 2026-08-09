import subprocess


def run_command(command: str):

    print(f"\n[LINUX] {command}")

    result = subprocess.run(
        command,
        shell=True,
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

    return run_command(
        "top -bn1 | head -n 5"
    )


def check_memory():

    return run_command(
        "free -h"
    )


def check_disk():

    return run_command(
        "df -h /"
    )


def check_uptime():

    return run_command(
        "uptime"
    )


def cleanup_tmp():

    print(
        "\n[LINUX] Removing files older than 7 days from /tmp"
    )

    return run_command(
        "find /tmp -type f -mtime +7 -print -delete"
    )


def verify_disk():

    return run_command(
        "df -h /"
    )


TOOLS = {

    "check_cpu": check_cpu,

    "check_memory": check_memory,

    "check_disk": check_disk,

    "check_uptime": check_uptime,

    "cleanup_tmp": cleanup_tmp,

    "verify_disk": verify_disk,
}