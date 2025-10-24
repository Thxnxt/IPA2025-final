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

def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        ssh.disable_paging()
        up = 0
        down = 0
        admin_down = 0
        interfaces = []
        result = ssh.send_command("sh ip int bri", use_textfsm=True)
        for status in result:
            if status["interface"].startswith("GigabitEthernet"):
                interfaces.append(f"{status['interface']} {status['status']}")
                if status["status"] == "up":
                    up += 1
                elif status["status"] == "down":
                    down += 1
                elif status["status"] == "administratively down":
                    admin_down += 1
        ans = ", ".join(interfaces) + f" -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans

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
            result = ssh.send_command("show run | include banner motd")
            # ตัวอย่าง output: banner motd ^Authorized users only! Managed by 66070123^
            if not result.strip():
                return "Error: No MOTD Configured"
            if "banner motd" in result:
                start = result.find("^") + 1
                end = result.rfind("^")
                if start > 0 and end > start:
                    return result[start:end].strip()
                else:
                    return "Error: Unable to parse MOTD"
            else:
                return "Error: No MOTD Configured"
    except Exception as e:
        return f"Error: {str(e)}"