const mqtt = require("mqtt");

// ---- CONFIG ----
const TOPIC_PREFIX = "nti_smartfactory_teamX"; // change to your team name
const BROKER_URL = "mqtts://aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud:8883";
const MQTT_OPTIONS = {
  username: "smartfactory_sim",
  password: "Factory2026!Sim",
};
const MACHINES = ["machine1", "machine2", "machine3", "machine4"];
const PUBLISH_INTERVAL_MS = 3000;

const state = {};
MACHINES.forEach((m) => {
  state[m] = {
    temperature: 45,
    vibration: 2.0,
    current: 10.0,
    rpm: 1500,
  };
});

let demoTick = 0;

const client = mqtt.connect(BROKER_URL, MQTT_OPTIONS);

client.on("connect", () => {
  console.log("Connected to MQTT broker!");
  setInterval(publishAllSensorData, PUBLISH_INTERVAL_MS);
});

client.on("error", (err) => {
  console.error("MQTT connection error:", err);
});

function publishAllSensorData() {
  demoTick++;

  MACHINES.forEach((machine) => {
    const s = state[machine];

    // Normal random fluctuation for all machines
    s.temperature += randomBetween(-0.5, 0.5);
    s.vibration += randomBetween(-0.1, 0.1);
    s.current += randomBetween(-0.2, 0.2);
    s.rpm += randomBetween(-10, 10);

    // Special case: machine2 slowly degrades (for the demo scenario), but caps out realistically
    if (machine === "machine2" && demoTick > 5) {
      if (s.temperature < 95) s.temperature += 0.8;
      if (s.vibration < 12) s.vibration += 0.15;
    }

    // Keep all machines within realistic bounds (prevents endless drift)
    s.temperature = clamp(s.temperature, 20, machine === "machine2" ? 100 : 60);
    s.vibration = clamp(s.vibration, 0.5, machine === "machine2" ? 15 : 5);
    s.current = clamp(s.current, 5, 15);
    s.rpm = clamp(s.rpm, 1200, 1800);

    publishSensor(machine, "temperature", round(s.temperature), "C");
    publishSensor(machine, "vibration", round(s.vibration), "mm/s");
    publishSensor(machine, "current", round(s.current), "A");
    publishSensor(machine, "rpm", Math.round(s.rpm), "RPM");
  });
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function publishSensor(machine, sensor, value, unit) {
  const topic = `${TOPIC_PREFIX}/factory/${machine}/${sensor}`;
  const payload = JSON.stringify({
    machine,
    sensor,
    value,
    unit,
    timestamp: new Date().toISOString(),
  });

  client.publish(topic, payload);
  console.log(`Published -> ${topic}: ${payload}`);
}

function randomBetween(min, max) {
  return Math.random() * (max - min) + min;
}

function round(num) {
  return Math.round(num * 10) / 10;
}