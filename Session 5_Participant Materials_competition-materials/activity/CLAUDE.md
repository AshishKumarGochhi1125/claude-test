# Competition Project

## What This Is
An intelligent IT Helpdesk triage agent (Scenario 3) that classifies inbound support requests, assigns priority (P1–P4), routes to the correct queue, and auto-resolves low-risk tickets (e.g., password resets) — all via the Claude API on AWS Bedrock.

## Tech Stack
- Python 3.11+
- `anthropic` SDK via `AnthropicBedrock` client (AWS Bedrock)
- `boto3` for any AWS integrations
- `pydantic` for structured request/response schemas
- `pytest` for the eval harness (Challenge 5)

## Project Structure
```
activity/
├── CLAUDE.md               # This file — domain rules and conventions
├── agent/
│   ├── triage_agent.py     # Core agent loop (Challenge 3)
│   ├── tools.py            # Tool definitions: knowledge_lookup, check_status (Challenge 4)
│   ├── mandate.md          # Agent mandate document (Challenge 1)
│   └── architecture.md     # Architecture diagram and routing logic (Challenge 2)
├── data/
│   ├── faq.json            # Mock FAQ knowledge base
│   └── tickets.json        # Mock system-of-record ticket data
└── tests/
    └── eval_harness.py     # 10+ test cases and scorecard (Challenge 5)
```

## Conventions

### Priority Levels
| Priority | Label | SLA (first response) | Examples |
|----------|-------|----------------------|---------|
| P1 | Critical | 15 min | Production outage, security breach, all users blocked |
| P2 | High | 1 hour | Key user or team fully blocked, data loss risk |
| P3 | Medium | 4 hours | Partial degradation, workaround available |
| P4 | Low | 1 business day | General questions, cosmetic issues, password resets |

### Queues / Routing Targets
- `SECURITY` — any credential compromise, phishing, or data-exfiltration signal
- `NETWORKING` — VPN, Wi-Fi, DNS, firewall, connectivity issues
- `IDENTITY` — Active Directory, SSO, MFA, account unlock, access provisioning
- `HARDWARE` — laptop, printer, peripheral failures
- `SOFTWARE` — application installs, license issues, OS bugs
- `AUTO_RESOLVE` — password resets and account unlocks that pass policy checks (no P1/P2, no security flags)
- `ESCALATION` — anything the agent cannot confidently classify (confidence < 0.70) or that hits a guardrail

### Naming Conventions
- Tool functions: `snake_case`, prefixed by verb (`lookup_`, `check_`, `send_`)
- Structured responses: `TriageResult` Pydantic model with fields: `classification`, `priority`, `queue`, `confidence`, `action`, `reasoning`
- Test case IDs: `TC-{number:03d}` (e.g., `TC-001`)

## Important Context

### Agent Mandate (summary — full doc in `agent/mandate.md`)
**The agent CAN decide autonomously:**
- Classify any inbound ticket into one of the queues above
- Assign P3 or P4 priority
- Auto-resolve P4 password-reset tickets that pass the identity-policy check

**The agent MUST escalate to a human when:**
- Confidence score < 0.70
- Any P1 or P2 signal detected
- Request involves data deletion, privilege escalation, or firewall-rule changes
- A SECURITY queue signal is present
- The requester mentions legal, HR, or executive names

**The agent must NEVER:**
- Execute system commands or make live API calls to production systems
- Store or log credentials, PII beyond ticket ID and email domain, or raw passwords
- Auto-approve access to sensitive systems (finance, payroll, source code repos)
- Take irreversible actions without a human confirmation step

### Escalation Triggers (specific)
- Keywords: `"breach"`, `"ransomware"`, `"executive"`, `"GDPR"`, `"lawsuit"`, `"delete all"`
- Sender domain not in approved internal list → flag for identity verification
- Ticket older than SLA with no first-response → auto-escalate with `sla_breach=True`

### Tool Schemas

**`knowledge_lookup(query: str) -> list[FAQResult]`**
Searches the mock FAQ (`data/faq.json`) and returns up to 3 matching articles with `title`, `content`, and `relevance_score`.

**`check_status(ticket_id: str) -> TicketRecord | None`**
Looks up a ticket in the mock system of record (`data/tickets.json`). Returns `None` if not found.
Returns: `ticket_id`, `requester_email`, `current_status`, `assigned_queue`, `created_at`, `sla_breach`.

### Reasoning Log
Every `TriageResult` must include a `reasoning` field — a 2–4 sentence explanation of why the agent chose this classification and action. Judges evaluate the thinking, not just the answer.

### Domain Vocabulary
- **Ticket** — a single inbound support request
- **Queue** — the team that owns resolution
- **SLA breach** — ticket has exceeded its priority-level response time
- **Auto-resolve** — agent closes the ticket and sends a self-service link without human involvement
- **Escalation** — ticket is handed to a human with the agent's classification and reasoning attached
