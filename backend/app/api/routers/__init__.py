"""API routers package."""

from .incidents import router as incidents_router
from .events import router as events_router
from .resources import router as resources_router
from .decisions import router as decisions_router
from .world_state import router as world_state_router
from .agent import router as agent_router
from .locations import router as locations_router
from .teams import router as teams_router

__all__ = [
    "incidents_router",
    "events_router",
    "resources_router",
    "decisions_router",
    "world_state_router",
    "agent_router",
    "locations_router",
    "teams_router",
]
