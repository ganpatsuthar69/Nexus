"""NEXUS Agent Orchestrator.

Implements the decision loop and state machine:
OBSERVING → ANALYZING → VERIFYING → PLANNING → VALIDATING_PLAN → EXECUTING → 
VERIFYING_RESULT → (SUCCESS | FAILURE→REPLANNING | HUMAN_REQUIRED→WAITING_HUMAN)
"""

import logging
from typing import Literal

from app.agents.registry import registry
from app.agents.resilience import safe_invoke, AgentDegradedError

logger = logging.getLogger(__name__)

State = Literal[
    "OBSERVING",
    "ANALYZING",
    "VERIFYING",
    "PLANNING",
    "VALIDATING_PLAN",
    "EXECUTING",
    "VERIFYING_RESULT",
    "SUCCESS",
    "FAILURE",
    "WAITING_HUMAN"
]

class Orchestrator:
    def __init__(self, incident_id: str):
        self.incident_id = incident_id
        self.state: State = "OBSERVING"
        self.supervisor = registry["SupervisorAgent"]
        self.situation_agent = registry["SituationAgent"]
        self.verification_agent = registry["VerificationAgent"]
        self.planning_agent = registry["PlanningAgent"]
        self.resource_agent = registry["ResourceAgent"]
        self.execution_agent = registry["ExecutionAgent"]

    async def step(self):
        """Executes a single step in the state machine."""
        logger.info(f"[Orchestrator] Incident {self.incident_id} entered state: {self.state}")
        
        try:
            if self.state == "OBSERVING":
                prompt = f"Analyze new events for incident {self.incident_id}."
                await safe_invoke(self.situation_agent, prompt, self.incident_id)
                self.state = "ANALYZING"

            elif self.state == "ANALYZING":
                prompt = f"Summarize the situation for incident {self.incident_id}."
                analysis = await safe_invoke(self.supervisor, prompt, self.incident_id)
                if "replan" in analysis.lower() or "new plan" in analysis.lower():
                    self.state = "PLANNING"
                else:
                    self.state = "VERIFYING"

            elif self.state == "VERIFYING":
                prompt = f"Verify unverified events for incident {self.incident_id}."
                await safe_invoke(self.verification_agent, prompt, self.incident_id)
                self.state = "PLANNING"

            elif self.state == "PLANNING":
                prompt = f"Draft tasks for the current plan of incident {self.incident_id}. If needed, trigger replan."
                await safe_invoke(self.planning_agent, prompt, self.incident_id)
                self.state = "VALIDATING_PLAN"

            elif self.state == "VALIDATING_PLAN":
                prompt = f"Find resources and verify feasibility of the plan for incident {self.incident_id}."
                validation = await safe_invoke(self.resource_agent, prompt, self.incident_id)
                if "infeasible" in validation.lower() or "missing" in validation.lower():
                    self.state = "PLANNING"  # Back to planning
                else:
                    self.state = "EXECUTING"

            elif self.state == "EXECUTING":
                prompt = f"Execute pending tasks for incident {self.incident_id}."
                exec_result = await safe_invoke(self.execution_agent, prompt, self.incident_id)
                
                if "human_decision_requested" in exec_result:
                    self.state = "WAITING_HUMAN"
                else:
                    self.state = "VERIFYING_RESULT"

            elif self.state == "VERIFYING_RESULT":
                prompt = f"Verify task execution results for incident {self.incident_id}."
                verif_result = await safe_invoke(self.verification_agent, prompt, self.incident_id)
                
                if "failed" in verif_result.lower():
                    self.state = "FAILURE"
                elif "complete" in verif_result.lower() or "success" in verif_result.lower():
                    self.state = "SUCCESS"
                else:
                    # Continue loop
                    self.state = "OBSERVING"

        except AgentDegradedError:
            logger.error("[Orchestrator] Halting due to agent degradation.")
            self.state = "WAITING_HUMAN"

    async def run_loop(self, max_steps: int = 10):
        """Runs the agent loop up to max_steps or until terminal state."""
        terminal_states = {"SUCCESS", "FAILURE", "WAITING_HUMAN"}
        steps = 0
        
        while self.state not in terminal_states and steps < max_steps:
            await self.step()
            steps += 1
            
        logger.info(f"[Orchestrator] Loop finished at state: {self.state}")
        return self.state
