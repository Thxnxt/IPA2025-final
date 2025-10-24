from ncclient import manager
import xmltodict

INTERFACE_NAME = "Loopback66070084"

def netconf_connect(ip_address):
    m = manager.connect(
        host=ip_address,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False,
    )
    return m
def create(ip_address):
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
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
        netconf_reply = netconf_edit_config(m, netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface {INTERFACE_NAME} is created successfully using Netconf."
        else:
            return f"Cannot create: interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")


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
        netconf_reply = netconf_edit_config(m, netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface {INTERFACE_NAME} is deleted successfully using Netconf."
        else:
            return f"Cannot delete: interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")


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
        netconf_reply = netconf_edit_config(m, netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface {INTERFACE_NAME} is enabled successfully using Netconf."
        else:
            return f"Cannot enable: Interface {INTERFACE_NAME}."
    except Exception as e:
        print(f"Error! {e}")


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
        netconf_reply = netconf_edit_config(m, netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return f"Interface {INTERFACE_NAME} is shutdowned successfully using Netconf."
        else:
            return f"Cannot shutdown: Interface {INTERFACE_NAME} (checked by Netconf)."
    except Exception as e:
        print(f"Error! {e}")

def netconf_edit_config(m, netconf_config):
    return m.edit_config(target="running", config=netconf_config)


def status(ip_address):
    
    # 3.1 สร้าง Filter
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces-state">
        <interface>
          <name>{INTERFACE_NAME}</name>
          <admin-status/>
          <oper-status/>
        </interface>
      </interfaces-state>
    </filter>
    """

    # 3.2 เชื่อมต่อ
    m = netconf_connect(ip_address)
    if m is None:
        return f"Error: Cannot connect to {ip_address} (NETCONF)."

    try:
        # 3.3 รัน m.get()
        netconf_reply = m.get(filter=netconf_filter)
        print(netconf_reply) # พิมพ์ผลลัพธ์ XML ดิบ
        
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # 3.4 ตรวจสอบผลลัพธ์ (นี่คือส่วนที่เลียนแบบ if/elif/else)
        
        rpc_reply_data = netconf_reply_dict.get('rpc-reply', {}).get('data')

        # --- ตรรกะเทียบเท่า "if (resp.status_code >= 200 ...)" ---
        # ถ้า 'data' ไม่ว่างเปล่า (None) และมี 'interfaces-state' อยู่ข้างใน
        if rpc_reply_data is not None and 'interfaces-state' in rpc_reply_data:
            
            interface_data = rpc_reply_data.get('interfaces-state', {}).get('interface')
            
            # (กันเหนียว) ถ้า <interfaces-state> ว่างเปล่า
            if interface_data is None:
                print("STATUS NOT FOUND: (interfaces-state is empty)")
                return f"No Interface {INTERFACE_NAME} (checked by Netconf)."
            
            # --- เริ่มตรรกะ Success ---
            print("STATUS OK: (Data found)")
            admin_status = interface_data.get("admin-status", "unknown")
            oper_status = interface_data.get("oper-status", "unknown")

            if admin_status == 'up' and oper_status == 'up':
                return f"Interface {INTERFACE_NAME} is enabled (checked by Netconf)."
            elif admin_status == 'down' and oper_status == 'down':
                return f"Interface {INTERFACE_NAME} is disabled (checked by Netconf)."
            else:
                # กรณีอื่นๆ เช่น up/down
                return f"Interface {INTERFACE_NAME} state is: admin={admin_status}, oper={oper_status} (checked by Netconf)."
        
        # --- ตรรกะเทียบเท่า "elif (resp.status_code == 404)" ---
        # ถ้า 'data' ว่างเปล่า (None) หรือ ไม่มี 'interfaces-state' (แปลว่าหาไม่เจอ)
        else:
            print(f"STATUS NOT FOUND: (Data is empty or key not found)")
            return f"No Interface {INTERFACE_NAME} (checked by Netconf)."

    except Exception as e:
        # --- ตรรกะเทียบเท่า "else: print(Error)" ---
        # (เช่น m.get() ล้มเหลว, XML ผิดพลาด, Timeout ระหว่าง get)
        print(f'Error. Exception during GET: {e}')
        return f"Error getting status for {INTERFACE_NAME}. (Exception: {e})"