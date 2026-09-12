"""Resilience wrapper for Agent invocations."""

import asyncio
import logging
from uuid import UUID

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from strands import Agent

from app.db.session import SessionLocal
from app.services.audit import log_action

logger = logging.getLogger(__name__)

# Number of attempts before Circuit Breaking
MAX_RETRIES = 3


class AgentDegradedError(Exception):
    """Raised when an agent repeatedly fails and requires human intervention."""
    pass


def log_retry_attempt(retry_state):
    """Logs the retry attempt."""
    logger.warning(
        f"Agent invocation failed. Attempt {retry_state.attempt_number}/{MAX_RETRIES}. "
        f"Retrying... Exception: {retry_state.outcome.exception()}"
    )


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception, asyncio.TimeoutError)),
    before_sleep=log_retry_attempt,
    reraise=True,
)
async def _invoke_with_retry(agent: Agent, prompt: str, timeout_seconds: int = 30) -> str:
    """Internal function that wraps the LLM invocation with timeout and retry."""
    # Use asyncio.wait_for to enforce a strict timeout on the LLM request
    response = await asyncio.wait_for(agent.invoke_async(prompt), timeout=timeout_seconds)
    # The response is usually an object with a text attribute
    return response.text if hasattr(response, "text") else str(response)


async def safe_invoke(agent: Agent, prompt: str, incident_id: str | None = None) -> str:
    """
    Safely invokes an agent with bounded exponential backoff.
    If it fails 3 times, halts autonomous execution and logs an audit record.
    """
    try:
        return await _invoke_with_retry(agent, prompt)
    except Exception as e:
        logger.error(f"Agent {agent.name} failed after {MAX_RETRIES} attempts. Error: {e}")
        
        # Circuit Break: Log to audit_logs that agent is degraded
        if incident_id:
            with SessionLocal() as db:
                log_action(
                    db=db,
                    entity_type="incident",
                    entity_id=UUID(incident_id),
                    action="agent_degraded",
                    actor=agent.name,
                    details={"error": str(e), "message": "agent degraded, human review needed"}
                )
                db.commit()
                
        raise AgentDegradedError(f"Agent {agent.name} is degraded and requires human review.") from e
