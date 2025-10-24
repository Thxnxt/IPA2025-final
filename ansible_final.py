import subprocess
import os

hostname = "Exam"
student_id = "66070084"
output_filename = f"show_run_{student_id}_{hostname}.txt"

def showrun():
    if os.path.exists(output_filename):
        os.remove(output_filename)

    command = ['ansible-playbook', 'playbook.yaml']
    result = subprocess.run(command, capture_output=True, text=True)
    
    # --- นี่คือส่วนที่แก้ไข ---
    # เราจะพิมพ์ทั้ง stdout (ผลลัพธ์ปกติ) และ stderr (ผลลัพธ์ Error)
    print("----- Ansible STDOUT -----")
    print(result.stdout)
    print("----- Ansible STDERR (Error) -----")
    print(result.stderr) # <-- เพิ่มบรรทัดนี้เพื่อดู Error ที่แท้จริง
    print("----- End Ansible Output -----")

    # เราจะเช็คผลลัพธ์จาก stdout เหมือนเดิม
    # แต่ตอนนี้เราจะเห็น Error ที่แท้จริงใน Terminal แล้ว
    if 'failed=0' in result.stdout:
        return output_filename
    else:
        return "Error: Ansible playbook failed. Please check terminal for errors."

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
