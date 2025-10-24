import subprocess
import os

hostname = "Test-Pod"
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