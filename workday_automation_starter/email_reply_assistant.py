from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .email_digest import EmailItem, infer_next_action, parse_email_items, summarize_body


@dataclass
class ReplyPlanItem:
    sender: str
    subject: str
    received_at: str
    priority: str
    reason: str
    summary: str
    suggested_reply: str
    notion_status: str = "Pending review"


def build_email_reply_package(
    email_path: Path,
    output_dir: Path,
    important_senders: list[str] | None = None,
    status: str = "Pending review",
) -> dict[str, object]:
    package_dir = output_dir.expanduser()
    package_dir.mkdir(parents=True, exist_ok=True)

    items = parse_email_items(email_path)
    reply_items = build_reply_plan(items, important_senders or [], status)
    manifest = {
        "source": str(email_path.expanduser().resolve()),
        "package_dir": str(package_dir),
        "email_count": len(items),
        "reply_count": len(reply_items),
        "files": {
            "reply_drafts": "reply-drafts.md",
            "notion_archive": "notion-archive.csv",
            "approval_checklist": "approval-checklist.md",
            "manifest": "email-reply-manifest.json",
        },
        "privacy_note": "Generated from local sample email text. Review every draft before using Gmail or Notion connectors.",
    }

    (package_dir / "reply-drafts.md").write_text(render_reply_drafts(reply_items), encoding="utf-8")
    (package_dir / "notion-archive.csv").write_text(render_notion_archive_csv(reply_items), encoding="utf-8")
    (package_dir / "approval-checklist.md").write_text(render_approval_checklist(reply_items), encoding="utf-8")
    (package_dir / "email-reply-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_reply_plan(items: list[EmailItem], important_senders: list[str], status: str) -> list[ReplyPlanItem]:
    important = {sender.lower() for sender in important_senders}
    reply_items: list[ReplyPlanItem] = []
    for item in items:
        reason = classify_reply_reason(item, important)
        if not reason:
            continue
        reply_items.append(
            ReplyPlanItem(
                sender=item.sender,
                subject=item.subject,
                received_at=item.received_at,
                priority="high" if item.sender.lower() in important else "normal",
                reason=reason,
                summary=summarize_body(item.body),
                suggested_reply=draft_business_reply(item),
                notion_status=status,
            )
        )
    return reply_items


def classify_reply_reason(item: EmailItem, important_senders: set[str]) -> str:
    lower_body = item.body.lower()
    lower_subject = item.subject.lower()
    if item.sender.lower() in important_senders:
        return "important sender"
    if any(word in lower_body or word in lower_subject for word in ["review", "confirm", "send", "schedule", "reply"]):
        return "reply likely needed"
    if any(word in item.body for word in ["검토", "확인", "보내", "일정", "회신"]):
        return "reply likely needed"
    return ""


def draft_business_reply(item: EmailItem) -> str:
    action = infer_next_action(item.body)
    if "Review" in action:
        body = "I will review the material and send comments before the requested deadline."
    elif "schedule" in action.lower():
        body = "I will check the updated schedule and confirm the meeting time."
    elif "send" in action.lower():
        body = "I will prepare the requested item and send it after a final review."
    else:
        body = "I received your message and will follow up after reviewing the details."
    return f"Hi,\n\nThanks for the update. {body}\n\nBest,"


def render_reply_drafts(items: list[ReplyPlanItem]) -> str:
    lines = ["# Email Reply Drafts", ""]
    if not items:
        lines.extend(["No reply-worthy emails found.", ""])
    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"## Draft {index}: {item.subject}",
                "",
                f"- To review from: {item.sender}",
                f"- Received: {item.received_at or 'not provided'}",
                f"- Priority: {item.priority}",
                f"- Reason: {item.reason}",
                f"- Summary: {item.summary}",
                "",
                "```text",
                item.suggested_reply,
                "```",
                "",
            ]
        )
    lines.append("Do not send these drafts without human review.")
    return "\n".join(lines).rstrip() + "\n"


def render_notion_archive_csv(items: list[ReplyPlanItem]) -> str:
    output = io.StringIO()
    fieldnames = ["status", "priority", "sender", "subject", "received_at", "reason", "summary", "draft"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in items:
        row = asdict(item)
        writer.writerow(
            {
                "status": row["notion_status"],
                "priority": row["priority"],
                "sender": row["sender"],
                "subject": row["subject"],
                "received_at": row["received_at"],
                "reason": row["reason"],
                "summary": row["summary"],
                "draft": row["suggested_reply"],
            }
        )
    return output.getvalue()


def render_approval_checklist(items: list[ReplyPlanItem]) -> str:
    lines = [
        "# Email Approval Checklist",
        "",
        "Complete this checklist before creating Gmail drafts, sending replies, or importing rows into Notion.",
        "",
        f"- [ ] Review {len(items)} suggested reply draft(s).",
        "- [ ] Remove private, legal, financial, or account details that should not be stored in Notion.",
        "- [ ] Confirm recipient, tone, deadline, and promised action.",
        "- [ ] Create Gmail drafts only after review.",
        "- [ ] Send email only after a human clicks the final send button.",
        "- [ ] Import the CSV into Notion only after checking workspace permissions.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_email_reply_package_summary(manifest: dict[str, object]) -> str:
    files = manifest["files"]
    assert isinstance(files, dict)
    lines = [
        "# Email Reply Assistant Package",
        "",
        f"Emails reviewed: {manifest['email_count']}",
        f"Reply drafts: {manifest['reply_count']}",
        f"Folder: `{manifest['package_dir']}`",
        "",
        "## Files",
        "",
    ]
    for label, filename in files.items():
        lines.append(f"- {label}: `{filename}`")
    lines.extend(["", "## Privacy Note", "", str(manifest["privacy_note"])])
    return "\n".join(lines).rstrip() + "\n"
