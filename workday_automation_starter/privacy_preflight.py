from __future__ import annotations

import json
import re
from pathlib import Path

from .file_plan import classify_file


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_PATTERN = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,}|AKIA[A-Z0-9]{16})\b")
PRIVATE_WORDS = {"password", "passwd", "secret", "token", "credential", "private", "apikey", "api_key"}
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".yml", ".yaml", ".py", ".js", ".ts", ".html", ".css"}


def build_privacy_preflight(path: Path) -> dict[str, object]:
    root = path.expanduser().resolve()
    findings: list[dict[str, str]] = []
    summary = {"files": 0, "high": 0, "medium": 0, "low": 0}

    if not root.exists():
        return {"root": str(root), "error": "Path does not exist.", "summary": summary, "findings": findings}

    for item in sorted(root.rglob("*")):
        if not item.is_file():
            continue
        summary["files"] += 1
        rel = item.relative_to(root).as_posix()
        category = classify_file(item)
        if category == "possible_private":
            add_finding(findings, summary, "high", rel, "Possible private file name or extension.")
        if any(word in item.name.lower() for word in PRIVATE_WORDS):
            add_finding(findings, summary, "medium", rel, "File name suggests private or credential-like content.")
        if item.suffix.lower() in TEXT_SUFFIXES:
            scan_text_file(item, rel, findings, summary)

    return {"root": str(root), "summary": summary, "findings": findings}


def scan_text_file(path: Path, rel: str, findings: list[dict[str, str]], summary: dict[str, int]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if SECRET_PATTERN.search(text):
        add_finding(findings, summary, "high", rel, "Secret-like token found in text.")
    if EMAIL_PATTERN.search(text):
        add_finding(findings, summary, "medium", rel, "Email-like personal data found in text.")
    lowered = text.lower()
    if any(word in lowered for word in PRIVATE_WORDS):
        add_finding(findings, summary, "low", rel, "Private or credential-like wording found in text.")


def add_finding(
    findings: list[dict[str, str]],
    summary: dict[str, int],
    severity: str,
    path: str,
    message: str,
) -> None:
    summary[severity] += 1
    findings.append({"severity": severity, "path": path, "message": message})


def render_privacy_preflight(report: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if "error" in report:
        return f"# Privacy Preflight\n\nError: {report['error']}\n"

    summary = report["summary"]
    findings = report["findings"]
    assert isinstance(summary, dict)
    assert isinstance(findings, list)
    lines = [
        "# Privacy Preflight",
        "",
        f"Root: `{report['root']}`",
        "",
        "## Summary",
        "",
        f"- Files scanned: {summary['files']}",
        f"- High: {summary['high']}",
        f"- Medium: {summary['medium']}",
        f"- Low: {summary['low']}",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No privacy preflight findings.")
    for finding in findings:
        lines.append(f"- [{finding['severity']}] `{finding['path']}`: {finding['message']}")
    lines.extend(
        [
            "",
            "## Review Boundary",
            "",
            "This is a local preflight report. Review findings manually before processing real folders or publishing files.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
