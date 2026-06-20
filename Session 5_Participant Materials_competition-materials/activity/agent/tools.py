"""
Tool implementations for the IT Helpdesk Triage Agent.
Each function maps to a Claude API tool definition.
"""

import json
import os
from dataclasses import dataclass
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@dataclass
class FAQResult:
    id: str
    title: str
    content: str
    queue: str
    relevance_score: float

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "queue": self.queue,
            "relevance_score": self.relevance_score,
        }


@dataclass
class TicketRecord:
    ticket_id: str
    requester_email: str
    subject: str
    current_status: str
    assigned_queue: str
    priority: str
    created_at: str
    sla_breach: bool
    notes: str

    def to_dict(self) -> dict:
        return {
            "ticket_id": self.ticket_id,
            "requester_email": self.requester_email,
            "subject": self.subject,
            "current_status": self.current_status,
            "assigned_queue": self.assigned_queue,
            "priority": self.priority,
            "created_at": self.created_at,
            "sla_breach": self.sla_breach,
            "notes": self.notes,
        }


def _load_faq() -> list[dict]:
    path = os.path.join(DATA_DIR, "faq.json")
    with open(path, "r") as f:
        return json.load(f)


def _load_tickets() -> list[dict]:
    path = os.path.join(DATA_DIR, "tickets.json")
    with open(path, "r") as f:
        return json.load(f)


def knowledge_lookup(query: str) -> list[FAQResult]:
    """
    Search the FAQ knowledge base for articles relevant to the query.
    Returns up to 3 results ranked by keyword overlap score.
    """
    query_terms = set(query.lower().split())
    results = []

    for article in _load_faq():
        keyword_set = set(k.lower() for k in article["keywords"])
        title_terms = set(article["title"].lower().split())
        all_terms = keyword_set | title_terms

        overlap = len(query_terms & all_terms)
        if overlap > 0:
            score = round(overlap / max(len(query_terms), 1), 2)
            results.append(
                FAQResult(
                    id=article["id"],
                    title=article["title"],
                    content=article["content"],
                    queue=article["queue"],
                    relevance_score=min(score, 1.0),
                )
            )

    results.sort(key=lambda r: r.relevance_score, reverse=True)
    return results[:3]


def check_status(ticket_id: str) -> Optional[TicketRecord]:
    """
    Look up an existing ticket by ID in the system of record.
    Returns None if the ticket is not found.
    """
    for t in _load_tickets():
        if t["ticket_id"].upper() == ticket_id.upper():
            return TicketRecord(
                ticket_id=t["ticket_id"],
                requester_email=t["requester_email"],
                subject=t["subject"],
                current_status=t["current_status"],
                assigned_queue=t["assigned_queue"],
                priority=t["priority"],
                created_at=t["created_at"],
                sla_breach=t["sla_breach"],
                notes=t["notes"],
            )
    return None


def dispatch_tool_call(tool_name: str, tool_input: dict) -> str:
    """
    Route a tool_use block from Claude to the correct function.
    Returns a JSON string to be sent back as tool_result content.
    """
    if tool_name == "knowledge_lookup":
        results = knowledge_lookup(tool_input["query"])
        return json.dumps([r.to_dict() for r in results])

    if tool_name == "check_status":
        record = check_status(tool_input["ticket_id"])
        if record is None:
            return json.dumps({"error": f"Ticket {tool_input['ticket_id']} not found"})
        return json.dumps(record.to_dict())

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


# Claude API tool definitions — passed to the messages.create() call
TOOL_DEFINITIONS = [
    {
        "name": "knowledge_lookup",
        "description": (
            "Search the IT helpdesk FAQ knowledge base for articles relevant to the support request. "
            "Use this to find self-service solutions or to determine the correct routing queue. "
            "Returns up to 3 articles with title, content, queue, and relevance score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A short search query describing the user's issue (e.g. 'vpn not connecting', 'password reset')",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_status",
        "description": (
            "Look up an existing ticket in the system of record by its ticket ID. "
            "Use this when the user references an existing ticket number or when you need to check for SLA breaches or prior escalations. "
            "Returns ticket details including current status, assigned queue, priority, and SLA breach flag."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The ticket ID to look up, e.g. 'TKT-1001'",
                }
            },
            "required": ["ticket_id"],
        },
    },
]
