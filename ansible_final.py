import subprocess
import os
import datetime

hostname = "Exam"
student_id = "66070084"
output_filename = f"show_run_{student_id}_{hostname}.txt"

def showrun(ip):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"show_run_{student_id}_{ip}_{ts}.txt"
    cmd = [
        "ansible-playbook",
        "playbook_showrun.yaml",
        "-i", f"{ip},",
        "--extra-vars", "username=admin password=cisco"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(result.stdout.strip() + "\n")
        if result.stderr:
            f.write("\n----- STDERR -----\n")
            f.write(result.stderr.strip() + "\n")
    if (result.returncode == 0 or "failed=0" in result.stdout) and os.path.getsize(output_filename) > 0:
        return output_filename
    return f"Error: Failed to get running-config for {ip}"

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
