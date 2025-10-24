#######################################################################################
# Yourname: Thanat
# Your student ID: 66070084
# Your GitHub Repo: https://github.com/Thxnxt/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
import requests
import json
import time
import os
from dotenv import load_dotenv
import restconf_final
import netconf_final
import netmiko_final
import ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise Exception("ACCESS_TOKEN environment variable not set!")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)
last_message_id = None
current_method = None
ACTION_COMMANDS = ["create", "delete", "enable", "disable", "status"]
NETMIKO_COMMANDS = ["gigabit_status"]
ANSIBLE_COMMANDS = ["showrun"]
ALL_COMMANDS = ACTION_COMMANDS + NETMIKO_COMMANDS + ANSIBLE_COMMANDS

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            f"Incorrect reply from Webex Teams API. Status code: {r.status_code}"
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    message_webex = json_data["items"]
    
    # store the text of the first message in the array
    message_id = message_webex[0]["id"]
    if message_id != last_message_id:
        
        # 3. ถ้าเป็นข้อความใหม่ ให้เก็บ ID ของข้อความนี้ไว้ เพื่อใช้เทียบในครั้งถัดไป
        last_message_id = message_id

        message = message_webex[0]["text"]
        print(f"Received message: {message}")

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    student_id = "66070084"
    text = message_webex[0].get("text", "")
    if text.startswith(f"/{student_id} "):

        # extract the command
        parts = text.split(" ")
        responseMessage = ""
        command_processed = False

# 5. Complete the logic for each command
        if len(parts) == 2:
            # --- กรณี 2 ส่วน: /[ID] [command] ---
            command = parts[1].lower()
            if command == "restconf":
                current_method = "restconf"
                responseMessage = "Ok: Restconf"
            elif command == "netconf":
                current_method = "netconf"
                responseMessage = "Ok: Netconf"
            elif command in ALL_COMMANDS:
                # กรณี: /... create (เป็น action command)
                if current_method is None:
                    responseMessage = "Error: No method specified"
                else:
                    responseMessage = "Error: No IP specified."
            elif command.startswith("10.0.15."):
                    # กรณี: /... 10.0.15.61 (เป็น IP) (ตามที่คุณขอ)
                if current_method is None:
                    responseMessage = "Error: No method specified"
                else:
                    responseMessage = "Error: No command found."
            else:
                responseMessage = "Error: No method specified."
            command_processed = True
        elif len(parts) == 3:
            # --- กรณี 3 ส่วน: /[ID] [ip] [command] ---
            ip_address = parts[1]
            command = parts[2].lower()
            if not ip_address.startswith("10.0.15."):
                responseMessage = f"Error: Invalid IP address '{ip_address}'"
                command_processed = True

            elif command == "motd":
                responseMessage = netmiko_final.get_motd(ip_address)
                command_processed = True
            elif command == "gigabit_status":
                responseMessage = netmiko_final.gigabit_status(ip_address)
                command_processed = True
            elif command == "showrun":
                responseMessage = ansible_final.showrun(ip_address)
                command_processed = True

            elif command in ALL_COMMANDS:
                if current_method is None:
                    responseMessage = "Error: No method specified."
                elif current_method == "restconf":
                    if command == "create":
                        responseMessage = restconf_final.create(ip_address)
                    elif command == "delete":
                        responseMessage = restconf_final.delete(ip_address)
                    elif command == "enable":
                        responseMessage = restconf_final.enable(ip_address)
                    elif command == "disable":
                        responseMessage = restconf_final.disable(ip_address)
                    elif command == "status":
                        responseMessage = restconf_final.status(ip_address)
                    else:
                        responseMessage = "Error: No command found"

                elif current_method == "netconf":
                    if command == "create":
                        responseMessage = netconf_final.create(ip_address)
                    elif command == "delete":
                        responseMessage = netconf_final.delete(ip_address)
                    elif command == "enable":
                        responseMessage = netconf_final.enable(ip_address)
                    elif command == "disable":
                        responseMessage = netconf_final.disable(ip_address)
                    elif command == "status":
                        responseMessage = netconf_final.status(ip_address)
                    else:
                        responseMessage = "Error: No command found"
        elif len(parts) >= 4:
            ip_address = parts[1]
            command = parts[2].lower()

            if not ip_address.startswith("10.0.15."):
                responseMessage = f"Error: Invalid IP address '{ip_address}'"
                command_processed = True

            elif command == "motd":
                motd_text = " ".join(parts[3:])
                responseMessage = ansible_final.motd(ip_address, motd_text)
                command_processed = True


# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        # the Webex Teams HTTP headers, including the Authorization and Content-Type
        if responseMessage.endswith(".txt") and "Error:" not in responseMessage:

            # เปิดไฟล์ที่ Ansible สร้างขึ้น
            with open(responseMessage, 'rb') as f:
                # สร้างข้อมูลสำหรับส่งแบบ multipart (ข้อความ + ไฟล์)
                m = MultipartEncoder({
                    "roomId": roomIdToGetMessages,
                    "text": f"Show running config",
                    "files": (responseMessage, f, 'text/plain')
                })

                # ตั้งค่า HTTP Headers
                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": m.content_type
                }

                # ส่ง Request
                r = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=m,
                    headers=HTTPHeaders
                )
        else:
            # ถ้าไม่ใช่ไฟล์ (เป็นข้อความตอบกลับปกติ)
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }
            postData = {
                "roomId": roomIdToGetMessages,
                "text": responseMessage
            }
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=json.dumps(postData),
                headers=HTTPHeaders,
            )