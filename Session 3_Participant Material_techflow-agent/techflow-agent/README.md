# TechFlow Support Agent

A simple AI agent that demonstrates the agentic loop pattern — the same pattern that powers Claude Code.

## Setup
```bash
cd techflow-agent
pip install -r requirements.txt
```

## Prerequisites
- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set

## The Exercise

Open `agent.py` — it has 6 TODOs for you to complete. The mock data, tool definitions, and tool executor are done. Your job is to build the agentic loop.

### The 6 TODOs:
1. Make the initial API call
2. Write the while loop condition
3. Extract tool_use blocks from the response
4. Execute each tool and build tool_result messages
5. Add messages to the conversation history
6. Make the next API call inside the loop

## Run Your Agent
```bash
python agent.py
```

Default query: "Check order ORD-1234 for customer alice@example.com and create a ticket if it's delayed"

Custom query:
```bash
python agent.py "What's the status of order ORD-5678?"
```

## If You Get Stuck
Check `agent_solution.py` for the complete working version.

## Available Test Queries
- `"Check order ORD-1234 for alice@example.com"` — Multi-step (lookup + check + ticket)
- `"What's the status of order ORD-5678?"` — Simple lookup
- `"Look up customer bob@example.com"` — Single tool call
- `"Find order ORD-0000"` — Edge case (order doesn't exist)
- `"Look up customer unknown@example.com"` — Edge case (customer doesn't exist)

## How It Works
1. User sends a message
2. Claude API receives it with 3 tool definitions
3. Claude responds with `stop_reason: "tool_use"`
4. Agent executes the tool and sends result back
5. Loop continues until Claude responds with `stop_reason: "end_turn"`

## The Three Tools
- **lookup_customer**: Find customer by email
- **check_order_status**: Check order by ID
- **create_ticket**: Create a support ticket

## Run Evaluations (Block 3)
```bash
python eval.py
```
