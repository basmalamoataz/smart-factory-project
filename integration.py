import paho.mqtt.client as mqtt
import json

# MQTT Broker
BROKER = "aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smartfactory_sim"
PASSWORD = "Factory2026!Sim"

# Topics
HEALTH_TOPIC = "nti_smartfactory_teamX/factory/health"
ANALYTICS_TOPIC = "nti_smartfactory_teamX/factory/analytics"
ALERTS_TOPIC = "nti_smartfactory_teamX/factory/alerts"
MAINTENANCE_TOPIC = "nti_smartfactory_teamX/factory/maintenance"


# عند الاتصال
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT Broker")

    client.subscribe(HEALTH_TOPIC)
    client.subscribe(ANALYTICS_TOPIC)
    client.subscribe(ALERTS_TOPIC)
    client.subscribe(MAINTENANCE_TOPIC)

    print("Subscribed to all topics")


# عند استقبال أي رسالة
def on_message(client, userdata, msg):
    print("\n==============================")
    print("Topic:", msg.topic)

    try:
        payload = json.loads(msg.payload.decode())
        print(json.dumps(payload, indent=4))
    except:
        print(msg.payload.decode())


# إنشاء Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

print("Waiting for messages...\n")

client.loop_forever()