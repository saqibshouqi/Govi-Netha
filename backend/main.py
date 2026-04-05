"""
GOVI NETHA — FastAPI Backend
Entry point: registers all component routers
Run with: uvicorn main:app --reload --port 8000
API docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import connect_db, close_db
from routes import sensors, irrigation, npk, ph, stress

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Govi Netha API",
    description="AI Smart Agriculture Monitoring System — CM3603 Group 17",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow React dev server and any deployed frontend ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(sensors.router,    prefix="/api/sensors",    tags=["Sensors (Shared)"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation — Saqib"])
app.include_router(npk.router,        prefix="/api/npk",        tags=["NPK — Januki"])
app.include_router(ph.router,         prefix="/api/ph",         tags=["pH — Ravisha"])
app.include_router(stress.router,     prefix="/api/stress",     tags=["Stress — Roshana"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "system": "Govi Netha", "docs": "/docs"}

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
