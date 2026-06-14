"""
Session 3, Block 2: TechFlow Support Agent — COMPLETE SOLUTION

This is the finished version of agent.py with all TODOs completed.
Use this if you get stuck, or to check your work.

Run with: python agent_solution.py
Custom query: python agent_solution.py "What's the status of order ORD-5678?"
"""

import sys
import json
from datetime import datetime

from anthropic import AnthropicBedrock

client = AnthropicBedrock(
    aws_region="us-west-2",
    aws_profile="bootcamp",
)

# ============================================================
# MOCK--DUMMY DATA (simulating a real database)
# ============================================================

customers = {
    "alice@example.com": {"name": "Alice Johnson", "email": "alice@example.com", "plan": "Pro", "signup_date": "2024-03-15"},
    "bob@example.com": {"name": "Bob Smith", "email": "bob@example.com", "plan": "Free", "signup_date": "2024-08-01"},
    "carol@example.com": {"name": "Carol Davis", "email": "carol@example.com", "plan": "Enterprise", "signup_date": "2023-11-20"},
}

orders = {
    "ORD-1234": {"order_id": "ORD-1234", "customer": "alice@example.com", "status": "delayed", "items": ["Widget Pro", "Gadget Plus"], "eta": "2025-04-20"},
    "ORD-5678": {"order_id": "ORD-5678", "customer": "bob@example.com", "status": "shipped", "items": ["Basic Widget"], "eta": "2025-04-15"},
    "ORD-9999": {"order_id": "ORD-9999", "customer": "carol@example.com", "status": "delivered", "items": ["Enterprise Suite"], "eta": "2025-04-10"},
}

ticket_counter = 1000

# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def lookup_customer(email: str) -> str:
    customer = customers.get(email)
    if not customer:
        return json.dumps({"error": f"No customer found with email: {email}"})
    return json.dumps(customer)


def check_order_status(order_id: str) -> str:
    order = orders.get(order_id)
    if not order:
        return json.dumps({"error": f"No order found with ID: {order_id}"})
    return json.dumps(order)


def create_ticket(customer_email: str, subject: str, priority: str) -> str:
    global ticket_counter
    ticket_counter += 1
    return json.dumps({
        "ticket_id": f"TKT-{ticket_counter}",
        "customer": customer_email,
        "subject": subject,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
    })

# ============================================================
# TOOL DEFINITIONS (what Claude sees)
# ============================================================

tools = [
    {
        "name": "lookup_customer",
        "description": "Look up a customer by their email address. Returns customer name, email, plan type, and signup date. Use this when you need to find information about a specific customer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email address"},
            },
            "required": ["email"],
        },
    },
    {
        "name": "check_order_status",
        "description": "Check the status of an order by order ID. Returns order status (pending/shipped/delivered/delayed), items, and estimated delivery date. Use this when a customer asks about their order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID (e.g., ORD-1234)"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "create_ticket",
        "description": "Create a new support ticket for a customer. Use this when an issue needs to be tracked or escalated — for example, when an order is delayed or a customer reports a problem.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_email": {"type": "string", "description": "Customer's email address"},
                "subject": {"type": "string", "description": "Brief description of the issue"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Ticket priority level"},
            },
            "required": ["customer_email", "subject", "priority"],
        },
    },
]

# ============================================================
# TOOL EXECUTOR (routes tool calls to implementations)
# ============================================================

def execute_tool(name: str, tool_input: dict) -> str:
    if name == "lookup_customer":
        return lookup_customer(tool_input["email"])
    elif name == "check_order_status":
        return check_order_status(tool_input["order_id"])
    elif name == "create_ticket":
        return create_ticket(tool_input["customer_email"], tool_input["subject"], tool_input["priority"])
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

# ============================================================
# THE AGENTIC LOOP (COMPLETE)
# ============================================================

SYSTEM_PROMPT = """You are a helpful support agent for TechFlow, a technology company.
You help customers with order inquiries, account questions, and support issues.
Always be polite and professional. When an order is delayed, proactively offer to create a support ticket.
Use the available tools to look up real customer and order data — never make up information."""


def run_agent(user_message: str) -> str:
    print(f"\n{'=' * 60}")
    print(f"User: {user_message}")
    print(f"{'=' * 60}\n")

    messages = [
        {"role": "user", "content": user_message},
    ]

    # TODO 1: Make the initial API call
    response = client.messages.create(
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )

    loop_count = 0
    max_loops = 10

    # TODO 2: The while loop condition
    while response.stop_reason == "tool_use" and loop_count < max_loops:

        loop_count += 1

        # TODO 3: Extract tool_use blocks from the response
        tool_blocks = [block for block in response.content if block.type == "tool_use"]
py
        print(f"--- Loop {loop_count}: {len(tool_blocks)} tool call(s) ---")

        # TODO 4: Execute each tool and build tool_result messages
        tool_results = []
        for block in tool_blocks:
            print(f"  Tool: {block.name}({json.dumps(block.input)})")
            result = execute_tool(block.name, block.input)
            print(f"  Result: {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        # TODO 5: Add messages to the conversation history
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        # TODO 6: Make the next API call
        response = client.messages.create(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

    # Extract the final text response
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text

    print(f"\nAgent: {final_text}")
    print(f"\n({loop_count} tool loop(s), stop_reason: {response.stop_reason})")

    return final_text


# ============================================================
# RUN THE AGENT
# ============================================================

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Check order ORD-1234 for customer alice@example.com and create a ticket if it's delayed"
    run_agent(query)
