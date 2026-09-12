"""Registry of specialized Strands Agents for NEXUS."""

import os
from strands import Agent
from app.tools import retrieval, actions

# Model configuration from environment
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


# 1. SupervisorAgent
supervisor_agent = Agent(
    name="SupervisorAgent",
    description="Orchestrates the NEXUS loop. Delegates specific subtasks to specialized agents.",
    system_prompt=(
        "You are the NEXUS Supervisor Agent. Your job is to orchestrate the response to emergency incidents. "
        "You do not execute actions directly. Instead, you analyze the state and decide which specialized "
        "agent to consult next in the loop (Situation, Verification, Planning, Execution)."
    ),
    tools=[
        retrieval.get_incident,
        retrieval.get_world_state,
        actions.write_audit_log,
    ],
    model=BEDROCK_MODEL_ID,
)

# 2. SituationAgent
situation_agent = Agent(
    name="SituationAgent",
    description="Interprets incoming events and updates against the world state.",
    system_prompt=(
        "You are the Situation Agent. Your role is to interpret raw events and assess their impact on the current "
        "world state. You summarize the situational context so the Supervisor can decide if replanning is needed."
    ),
    tools=[
        retrieval.get_world_state,
        retrieval.get_recent_events,
    ],
    model=BEDROCK_MODEL_ID,
)

# 3. VerificationAgent
verification_agent = Agent(
    name="VerificationAgent",
    description="Calculates event confidence scores and verifies action success.",
    system_prompt=(
        "You are the Verification Agent. Your role is to verify the legitimacy of incoming events by calculating "
        "confidence scores based on source trust, corroboration, recency, and contradictions. You also verify "
        "the outcome of executed actions."
    ),
    tools=[
        actions.verify_event,
        actions.verify_action,
        retrieval.get_recent_events,
    ],
    model=BEDROCK_MODEL_ID,
)

# 4. ResourceAgent
resource_agent = Agent(
    name="ResourceAgent",
    description="Evaluates resource and team availability for the planning process.",
    system_prompt=(
        "You are the Resource Agent. You specialize in logistics. Given a location or need, you find nearby "
        "resources and available teams, checking their current status and capacities."
    ),
    tools=[
        retrieval.find_nearby_resources,
        retrieval.get_resource_status,
        retrieval.get_available_teams,
    ],
    model=BEDROCK_MODEL_ID,
)

# 5. PlanningAgent
planning_agent = Agent(
    name="PlanningAgent",
    description="Produces or revises autonomous plans and their associated tasks.",
    system_prompt=(
        "You are the Planning Agent. Your role is to create structured plans to address emergencies. "
        "You break down large goals into discrete tasks with priorities. If a plan is no longer viable, you "
        "trigger a replan and create new tasks."
    ),
    tools=[
        actions.create_plan,
        actions.create_task,
        actions.trigger_replan,
    ],
    model=BEDROCK_MODEL_ID,
)

# 6. ExecutionAgent
execution_agent = Agent(
    name="ExecutionAgent",
    description="Executes tasks by assigning resources/teams and handling human-in-the-loop decisions.",
    system_prompt=(
        "You are the Execution Agent. Your job is to execute the tasks defined in the plan safely. "
        "You assign resources and teams idempotently. If an action exceeds policy limits or requires human "
        "approval, you MUST request a human decision rather than executing it autonomously."
    ),
    tools=[
        actions.assign_resource,
        actions.assign_team,
        actions.execute_action,
        actions.request_human_decision,
        actions.mark_task_complete,
        actions.mark_task_failed,
        actions.update_world_state,
    ],
    model=BEDROCK_MODEL_ID,
)

registry = {
    "SupervisorAgent": supervisor_agent,
    "SituationAgent": situation_agent,
    "VerificationAgent": verification_agent,
    "ResourceAgent": resource_agent,
    "PlanningAgent": planning_agent,
    "ExecutionAgent": execution_agent,
}
