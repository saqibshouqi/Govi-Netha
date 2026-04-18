"""
GOVI NETHA — FastAPI Backend (Irrigation scope)
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import connect_db, close_db
from routes import sensors, irrigation


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Govi Netha API",
    description="AI Smart Irrigation System — CM3603 Group 17",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router,    prefix="/api/sensors",    tags=["Sensors"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "system": "Govi Netha", "docs": "/docs"}


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "healthy"}