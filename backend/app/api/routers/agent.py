"""Agent API routes."""

import asyncio
import json
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_db
from app.models import AuditLog, Event
from app.schemas.event import EventCreate, EventRead
from app.agents.orchestrator import Orchestrator
import hashlib

router = APIRouter(prefix="/api/agent", tags=["agent"])

@router.post("/run")
async def run_agent(incident_id: str, background_tasks: BackgroundTasks):
    """Starts or advances the supervisor loop for a specific incident."""
    orchestrator = Orchestrator(incident_id=incident_id)
    background_tasks.add_task(orchestrator.run_loop, max_steps=10)
    return {"status": "accepted", "message": "Agent loop started in background"}


@router.post("/events")
async def ingest_agent_event(event_in: EventCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Ingests an event and triggers the agent to react to it."""
    # Re-use dedup logic
    dedup_string = f"{event_in.incident_id}-{event_in.source}-{event_in.event_type}-{event_in.description}"
    dedup_key = hashlib.sha256(dedup_string.encode()).hexdigest()
    
    existing = db.query(Event).filter(Event.dedup_key == dedup_key).first()
    if existing:
        return {"status": "duplicate", "event_id": str(existing.id)}
        
    db_event = Event(
        incident_id=event_in.incident_id,
        event_type=event_in.event_type,
        source=event_in.source,
        description=event_in.description,
        location_id=event_in.location_id,
        severity=event_in.severity,
        dedup_key=dedup_key
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Trigger the agent to react
    orchestrator = Orchestrator(incident_id=str(event_in.incident_id))
    background_tasks.add_task(orchestrator.run_loop, max_steps=10)
    
    return {"status": "accepted", "event_id": str(db_event.id), "message": "Event ingested and agent loop triggered"}


@router.get("/activity")
async def stream_agent_activity(request: Request, db: Session = Depends(get_db)):
    """Streams recent agent decisions and tool calls via Server-Sent Events."""
    
    async def event_generator():
        last_yielded_id = None
        
        while True:
            # If client disconnects, stop streaming
            if await request.is_disconnected():
                break
                
            # Query AuditLogs created by Agents, ordered by created_at
            query = db.query(AuditLog).filter(AuditLog.actor.ilike("%Agent%")).order_by(AuditLog.created_at.asc())
            
            if last_yielded_id:
                # We need to filter for logs created AFTER our last yielded log
                # For simplicity in this demo, we'll fetch all and slice
                logs = query.all()
                idx = 0
                for i, log in enumerate(logs):
                    if str(log.id) == str(last_yielded_id):
                        idx = i + 1
                        break
                new_logs = logs[idx:]
            else:
                # First connection: get the last 5 logs
                new_logs = query.limit(5).all()
                
            for log in new_logs:
                yield {
                    "event": "agent_activity",
                    "data": json.dumps({
                        "id": str(log.id),
                        "entity_type": log.entity_type,
                        "entity_id": str(log.entity_id),
                        "action": log.action,
                        "actor": log.actor,
                        "details": log.details,
                        "created_at": log.created_at.isoformat()
                    })
                }
                last_yielded_id = log.id
                
            await asyncio.sleep(1)
            
    return EventSourceResponse(event_generator())
