"""NEXUS — Autonomous Real-World Coordination Agent

FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="NEXUS API",
    description="Autonomous coordination agent for community-scale disruptions",
    version="0.1.0",
)

# ── CORS ──────────────────────────────────────────────────────────────
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
from app.api.health import router as health_router  # noqa: E402

app.include_router(health_router)

# Future routers:
# from app.api.events import router as events_router
# from app.api.plans  import router as plans_router
# app.include_router(events_router)
# app.include_router(plans_router)
