import subprocess
import os
import re

student_id = "66070084"
def get_hostname_from_ip(ip_address):
    try:
        with open("hosts", "r") as f:
            for line in f:
                match = re.search(r"^\s*([\w\d\-_]+)\s+ansible_host=([\d\.]+)", line)
                if match:
                    hostname = match.group(1)
                    ip = match.group(2)
                    if ip == ip_address:
                        return hostname
    except Exception as e:
        print(f"Error reading hosts file: {e}")
        return None
    return None

def showrun(ip):
    hostname = get_hostname_from_ip(ip)
    
    if not hostname:
        return f"Error: IP {ip} not found in 'hosts' file."
    output_filename = f"show_run_{student_id}_{hostname}.txt"
    if os.path.exists(output_filename):
        os.remove(output_filename)

    cmd = [
        "ansible-playbook",
        "playbook_motd.yaml", 
        "-i", "hosts",
        "--limit", ip,
        "--extra-vars", f"student_id={student_id} username=admin password=cisco"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0 and os.path.exists(output_filename):
            return output_filename
        else:
            print("----- Ansible STDOUT (Error showrun) -----")
            print(result.stdout)
            print("----- Ansible STDERR (Error showrun) -----")
            print(result.stderr)
            return "Error: Ansible"
            
    except subprocess.TimeoutExpired:
        return f"Error: Ansible command timed out for {ip}"
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
