# 🌾 Govi Netha - AI Smart Irrigation System

A low-cost, end-to-end Edge AI prototype that monitors paddy field soil moisture in real time, classifies irrigation urgency directly on a field-deployed ESP32, and delivers live recommendations to a mobile-friendly web dashboard - no internet connection required for field alerts.

---

## 📋 Table of Contents

- [System Overview](#-system-overview)
- [Hardware](#-hardware)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Edge AI - Irrigation Classes](#-edge-ai--irrigation-classes)
- [API Reference](#-api-reference)
- [Moisture Sensor Calibration](#-moisture-sensor-calibration)
- [Running the Tests](#-running-the-tests)
- [Troubleshooting](#-troubleshooting)

---

## 🏗 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        ESP32 (Field)                        │
│                                                             │
│  Soil Moisture Sensor ──┐                                   │
│  DHT22 (Temp/Humidity) ─┼──► Edge AI Classifier            │
│                         │    (TFLite Micro / Rule-based)    │
│                         │         │                         │
│                         │    LED + Buzzer Alerts            │
└─────────────────────────┼─────────────────────────────────-─┘
                          │ HTTP POST every 5 min
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Your PC / Server)             │
│                                                             │
│  POST /api/sensors/data  ──► MongoDB Atlas                  │
│  GET  /api/irrigation/*  ──► Random Forest ML Model         │
└─────────────────────────────────────────────────────────────┘
                          │ REST API
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              React Dashboard (Browser / Mobile)             │
│                                                             │
│  Live moisture reading · Irrigation status · Trend chart    │
│  AI prediction · Alerts · Recommendations                   │
└─────────────────────────────────────────────────────────────┘
```

**Edge AI runs every 1 minute** - immediate local alerts, no internet needed.  
**Cloud sync every 5 minutes** - dashboard updates, ML predictions, historical data.

---

## 🔧 Hardware

| Component | Model | Purpose |
|---|---|---|
| Microcontroller | ESP32 Dev Board | Runs firmware + Edge AI |
| Soil Sensor | Capacitive Moisture v1.2 | Reads soil moisture % |
| Climate Sensor | DHT22 | Reads temperature + humidity |
| Indicator | Red LED + 220Ω resistor | Visual irrigation alert |
| Alert | Buzzer Module (Arduino) | Audio irrigation alert |
| Other | Breadboard + jumper wires + USB cable | Wiring |

### Wiring Reference

| Sensor | ESP32 Pin |
|---|---|
| Soil Moisture (analog out) | GPIO 34 |
| DHT22 (data) | GPIO 4 |
| LED (anode via 220Ω) | GPIO 18 |
| Buzzer (signal) | GPIO 19 |

---

## 📁 Repository Structure

```
govi-netha/
│
├── govi-netha-edge/               # ESP32 firmware (PlatformIO / Arduino C++)
│   ├── platformio.ini             # Build config - board, libraries, upload port
│   └── src/
│       ├── main.cpp               # Entry point - reads sensors, runs AI, posts to cloud
│       ├── config.h               # WiFi credentials, API URL, thresholds, pins ← EDIT THIS
│       ├── TFLiteInference.h      # TFLite Micro wrapper - runs the neural network
│       ├── EdgeAI.h               # Rule-based fallback classifier (same 0/1/2 output)
│       └── irrigation_model.h     # Generated C array - run tflite-training scripts first
│
├── backend/                       # Python FastAPI backend
│   ├── main.py                    # App entry point, CORS, lifespan hooks
│   ├── config.py                  # Pydantic settings - reads from .env
│   ├── database.py                # MongoDB Atlas async connection (motor)
│   ├── requirements.txt           # All Python dependencies
│   ├── routes/
│   │   ├── sensors.py             # POST /api/sensors/data · GET /api/sensors/*
│   │   └── irrigation.py          # GET /api/irrigation/status|prediction|history
│   ├── controllers/
│   │   └── irrigation_controller.py   # Business logic - thresholds + ML calls
│   ├── models/
│   │   └── sensor_data.py         # Pydantic schemas for sensor readings + alerts
│   ├── ml/irrigation/
│   │   └── train.py               # Random Forest - predicts hours until irrigation
│   └── tests/
│       ├── conftest.py
│       ├── test_irrigation_controller.py
│       └── test_sensors_route.py
│
├── frontend/                      # React (Vite) dashboard
│   ├── index.html
│   ├── vite.config.js             # Dev server with /api proxy to backend
│   ├── package.json
│   └── src/
│       ├── App.jsx                # Router + top bar + bottom nav
│       ├── index.css              # Design system - colours, cards, badges
│       ├── api/
│       │   └── index.js           # All API calls centralised (axios)
│       └── pages/
│           ├── Dashboard.jsx      # Hero moisture card + live stats
│           ├── Irrigation.jsx     # Status + ML prediction + trend chart
│           ├── Alerts.jsx         # Active alerts list
│           └── Tips.jsx           # AI-powered irrigation recommendations
│
├── tflite-training/               # Train + export the TFLite model for ESP32
│   ├── train_irrigation_model.py  # Trains neural network, exports .tflite
│   └── convert_to_c_array.py     # Converts .tflite binary → irrigation_model.h
│
├── .env                           # Your secrets - NEVER commit this file
├── .env.example                   # Template - copy to .env and fill in values
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- **Python** 3.10 or newer
- **Node.js** 18 or newer
- **VS Code** with the [PlatformIO IDE extension](https://platformio.org/install/ide?install=vscode)
- ESP32 connected via USB (check Device Manager - should show a COM port)

---

### Step 1 - Generate the TFLite Model

The firmware requires `irrigation_model.h`. Generate it first:

```bash
cd tflite-training

# Install training dependencies
pip install tensorflow numpy scikit-learn

# Train the neural network and export to .tflite
python train_irrigation_model.py

# Convert .tflite binary to a C header file
python convert_to_c_array.py

# Copy the generated header into the firmware source folder
copy irrigation_model.h ..\govi-netha-edge\src\irrigation_model.h
```

> **Note the scaler values** printed by `train_irrigation_model.py` and compare them with the constants at the top of `govi-netha-edge/src/TFLiteInference.h`. Update them if they differ.

---

### Step 2 - Configure the ESP32 Firmware

Open `govi-netha-edge/src/config.h` and update your WiFi credentials and backend IP address:

```cpp
#define WIFI_SSID     "YourNetworkName"
#define WIFI_PASSWORD "YourPassword"

// Run `ipconfig` (Windows) to find your PC's local IP address
#define API_BASE_URL "http://192.168.0.XX:8000/api"
```

> **Finding your IP:** Open Command Prompt and run `ipconfig`. Look for the **IPv4 Address** under your active Wi-Fi adapter (e.g. `192.168.0.4`).

---

### Step 3 - Flash the ESP32

1. Open the `govi-netha-edge/` folder in VS Code with PlatformIO
2. Click **Build** (✓ checkmark in the bottom toolbar)
3. Click **Upload** (→ arrow in the bottom toolbar)
4. Click **Serial Monitor** (plug icon) - set baud rate to **115200**

You should see sensor readings every minute and cloud sends every 5 minutes.

---

### Step 4 - Start the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Train the Random Forest prediction model
python ml/irrigation/train.py

# Start the API server (0.0.0.0 allows ESP32 to connect from the network)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ API docs available at: **http://localhost:8000/docs**

> **Important:** Always use `--host 0.0.0.0`. Without it, the backend only listens on localhost and the ESP32 cannot connect.

---

### Step 5 - Start the Frontend

Open a new terminal (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

✅ Dashboard available at: **http://localhost:5173**

---

### Step 6 - Verify the Full Pipeline

Open the Serial Monitor in PlatformIO. After the cloud send interval, you should see:

```
── Cloud Send ──────────────────────────────
  Payload: {"moisture":55.2,"temperature":28.5,"humidity":71.3,...}
  [OK] HTTP 201 - data stored in MongoDB
────────────────────────────────────────────
```

Then open the dashboard at `http://localhost:5173` - the hero card will show live moisture data from your sensor.

---

## ⚙️ Configuration

### Environment Variables (`.env`)

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env` to GitHub.**

| Variable | Description | Example |
|---|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/...` |
| `MONGODB_DB_NAME` | Database name | `govi_netha` |
| `API_HOST` | Backend bind address | `0.0.0.0` |
| `API_PORT` | Backend port | `8000` |
| `SECRET_KEY` | App secret (change this) | `your_random_secret` |
| `VITE_API_BASE_URL` | Frontend API base (Vite only) | `http://localhost:8000/api` |

### Firmware Constants (`govi-netha-edge/src/config.h`)

| Constant | Default | Description |
|---|---|---|
| `WIFI_SSID` | - | Your WiFi network name |
| `WIFI_PASSWORD` | - | Your WiFi password |
| `API_BASE_URL` | - | Your PC's local IP + port |
| `EDGE_READ_INTERVAL_MS` | `60000` (1 min) | How often to read sensors + run AI |
| `CLOUD_SEND_INTERVAL_MS` | `300000` (5 min) | How often to POST to backend |
| `MOISTURE_CRITICAL` | `40.0` | Moisture % below which = irrigate now |
| `MOISTURE_WARNING` | `60.0` | Moisture % below which = monitor |
| `TEMP_HIGH_THRESHOLD` | `35.0` | Temperature °C above which worsens urgency |
| `LED_PIN` | `18` | GPIO pin for the indicator LED |
| `BUZZER_PIN` | `19` | GPIO pin for the buzzer |
| `PIN_MOISTURE` | `34` | GPIO pin for soil moisture sensor (analog) |
| `PIN_DHT` | `4` | GPIO pin for DHT22 data line |

---

## 🤖 Edge AI - Irrigation Classes

The TFLite Micro neural network (3 inputs → 16 → 8 → 3 outputs) classifies each reading into one of three states:

| State | Label | Condition | LED | Buzzer |
|---|---|---|---|---|
| `0` | `OK` | Moisture ≥ 60% | Off | Off |
| `1` | `IRRIGATE_SOON` | Moisture 40–60% | Slow blink × 3 | Slow beep × 3 |
| `2` | `IRRIGATE_NOW` | Moisture < 40% **or** moisture < 60% + temp > 35°C | Fast blink × 6 | Fast beep × 6 |

If the TFLite model fails to load for any reason, `EdgeAI.h` provides an identical rule-based fallback with the same output states.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check - returns system name |
| `GET` | `/api/health` | Returns `{"status": "healthy"}` |
| `POST` | `/api/sensors/data` | ESP32 posts a sensor reading (runs auto-alert logic) |
| `GET` | `/api/sensors/latest` | Most recent sensor snapshot |
| `GET` | `/api/sensors/history` | Last N readings (default 50) |
| `GET` | `/api/sensors/alerts` | All unresolved alerts |
| `GET` | `/api/irrigation/status` | Current irrigation recommendation |
| `GET` | `/api/irrigation/prediction` | ML prediction - hours until irrigation needed |
| `GET` | `/api/irrigation/history` | Moisture + temperature trend data for chart |

> Full interactive documentation: **http://localhost:8000/docs** (Swagger UI)

---

## 💧 Moisture Sensor Calibration

The capacitive soil moisture sensor needs calibration for accurate readings. Do this once after first flash:

1. Open the PlatformIO Serial Monitor
2. Hold the sensor in **open air** - note the `Soil Raw:` value → this is your `DRY_VALUE`
3. Submerge the sensor tip in a **glass of water** - note the value → this is your `WET_VALUE`
4. Open `govi-netha-edge/src/main.cpp` and update the calibration constants:

```cpp
const int DRY_VALUE = 2900;  // ← replace with your open-air reading
const int WET_VALUE = 1200;  // ← replace with your in-water reading
```

5. Re-flash the ESP32

---

## 🧪 Running the Tests

```bash
cd backend
venv\Scripts\activate
pytest
```

Expected output:

```
tests/test_irrigation_controller.py .........    [ 52%]
tests/test_sensors_route.py .....                [100%]

17 passed in X.XXs
```

Tests cover:
- Irrigation threshold evaluation (critical, warning, monitor, OK)
- Prediction logic including the critical-moisture-returns-zero business rule
- Sensor data ingestion endpoint (valid payload, invalid payload, alert triggering)
- Health and root endpoints

---

## 🛠 Troubleshooting

### ESP32 - WiFi won't connect

- Confirm `WIFI_SSID` and `WIFI_PASSWORD` in `config.h` are correct
- ESP32 only supports **2.4 GHz** networks - it will not connect to 5 GHz
- The SSID is case-sensitive

### ESP32 - HTTP -1 (connection failed)

- Run `ipconfig` and confirm your `API_BASE_URL` uses the correct IPv4 address
- Make sure you start the backend with `--host 0.0.0.0` (not just `--port 8000`)
- Add an inbound firewall rule in Windows Defender for **TCP port 8000**
- Confirm your PC and the ESP32 are on the same WiFi network

### Backend - `ValidationError: vite_api_base_url extra inputs not permitted`

The `.env` file contains frontend variables that Pydantic rejects. Add `extra = "ignore"` to the `Config` class in `backend/config.py`:

```python
class Config:
    env_file = "../.env"
    env_file_encoding = "utf-8"
    extra = "ignore"   # ← add this line
```

### Backend - MongoDB connection timeout

- Check the `MONGODB_URI` in `.env` - special characters in the password must be URL-encoded
- In MongoDB Atlas, go to **Network Access** and confirm `0.0.0.0/0` is in the allowlist
- Test the connection directly:

```bash
python -c "from database import *; import asyncio; asyncio.run(connect_db())"
```

### Backend - `FileNotFoundError: model.pkl`

The Random Forest model hasn't been trained yet. Run:

```bash
python ml/irrigation/train.py
```

The controller falls back to rule-based predictions automatically until the model exists.

### Firmware - `irrigation_model.h: No such file or directory`

The TFLite model header hasn't been generated. Run from the `tflite-training/` folder:

```bash
python train_irrigation_model.py
python convert_to_c_array.py
copy irrigation_model.h ..\govi-netha-edge\src\irrigation_model.h
```

### Firmware - TFLite compilation errors

If the `TensorFlowLite_ESP32` library version doesn't match the API in `TFLiteInference.h`, switch to the rule-based fallback. In `main.cpp`, replace:

```cpp
#include "TFLiteInference.h"
```

with:

```cpp
#include "EdgeAI.h"
```

And in `doEdgeRead()`, replace `TFLiteInference::predict(...)` with `EdgeAI::classify(...)`.

### Dashboard - "Could not load data"

- Confirm the backend is running on port 8000
- The Vite dev server automatically proxies `/api` calls to `http://localhost:8000` - no CORS issues in development
- Check the browser console (F12) for network errors

### Irrigation Prediction - 400 Bad Request

The `/api/irrigation/prediction` endpoint requires at least 3 stored sensor readings. This resolves automatically after the ESP32 successfully sends a few readings to the cloud.

### DHT22 returns `nan`

- Check the GPIO pin in `config.h` matches your physical wiring (default: GPIO 4)
- DHT22 requires a **10 kΩ pull-up resistor** between the data pin and 3.3 V
- Add a 2-second delay after `dht.begin()` - the sensor needs warm-up time

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Edge firmware | Arduino C++ · TensorFlow Lite Micro · PlatformIO |
| Edge AI model | 3-layer neural network → INT8 quantised TFLite |
| Cloud prediction | Random Forest Regressor (scikit-learn) |
| Backend | Python 3.12 · FastAPI · Motor (async MongoDB) |
| Database | MongoDB Atlas (free M0 tier) |
| Frontend | React 18 · Vite · Recharts · Axios |

---

*Govi Netha - bringing affordable data-driven irrigation to Sri Lanka's paddy farmers.*