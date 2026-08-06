# Smart Factory Predictive Maintenance

A simulated smart factory system that monitors 4 machines in real time, detects potential failures before they occur, and calculates reliability metrics to support predictive maintenance decisions.

## Project Overview

The system simulates 4 machines, each monitored by 4 sensors: Temperature, Vibration, Current, and RPM. Sensor data flows through an MQTT broker to a Health Score calculation service, which is then consumed by an analytics engine (MTBF, MTTR, RUL calculations), an alerting/ticketing service, and a live dashboard.

## Architecture

All components communicate through a single shared MQTT broker (HiveMQ Cloud). Each component publishes and/or subscribes to specific topics, using JSON payloads unless noted otherwise.

```
Wokwi ESP32 Simulator
        |
        v
  Sensor Topics (temperature, vibration, current, rpm)
        |
        v
  Health Score Service (health_score.py)
        |
        v
  Health Topics (per machine)
        |
        +---> Analytics Calculations (Node-RED) ---> Reliability/RUL Topics
        |
        +---> Alerts/Ticketing Service (subscriber.py) ---> Alarm Topics
        |
        v
  Dashboard (Node-RED Dashboard)
```

## Broker Connection

- Host: aa0f2fd81d884e9595bd4ef646c78fd8.s1.eu.hivemq.cloud
- Port: 8883 (TLS required)
- Username: smartfactory_sim
- Password: Factory2026!Sim

TLS is required because HiveMQ Cloud does not accept unencrypted connections on this port. All components must have TLS/secure connection enabled to connect successfully.

## Topic Structure

### Sensor Data (published by the Wokwi simulator)
```
nti_smartfactory_teamX/factory/{machine}/temperature
nti_smartfactory_teamX/factory/{machine}/vibration
nti_smartfactory_teamX/factory/{machine}/current
nti_smartfactory_teamX/factory/{machine}/rpm
```
Payload:
```json
{"machine": "machine2", "sensor": "temperature", "value": 48.5, "unit": "C"}
```

### Health Score (published by health_score.py)
```
nti_smartfactory_teamX/factory/{machine}/health
```
Payload:
```json
{"machine": "machine2", "health_score": 62, "status": "Warning", "diagnosis": "Overheating"}
```

### Alarm State (published by subscriber.py)
```
nti_smartfactory_teamX/factory/{machine}/alarm
```
Payload: plain string, "ON" or "OFF"

### Analytics Output (published by the Analytics Calculations flow)
```
nti_smartfactory_teamX/analytics/reliability
```
Payload:
```json
{"machine": "machine2", "mtbf_seconds": 175, "mttr_seconds": 78, "failureCount": 1, "timestamp": "..."}
```

```
nti_smartfactory_teamX/analytics/rul
```
Payload:
```json
{"machine": "machine2", "rul_minutes": 4.2, "currentHealthScore": 55, "timestamp": "..."}
```

Machines are identified as: machine1, machine2, machine3, machine4. Machine 2 is the designated demo machine, engineered to automatically cycle between overheating and recovering to demonstrate the full failure-detection pipeline without manual intervention.

## Components

### 1. Sensor Simulation (Wokwi / ESP32)
Simulates all 4 machines and publishes sensor data every 3 seconds. Machine 2 is wired to 4 real potentiometers (temperature, vibration, current, rpm), providing genuine analog hardware input in addition to an automatic overheat/recover cycle. Machines 1, 3, and 4 use software-generated fluctuation within a normal healthy range.

File: sketch.ino (Wokwi web) or main.cpp (PlatformIO / Wokwi for VS Code)

### 2. Health Score Service (health_score.py)
Subscribes to all sensor topics, accumulates a full reading set per machine, then calculates a Health Score using the following rules:
- Score starts at 100
- Temperature over 70: minus 20
- Vibration over 5: minus 25
- Current over 15: minus 20
- RPM outside 1200-1800: minus 15

Status thresholds: 80 or above is Healthy, 60 or above is Warning, below 60 is Critical.

### 3. Analytics Calculations (Node-RED flow, analytics-calculations-flow.json)
Subscribes to each machine's health topic, maintains a rolling history per machine, and calculates:

MTBF (Mean Time Between Failures): the average time between the start of consecutive failure periods, where a failure period begins when Health Score drops below the critical threshold (60) and ends when it recovers above it. Measured in seconds.

MTTR (Mean Time To Repair): the average duration of each failure period, from when Health Score drops below the threshold until it recovers. Measured in seconds.

RUL (Remaining Useful Life): a linear projection based on the decline rate over the last 10 readings, estimating minutes remaining until Health Score reaches the critical threshold. Returns null if the score is not currently declining.

### 4. Alerts and Maintenance Tickets (subscriber.py)
Subscribes to all health topics. On any Critical reading, sends a Telegram notification, creates a maintenance ticket entry in maintenance_tickets.csv, and publishes an alarm state. Also logs every reading to machine_history.csv.

### 5. Dashboard (Node-RED Dashboard)
Displays live data across several tabs: Factory Overview, Factory Status, Machine Details, and Analytics (Performance Metrics, Machine Ranking, Energy Monitoring).

## Setup Instructions

1. Install Node-RED and open it at http://127.0.0.1:1880
2. Import the provided flow files (analytics-calculations-flow.json and the dashboard flow file) via the Node-RED menu, Import option
3. Configure the MQTT broker connection once (Server, Port, TLS, Security credentials as listed above); all mqtt nodes should reference this single broker configuration
4. Install and run health_score.py: pip install paho-mqtt, then python health_score.py
5. Install and run subscriber.py (requires a config.py file with BOT_TOKEN and CHAT_ID for Telegram notifications)
6. Open the Wokwi simulation and press Play to start the sensor simulator
7. Open the dashboard at http://127.0.0.1:1880/ui

All components (Wokwi simulator, health_score.py, subscriber.py, and the Node-RED flows) must be running simultaneously for live data to flow end to end.

## Known Issues and Open Items

Threshold inconsistency: different components currently use different numeric thresholds for what counts as Critical (health_score.py uses 60, some dashboard functions previously used 50). The team should agree on a single set of thresholds across all components.

Alarm and analytics topics must remain per-machine (not a single shared topic) to match the rest of the system's topic structure.

Any script or flow that reads msg.payload as a number directly must be updated if the source topic sends a JSON object instead of a raw value, and vice versa, to avoid NaN or undefined results.

## Repository Structure

```
/simulation           Node.js simulator (alternative to Wokwi)
/wokwi-esp32           Wokwi/ESP32 source files (sketch.ino, diagram.json, libraries.txt)
health_score.py        Health Score calculation service
subscriber.py          Alerts, ticketing, and alarm publishing service
analytics-calculations-flow.json   Node-RED analytics flow
dashboard-flow.json    Node-RED dashboard flow
TEAM_INFO.md           Broker credentials and topic reference
Analytics_Formulas.md  MTBF, MTTR, and RUL formula documentation
```
