from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from .email_digest import infer_next_action, parse_email_items, summarize_body


@dataclass
class CalendarEvent:
    date: str
    time: str
    title: str
    status: str
    notes: str


def parse_calendar_events(path: Path) -> list[CalendarEvent]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            CalendarEvent(
                row.get("date", ""),
                row.get("time", ""),
                row.get("title", "Untitled event"),
                row.get("status", "scheduled"),
                row.get("notes", ""),
            )
            for row in reader
        ]


def build_report_draft(email_path: Path, calendar_path: Path, period: str, output_format: str) -> str:
    emails = parse_email_items(email_path)
    events = parse_calendar_events(calendar_path)
    report = {
        "period": period,
        "summary": {
            "email_count": len(emails),
            "event_count": len(events),
            "completed_events": sum(1 for event in events if event.status.lower() == "completed"),
            "follow_ups": sum(1 for item in emails if infer_next_action(item.body) != "Read and decide whether follow-up is needed."),
        },
        "key_issues": build_key_issues(emails, events),
        "meetings": [
            {
                "date": event.date,
                "time": event.time,
                "title": event.title,
                "status": event.status,
                "notes": event.notes,
            }
            for event in events
        ],
        "email_brief": [
            {
                "sender": item.sender,
                "subject": item.subject,
                "summary": summarize_body(item.body),
                "next_action": infer_next_action(item.body),
            }
            for item in emails
        ],
        "next_actions": build_next_actions(emails, events),
    }

    if output_format == "json":
        return json.dumps(report, indent=2, ensure_ascii=False) + "\n"

    return render_report_markdown(report)


def build_key_issues(emails, events: list[CalendarEvent]) -> list[str]:
    issues: list[str] = []
    for item in emails:
        action = infer_next_action(item.body)
        if action != "Read and decide whether follow-up is needed.":
            issues.append(f"{item.subject}: {action}")
    for event in events:
        if event.status.lower() not in {"completed", "done"}:
            issues.append(f"{event.title}: {event.status}")
    return issues[:8]


def build_next_actions(emails, events: list[CalendarEvent]) -> list[str]:
    actions: list[str] = []
    for item in emails:
        action = infer_next_action(item.body)
        if action != "Read and decide whether follow-up is needed.":
            actions.append(f"{action} ({item.subject})")
    for event in events:
        if event.status.lower() in {"scheduled", "pending"}:
            actions.append(f"Prepare for {event.title} on {event.date} {event.time}".strip())
    return actions[:10]


def render_report_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        f"# {str(report['period']).title()} Work Report Draft",
        "",
        "## Summary",
        "",
        f"- Emails reviewed: {summary['email_count']}",
        f"- Calendar events reviewed: {summary['event_count']}",
        f"- Completed events: {summary['completed_events']}",
        f"- Follow-ups detected: {summary['follow_ups']}",
        "",
        "## Key Issues",
        "",
    ]

    key_issues = report["key_issues"]
    assert isinstance(key_issues, list)
    if not key_issues:
        lines.append("- No key issues detected from the sample inputs.")
    for issue in key_issues:
        lines.append(f"- {issue}")

    lines.extend(["", "## Meetings", ""])
    meetings = report["meetings"]
    assert isinstance(meetings, list)
    if not meetings:
        lines.append("- No calendar events provided.")
    for meeting in meetings:
        lines.append(
            f"- {meeting['date']} {meeting['time']} - {meeting['title']} "
            f"({meeting['status']}): {meeting['notes']}"
        )

    lines.extend(["", "## Email Brief", ""])
    email_brief = report["email_brief"]
    assert isinstance(email_brief, list)
    if not email_brief:
        lines.append("- No email items provided.")
    for item in email_brief:
        lines.extend(
            [
                f"### {item['subject']}",
                "",
                f"- Sender: {item['sender']}",
                f"- Summary: {item['summary']}",
                f"- Next action: {item['next_action']}",
                "",
            ]
        )

    lines.extend(["## Next Actions", ""])
    next_actions = report["next_actions"]
    assert isinstance(next_actions, list)
    if not next_actions:
        lines.append("- Review the report and decide whether follow-up is needed.")
    for action in next_actions:
        lines.append(f"- {action}")

    lines.extend(
        [
            "",
            "## Privacy Note",
            "",
            "This draft was generated from local sample files. Review and remove private information before sharing.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
