# IT Helpdesk Triage Agent — Architecture

---

## Overview

The agent follows a **tool-augmented agentic loop** pattern using the Claude API via AWS Bedrock. It ingests a raw support request, enriches it via tools, then produces a structured `TriageResult`.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INBOUND CHANNELS                         │
│   Email  │  Slack  │  Web Form  │  Chat  │  Phone Transcript    │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Raw ticket (text + metadata)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TRIAGE AGENT (Claude)                       │
│                                                                 │
│  1. Receive ticket                                              │
│  2. Check for hard guardrail keywords → immediate escalation    │
│  3. Call tools as needed:                                       │
│     ├── knowledge_lookup(query)  →  FAQ match                   │
│     └── check_status(ticket_id)  →  SoR lookup                  │
│  4. Classify: queue + priority + confidence                     │
│  5. Apply mandate rules (auto-resolve vs. escalate vs. route)   │
│  6. Produce TriageResult with reasoning                         │
└──────────────┬──────────────────────────┬───────────────────────┘
               │                          │
       confidence ≥ 0.70           confidence < 0.70
       no guardrail hit             or guardrail hit
               │                          │
               ▼                          ▼
┌──────────────────────┐      ┌───────────────────────┐
│   ROUTING DECISION   │      │   HUMAN ESCALATION    │
│                      │      │   Queue: ESCALATION   │
│  P4 + pass checks    │      │   Priority: as-is     │
│  → AUTO_RESOLVE      │      │   + agent reasoning   │
│                      │      │   attached            │
│  P3/P4 + classified  │      └───────────────────────┘
│  → Route to queue    │
│  (IDENTITY,          │
│   NETWORKING, etc.)  │
└──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AUDIT LOG                                │
│   ticket_id | queue | priority | confidence | action | reasoning│
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Triage Agent (`agent/triage_agent.py`)
- **Entry point:** `triage(ticket: TicketInput) -> TriageResult`
- Runs an agentic loop: sends ticket to Claude, handles `tool_use` blocks, feeds results back, loops until `end_turn` or max iterations.
- Applies post-loop mandate rules (guardrail keyword check, confidence threshold, SLA breach flag).

### 2. Tools (`agent/tools.py`)
Two tools are registered with the Claude API:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `knowledge_lookup` | Search FAQ for relevant articles | `query: str` | `list[FAQResult]` (max 3) |
| `check_status` | Look up existing ticket in SoR | `ticket_id: str` | `TicketRecord \| None` |

### 3. Data Layer (`data/`)
- `faq.json` — 15 mock FAQ articles covering common IT issues. Each entry: `id`, `title`, `keywords`, `content`, `queue`.
- `tickets.json` — 10 mock open tickets. Each entry: `ticket_id`, `requester_email`, `current_status`, `assigned_queue`, `created_at`, `sla_breach`.

### 4. Eval Harness (`tests/eval_harness.py`)
- 10+ test cases: happy paths, edge cases, adversarial.
- Runs each case through the agent and checks: correct queue, correct priority, guardrail compliance, confidence threshold.
- Prints a scorecard.

---

## Routing Logic

```
ticket received
    │
    ├── keyword in ESCALATION_KEYWORDS?  ──► queue=ESCALATION, priority=P1
    │
    ├── agent classifies ticket
    │       │
    │       ├── queue=SECURITY?  ──────────► ESCALATION (security policy)
    │       │
    │       ├── priority=P1 or P2?  ───────► ESCALATION (human required)
    │       │
    │       ├── confidence < 0.70?  ────────► ESCALATION (low confidence)
    │       │
    │       ├── sla_breach=True?  ──────────► ESCALATION (SLA override)
    │       │
    │       ├── queue=IDENTITY + P4
    │       │   + no security flags
    │       │   + domain approved?  ────────► AUTO_RESOLVE
    │       │
    │       └── all other cases  ───────────► route to classified queue
```

---

## State & Context

- **No persistent session state** — each ticket is processed independently.
- **Context passed per call:** ticket body, sender email domain, ticket ID (if reference exists), current timestamp.
- **Tool results** are fed back into the Claude conversation as `tool_result` blocks within the same agentic loop turn.
- **Max iterations:** 5 tool calls per ticket (prevents runaway loops).

---

## Bedrock Configuration

- **Client:** `AnthropicBedrock` from the `anthropic` SDK
- **Model:** `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Region:** `us-east-1` (configurable via env var `AWS_REGION`)
- **Credentials:** standard AWS credential chain (env vars, instance profile, or `~/.aws/credentials`)
