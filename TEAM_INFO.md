# Shared Connection Info

## MQTT Broker (HiveMQ Cloud, free tier)
- Cluster URL: `aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud`
- Port: `8883` (TLS/SSL required — this broker does not allow unencrypted connections)
- Full broker URL for code: `mqtts://aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud:8883`

## Credentials
- Username: `smartfactory_sim`
- Password: `Factory2026!Sim`
- Permission: Publish and Subscribe


## Topic Structure
Pattern:
```
nti_smartfactory_teamX/factory/{machine}/{sensor}
```
Where:
- `{machine}` = `machine1`, `machine2`, `machine3`, `machine4`
- `{sensor}` = `temperature`, `vibration`, `current`, `rpm`

Example topics:
```
nti_smartfactory_teamX/factory/machine1/temperature
nti_smartfactory_teamX/factory/machine2/vibration
nti_smartfactory_teamX/factory/machine3/current
nti_smartfactory_teamX/factory/machine4/rpm
```

## JSON Payload Format
Every message on every topic looks like this:
```json
{
  "machine": "machine2",
  "sensor": "temperature",
  "value": 48.5,
  "unit": "C",
  "timestamp": "2026-08-02T18:37:23.156Z"
}
```

Units per sensor:
| Sensor | Unit |
|---|---|
| temperature | C |
| vibration | mm/s |
| current | A |
| rpm | RPM |

## Realistic Value Ranges
- Machines 1, 3, 4 (normal): temperature 20–60°C, vibration 0.5–5 mm/s, current 5–15 A, RPM 1200–1800
- Machine 2 (demo scenario — gradually overheats): temperature climbs toward 100°C, vibration climbs toward 15 mm/s over time, then holds there

## Demo Scenario (built into the simulator)
Machine 2 starts normal, then after ~15 seconds of runtime its temperature and vibration begin climbing steadily (capped at 100°C / 15 mm/s) — this is what should trigger a falling Health Score, a red dashboard status, a notification, and an auto-created maintenance ticket in the other tasks.

## How to Connect (any language/tool)
- Protocol: MQTT over TLS
- Host: `aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud`
- Port: `8883`
- Username: `smartfactory_sim`
- Password: `Factory2026!Sim`
- Subscribe to: `nti_smartfactory_teamX/factory/#` to receive everything at once

## Verifying Your Connection
Use MQTT Explorer (https://mqtt-explorer.com) — connect with the details above, TLS enabled — to visually confirm you're receiving live data before writing your own code against it.
