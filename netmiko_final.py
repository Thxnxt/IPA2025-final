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
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": "admin",
        "password": "cisco",
        "fast_cli": True
    }

    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            ssh.disable_paging()
            
            # พยายามใช้ TextFSM ถ้ามี template
            try:
                result = ssh.send_command("show ip interface brief", use_textfsm=True)
                if isinstance(result, list):
                    gigabits = [row for row in result if row.get('interface', '').startswith("GigabitEthernet")]
                    
                    interface_messages = []
                    count_up = count_down = count_admin_down = 0

                    for row in gigabits:
                        name = row.get('interface', '')
                        status = row.get('status', '').lower()
                        
                        if status == 'up':
                            interface_messages.append(f"{name} up")
                            count_up += 1
                        elif status == 'down':
                            interface_messages.append(f"{name} down")
                            count_down += 1
                        elif 'administratively down' in status:
                            interface_messages.append(f"{name} administratively down")
                            count_admin_down += 1
                        else:
                            interface_messages.append(f"{name} {status}")

                    if interface_messages:
                        summary = f" -> {count_up} up, {count_down} down, {count_admin_down} administratively down"
                        return ", ".join(interface_messages) + summary
                    else:
                        return "No GigabitEthernet interfaces found."
            except Exception:
                pass  # ถ้าไม่มี TextFSM template จะใช้ regex ด้านล่างแทน

            # fallback: ใช้ manual parsing
            raw = ssh.send_command("show ip interface brief | include GigabitEthernet")
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            if not lines:
                return "No GigabitEthernet interfaces found."

            interface_messages = []
            count_up = count_down = count_admin_down = 0

            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    name = parts[0]
                    status = parts[4].lower()
                    if status == 'up':
                        interface_messages.append(f"{name} up")
                        count_up += 1
                    elif status == 'down':
                        interface_messages.append(f"{name} down")
                        count_down += 1
                    elif 'administratively down' in status:
                        interface_messages.append(f"{name} administratively down")
                        count_admin_down += 1
                    else:
                        interface_messages.append(f"{name} {status}")

            summary = f" -> {count_up} up, {count_down} down, {count_admin_down} administratively down"
            return ", ".join(interface_messages) + summary

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