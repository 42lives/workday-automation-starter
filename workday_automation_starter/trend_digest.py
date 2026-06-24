from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path


IMPORTANT_TERMS = {
    "openai",
    "codex",
    "automation",
    "security",
    "agent",
    "agents",
    "release",
    "regulation",
    "funding",
    "model",
    "workflow",
}


@dataclass
class TrendItem:
    date: str
    topic: str
    source: str
    title: str
    url: str
    summary: str


def parse_trend_items(path: Path) -> list[TrendItem]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            TrendItem(
                row.get("date", ""),
                row.get("topic", ""),
                row.get("source", ""),
                row.get("title", "Untitled"),
                row.get("url", ""),
                row.get("summary", ""),
            )
            for row in reader
        ]


def build_trend_digest(path: Path, topic: str | None, limit: int, output_format: str) -> str:
    items = parse_trend_items(path)
    if topic:
        lowered_topic = topic.lower()
        items = [item for item in items if lowered_topic in item.topic.lower()]

    rows = [
        {
            "date": item.date,
            "topic": item.topic,
            "source": item.source,
            "title": item.title,
            "url": item.url,
            "summary_lines": three_line_summary(item.summary),
            "importance": score_importance(item),
        }
        for item in items
    ]
    rows.sort(key=lambda row: (-int(row["importance"]), row["date"], row["title"]))
    rows = rows[: max(1, limit)]

    if output_format == "json":
        return json.dumps({"topic": topic or "all", "items": rows}, indent=2, ensure_ascii=False) + "\n"
    if output_format == "csv":
        return render_trend_csv(rows)
    return render_trend_markdown(topic or "all", rows)


def three_line_summary(summary: str) -> list[str]:
    clean_parts = [part.strip() for part in summary.replace("\n", " ").split(".") if part.strip()]
    if not clean_parts:
        return ["No summary provided.", "Review source manually.", "Decide whether to save this item."]
    lines = [part + "." for part in clean_parts[:3]]
    while len(lines) < 3:
        lines.append("No additional detail provided.")
    return lines


def score_importance(item: TrendItem) -> int:
    text = f"{item.topic} {item.title} {item.summary}".lower()
    score = 1
    for term in IMPORTANT_TERMS:
        if term in text:
            score += 1
    if item.url:
        score += 1
    return min(score, 10)


def render_trend_markdown(topic: str, rows: list[dict[str, object]]) -> str:
    lines = [f"# Trend Digest: {topic}", "", f"Items: {len(rows)}", ""]
    if not rows:
        lines.append("No trend items matched the request.")
        return "\n".join(lines) + "\n"

    for row in rows:
        summary_lines = row["summary_lines"]
        assert isinstance(summary_lines, list)
        lines.extend(
            [
                f"## {row['title']}",
                "",
                f"- Date: {row['date']}",
                f"- Topic: {row['topic']}",
                f"- Source: {row['source']}",
                f"- URL: {row['url']}",
                f"- Importance: {row['importance']}/10",
                "- Summary:",
            ]
        )
        for line in summary_lines:
            lines.append(f"  - {line}")
        lines.append("")

    lines.extend(
        [
            "## Notion Boundary",
            "",
            "This digest is local output. Review it before importing to Notion or publishing anywhere.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_trend_csv(rows: list[dict[str, object]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date", "topic", "source", "title", "url", "importance", "summary_1", "summary_2", "summary_3"],
    )
    writer.writeheader()
    for row in rows:
        summary_lines = row["summary_lines"]
        assert isinstance(summary_lines, list)
        writer.writerow(
            {
                "date": row["date"],
                "topic": row["topic"],
                "source": row["source"],
                "title": row["title"],
                "url": row["url"],
                "importance": row["importance"],
                "summary_1": summary_lines[0],
                "summary_2": summary_lines[1],
                "summary_3": summary_lines[2],
            }
        )
    return output.getvalue()
