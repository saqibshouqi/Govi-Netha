# GOVI NETHA - Complete Setup Guide

---

## PART 1: MongoDB Atlas Free Tier Setup (Shared Cloud Database)

Do this once as a group. **One person** (suggest Saqib as group lead) creates
the cluster and shares the connection string with everyone.

### Step 1 - Create a free account
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up with a Google/GitHub account or email
3. Choose **"Deploy a free cluster"** when prompted

### Step 2 - Create your free M0 cluster
1. Select **"M0 FREE"** tier (512 MB storage - plenty for coursework)
2. Cloud provider: **AWS** | Region: choose one nearest to Sri Lanka
   → recommended: **Asia Pacific (Singapore)** `ap-southeast-1`
3. Cluster name: `govi-netha-cluster`
4. Click **"Create Deployment"**

### Step 3 - Create a database user
1. In the dialog that appears, set:
   - Username: `govinetha`
   - Password: Click "Autogenerate" - **copy this password**
2. Click **"Create Database User"**

### Step 4 - Whitelist IP addresses (allow all)
1. In the "Where would you like to connect from?" dialog
2. Click **"Add My Current IP Address"**
3. ALSO click **"Allow Access from Anywhere"** → `0.0.0.0/0`
   *(This lets the ESP32 and deployed backend connect)*
4. Click **"Finish and Close"**

### Step 5 - Get your connection string
1. In Atlas dashboard, click **"Connect"** on your cluster
2. Choose **"Drivers"**
3. Select Driver: **Python**, Version: **3.12 or later**
4. Copy the connection string - it looks like:
   ```
   mongodb+srv://govinetha:<password>@govi-netha-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with the password you copied in Step 3
6. Add your database name at the end:
   ```
   mongodb+srv://govinetha:YOURPASSWORD@govi-netha-cluster.xxxxx.mongodb.net/govi_netha?retryWrites=true&w=majority
   ```

### Step 6 - Put the string in your .env file
```
MONGODB_URI=mongodb+srv://govinetha:YOURPASSWORD@govi-netha-cluster.xxxxx.mongodb.net/govi_netha?retryWrites=true&w=majority
MONGODB_DB_NAME=govi_netha
```

### Step 7 - Share with the team
Share the final MONGODB_URI string with all 4 members via WhatsApp/Discord.
**Never commit this string to GitHub.**

### Collections that will be auto-created
- `sensor_readings` - all ESP32 telemetry
- `alerts`          - edge + cloud alerts from all components

---

## PART 2: GitHub Repository Setup

### One person (Saqib) does this:
```bash
cd govi-netha
git init
git add .
git commit -m "chore: initial project scaffold"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_ORG/govi-netha.git
git branch -M main
git push -u origin main
```

### Everyone else:
```bash
git clone https://github.com/YOUR_ORG/govi-netha.git
cd govi-netha
cp .env.example .env
# Paste the MONGODB_URI from Saqib into .env
```

### Each person creates their working branch:
```bash
# Saqib:
git checkout -b feature/saqib-irrigation

# Januki:
git checkout -b feature/januki-npk

# Ravisha:
git checkout -b feature/ravisha-ph

# Roshana:
git checkout -b feature/roshana-stress
```

---

## PART 3: Day-by-Day Development Plan

---

### DAY 1 - Sunday 5th: Foundation & Edge AI
**Goal: Shared architecture running, hardware wired, edge logic verified on serial monitor**

#### All members (30 min together):
- [ ] Saqib sets up GitHub repo and shares with team
- [ ] Everyone clones and creates their branch
- [ ] Saqib sets up MongoDB Atlas, shares URI
- [ ] Everyone adds URI to their .env
- [ ] All run the backend: `cd backend && uvicorn main:app --reload`
      → confirm http://localhost:8000/docs loads
- [ ] All run the frontend: `cd frontend && npm install && npm run dev`
      → confirm http://localhost:5173 loads (will show loading - that's OK)

#### Hardware (together if using one ESP32):
Wire up in this order:
1. DHT22 → GPIO4 (temp/humidity)
2. Soil Moisture → GPIO34 (analog)
3. pH Sensor → GPIO35 (analog)
4. NPK Sensor → GPIO16 (RX), GPIO17 (TX), needs 5V supply

#### Individual Edge AI tasks:
- **Saqib:** Edit `edge/src/components/irrigation/IrrigationEdge.h`
  → tune IRRIGATION thresholds in config.h for your test conditions
  → verify serial prints "CRITICAL / WARNING / OK" correctly
  → test with finger on sensor (low moisture → should trigger CRITICAL)

- **Januki:** Edit `edge/src/components/npk/NPKEdge.h`
  → test NPK sensor RS485 communication
  → if no NPK sensor yet: add `#define SIMULATE_NPK 1` in config.h
    and return test values from NPKSensor::readNitrogen() etc.

- **Ravisha:** Edit `edge/src/components/ph/PHEdge.h`
  → perform 2-point calibration with pH 4 and pH 7 buffer solutions
  → adjust `_calibrationOffset` in SoilPH.cpp until readings match

- **Roshana:** Edit `edge/src/components/stress/StressEdge.h`
  → tune stress weights - hold DHT sensor over hot lamp to trigger HIGH stress
  → verify stress index rises above STRESS_INDEX_CRITICAL threshold

#### End of Day 1 checkpoint:
- Serial monitor shows sensor readings every 10s
- Edge AI prints correct CRITICAL/WARNING/OK for all 4 components
- Backend starts without errors
- Frontend loads (data pages show "No sensor data" - this is fine)

---

### DAY 2 - Saturday 11th: Cloud (APIs + ML Models)
**Goal: ESP32 → API → MongoDB working; ML models trained and predictions live**

#### Morning (shared, 1 hour together):
- Run backend, open http://localhost:8000/docs
- Manually POST test data to `/api/sensors/data` using the Swagger UI
- Verify data appears in MongoDB Atlas → Browse Collections → sensor_readings
- Confirm `/api/sensors/latest` returns the data you just posted

#### Afternoon (individual):

##### Saqib - Irrigation:
```bash
cd backend
python ml/irrigation/train.py   # trains + saves model.pkl
```
- Open `controllers/irrigation_controller.py`, review predict()
- Test: GET /api/irrigation/prediction in Swagger UI
- Check the response includes `irrigate_in_hours` from ML model (source: "ml_model")
- Edit `edge/src/main.cpp`: confirm CLOUD_SEND_INTERVAL_MS and API_POST_SENSORS
  are set correctly in config.h (use your PC's local IP)
- Flash ESP32, watch serial - confirm "[CLOUD] Data sent successfully."

##### Januki - NPK:
```bash
python ml/npk/train.py
```
- Test GET /api/npk/recommendation in Swagger
- Verify fertilizer labels ("apply_nitrogen" etc.) return correctly
- Add your component's alerts: in `controllers/npk_controller.py`,
  after evaluate_status(), also insert an alert to db.alerts if severity != "normal"
  (pattern: copy from irrigation_controller)

##### Ravisha - pH:
```bash
python ml/ph/train.py
```
- Test GET /api/ph/correction in Swagger
- Verify lime/sulphur kg/acre recommendation appears
- Test with ph=4.0 → should return ~1250 kg/acre lime

##### Roshana - Stress:
```bash
python ml/stress/train.py
```
- Test GET /api/stress/prediction in Swagger
- Verify risk_level: "low"|"medium"|"high" and recommendations list

#### End of Day 2 checkpoint:
- ESP32 → backend → MongoDB pipeline is live
- All 4 ML models trained and returning predictions via API
- http://localhost:8000/docs shows all 10 endpoints working

---

### DAY 3 - Sunday 12th: Integration, UI, Bug Fixing
**Goal: All 4 pages populated with live data, final demo-ready build**

#### Morning: Merge all branches into main
```bash
# Each person pushes their branch, create PR, review, merge
git add .
git commit -m "feat(irrigation): complete edge + cloud + ML"
git push origin feature/saqib-irrigation
# → Create PR on GitHub → merge to main
```

#### After merging everyone pulls main:
```bash
git checkout main
git pull origin main
```

#### Individual UI work (2–3 hours):
Each person:
1. Opens their page in the frontend and fixes any missing data
2. Verifies their API endpoints are returning real data
3. Makes the UI match the wireframe as closely as possible

Shared UI tasks (decide who does what):
- **Dashboard.jsx** - Saqib (overview of all sensors)
- **Soil.jsx**      - Januki + Ravisha (NPK + pH together)
- **Stress.jsx**    - Roshana
- **Tips.jsx**      - Januki or whoever finishes early
- **Alerts.jsx**    - Roshana or whoever finishes early

#### Afternoon: Integration testing
Run the full stack together:
```bash
# Terminal 1
cd backend && uvicorn main:app --reload

# Terminal 2
cd frontend && npm run dev

# Terminal 3
cd edge && pio device monitor
```

Check the full flow:
- [ ] ESP32 serial shows sensor readings every 10s
- [ ] ESP32 serial shows "[CLOUD] Data sent successfully." every 60s
- [ ] MongoDB Atlas → Browse Collections → sensor_readings has new documents
- [ ] Dashboard shows live sensor values
- [ ] All 5 pages load without errors
- [ ] Alerts page shows active alerts
- [ ] Tips page shows ML recommendations
- [ ] Soil page shows NPK bars + pH gauge
- [ ] Stress page shows stress index

#### Final build:
```bash
cd frontend && npm run build   # generates dist/ folder
```

---

## PART 4: Quick Reference - Common Issues & Fixes

### ESP32 can't connect to WiFi
→ Double-check WIFI_SSID and WIFI_PASSWORD in `edge/src/config.h`
→ Make sure your phone hotspot / router is 2.4GHz (ESP32 doesn't support 5GHz)

### ESP32 can't reach backend
→ Find your PC's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
→ Update API_BASE_URL in config.h: `"http://192.168.X.X:8000/api"`
→ Make sure your PC firewall allows port 8000

### Backend "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### MongoDB connection timeout
→ Check your MONGODB_URI in .env - password must not contain special chars unescaped
→ Check Network Access in Atlas → `0.0.0.0/0` must be in the list
→ Try pinging from Python: `python -c "from database import *; import asyncio; asyncio.run(connect_db())"`

### ML model not found (KeyError or FileNotFoundError)
→ You haven't trained the model yet: `python backend/ml/<component>/train.py`
→ The controller will fall back to rule-based automatically if model.pkl doesn't exist

### Frontend shows "Could not load data"
→ Make sure backend is running on port 8000
→ Check browser console for CORS errors - ensure your URL is in CORS allow_origins in main.py

### pH sensor reading 14.0 or 0.0
→ Sensor needs calibration - use buffer solution pH 4 and pH 7
→ Adjust `_calibrationOffset` in `edge/src/sensors/SoilPH.cpp`

### DHT sensor returns -1
→ Check GPIO pin number in config.h matches your wiring
→ DHT22 needs a 10kΩ pull-up resistor between data pin and 3.3V

---

## PART 5: Simulating Sensor Data (if hardware isn't ready)

If hardware is not available or sensor values are all 0, add this to `edge/src/main.cpp`
in `readAllSensors()` for simulation:

```cpp
// SIMULATION MODE - remove when hardware is ready
moisturePct   = 35.0 + random(-5, 5);   // trigger irrigation alerts
temperatureC  = 29.0 + random(-2, 8);
humidityPct   = 68.0 + random(-10, 10);
phValue       = 5.2  + (random(-20, 20) / 100.0);
nitrogen      = 45.0 + random(-15, 15);
phosphorus    = 22.0 + random(-10, 10);
potassium     = 95.0 + random(-20, 20);
```

You can also POST directly to the API without the ESP32:
```bash
curl -X POST http://localhost:8000/api/sensors/data \
  -H "Content-Type: application/json" \
  -d '{"moisture":35,"temperature":36,"humidity":45,"ph":4.8,"nitrogen":30,"phosphorus":20,"potassium":80}'
```
