import paho.mqtt.client as mqtt
import json

# بيانات الاتصال
BROKER = "aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "smartfactory_sim"
PASSWORD = "Factory2026!Sim"

# Topic لاستقبال بيانات الحساسات
SUB_TOPIC = "nti_smartfactory_teamX/factory/#"

# Topic لإرسال نتيجة Health Score
PUB_TOPIC = "nti_smartfactory_teamX/factory/health"

# لتخزين آخر قراءة لكل ماكينة
machines = {}

# حساب Health Score
def calculate_health(data):
    score = 100

    temp = data.get("temperature", 0)
    vib = data.get("vibration", 0)
    current = data.get("current", 0)
    rpm = data.get("rpm", 0)

    if temp > 70:
        score -= 20

    if vib > 5:
        score -= 25

    if current > 15:
        score -= 20

    if rpm < 1200 or rpm > 1800:
        score -= 15

    if score >= 80:
        status = "Healthy"
    elif score >= 60:
        status = "Warning"
    else:
        status = "Critical"

    diagnosis = "Normal"

    if temp > 70 and vib > 5:
        diagnosis = "Possible Bearing Failure"
    elif temp > 70:
        diagnosis = "Overheating"
    elif vib > 5:
        diagnosis = "High Vibration"
    elif current > 15:
        diagnosis = "Motor Overload"

    return score, status, diagnosis


# عند الاتصال
def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected")
    client.subscribe(SUB_TOPIC)


# عند استقبال رسالة
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print("Bad JSON, ignored:", msg.topic)
        return

    # لو الرسالة دي مش بيانات حساس (زي رسالة الـ health اللي بنبعتها إحنا) نتجاهلها
    if "sensor" not in payload or "value" not in payload or "machine" not in payload:
        return

    machine = payload["machine"]
    sensor = payload["sensor"]
    value = payload["value"]

    if machine not in machines:
        machines[machine] = {}

    machines[machine][sensor] = value

    if len(machines[machine]) == 4:
        score, status, diagnosis = calculate_health(machines[machine])

        result = {
            "machine": machine,
            "health_score": score,
            "status": status,
            "diagnosis": diagnosis
        }

        print(result)

        client.publish(PUB_TOPIC, json.dumps(result))

        # تصفير القراءات عشان الدورة الجاية
        machines[machine] = {}


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

client.loop_forever()