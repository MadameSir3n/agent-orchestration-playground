# Agent Orchestration Playground

A multi-agent orchestration system that coordinates AI workflows with built-in retry logic, backoff policies, and failure recovery using Temporal.

---

## Problem

AI agents that call external APIs fail silently, cascade failures across dependent steps, and leave no record of what went wrong or where. Debugging a failed 5-step agent pipeline with no observability wastes hours.

## Solution

This system wraps each agent activity inside a Temporal workflow, giving every step automatic retries, configurable backoff, idempotency guarantees, and a full execution trace — so failures are caught, retried, and logged without any manual intervention.

## Key Features

- Sequential agent execution with isolated failure boundaries
- Configurable retry policies with exponential backoff per activity
- Rate-limit detection and automatic pause-and-retry
- Dead-letter queue for tasks that exhaust all retries
- Idempotency keys to prevent duplicate side effects on retry
- Monitoring dashboard showing live workflow state

## Tech Stack

- **Python** — agent logic and workflow definitions
- **Temporal** — durable workflow orchestration engine
- **FastAPI** — HTTP interface for triggering workflows
- **Docker / Docker Compose** — single-command local deployment
- **MongoDB** — workflow state and result persistence

## Example Flow

```
1. POST /workflow/run  →  workflow queued in Temporal
2. Worker picks up task  →  validate_input() runs
3. Agent 1: fetch_market_price("AAPL")  →  returns $182.50
4. Agent 2: calculate_tax(182.50, "US-CA")  →  returns $15.51
5. Agent 3: send_notification("Trade complete")  →  delivered
6. Result written to MongoDB, workflow marked COMPLETED
```

If step 3 fails (API timeout), Temporal retries up to 3× with exponential backoff before routing to the dead-letter queue.

## How to Run

```bash
git clone https://github.com/MadameSir3n/agent-orchestration-playground.git
cd agent-orchestration-playground
pip install -r requirements.txt
python main.py
```

Run tests:

```bash
python -m pytest tests/ -v
```

Or with Docker (includes Temporal server + monitoring dashboard):

```bash
docker-compose up
# Dashboard: http://localhost:3000
# Temporal UI: http://localhost:8080
```

## Known Limitations

- Full workflow execution requires a running Temporal server (included in docker-compose)
- Some components are still being refined
- This is an active development system

## Sample Test Output

```
tests/test_agents.py::test_market_price_agent PASSED
tests/test_agents.py::test_tax_calculation_agent PASSED
tests/test_agents.py::test_notification_agent PASSED
tests/test_agents.py::test_agent_retry_on_failure PASSED
tests/test_workflows.py::test_validate_input PASSED
tests/test_workflows.py::test_fetch_market_price PASSED
tests/test_workflows.py::test_calculate_tax PASSED

7 passed in 0.91s
```

## Why This Matters

Production AI systems are only as reliable as their weakest integration point. This project demonstrates how durable workflow orchestration turns fragile agent pipelines into observable, self-healing systems — a critical pattern for any AI product that calls external services at scale.