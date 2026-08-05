import json
import paho.mqtt.client as mqtt
import requests
import csv
import os
from datetime import datetime
from config import BOT_TOKEN, CHAT_ID

BROKER = "aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smartfactory_sim"
PASSWORD = "Factory2026!Sim"


TOPIC = "nti_smartfactory_teamX/factory/health"
ALARM_TOPIC = "nti_smartfactory_teamX/factory/alarm"


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()



def on_connect(client, userdata, flags, rc, properties=None):

    if rc == 0:
        print("Connected Successfully")
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}")
    else:
        print(f"Connection Failed. Code = {rc}")


def on_message(client, userdata, msg):

    data = json.loads(msg.payload.decode())

    machine = data["machine"]
    score = data["health_score"]
    status = data["status"]
    diagnosis = data["diagnosis"]

    print(f"\nMachine: {machine}")
    print(f"Health Score: {score}")
    print(f"Status: {status}")
    print(f"Diagnosis: {diagnosis}")


    save_history(machine, score, diagnosis)

    if status == "Critical":

        send_notification(machine, score, diagnosis)

        create_ticket(machine, score, diagnosis)

        publish_alarm(client, machine, True)

    else:

        publish_alarm(client, machine, False)

## --------------------telegram notification------------------------------

# BOT_TOKEN = "YOUR_BOT_TOKEN"
# CHAT_ID = "YOUR_CHAT_ID"

def send_notification(machine, score, diagnosis):

    suggested = get_suggested_action(score, diagnosis)

    message = (
        f"🚨 Smart Factory Alert 🚨\n\n"
        f"Machine: {machine}\n"
        f"Health Score: {score}\n"
        f"Diagnosis: {diagnosis}\n"
        f"Suggested Action: {suggested}\n\n"
        f"Immediate maintenance is required."
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    if response.status_code == 200:
        print("Telegram Notification Sent")
    else:
        print("Telegram Error:", response.text)

##--------------------create ticket-----------------------------------
ticket_counter = 1

def generate_ticket_id():
    global ticket_counter

    ticket_id = f"TKT-{ticket_counter:04d}"
    ticket_counter += 1

    return ticket_id

def get_suggested_action(score, diagnosis):

    actions = {

        "Possible Bearing Failure": {
            "critical": "Stop machine immediately. Inspect bearings and replace if necessary.",
            "warning": "Schedule bearing inspection within 24 hours.",
            "healthy": "Continue monitoring bearings."
        },

        "Overheating": {
            "critical": "Shutdown machine. Check cooling system and fan.",
            "warning": "Check coolant level and reduce operating load.",
            "healthy": "Monitor temperature readings."
        },

        "High Vibration": {
            "critical": "Stop operation and inspect shaft alignment.",
            "warning": "Inspect bolts and rotating parts.",
            "healthy": "Monitor vibration levels."
        },

        "Motor Overload": {
            "critical": "Disconnect power and inspect motor load.",
            "warning": "Check electrical connections and motor current.",
            "healthy": "Monitor motor current."
        }
    }

    if diagnosis not in actions:
        return "Perform a full machine inspection."

    if score < 30:
        return actions[diagnosis]["critical"]
    elif score < 60:
        return actions[diagnosis]["warning"]
    else:
        return actions[diagnosis]["healthy"]


def create_ticket(machine, score, diagnosis):

    filename = "maintenance_tickets.csv"

    ticket_id = generate_ticket_id()

    suggested = get_suggested_action(score, diagnosis)

    file_exists = os.path.isfile(filename)


    with open(filename, "a", newline="") as file:


        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Ticket ID",
                "Time",
                "Machine",
                "Health Score",
                "Diagnosis",
                "Suggested Action",
                "Status"
            ])

        if score < 30:
            ticket_status = "URGENT"
        elif score < 60:
            ticket_status = "OPEN"
        else:
            ticket_status = "MONITOR"

        writer.writerow([
            ticket_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            machine,
            score,
            diagnosis,
            suggested,
            ticket_status
        ])

    print(f"Ticket {ticket_id} Created")


##--------------------save history-----------------------------------

def save_history(machine, score, diagnosis):

    filename = "machine_history.csv"

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Time",
                "Machine",
                "Health Score",
                "Diagnosis",
                "Status"
            ])

        status = (
            "Healthy" if score >= 60
            else "Warning" if score >= 30
            else "Critical"
        )

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            machine,
            score,
            diagnosis,
            status
        ])

    print("History Saved")

##--------------------publish active alarm------------------------------

def publish_alarm(client, machine, alarm_state):

    alarm = {
        "machine": machine,
        "alarm": "ON" if alarm_state else "OFF"
    }

    client.publish(ALARM_TOPIC, json.dumps(alarm))

    print(f"{machine} Alarm = {alarm['alarm']}")

#-------------------------------------------------------------

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)
client.loop_forever()
