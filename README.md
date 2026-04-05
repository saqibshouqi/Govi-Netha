# 🌾 GOVI NETHA — AI Smart Agriculture Monitoring System
> CM3603 Edge Artificial Intelligence | Group 17 | Robert Gordon University

---

## 👥 Component Ownership

| Component | Developer | Responsibility |
|---|---|---|
| 1 — Smart Irrigation Optimization | **Saqib** | `edge/src/components/irrigation/` · `backend/routes/irrigation.py` · `backend/ml/irrigation/` |
| 2 — Soil Nutrient (NPK) Detection | **Januki** | `edge/src/components/npk/` · `backend/routes/npk.py` · `backend/ml/npk/` |
| 3 — Soil pH Monitoring | **Ravisha** | `edge/src/components/ph/` · `backend/routes/ph.py` · `backend/ml/ph/` |
| 4 — Crop Stress Detection | **Roshana** | `edge/src/components/stress/` · `backend/routes/stress.py` · `backend/ml/stress/` |

---

## 📁 Repository Structure

```
govi-netha/
├── edge/                        # ESP32 firmware (PlatformIO / Arduino C++)
│   ├── platformio.ini
│   └── src/
│       ├── main.cpp             # Entry point — reads sensors, runs edge logic, posts to cloud
│       ├── config.h             # WiFi, API URL, thresholds — EDIT THIS
│       ├── sensors/             # Shared sensor drivers (touch carefully)
│       │   ├── SoilMoisture.h/cpp
│       │   ├── TempHumidity.h/cpp
│       │   ├── SoilPH.h/cpp
│       │   └── NPKSensor.h/cpp
│       └── components/          # ← Each person owns their folder
│           ├── irrigation/      # Saqib
│           ├── npk/             # Januki
│           ├── ph/              # Ravisha
│           └── stress/          # Roshana
│
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # App entry point
│   ├── config.py                # Env vars / settings
│   ├── database.py              # MongoDB Atlas connection
│   ├── requirements.txt
│   ├── models/                  # Pydantic + MongoDB schemas
│   │   └── sensor_data.py
│   ├── routes/                  # ← Each person owns their route file
│   │   ├── sensors.py           # Shared: POST sensor readings
│   │   ├── irrigation.py        # Saqib
│   │   ├── npk.py               # Januki
│   │   ├── ph.py                # Ravisha
│   │   └── stress.py            # Roshana
│   ├── controllers/             # Business logic (called by routes)
│   │   ├── irrigation_controller.py
│   │   ├── npk_controller.py
│   │   ├── ph_controller.py
│   │   └── stress_controller.py
│   └── ml/                      # ← Each person owns their ML folder
│       ├── irrigation/          # Saqib  — Random Forest (regression)
│       ├── npk/                 # Januki — Classification
│       ├── ph/                  # Ravisha — Regression
│       └── stress/              # Roshana — Classification
│
├── frontend/                    # React (Vite) dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/index.js         # All API calls — centralised
│   │   ├── pages/               # One page per component + shared
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Alerts.jsx
│   │   │   ├── Tips.jsx
│   │   │   ├── Soil.jsx
│   │   │   └── Stress.jsx
│   │   └── components/          # Reusable UI widgets
│   └── package.json
│
├── .env.example                 # Copy to .env — never commit .env
└── .gitignore
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PlatformIO (VS Code extension or CLI)
- Git

### 1 — Clone & configure environment
```bash
git clone https://github.com/YOUR_ORG/govi-netha.git
cd govi-netha
cp .env.example .env
# → Fill in your MONGODB_URI and other values in .env
```

### 2 — Start the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API docs available at http://localhost:8000/docs
```

### 3 — Start the frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

### 4 — Flash the ESP32
```bash
cd edge
# Open in VS Code with PlatformIO, OR:
pio run --target upload
pio device monitor   # serial output
```

---

## 🔑 Environment Variables

See `.env.example` for all required variables.  
**Never commit `.env` to GitHub.**

---

## 📡 API Reference (Backend)

| Method | Endpoint | Owner | Description |
|---|---|---|---|
| POST | `/api/sensors/data` | Shared | ESP32 posts all sensor readings |
| GET | `/api/sensors/latest` | Shared | Latest sensor snapshot |
| GET | `/api/irrigation/status` | Saqib | Current irrigation recommendation |
| GET | `/api/irrigation/prediction` | Saqib | Next irrigation window (ML) |
| GET | `/api/npk/status` | Januki | NPK levels + deficiency flags |
| GET | `/api/npk/recommendation` | Januki | Fertilizer recommendation (ML) |
| GET | `/api/ph/status` | Ravisha | pH level + imbalance flag |
| GET | `/api/ph/correction` | Ravisha | pH correction plan (ML) |
| GET | `/api/stress/level` | Roshana | Current stress index |
| GET | `/api/stress/prediction` | Roshana | Risk prediction (ML) |
| GET | `/api/alerts` | Shared | All active alerts |

---

## 🗓️ 3-Day Plan

| Day | Goal |
|---|---|
| **Sun 5th** | Foundation & Edge — shared architecture running, sensors wired, edge AI logic executing locally |
| **Sat 11th** | Cloud — Edge → API → MongoDB, ML models trained and deployed |
| **Sun 12th** | Integration & UI — full React dashboard, bug fixing, final polish |

---

## ⚠️ Git Workflow — Avoid Conflicts

- Each person works in their own branch: `feature/saqib-irrigation`, `feature/januki-npk`, etc.
- Only edit files in your component folder + your route/controller/ml files
- Merge to `main` at the end of each day via Pull Request
- **Never directly push to `main`**
