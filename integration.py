import paho.mqtt.client as mqtt
import json

BROKER = "aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smartfactory_sim"
PASSWORD = "Factory2026!Sim"

# Corrected topics — matching what's actually tested and working tonight
HEALTH_TOPIC = "nti_smartfactory_teamX/factory/+/health"
RELIABILITY_TOPIC = "nti_smartfactory_teamX/analytics/reliability"
RUL_TOPIC = "nti_smartfactory_teamX/analytics/rul"

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT Broker")
    client.subscribe(HEALTH_TOPIC)
    client.subscribe(RELIABILITY_TOPIC)
    client.subscribe(RUL_TOPIC)
    print("Subscribed to all topics")

def on_message(client, userdata, msg):
    print("\n==============================")
    print("Topic:", msg.topic)
    try:
        payload = json.loads(msg.payload.decode())
        print(json.dumps(payload, indent=4))
    except:
        print(msg.payload.decode())

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
print("Waiting for messages...\n")
client.loop_forever()
