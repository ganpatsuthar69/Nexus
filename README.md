# NEXUS — Autonomous Real-World Coordination Agent

> **NEXUS — The AI that coordinates reality, not just conversations.**

Built for the **Agents for Humans Hackathon** (AWS × Devpost) — **Good Neighbor Agents** track.

---

## 1. What NEXUS Does

NEXUS is an autonomous coordination agent for community-scale disruptions (power outages, water shortages, shelter/resource allocation, volunteer coordination). Instead of just answering questions, it:

1. Observes incoming events and reports.
2. Builds and maintains a live world state.
3. Verifies conflicting or incomplete information.
4. Plans, executes, and monitors safe actions through tools.
5. Detects failures and **replans automatically**.
6. Escalates to a human **only** when a decision genuinely requires human judgment.
7. Records every action and decision in an audit trail.

**Core loop:** `Observe → Understand → Verify → Plan → Act → Verify → Replan`

## 2. Problem & Audience

Real-world coordination (disaster response, local resource shortages, volunteer logistics) is hard because information is incomplete, contradictory, and constantly changing, while resources are limited and contested. Community organizers and volunteer coordinators currently do this verification/replanning work manually. NEXUS automates the routine coordination work and surfaces only the decisions that need a human.

## 3. Why Strands Agents

NEXUS's supervisor/sub-agent design is implemented with the **Strands Agents SDK**:

- **Supervisor Agent** — orchestrates the overall loop and delegates to sub-agents.
- **Situation Agent** — interprets incoming events against current world state.
- **Resource Agent** — evaluates resource availability/allocation.
- **Verification Agent** — scores confidence and detects conflicts/duplicates.
- **Planning Agent** — converts world state + goal into an executable plan.
- **Execution Agent** — calls tools to carry out safe actions, or routes to human review.

Tools are explicit and deterministic where possible (`create_plan`, `assign_resource`, `verify_action`, `request_human_decision`, `trigger_replan`, etc.) — the LLM reasons and selects tools, but state-changing operations go through validated backend tools rather than free-form generation. See [`docs/agent-design.md`](docs/agent-design.md) for the full tool list, decision loop, and state machine.

## 4. Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full diagram and component breakdown.

```text
React (TypeScript) → FastAPI → Strands Supervisor Agent
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
             Situation Agent   Resource Agent   Verification Agent
                    └────────────────┼────────────────┘
                                     ▼
                              Planning Agent → Execution Agent
                                     │
                        ┌────────────┴────────────┐
                        ▼                          ▼
                  Safe Tool Action           Human Decision Center
                        └────────────┬────────────┘
                                     ▼
                        Verification → World State (PostgreSQL) → Replan
```

## 5. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript |
| Backend | Python + FastAPI |
| Agent layer | **Strands Agents SDK** |
| LLM | Amazon Bedrock |
| Database | PostgreSQL |
| Optional AWS | Bedrock AgentCore, S3, SQS, EventBridge, Lambda |

AWS services are added only where they support a demonstrated capability — see `docs/architecture.md` for justification per service.

## 6. Repository Structure

```text
nexus/
├── backend/            # FastAPI app, Strands agents, tools, DB models
│   ├── app/
│   │   ├── api/ agents/ tools/ services/ models/ schemas/ db/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/            # React + TypeScript dashboard
│   ├── src/
│   └── package.json
├── simulation/          # Scenario/event data for the demo
│   ├── scenarios/ events/ seed_data/
├── docs/
│   ├── architecture.md
│   ├── agent-design.md
│   └── demo-script.md
├── architecture/
│   └── nexus-architecture.png
├── README.md
├── LICENSE
└── .gitignore
```

## 7. Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- An AWS account with Amazon Bedrock access
- A [Strands Agents SDK](https://strandsagents.com) API key/config

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # fill in DB + AWS/Bedrock credentials
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Database
```bash
# create the database, then run migrations (see backend/app/db)
createdb nexus
```

### Run the Demo Scenario
```bash
cd simulation
python run_scenario.py scenarios/heatwave_demo.json
```
This replays the signature demo: autonomous processing → injected tanker breakdown → autonomous replan → resource conflict → human decision → resume → verified completion.

## 8. Environment Variables

See [`.env.example`](.env.example) for the full list (database connection, AWS region/credentials, Bedrock model ID, Strands config, demo mode flag).

## 9. Demo

- **Demo video:** _add public YouTube/Vimeo link here before submission_
- **Live demo (optional):** _add URL here if available_
- **Demo script:** see [`docs/demo-script.md`](docs/demo-script.md)

## 10. Hackathon Submission Info

- **Event:** Agents for Humans Hackathon (AWS × Devpost)
- **Track:** Good Neighbor Agents
- **New project:** Yes — created during the submission period
- **Required tech used:** Strands Agents SDK, AWS account (Amazon Bedrock)
- **License:** MIT (see [`LICENSE`](LICENSE))

## 11. Disclosures

This project uses no pre-existing proprietary code. Third-party dependencies (see `backend/requirements.txt` and `frontend/package.json`) are used under their respective open-source licenses. Any starter templates or AI-assisted code will be documented here per the hackathon rules.

## 12. Success Metrics (Demo)

Measured against the simulated scenario, not real-world claims:
- Automation rate (tasks completed without human input / total tasks)
- Human intervention rate
- Recovery rate (failed plans successfully replanned)
- Coordination time vs. a manual baseline

## License

MIT — see [`LICENSE`](LICENSE).
