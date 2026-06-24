from __future__ import annotations

import json
from pathlib import Path


CATEGORIES = {
    "documents": {".txt", ".md", ".rtf"},
    "presentations": {".ppt", ".pptx", ".key"},
    "spreadsheets": {".csv", ".tsv", ".xls", ".xlsx"},
    "images": {".png", ".jpg", ".jpeg", ".webp", ".gif"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml"},
    "archives": {".zip", ".tar", ".gz", ".7z"},
}

PRIVATE_NAMES = {".env", "credentials.json", "cookies.txt", "id_rsa", "id_dsa"}
PRIVATE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".db", ".sqlite"}


def build_file_plan(path: Path) -> dict[str, object]:
    root = path.expanduser().resolve()
    groups: dict[str, list[dict[str, str]]] = {
        "documents": [],
        "presentations": [],
        "spreadsheets": [],
        "images": [],
        "code": [],
        "archives": [],
        "possible_private": [],
        "other": [],
    }

    if not root.exists():
        return {"root": str(root), "error": "Path does not exist.", "groups": groups}

    for item in sorted(root.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(root).as_posix()
        category = classify_file(item)
        groups[category].append({"path": rel, "target": f"{category}/{item.name}"})

    summary = {name: len(files) for name, files in groups.items()}
    return {"root": str(root), "summary": summary, "groups": groups}


def classify_file(path: Path) -> str:
    lower_name = path.name.lower()
    suffix = path.suffix.lower()

    if lower_name in PRIVATE_NAMES or suffix in PRIVATE_SUFFIXES:
        return "possible_private"

    for category, suffixes in CATEGORIES.items():
        if suffix in suffixes:
            return category

    return "other"


def render_file_plan(plan: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(plan, indent=2, ensure_ascii=False) + "\n"

    if "error" in plan:
        return f"# File Organization Plan\n\nError: {plan['error']}\n"

    summary = plan["summary"]
    groups = plan["groups"]
    assert isinstance(summary, dict)
    assert isinstance(groups, dict)

    lines = ["# File Organization Plan", "", f"Root: `{plan['root']}`", "", "## Summary", ""]
    for category, count in summary.items():
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Dry-Run Moves", ""])

    for category, files in groups.items():
        if not files:
            continue
        lines.extend([f"### {category}", ""])
        for file_info in files:
            lines.append(f"- `{file_info['path']}` -> `{file_info['target']}`")
        lines.append("")

    lines.append("No files were moved. Review the plan before running any real file operation.")
    return "\n".join(lines).rstrip() + "\n"
