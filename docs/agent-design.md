# NEXUS — Agent & Tool Design (Strands Agents SDK)

## Agents

- **Supervisor Agent** — top-level Strands agent; owns the observe→plan→act→verify→replan loop and delegates to sub-agents.
- **Situation Agent** — reasons about incoming events: what happened, where, when, severity, new vs. update vs. duplicate.
- **Resource Agent** — reasons about available resources/teams: distance, capacity, priority, existing assignments.
- **Verification Agent** — scores confidence on reports and on post-action outcomes; flags conflicts.
- **Planning Agent** — produces/revises the task plan for a given goal.
- **Execution Agent** — executes tool calls for safe actions or requests a human decision.

## Tools (Strands tool-calling surface)

```text
get_incident()
get_world_state()
get_recent_events()
verify_event()
find_nearby_resources()
get_resource_status()
get_available_teams()
create_plan()
create_task()
assign_resource()
assign_team()
execute_action()
request_human_decision()
update_world_state()
verify_action()
mark_task_complete()
mark_task_failed()
trigger_replan()
write_audit_log()
```

Tools are deterministic and backed by validated backend logic. The LLM (via Strands) reasons and selects which tool to call; it never mutates world state directly — every state change goes through one of the tools above, which is what makes the audit trail complete and the human-escalation boundary enforceable.

## Agent State Machine

```text
OBSERVING → ANALYZING → VERIFYING → PLANNING → VALIDATING_PLAN → EXECUTING → VERIFYING_RESULT
                                                                                   │
                                                    ┌──────────────────────────────┼───────────────────────────┐
                                                    ▼                              ▼                            ▼
                                            SUCCESS → COMPLETED             FAILURE → REPLANNING        HUMAN_REQUIRED → WAITING_HUMAN
                                                                                                                  │
                                                                                                          DECISION_RECEIVED → REPLANNING
```

## Reliability Notes

- Tool calls use bounded retries with exponential backoff.
- After N consecutive tool/LLM failures, the Supervisor halts autonomous execution and escalates with reason `"agent degraded, human review needed"` rather than looping silently.
- State-changing tools (`assign_resource`, `execute_action`) are idempotent so a retried call can't double-book a resource.

See the main project documentation (`docs/NEXUS_Whole_Project_Documentation.md` if included, or the team's planning doc) for the full confidence-scoring formula and authorization-policy schema.
