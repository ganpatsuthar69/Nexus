# NEXUS — Autonomous Real-World Coordination Agent

## 1. Project Overview

**NEXUS** is an autonomous coordination platform designed to handle complex, rapidly changing real-world situations.

Instead of simply answering questions, NEXUS:

1. Observes incoming events and reports.
2. Builds and maintains a live world state.
3. Verifies conflicting or incomplete information.
4. Identifies priorities.
5. Finds available resources.
6. Creates an operational plan.
7. Executes safe actions through tools.
8. Monitors the results.
9. Detects failures or changes.
10. Replans automatically.
11. Escalates only decisions that genuinely require human judgment.
12. Records every important action and decision.

### Core Principle

> **NEXUS does not merely respond to a changing world. It continuously reasons about the world, acts on it, verifies the outcome, and replans when reality changes.**

---

# 2. Hackathon Track

**Agents for Humans Hackathon**

Recommended track:

## Good Neighbor Agents

NEXUS can coordinate community-scale problems such as:
- Disaster response
- Local resource shortages
- Community incidents
- Volunteer coordination
- Emergency logistics
- Shelter/resource allocation
- Infrastructure disruptions

The same underlying coordination engine can later support professional and organizational workflows.

---

# 3. Main Goal

The goal of NEXUS is to demonstrate a new class of AI agent:

> **A goal-oriented autonomous coordination agent that maintains a live representation of a changing environment and continuously adapts its plan until the objective is achieved or human judgment is required.**

Traditional automation usually follows:

```text
Trigger
  ↓
Fixed Workflow
  ↓
Action
  ↓
Done
```

NEXUS follows:

```text
Observe
  ↓
Understand
  ↓
Verify
  ↓
Plan
  ↓
Act
  ↓
Observe Again
  ↓
Did Reality Change?
  ├── No → Continue
  └── Yes
        ↓
      Replan
        ↓
      Act Again
```

---

# 4. Problem Statement

Real-world coordination is difficult because:

- Information comes from many sources.
- Reports can be incomplete.
- Different reports can contradict each other.
- Resources are limited.
- Multiple locations may compete for the same resource.
- Conditions change while a plan is being executed.
- Humans must repeatedly communicate, verify, update, and re-plan.
- Important decisions can become buried inside repetitive operational work.

NEXUS addresses this coordination gap.

---

# 5. Example Scenario — Community Disruption

Example incident:

> A severe heatwave causes power failures and water shortages across several neighborhoods.

Incoming information:

```text
Citizen reports
Weather events
Power outage reports
Water availability
Shelter capacity
Volunteer availability
Medical/resource requests
Community notices
Resource inventory
```

NEXUS creates a live situation model.

Example:

```text
AREA A
Population: 100
Water: CRITICAL
Power: OFF
Priority: HIGH

AREA B
Population: 20
Water: AVAILABLE
Power: OFF
Priority: MEDIUM

AREA C
Population: 25
Elderly residents: HIGH
Cooling: UNAVAILABLE
Priority: CRITICAL
```

NEXUS then allocates resources and coordinates actions.

---

# 6. Core Functionalities

## 6.1 Event Ingestion

NEXUS accepts incoming events such as:

- Citizen reports
- Organization reports
- Resource updates
- Volunteer availability
- Incident updates
- Infrastructure status changes
- System-generated events

Each event should contain:

```text
event_id
event_type
source
timestamp
location
description
severity
metadata
```

---

## 6.2 Situation Understanding

The agent analyzes incoming events and determines:

- What happened?
- Where did it happen?
- When did it happen?
- Who/what is affected?
- How severe is it?
- Is this a new incident or an update?
- Is it potentially a duplicate?
- Does it conflict with existing information?

---

## 6.3 Information Verification

NEXUS should not blindly trust every report.

Verification can compare:

```text
New report
    +
Existing world state
    +
Other reports
    +
Trusted sources
    ↓
Confidence assessment
```

Example:

```text
Report:
"Water tanker arrived."

Existing state:
"Tanker #1 unavailable."

NEXUS:
Conflict detected.

Action:
Verify tanker status.
```

---

## 6.4 World State Management

PostgreSQL stores the current operational state.

Core entities:

```text
Incidents
Locations
Resources
People / Teams
Assignments
Events
Tasks
Plans
Decisions
Audit Logs
```

The world state represents the current known condition.

---

# 7. Planning Engine

NEXUS converts the current world state into a plan.

Example:

```text
Goal:
Restore water access to Area A.

Available:
Tanker #2
Volunteer Team C
Temporary reserve at Shelter #2

Plan:
1. Assign Tanker #2.
2. Assign Volunteer Team C.
3. Coordinate reserve water.
4. Notify affected residents.
5. Verify delivery.
```

The plan is not static.

If a dependency fails, NEXUS recalculates.

---

# 8. Autonomous Replanning

This is one of the project's most important features.

Example:

```text
PLAN
Tanker #1 → Area A
```

Then:

```text
EVENT
Tanker #1 broken down
```

NEXUS detects:

```text
Current plan is no longer executable.
```

It then:

```text
Find alternative resources
        ↓
Evaluate alternatives
        ↓
Generate new plan
        ↓
Validate plan
        ↓
Execute
```

Example:

```text
NEW PLAN

Tanker #2 → Area A
Volunteer Team C → delivery coordination
Shelter #2 → temporary reserve
```

No human is required if the replacement is within predefined safe operating rules.

---

# 9. Resource Allocation

NEXUS maintains resource availability.

Example:

```text
RESOURCE
Generator #2

Status:
AVAILABLE

Capacity:
50 households

Location:
Area B
```

The agent evaluates:

- Distance
- Availability
- Capacity
- Priority
- Existing assignments
- Estimated time
- Constraints

It should avoid assigning the same resource to conflicting tasks.

---

# 10. Human-in-the-Loop

NEXUS must know when **not** to act autonomously.

Example:

```text
Two critical locations

Area A:
100 residents

Area C:
25 elderly residents

Only one generator available.
```

NEXUS can reason about the trade-off but should request human judgment when the decision crosses an authorization/policy boundary.

UI:

```text
┌──────────────────────────────────────┐
│ HUMAN DECISION REQUIRED              │
├──────────────────────────────────────┤
│ One generator is available.          │
│                                      │
│ Option A                             │
│ Area A — 100 residents              │
│                                      │
│ Option B                             │
│ Area C — 25 elderly residents       │
│                                      │
│ Why I stopped:                       │
│ Resource allocation requires human   │
│ priority selection.                  │
│                                      │
│ [Allocate A] [Allocate C]            │
└──────────────────────────────────────┘
```

After the decision:

```text
Human Decision
      ↓
World State Updated
      ↓
NEXUS Resumes
      ↓
Plan Executed
```

---

# 11. Verification After Action

NEXUS should not assume that an action succeeded.

Example:

```text
Action:
Send water tanker.

Expected:
Tanker reaches Area A.
```

NEXUS then verifies:

```text
Delivery confirmation
    +
Resource status
    +
New reports
    ↓
Success?
```

If successful:

```text
Task → COMPLETED
```

If failed:

```text
Task → FAILED
      ↓
Replan
```

This closed loop is a major differentiator.

---

# 12. Agent Architecture

```text
                         ┌───────────────────────┐
                         │       React UI        │
                         │     TypeScript        │
                         └───────────┬───────────┘
                                     │
                                  REST/API
                                     │
                         ┌───────────▼───────────┐
                         │       FastAPI         │
                         │       Backend         │
                         └───────────┬───────────┘
                                     │
                         ┌───────────▼───────────┐
                         │    NEXUS Supervisor   │
                         │    Strands Agent      │
                         └───────────┬───────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ Situation Agent │       │ Resource Agent  │       │ Verification    │
 │                 │       │                 │       │ Agent           │
 └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
                           ┌─────────────────┐
                           │ Planning Agent  │
                           └────────┬────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Execution Agent │
                           └────────┬────────┘
                                    │
                           ┌────────┴────────┐
                           ▼                 ▼
                      Safe Action      Human Decision
                           │                 │
                           └────────┬────────┘
                                    ▼
                             Verification
                                    │
                                    ▼
                             World State
                                    │
                                    ▼
                                Replan
```

---

# 13. Technology Stack

## Frontend

**ReactJS + TypeScript**

Recommended responsibilities:
- Incident dashboard
- Live world state
- Resource map/list
- Active plans
- Agent activity
- Human decision center
- Event timeline
- Audit history

## Backend

**Python + FastAPI**

Responsibilities:
- REST API
- Event ingestion
- Authentication if needed
- Database access
- Agent invocation
- WebSocket/SSE event streaming
- Human decision callbacks

## Agent Layer

**Strands Agents SDK**

Responsibilities:
- Agent reasoning
- Tool selection
- Agent orchestration
- Planning
- Verification
- Replanning
- Human escalation

## Database

**PostgreSQL**

Responsibilities:
- Persistent world state
- Events
- Incidents
- Resources
- Assignments
- Plans
- Tasks
- Human decisions
- Audit logs

## Optional AWS Layer

Potential services:
- Amazon Bedrock
- Amazon Bedrock AgentCore
- Amazon S3
- Amazon SQS
- Amazon EventBridge
- AWS Lambda

Do not add services solely for complexity. Each service should support an actual demonstrated capability.

---

# 14. High-Level System Architecture

```text
                    USERS / SIMULATION
                           │
                           ▼
                    React + TypeScript
                           │
                    REST / WebSocket
                           │
                           ▼
                        FastAPI
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       PostgreSQL                  Strands Agent
       World State                     │
             ▲                         │
             │              ┌──────────┼──────────┐
             │              ▼          ▼          ▼
             │         Situation    Resource   Verification
             │           Agent       Agent       Agent
             │              │          │          │
             │              └──────────┼──────────┘
             │                         ▼
             │                      Planner
             │                         │
             │                         ▼
             │                     Executor
             │                         │
             │                ┌────────┴────────┐
             │                ▼                 ▼
             │             Tools          Human Review
             │                │                 │
             └────────────────┴─────────────────┘
                              │
                              ▼
                         Verification
                              │
                              ▼
                           Replan
```

---

# 15. Suggested PostgreSQL Schema

## incidents

```text
id
title
description
status
severity
created_at
updated_at
```

## locations

```text
id
name
latitude
longitude
population
priority
current_status
```

## events

```text
id
incident_id
event_type
source
description
location_id
severity
confidence
created_at
processed_at
```

## resources

```text
id
name
resource_type
status
capacity
location_id
metadata
updated_at
```

## teams

```text
id
name
team_type
status
location_id
capacity
metadata
```

## assignments

```text
id
resource_id
team_id
task_id
status
assigned_at
completed_at
```

## plans

```text
id
incident_id
goal
status
version
reason
created_at
approved_by
```

## tasks

```text
id
plan_id
title
description
status
priority
assigned_resource_id
assigned_team_id
requires_human
created_at
completed_at
```

## decisions

```text
id
task_id
question
options
selected_option
decided_by
reason
created_at
```

## audit_logs

```text
id
entity_type
entity_id
action
actor
details
created_at
```

---

# 16. Core API Design

## Incidents

```http
POST   /api/incidents
GET    /api/incidents
GET    /api/incidents/{id}
```

## Events

```http
POST   /api/events
GET    /api/events
```

## Resources

```http
GET    /api/resources
POST   /api/resources
PATCH  /api/resources/{id}
```

## Plans

```http
GET    /api/incidents/{id}/plans
POST   /api/incidents/{id}/replan
```

## Human Decisions

```http
GET    /api/decisions/pending
POST   /api/decisions/{id}/resolve
```

## Agent

```http
POST   /api/agent/run
POST   /api/agent/events
GET    /api/agent/activity
```

## World State

```http
GET    /api/world-state
```

---

# 17. Strands Tool Design

The agent should interact with the system through explicit tools.

Potential tools:

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

The tools should be deterministic where possible.

The LLM should reason and select tools; business-critical state changes should happen through validated backend tools.

---

# 18. Agent Decision Loop

Pseudo-flow:

```text
1. Receive event
2. Load current world state
3. Analyze event
4. Check for conflicts/duplicates
5. Verify if necessary
6. Update world state
7. Determine whether current plans are affected
8. Recalculate priorities if required
9. Find available resources
10. Generate/revise plan
11. Validate plan
12. Execute safe actions
13. Verify results
14. If successful → continue
15. If failed → replan
16. If human judgment required → create decision
17. Wait for human decision
18. Resume from updated world state
19. Record audit trail
```

---

# 19. Agent State Machine

```text
OBSERVING
    ↓
ANALYZING
    ↓
VERIFYING
    ↓
PLANNING
    ↓
VALIDATING_PLAN
    ↓
EXECUTING
    ↓
VERIFYING_RESULT
    │
    ├── SUCCESS → COMPLETED / NEXT_TASK
    │
    ├── FAILURE → REPLANNING
    │
    └── HUMAN_REQUIRED → WAITING_HUMAN
                              ↓
                         DECISION_RECEIVED
                              ↓
                           REPLANNING
```

---

# 20. Safety and Authorization

NEXUS must distinguish between:

### Safe autonomous actions

Examples:
- Create internal task
- Update status
- Notify an assigned volunteer
- Recalculate a plan
- Mark duplicate reports
- Reserve an available non-critical resource according to configured rules

### Human-required actions

Examples:
- Conflicting high-priority resource allocation
- Actions outside authorization boundaries
- Sensitive decisions
- Irreversible actions
- Decisions involving policy ambiguity

The agent should explicitly explain:

```text
WHAT I KNOW
WHAT I DON'T KNOW
WHAT I RECOMMEND
WHY I STOPPED
WHAT DECISION I NEED
```

---

# 21. React Dashboard

Recommended screens:

## Dashboard

Show:

```text
Active Incidents
Critical Issues
Resources
Active Plans
Human Decisions
Agent Status
```

## Incident View

Show:
- Situation summary
- Affected locations
- Current world state
- Active plan
- Tasks
- Resources
- Timeline

## Human Decision Center

Show:
- Question
- Context
- Evidence
- Options
- Agent recommendation
- Reason for escalation

## Agent Activity

Show:

```text
13:04:21
Received report

13:04:22
Conflict detected

13:04:23
Verification started

13:04:25
Tanker #1 unavailable

13:04:27
Current plan invalidated

13:04:29
Alternative resource found

13:04:31
New plan created
```

## Resource Center

Show:
- Available
- Assigned
- Unavailable
- Location
- Capacity
- Current assignment

---

# 22. Signature Demo

The strongest demo should show **autonomy + failure + recovery + human judgment**.

### Initial state

```text
5 affected areas
8 resources
6 teams
30 incoming reports
```

NEXUS processes the information and creates an initial plan.

### Autonomous execution

Show several actions happening automatically.

### Inject failure

```text
Tanker #1 → BREAKDOWN
```

NEXUS detects that the plan is invalid.

### Autonomous recovery

It searches for alternatives and creates a new plan.

### Introduce ambiguity

Two critical areas require the same resource.

NEXUS stops and asks the human.

### Human decision

Human selects an option.

### Resume

NEXUS updates the world state and continues execution.

### Verify

NEXUS confirms the task succeeded.

This single sequence demonstrates most of the project's value.

---

# 23. What Makes NEXUS Different

NEXUS is not primarily:

- A chatbot
- A ticketing system
- A dashboard
- A recommendation engine
- A static workflow
- A notification system

NEXUS is:

> **A closed-loop autonomous coordination system.**

The defining loop is:

```text
OBSERVE
   ↓
REASON
   ↓
ACT
   ↓
VERIFY
   ↓
REPLAN
   ↓
ACT
```

The system continuously adapts to reality.

---

# 24. Key Innovation

## Live World Model + Autonomous Replanning

Traditional workflow:

```text
IF X
THEN Y
```

NEXUS:

```text
Given current world state:
What is happening?
What changed?
What is the goal?
What resources are available?
What plan should achieve the goal?
Can I safely execute it?
Did it work?
If not, what should I do next?
Do I need a human?
```

This is the central technical/product innovation.

---

# 25. Project Goals

### Primary Goal

Build a reliable autonomous agent capable of coordinating a simulated real-world disruption from detection through resolution.

### Secondary Goals

- Reduce manual coordination.
- Minimize unnecessary human intervention.
- Handle incomplete/contradictory information.
- Make resource allocation adaptive.
- Recover from execution failures.
- Keep humans in control of consequential decisions.
- Maintain a transparent audit trail.
- Demonstrate meaningful Strands Agents usage.

---

# 26. Success Metrics

For the demo, measure:

### Automation Rate

```text
Automatically completed tasks
-------------------------------- × 100
Total tasks
```

### Human Intervention Rate

```text
Human decisions
---------------- × 100
Total decisions/tasks
```

### Recovery Rate

```text
Failed plans successfully recovered
------------------------------------- × 100
Total failed plans
```

### Coordination Time

Compare:
- Manual simulated workflow
- NEXUS workflow

### Plan Adaptation

Measure:
- Number of detected plan invalidations
- Number of successful replans
- Time from failure detection to new plan

Do not invent real-world savings claims. Use measurable results from the demonstration/simulation.

---

# 27. Repository Structure

```text
nexus/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── db/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── simulation/
│   ├── scenarios/
│   ├── events/
│   └── seed_data/
│
├── docs/
│   ├── architecture.md
│   ├── agent-design.md
│   └── demo-script.md
│
├── architecture/
│   └── nexus-architecture.png
│
├── README.md
├── LICENSE
└── .gitignore
```

---

# 28. Development Principles

1. **Strands must be central**, not decorative.
2. LLM reasoning should be separated from deterministic business logic.
3. Database state must remain authoritative.
4. Every important state transition should be auditable.
5. Autonomous actions require explicit authorization boundaries.
6. Human escalation must be explainable.
7. The agent must verify actions instead of assuming success.
8. Failed plans should trigger controlled replanning.
9. UI should expose agent reasoning/results without exposing private chain-of-thought.
10. The demo must show actual end-to-end behavior.

---

# 29. MVP vs Advanced Version

## MVP

- Incident creation
- Event ingestion
- World state
- Resource management
- Strands Supervisor
- Situation analysis
- Planning
- Tool execution
- Failure injection
- Autonomous replanning
- Human decision
- Verification
- Audit log
- React dashboard

## Advanced

- Multi-incident coordination
- More sophisticated resource optimization
- Multiple independent organizations
- Negotiation between agents
- Real-time event streams
- Geographic visualization
- AgentCore deployment
- Observability
- Long-running workflows
- More realistic simulation
- A2A/multi-agent communication

---

# 30. Long-Term Vision

NEXUS should eventually become a general-purpose coordination engine.

The same architecture could coordinate:

```text
Disaster Response
       │
       ├── Community Operations
       ├── Infrastructure Incidents
       ├── Volunteer Networks
       ├── Logistics
       ├── Field Operations
       └── Organizational Operations
```

The domain-specific scenario is replaceable.

The core capability remains:

> **Maintain a live world model and autonomously coordinate actions toward a goal despite changing conditions.**

---

# 31. Hackathon Positioning

The project should be presented as:

> **NEXUS — The AI that coordinates reality, not just conversations.**

Alternative tagline:

> **“When reality changes, NEXUS changes the plan.”**

Core pitch:

> “Most automation follows a fixed workflow. Real life doesn't. NEXUS maintains a live model of a changing situation, coordinates resources, executes safe actions, verifies outcomes, and automatically replans when something goes wrong. It asks humans only when a decision genuinely requires human judgment.”

---

# 32. Recommended Hardening (Pre-Build Review)

Several earlier sections describe *what* NEXUS should do (verify, replan, escalate) but not precisely *how* — the gaps below are the most likely places a hackathon build would quietly fall over. None require new scope; they make existing sections concrete enough to implement without guesswork.

## 32.1 Event Deduplication & Idempotency

`event_id` uniqueness alone is not enough — retried submissions from a flaky citizen-report channel won't share an ID.

```text
Dedup key:
(source, location_id, description_hash, time_bucket)

If match found within time_bucket:
    treat as duplicate → link to existing event, do not create new one
Else:
    ingest as new event
```

## 32.2 Making "Confidence Assessment" Concrete

Section 6.3 names the concept; it needs a scoring rule the Verification Agent can actually run.

```text
confidence =
    source_trust_weight
  + corroboration_count_weight
  + recency_weight
  - contradiction_penalty

Example thresholds:
  > 0.8   → auto-accept into world state
  0.4–0.8 → flag, run verify_event() tool
  < 0.4   → hold; do not update world state; surface to human if blocking a plan
```

## 32.3 Authorization Boundaries as Config, Not Code

Section 20 draws the safe/human line conceptually. To keep it auditable and easy to demo, it should live as data, not scattered if-statements.

```text
policies table / policies.yaml

action_type
max_impact_scope        (# people / resources affected)
requires_human           (bool)
auto_approve_conditions  (e.g. "resource.priority == LOW")
```

This also makes Section 22's "human judgment" moment explainable in one line: *"this crossed policy threshold X."*

## 32.4 Resilience of the Agent Loop

The Decision Loop (Section 18) and State Machine (Section 19) assume every tool/LLM call succeeds. Add explicit failure handling:

```text
Tool/LLM call
    ↓
Timeout + bounded retry (exponential backoff)
    ↓
N consecutive failures?
    ├── No  → continue loop
    └── Yes → HALT autonomous execution
              → escalate: "agent degraded, human review needed"
```

Tool execution (especially `assign_resource`, `execute_action`) should be idempotent — re-running a step after a retry must not double-book a resource.

## 32.5 Observability Beyond the Audit Log

`audit_logs` (Section 15) records *what* happened. For debugging a live demo or a real incident, also carry a `trace_id` through one full observe→replan cycle so a single decision chain can be reconstructed, and track the loop-level metrics that already feed Section 26:

```text
loop_latency_ms
replans_triggered
escalations_raised
tool_call_failures
```

## 32.6 Security & Privacy (light-touch, not a blocker)

- Citizen reports can contain PII (names, addresses, phone numbers). Store free text and structured fields separately, and avoid echoing raw PII back into LLM prompts beyond what's needed.
- Even for a hackathon demo, put a basic API key/JWT check on the FastAPI endpoints — an unauthenticated `/api/agent/run` on a public URL during judging is an easy own-goal.

## 32.7 Demo Risk Mitigation

The Signature Demo (Section 22) depends on live LLM calls behaving well on stage.

- Keep a pre-recorded fallback video of the full sequence in case of rate limits or latency during judging.
- Support a `DEMO_MODE=scripted` flag that replays cached agent responses for the exact demo script, alongside `DEMO_MODE=live` for real runs.
- Rehearse and time the sequence — target 3–4 minutes end to end.

---

# 33. Final Product Definition

### NEXUS

**Input:**
A changing real-world situation.

**Processing:**
Observe → Understand → Verify → Plan → Execute → Verify → Replan.

**Output:**
Resolved tasks, updated world state, coordinated resources, and targeted human decisions.

### The ultimate product behavior

```text
              REAL WORLD CHANGES
                      ↓
                  NEXUS OBSERVES
                      ↓
                  NEXUS REASONS
                      ↓
                  NEXUS ACTS
                      ↓
                  NEXUS VERIFIES
                      ↓
             ┌────────┴────────┐
             │                 │
          SUCCESS            FAILURE
             │                 │
             ↓                 ↓
        Continue            REPLAN
                               │
                               ↓
                             ACT

                 HUMAN REQUIRED?
                       │
                      YES
                       ↓
                 ASK HUMAN
                       ↓
                 RECEIVE DECISION
                       ↓
                 UPDATE WORLD
                       ↓
                    RESUME
```

## Final Principle

> **NEXUS should make the human feel like the decision-maker, not the coordinator.**
