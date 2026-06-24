from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmailItem:
    sender: str
    subject: str
    body: str


def parse_email_items(path: Path) -> list[EmailItem]:
    text = path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in text.split("\n---\n") if block.strip()]
    items: list[EmailItem] = []

    for block in blocks:
        fields = {"from": "unknown", "subject": "No subject", "body": ""}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
        items.append(EmailItem(fields["from"], fields["subject"], fields["body"]))

    return items


def build_email_digest(path: Path, output_format: str) -> str:
    items = parse_email_items(path)
    rows = [
        {
            "sender": item.sender,
            "subject": item.subject,
            "summary": summarize_body(item.body),
            "next_action": infer_next_action(item.body),
        }
        for item in items
    ]

    if output_format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["sender", "subject", "summary", "next_action"])
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()

    lines = ["# Email Digest for Notion", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['subject']}",
                "",
                f"- Sender: {row['sender']}",
                f"- Summary: {row['summary']}",
                f"- Next action: {row['next_action']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def summarize_body(body: str) -> str:
    clean = " ".join(body.split())
    if not clean:
        return "No body provided."
    return clean[:117] + "..." if len(clean) > 120 else clean


def infer_next_action(body: str) -> str:
    lower = body.lower()
    if "review" in lower or "검토" in body:
        return "Review requested material."
    if "schedule" in lower or "일정" in body:
        return "Check schedule and confirm timing."
    if "send" in lower or "보내" in body:
        return "Prepare and send requested item."
    return "Read and decide whether follow-up is needed."
