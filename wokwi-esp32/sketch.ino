#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "smartfactory_sim";
const char* mqtt_password = "Factory2026!Sim";
const char* topicPrefix = "nti_smartfactory_teamX";

WiFiClientSecure espClient;
PubSubClient client(espClient);

const char* machines[] = {"machine1", "machine2", "machine3", "machine4"};
float temperature[4] = {45, 45, 45, 45};
float vibration[4]   = {2.0, 2.0, 2.0, 2.0};
float current[4]     = {10.0, 10.0, 10.0, 10.0};
float rpm[4]          = {1500, 1500, 1500, 1500};

int demoTick = 0;
unsigned long lastPublish = 0;
const unsigned long publishInterval = 3000;

bool machine2Recovering = false;

const int potTemp       = 32; // temperature
const int potVibration  = 33; // vibration
const int potCurrent    = 34; // current
const int potRpm        = 35; // rpm

// Forward declarations (required by PlatformIO)
void connectMQTT();
float randomFloat(float minV, float maxV);
float clampf(float v, float lo, float hi);
float potOffset(int pin, float range);
void publishSensor(int i, const char* sensor, float value, const char* unit);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  espClient.setInsecure();
  client.setServer(mqtt_server, mqtt_port);
  connectMQTT();
}

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    String clientId = "esp32-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 2s");
      delay(2000);
    }
  }
}

float randomFloat(float minV, float maxV) {
  return minV + (float)random(0, 1000) / 1000.0 * (maxV - minV);
}

float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

float potOffset(int pin, float range) {
  int raw = analogRead(pin);
  float normalized = ((float)raw / 4095.0) - 0.5;
  return normalized * range;
}

void publishSensor(int i, const char* sensor, float value, const char* unit) {
  String topic = String(topicPrefix) + "/factory/" + machines[i] + "/" + sensor;
  String payload = String("{\"machine\":\"") + machines[i] + "\",\"sensor\":\"" + sensor +
                    "\",\"value\":" + String(value, 1) + ",\"unit\":\"" + unit + "\"}";
  client.publish(topic.c_str(), payload.c_str());
  Serial.println("Published -> " + topic + ": " + payload);
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastPublish >= publishInterval) {
    lastPublish = now;
    demoTick++;

    for (int i = 0; i < 4; i++) {
      if (i == 1) {
        // ---- Machine 2: real potentiometer readings + automatic overheat/recover cycle (SPED UP for demo) ----
        temperature[i] += randomFloat(-0.5, 0.5) + potOffset(potTemp, 1.0);
        vibration[i]   += randomFloat(-0.1, 0.1) + potOffset(potVibration, 0.2);
        current[i]     += randomFloat(-0.2, 0.2) + potOffset(potCurrent, 0.4);
        rpm[i]         += randomFloat(-10, 10)   + potOffset(potRpm, 20);

        if (demoTick > 5) {
          if (!machine2Recovering) {
            temperature[i] += 3.0;
            vibration[i] += 0.5;

            if (temperature[i] >= 90) {
              machine2Recovering = true;
            }
          } else {
            temperature[i] -= 4.0;
            vibration[i] -= 0.6;

            if (temperature[i] <= 45) {
              machine2Recovering = false;
            }
          }
        }

        temperature[i] = clampf(temperature[i], 20, 100);
        vibration[i]   = clampf(vibration[i], 0.5, 15);
        current[i]     = clampf(current[i], 5, 15);
        rpm[i]         = clampf(rpm[i], 1200, 1800);

      } else {
        // ---- Machines 1, 3, 4: normal software-simulated fluctuation ----
        temperature[i] += randomFloat(-0.5, 0.5);
        vibration[i]   += randomFloat(-0.1, 0.1);
        current[i]     += randomFloat(-0.2, 0.2);
        rpm[i]         += randomFloat(-10, 10);

        temperature[i] = clampf(temperature[i], 20, 60);
        vibration[i]   = clampf(vibration[i], 0.5, 5);
        current[i]     = clampf(current[i], 5, 15);
        rpm[i]         = clampf(rpm[i], 1200, 1800);
      }

      publishSensor(i, "temperature", temperature[i], "C");
      publishSensor(i, "vibration", vibration[i], "mm/s");
      publishSensor(i, "current", current[i], "A");
      publishSensor(i, "rpm", rpm[i], "RPM");
    }
  }
}
