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

from fastapi import Depends
from app.api.deps import verify_api_key
from app.api.routers import incidents, events, resources, decisions, world_state, agent, locations, teams

# Require API Key for all of these routes
authenticated_routers = [
    incidents.router,
    events.router,
    resources.router,
    decisions.router,
    world_state.router,
    agent.router,
    locations.router,
    teams.router,
]

for auth_router in authenticated_routers:
    app.include_router(auth_router, dependencies=[Depends(verify_api_key)])
