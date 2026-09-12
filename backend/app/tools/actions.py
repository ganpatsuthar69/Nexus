"""State-modifying deterministic tools for Agents."""

import json
from uuid import UUID
from datetime import datetime, timezone
from strands import tool

from app.db.session import SessionLocal
from app.models import (
    Incident, Location, Event, Resource, Team, Plan, Task, Decision, AuditLog
)
from app.services.audit import log_action


@tool
def verify_event(
    event_id: str, 
    source_trust_weight: float, 
    corroboration_count_weight: float, 
    recency_weight: float, 
    contradiction_penalty: float
) -> str:
    """Verifies an event and sets its confidence score. Auto-accepts (>0.8), flags (0.4-0.8), or holds (<0.4)."""
    with SessionLocal() as db:
        event = db.query(Event).filter(Event.id == UUID(event_id)).first()
        if not event:
            return json.dumps({"error": "Event not found"})

        confidence = source_trust_weight + corroboration_count_weight + recency_weight - contradiction_penalty
        event.confidence = confidence
        event.processed_at = datetime.now(timezone.utc)
        
        status_result = ""
        if confidence > 0.8:
            status_result = "auto_accepted"
        elif confidence >= 0.4:
            status_result = "flagged_for_verification"
        else:
            status_result = "held"

        # You might add an Event attribute for status in a real system, but for now we log it.
        db.add(event)
        log_action(db, "event", event.id, "verified", "VerificationAgent", {"confidence": confidence, "status": status_result})
        db.commit()

        return json.dumps({
            "event_id": str(event.id),
            "confidence": confidence,
            "status": status_result
        })


@tool
def create_plan(incident_id: str, goal: str, reason: str) -> str:
    """Creates a new autonomous plan for an incident."""
    with SessionLocal() as db:
        plan = Plan(
            incident_id=UUID(incident_id),
            goal=goal,
            reason=reason,
            status="draft",
            version=1
        )
        db.add(plan)
        db.flush()
        log_action(db, "plan", plan.id, "created", "PlanningAgent", {"goal": goal})
        db.commit()
        return json.dumps({"plan_id": str(plan.id), "status": "draft"})


@tool
def create_task(plan_id: str, title: str, description: str, priority: int, requires_human: bool) -> str:
    """Creates a new task associated with a plan."""
    with SessionLocal() as db:
        task = Task(
            plan_id=UUID(plan_id),
            title=title,
            description=description,
            priority=priority,
            requires_human=requires_human,
            status="pending"
        )
        db.add(task)
        db.flush()
        log_action(db, "task", task.id, "created", "PlanningAgent", {"title": title})
        db.commit()
        return json.dumps({"task_id": str(task.id)})


@tool
def assign_resource(task_id: str, resource_id: str) -> str:
    """Assigns a resource to a task. Idempotent: checks if already assigned to avoid double-booking."""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        resource = db.query(Resource).filter(Resource.id == UUID(resource_id)).first()
        
        if not task or not resource:
            return json.dumps({"error": "Task or Resource not found"})
            
        if resource.status == "assigned":
            if task.assigned_resource_id == resource.id:
                return json.dumps({"status": "already_assigned", "task_id": str(task.id)})
            return json.dumps({"error": "Resource is already assigned to another task"})
            
        resource.status = "assigned"
        task.assigned_resource_id = resource.id
        
        db.add(resource)
        db.add(task)
        log_action(db, "resource", resource.id, "assigned", "ExecutionAgent", {"task_id": str(task.id)})
        db.commit()
        
        return json.dumps({"status": "success", "resource_id": str(resource.id)})


@tool
def assign_team(task_id: str, team_id: str) -> str:
    """Assigns a team to a task."""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        team = db.query(Team).filter(Team.id == UUID(team_id)).first()
        
        if not task or not team:
            return json.dumps({"error": "Task or Team not found"})
            
        if team.status == "deployed":
            if task.assigned_team_id == team.id:
                return json.dumps({"status": "already_assigned"})
            return json.dumps({"error": "Team is already deployed"})
            
        team.status = "deployed"
        task.assigned_team_id = team.id
        
        db.add(team)
        db.add(task)
        log_action(db, "team", team.id, "assigned", "ExecutionAgent", {"task_id": str(task.id)})
        db.commit()
        
        return json.dumps({"status": "success"})


@tool
def request_human_decision(task_id: str, question: str, options: list[str]) -> str:
    """Escalates a decision to a human via the Decisions table."""
    with SessionLocal() as db:
        decision = Decision(
            task_id=UUID(task_id),
            question=question,
            options=options
        )
        db.add(decision)
        db.flush()
        
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if task:
            task.status = "blocked_on_human"
            db.add(task)
            
        log_action(db, "decision", decision.id, "requested", "ExecutionAgent", {"question": question})
        db.commit()
        
        return json.dumps({"status": "human_decision_requested", "decision_id": str(decision.id)})


@tool
def execute_action(task_id: str, action_type: str, details: str, exceeds_policy_scope: bool = False, requires_human: bool = False) -> str:
    """Idempotently executes an action for a task. Auto-escalates if policy is exceeded."""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if not task:
            return json.dumps({"error": "Task not found"})
            
        if task.status == "in_progress" or task.status == "completed":
            return json.dumps({"status": "already_executed_or_executing"})
            
        if exceeds_policy_scope or requires_human or task.requires_human:
            # Delegate to human
            return request_human_decision(
                task_id=task_id, 
                question=f"Approval needed for action: {action_type}. Details: {details}", 
                options=["approve", "reject"]
            )
            
        task.status = "in_progress"
        db.add(task)
        log_action(db, "task", task.id, "execution_started", "ExecutionAgent", {"action_type": action_type, "details": details})
        db.commit()
        
        return json.dumps({"status": "execution_started"})


@tool
def update_world_state(location_id: str, current_status: str, population_change: int = 0) -> str:
    """Updates the status and population of a location."""
    with SessionLocal() as db:
        loc = db.query(Location).filter(Location.id == UUID(location_id)).first()
        if not loc:
            return json.dumps({"error": "Location not found"})
            
        loc.current_status = current_status
        loc.population += population_change
        
        db.add(loc)
        log_action(db, "location", loc.id, "updated", "ExecutionAgent", {"status": current_status, "population_change": population_change})
        db.commit()
        
        return json.dumps({"status": "success", "new_population": loc.population})


@tool
def mark_task_complete(task_id: str) -> str:
    """Marks a task as completed and frees up any assigned resources and teams."""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if not task:
            return json.dumps({"error": "Task not found"})
            
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        
        if task.assigned_resource_id:
            res = db.query(Resource).filter(Resource.id == task.assigned_resource_id).first()
            if res:
                res.status = "available"
                db.add(res)
                
        if task.assigned_team_id:
            team = db.query(Team).filter(Team.id == task.assigned_team_id).first()
            if team:
                team.status = "available"
                db.add(team)
                
        db.add(task)
        log_action(db, "task", task.id, "completed", "ExecutionAgent", {})
        db.commit()
        
        return json.dumps({"status": "success"})


@tool
def mark_task_failed(task_id: str, reason: str) -> str:
    """Marks a task as failed and frees up resources."""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if not task:
            return json.dumps({"error": "Task not found"})
            
        task.status = "failed"
        
        if task.assigned_resource_id:
            res = db.query(Resource).filter(Resource.id == task.assigned_resource_id).first()
            if res:
                res.status = "available"
                db.add(res)
                
        if task.assigned_team_id:
            team = db.query(Team).filter(Team.id == task.assigned_team_id).first()
            if team:
                team.status = "available"
                db.add(team)
                
        db.add(task)
        log_action(db, "task", task.id, "failed", "ExecutionAgent", {"reason": reason})
        db.commit()
        
        return json.dumps({"status": "failed_recorded"})


@tool
def trigger_replan(incident_id: str, reason: str) -> str:
    """Marks current plans as failed/stale and triggers a replan."""
    with SessionLocal() as db:
        plans = db.query(Plan).filter(Plan.incident_id == UUID(incident_id), Plan.status.in_(["draft", "approved"])).all()
        for p in plans:
            p.status = "abandoned"
            p.reason = reason
            db.add(p)
            
        log_action(db, "incident", UUID(incident_id), "replanning_triggered", "PlanningAgent", {"reason": reason})
        db.commit()
        
        return json.dumps({"status": "replanning_triggered"})


@tool
def verify_action(task_id: str) -> str:
    """VerificationAgent checks if the action executed successfully on the world state."""
    # In a real system, this would sense the environment.
    # We will just read the task status.
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if not task:
            return json.dumps({"error": "Task not found"})
            
        return json.dumps({"task_status": task.status})


@tool
def write_audit_log(entity_type: str, entity_id: str, action: str, details: str) -> str:
    """Writes an arbitrary audit log."""
    with SessionLocal() as db:
        log_action(db, entity_type, UUID(entity_id), action, "AutonomousAgent", {"details": details})
        db.commit()
        return json.dumps({"status": "logged"})
