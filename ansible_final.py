import subprocess
import os

hostname = "Exam"
student_id = "66070084"
output_filename = f"show_run_{student_id}_{hostname}.txt"

def showrun():
    ip = "10.0.15.61"  # หรือ IP ตายตัว
    output_filename = "show_run_static.txt"
    cmd = [
        "ansible-playbook",
        "playbook_showrun.yaml",
        "-i", f"{ip},",
        "--extra-vars", "username=admin password=cisco"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result.stdout.strip())
        if result.returncode == 0 and os.path.exists(output_filename):
            return output_filename
        return "Error: Failed to get running-config"
    except Exception as e:
        return f"Error: {str(e)}"

def motd(ip, message):
    command = [
        "ansible-playbook",
        "playbook_motd.yaml",
        "-i", f"{ip},",
        "--extra-vars",
        f'motd_message={message} username=admin password=cisco'
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    print("----- Ansible STDOUT -----")
    print(result.stdout)
    print("----- Ansible STDERR -----")
    print(result.stderr)

    if 'failed=0' in result.stdout:
        return "Ok: success"
    else:
        return "Error: No MOTD Configured"
