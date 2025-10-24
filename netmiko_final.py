from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.61"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
    "conn_timeout": 60,
}

def gigabit_status(ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": "admin",
        "password": "cisco",
        "conn_timeout": 60,
    }
    try:
        with ConnectHandler(**device_params) as ssh:
            ssh.disable_paging()
            # พยายามใช้ TextFSM ก่อน
            try:
                result = ssh.send_command("show ip interface brief", use_textfsm=True)
                if isinstance(result, list):
                    gi_lines = []
                    up = down = admin_down = 0
                    for row in result:
                        if str(row.get("interface","")).startswith("GigabitEthernet"):
                            st = row.get("status","").lower()
                            gi_lines.append(f"{row.get('interface')} {row.get('status')}")
                            if st == "up":
                                up += 1
                            elif st == "down":
                                down += 1
                            elif "administratively down" in st:
                                admin_down += 1
                    if gi_lines:
                        return ", ".join(gi_lines) + f" -> {up} up, {down} down, {admin_down} administratively down"
                    else:
                        return "No GigabitEthernet interfaces found."
            except Exception:
                pass

            # ถ้าไม่มี TextFSM template ให้ fallback เป็น include filter
            out = ssh.send_command("show ip interface brief | include GigabitEthernet")
            lines = [l for l in out.splitlines() if l.strip()]
            if not lines:
                return "No GigabitEthernet interfaces found."
            return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"

def get_motd(ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": "admin",
        "password": "cisco",
        "conn_timeout": 60,
    }

    try:
        with ConnectHandler(**device_params) as ssh:
            ssh.disable_paging()
            out = ssh.send_command("show banner motd")
            if out and out.strip() and "No banner" not in out and "not configured" not in out:
                return out.strip()
            run = ssh.send_command("show running-config | section banner motd")
            import re
            m = re.search(r"banner\\s+motd\\s+(\\S)([\\s\\S]*?)\\1", run)
            if m:
                return m.group(2).strip()

            if not out.strip() and not run.strip():
                return "Error: No MOTD Configured"
            return "Error: Unable to parse MOTD"
    except Exception as e:
        return f"Error: {str(e)}"