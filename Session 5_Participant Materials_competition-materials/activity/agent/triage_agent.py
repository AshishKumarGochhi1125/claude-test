"""
IT Helpdesk Triage Agent — Core agentic loop (Challenge 3 + 4).

Entry point: triage(ticket) -> TriageResult

Flow:
  1. Check hard guardrail keywords before sending to Claude.
  2. Run agentic loop: Claude classifies, calls tools, refines.
  3. Apply post-loop mandate rules (confidence, SLA breach, security flags).
  4. Return structured TriageResult with reasoning.
"""

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Optional

from anthropic import AnthropicBedrock

from tools import TOOL_DEFINITIONS, dispatch_tool_call

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
MAX_TOOL_ITERATIONS = 5

APPROVED_DOMAINS = {
    "acme.internal",
    "corp.acme.com",
    "acmepartner.com",
}

ESCALATION_KEYWORDS = {
    "breach", "ransomware", "hack", "hacked", "executive", "gdpr",
    "lawsuit", "legal action", "delete all", "wipe", "exfiltrate",
    "data exfiltration", "zero-day",
}

VALID_QUEUES = {"SECURITY", "NETWORKING", "IDENTITY", "HARDWARE", "SOFTWARE", "AUTO_RESOLVE", "ESCALATION"}
VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}
VALID_ACTIONS = {"AUTO_RESOLVE", "ROUTE", "ESCALATE"}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class TicketInput:
    body: str
    sender_email: str
    ticket_id: Optional[str] = None
    subject: Optional[str] = None


@dataclass
class TriageResult:
    ticket_id: Optional[str]
    classification: str       # queue name
    priority: str             # P1-P4
    confidence: float         # 0.0 - 1.0
    action: str               # AUTO_RESOLVE | ROUTE | ESCALATE
    reasoning: str            # 2-4 sentence explanation
    sla_breach: bool = False
    guardrail_triggered: bool = False
    guardrail_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an IT Helpdesk Triage Agent. Your job is to classify inbound support tickets, assign a priority, and decide how to handle them.

QUEUES (pick exactly one):
- SECURITY: credential compromise, phishing, malware, data breach signals
- NETWORKING: VPN, Wi-Fi, DNS, firewall, connectivity
- IDENTITY: Active Directory, SSO, MFA, account unlock, access provisioning
- HARDWARE: laptop, printer, monitor, peripheral failures
- SOFTWARE: application installs, licenses, OS bugs, configuration
- AUTO_RESOLVE: P4 password resets / account unlocks that pass all policy checks
- ESCALATION: low confidence, P1/P2, security signals, or out-of-mandate requests

PRIORITY LEVELS:
- P1 Critical: Production outage, security incident, all users blocked (15-min SLA)
- P2 High: Key user fully blocked, data loss risk (1-hour SLA)
- P3 Medium: Partial degradation, workaround available (4-hour SLA)
- P4 Low: General questions, cosmetic issues, password resets (1-day SLA)

AUTO_RESOLVE rules (ALL must be true):
1. Queue is IDENTITY (password reset or account unlock only)
2. Priority is P4
3. No security flags in the request
4. Sender domain is on the approved internal list (use check_status or note the domain)

ESCALATE when:
- Confidence < 0.70
- Priority is P1 or P2
- Queue is SECURITY
- Request involves data deletion, privilege escalation, or firewall changes
- Mentions legal, HR, executive names
- Sender domain is unrecognized

Use your tools to look up relevant FAQ articles and check existing ticket status before classifying.

ALWAYS respond with a JSON object in this exact format (no markdown, no extra text):
{
  "classification": "<QUEUE>",
  "priority": "<P1|P2|P3|P4>",
  "confidence": <0.0-1.0>,
  "action": "<AUTO_RESOLVE|ROUTE|ESCALATE>",
  "reasoning": "<2-4 sentence explanation>"
}"""


# ---------------------------------------------------------------------------
# Guardrail check
# ---------------------------------------------------------------------------

def _check_guardrails(ticket: TicketInput) -> Optional[tuple[str, str]]:
    """
    Returns (reason, description) if a hard guardrail is triggered, else None.
    Checks keyword triggers and sender domain.
    """
    text = f"{ticket.subject or ''} {ticket.body}".lower()
    for kw in ESCALATION_KEYWORDS:
        if kw in text:
            return ("KEYWORD_TRIGGER", f"Escalation keyword detected: '{kw}'")

    domain = ticket.sender_email.split("@")[-1].lower() if "@" in ticket.sender_email else ""
    if domain and domain not in APPROVED_DOMAINS:
        return ("UNKNOWN_DOMAIN", f"Sender domain '{domain}' is not on the approved list")

    return None


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def triage(ticket: TicketInput) -> TriageResult:
    """
    Main entry point. Runs the agentic loop and returns a TriageResult.
    """
    # Hard guardrail check before touching Claude
    guardrail = _check_guardrails(ticket)
    if guardrail:
        reason_code, reason_desc = guardrail
        return TriageResult(
            ticket_id=ticket.ticket_id,
            classification="ESCALATION",
            priority="P1" if reason_code == "KEYWORD_TRIGGER" else "P2",
            confidence=1.0,
            action="ESCALATE",
            reasoning=(
                f"Guardrail triggered before classification: {reason_desc}. "
                "This ticket requires immediate human review and cannot be processed autonomously."
            ),
            guardrail_triggered=True,
            guardrail_reason=reason_desc,
        )

    # Build user message
    user_content = (
        f"Please triage the following IT support ticket.\n\n"
        f"Ticket ID: {ticket.ticket_id or 'N/A'}\n"
        f"Sender: {ticket.sender_email}\n"
        f"Subject: {ticket.subject or '(no subject)'}\n\n"
        f"Request:\n{ticket.body}"
    )

    messages = [{"role": "user", "content": user_content}]

    client = AnthropicBedrock(aws_region=AWS_REGION)

    # Agentic loop
    for iteration in range(MAX_TOOL_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Append assistant response to conversation
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            if iteration >= MAX_TOOL_ITERATIONS:
                # Max iterations reached — escalate
                return TriageResult(
                    ticket_id=ticket.ticket_id,
                    classification="ESCALATION",
                    priority="P2",
                    confidence=0.0,
                    action="ESCALATE",
                    reasoning="Agent exceeded maximum tool iterations without reaching a conclusion. Human review required.",
                    guardrail_triggered=True,
                    guardrail_reason="MAX_TOOL_ITERATIONS exceeded",
                )

            # Execute each tool call and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_content = dispatch_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content,
                    })

            messages.append({"role": "user", "content": tool_results})

    # Extract text from the final response
    raw_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw_text += block.text

    return _parse_response(raw_text, ticket)


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def _parse_response(raw: str, ticket: TicketInput) -> TriageResult:
    """
    Parse Claude's JSON response into a TriageResult.
    Falls back to ESCALATION if parsing fails.
    """
    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        data = json.loads(cleaned)

        classification = data.get("classification", "ESCALATION").upper()
        priority = data.get("priority", "P3").upper()
        confidence = float(data.get("confidence", 0.5))
        action = data.get("action", "ESCALATE").upper()
        reasoning = data.get("reasoning", "No reasoning provided.")

        # Validate values
        if classification not in VALID_QUEUES:
            classification = "ESCALATION"
        if priority not in VALID_PRIORITIES:
            priority = "P3"
        if action not in VALID_ACTIONS:
            action = "ESCALATE"

        # Apply post-parse mandate rules
        if confidence < 0.70:
            classification = "ESCALATION"
            action = "ESCALATE"
            reasoning += " Confidence below threshold — escalating to human."

        if priority in ("P1", "P2"):
            action = "ESCALATE"

        if classification == "SECURITY":
            action = "ESCALATE"

        return TriageResult(
            ticket_id=ticket.ticket_id,
            classification=classification,
            priority=priority,
            confidence=confidence,
            action=action,
            reasoning=reasoning,
        )

    except (json.JSONDecodeError, KeyError, ValueError):
        return TriageResult(
            ticket_id=ticket.ticket_id,
            classification="ESCALATION",
            priority="P2",
            confidence=0.0,
            action="ESCALATE",
            reasoning=f"Failed to parse agent response. Raw output: {raw[:200]}",
            guardrail_triggered=True,
            guardrail_reason="PARSE_ERROR",
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("IT Helpdesk Triage Agent")
    print("=" * 40)
    print("Enter ticket details (Ctrl+C to quit)\n")

    sender = input("Sender email: ").strip()
    subject = input("Subject: ").strip()
    print("Request body (end with a blank line):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    body = "\n".join(lines)

    ticket = TicketInput(body=body, sender_email=sender, subject=subject)
    result = triage(ticket)

    print("\n--- TRIAGE RESULT ---")
    print(json.dumps(result.to_dict(), indent=2))
