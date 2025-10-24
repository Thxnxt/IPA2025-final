import json
import requests
requests.packages.urllib3.disable_warnings()


ROUTER_IP = "10.0.15.61"
INTERFACE_NAME = "Loopback66070084"
api_url = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}
basicauth = ("admin", "cisco")


def create():
    create_url = api_url
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": INTERFACE_NAME,
            "description": "Thanat's Loopback interface",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.0.84.1",
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }

    resp = requests.post(
        create_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if resp.status_code >= 200 and resp.status_code <= 299:
        print(f"STATUS OK: {resp.status_code}")
        return f"Interface {INTERFACE_NAME} is created successfully."
    else:
        print(f"Error. Status Code: {resp.status_code}")
        return f"Cannot create: Interface {INTERFACE_NAME}."


def delete():
    delete_url = f"{api_url}/interface={INTERFACE_NAME}"
    resp = requests.delete(
        delete_url,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {INTERFACE_NAME} is deleted successfully."
    else:
        print(f"Error. Status Code: {resp.status_code}")
        return f"Cannot delete: Interface {INTERFACE_NAME}."


def enable():
    check_url = f"{api_url}/interface={INTERFACE_NAME}"
    check_resp = requests.get(check_url, auth=basicauth, headers=headers, verify=False)
    if check_resp.status_code != 200:
        return f"Cannot enable: Interface {INTERFACE_NAME}"
    
    state_url = f"{api_url}/interface={INTERFACE_NAME}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": INTERFACE_NAME,
            "enabled": True
        }
    }

    resp = requests.patch(
        state_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {INTERFACE_NAME} is enabled successfully"
    else:
        print(f"Error. Status Code: {resp.status_code}")
        return f"Cannot enable: Interface {INTERFACE_NAME}"


def disable():
    state_url = f"{api_url}/interface={INTERFACE_NAME}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": INTERFACE_NAME,
            "enabled": False
        }
    }

    resp = requests.patch(
        state_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {INTERFACE_NAME} is shutdowned successfully."
    else:
        print(f"Error. Status Code: {resp.status_code}")
        return f"Cannot disable: Interface {INTERFACE_NAME}."


def status():
    api_url_status = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces-state/interface={INTERFACE_NAME}"

    resp = requests.get(
        api_url_status,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        interface_state = response_json.get("ietf-interfaces:interface", {})
        admin_status = interface_state.get("admin-status", "unknown")
        oper_status = interface_state.get("oper-status", "unknown")
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {INTERFACE_NAME} is enabled."
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {INTERFACE_NAME} is disabled."
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {INTERFACE_NAME}."
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
