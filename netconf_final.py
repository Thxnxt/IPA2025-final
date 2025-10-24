from ncclient import manager
import xmltodict
from ncclient.operations.rpc import RPCError

INTERFACE_NAME = "Loopback66070084"

def netconf_connect(ip_address):
    try:
        m = manager.connect(
            host=ip_address,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False,
        )
        return m
    except Exception as e:
        print(f"Connection failed: {e}")
        return None
def create(ip_address):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="create">
          <name>{INTERFACE_NAME}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>172.0.84.1</ip>
              <netmask>255.255.255.0</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        m.edit_config(target="running", config=netconf_config)
        return f"Interface {INTERFACE_NAME} is created successfully using Netconf."
    except RPCError as e:
        if e.tag == 'data-exists':
            print(f"Interface already exists: {e}")
            return f"Cannot create: Interface {INTERFACE_NAME}."
        else:
            print(f"Error! {e}")
            return f"Cannot create: interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")
        return f"Cannot create: interface {INTERFACE_NAME}"


def delete(ip_address):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>{INTERFACE_NAME}</name>
        </interface>
      </interfaces>
    </config>
    """
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        m.edit_config(target="running", config=netconf_config)
        return f"Interface {INTERFACE_NAME} is deleted successfully using Netconf."
    except RPCError as e:
        # 'invalid-value' หรือ 'data-missing' มักหมายความว่าสิ่งที่พยายามลบไม่มีอยู่
        if e.tag == 'data-missing' or e.tag == 'invalid-value':
            print(f"Interface not found to delete: {e}")
            return f"Cannot delete: Interface {INTERFACE_NAME}."
        else:
            print(f"Error! {e}")
            return f"Cannot delete: interface {INTERFACE_NAME}"
    except Exception as e:
        print(f"Error! {e}")
        return f"Cannot delete: interface {INTERFACE_NAME}"


def enable(ip_address):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{INTERFACE_NAME}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        m.edit_config(target="running", config=netconf_config)
        return f"Interface {INTERFACE_NAME} is enabled successfully using Netconf."
    except RPCError as e:
        # ถ้า interface ไม่มีอยู่จริง จะ merge <enabled> เข้าไปไม่ได้
        if e.tag == 'data-missing' or e.tag == 'invalid-value':
            print(f"Interface not found to enable: {e}")
            return f"Cannot enable: Interface {INTERFACE_NAME}."
        else:
            print(f"Error! {e}")
            return f"Cannot enable: interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")
        return f"Cannot enable: interface {INTERFACE_NAME}."


def disable(ip_address):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{INTERFACE_NAME}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        m.edit_config(target="running", config=netconf_config)
        return f"Interface {INTERFACE_NAME} is disabled successfully using Netconf."
    except RPCError as e:
        if e.tag == 'data-missing' or e.tag == 'invalid-value':
            print(f"Interface not found to disable: {e}")
            return f"Cannot disable: Interface {INTERFACE_NAME}."
        else:
            print(f"Error! {e}")
            return f"Cannot disable: interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")
        return f"Cannot disable: interface {INTERFACE_NAME}."

# def netconf_edit_config(m, netconf_config):
#     return m.edit_config(target="running", config=netconf_config)


def status(ip_address):
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        filter = """
        <filter>
          <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
        </filter>
        """
        print("Attempting m.get() with interfaces-state filter...")
        netconf_reply = m.get(filter)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)
        data_content = netconf_reply_dict.get('rpc-reply', {}).get('data')

        if not data_content:
            return "No data found (checked by Netconf)."

        # รองรับ namespace แบบ {urn:ietf:...}interfaces-state
        interfaces_state_data = None
        for key in data_content:
            if 'interfaces-state' in key:
                interfaces_state_data = data_content[key]
                break

        if not interfaces_state_data:
            return "No Interface data found (checked by Netconf)."

        interfaces_list = interfaces_state_data.get('interface')
        if not interfaces_list:
            return "No Interface data found (checked by Netconf)."

        if not isinstance(interfaces_list, list):
            interfaces_list = [interfaces_list]

        for iface in interfaces_list:
            if iface.get('name') == INTERFACE_NAME:
                admin_status = iface.get("admin-status", "unknown")
                oper_status = iface.get("oper-status", "unknown")
                if admin_status == 'up' and oper_status == 'up':
                    return f"Interface {INTERFACE_NAME} is enabled (checked by Netconf)."
                elif admin_status == 'down' and oper_status == 'down':
                    return f"Interface {INTERFACE_NAME} is disabled (checked by Netconf)."
                else:
                    return f"Interface {INTERFACE_NAME} state is: admin={admin_status}, oper={oper_status} (checked by Netconf)."

        return f"No Interface {INTERFACE_NAME} (checked by Netconf)."

    except Exception as e:
        print(f"Error during status check: {e}")
        return f"Error getting status for {INTERFACE_NAME}"
