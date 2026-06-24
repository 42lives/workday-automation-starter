from __future__ import annotations

import fnmatch
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .file_plan import classify_file


SENSITIVE_KEYWORDS = {
    "password",
    "credential",
    "credentials",
    "secret",
    "private",
    "contract",
    "passport",
    "resident",
    "bank",
    "계약",
    "주민",
    "여권",
    "통장",
    "비밀번호",
}


@dataclass
class SmartCleanOptions:
    include: list[str]
    exclude: list[str]
    destination: Path | None = None
    apply: bool = False
    manifest: Path | None = None


def build_smart_clean_plan(root_path: Path, options: SmartCleanOptions) -> dict[str, object]:
    root = root_path.expanduser().resolve()
    destination = (options.destination or root / "Organized").expanduser().resolve()
    actions: list[dict[str, str]] = []
    protected: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    if not root.exists():
        return {
            "root": str(root),
            "destination": str(destination),
            "error": "Path does not exist.",
            "actions": actions,
            "protected": protected,
            "skipped": skipped,
            "applied": False,
        }

    for item in sorted(root.rglob("*")):
        if not item.is_file():
            continue
        if destination in item.resolve().parents:
            continue

        rel = item.relative_to(root).as_posix()
        if not matches_rules(rel, options.include, options.exclude):
            skipped.append({"path": rel, "reason": "Filtered by include or exclude rules."})
            continue

        category = classify_file(item)
        if category == "possible_private" or has_sensitive_keyword(item):
            protected.append({"path": rel, "reason": "Possible private or sensitive file."})
            continue

        target = destination / category / item.name
        actions.append({"source": str(item), "relative_source": rel, "target": str(target), "category": category})

    return {
        "root": str(root),
        "destination": str(destination),
        "summary": {
            "planned_moves": len(actions),
            "protected": len(protected),
            "skipped": len(skipped),
        },
        "actions": actions,
        "protected": protected,
        "skipped": skipped,
        "applied": False,
    }


def apply_smart_clean_plan(plan: dict[str, object]) -> dict[str, object]:
    actions = plan["actions"]
    assert isinstance(actions, list)
    applied_actions: list[dict[str, str]] = []

    for action in actions:
        source = Path(action["source"])
        target = Path(action["target"])
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        final_target = unique_target(target)
        shutil.move(str(source), str(final_target))
        applied_actions.append(
            {
                "source": str(source),
                "target": str(final_target),
                "relative_source": action["relative_source"],
                "category": action["category"],
            }
        )

    plan["actions"] = applied_actions
    plan["applied"] = True
    return plan


def write_manifest(plan: dict[str, object], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_smart_clean_plan(plan: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(plan, indent=2, ensure_ascii=False) + "\n"

    if "error" in plan:
        return f"# Smart Clean Plan\n\nError: {plan['error']}\n"

    summary = plan["summary"]
    actions = plan["actions"]
    protected = plan["protected"]
    skipped = plan["skipped"]
    assert isinstance(summary, dict)
    assert isinstance(actions, list)
    assert isinstance(protected, list)
    assert isinstance(skipped, list)

    lines = [
        "# Smart Clean Plan",
        "",
        f"Root: `{plan['root']}`",
        f"Destination: `{plan['destination']}`",
        f"Applied: `{plan['applied']}`",
        "",
        "## Summary",
        "",
        f"- Planned moves: {summary['planned_moves']}",
        f"- Protected files: {summary['protected']}",
        f"- Skipped files: {summary['skipped']}",
        "",
        "## Planned Moves",
        "",
    ]

    if not actions:
        lines.append("No files will be moved.")
    for action in actions:
        lines.append(f"- `{action['relative_source']}` -> `{action['target']}`")

    lines.extend(["", "## Protected", ""])
    if not protected:
        lines.append("No protected files detected.")
    for item in protected:
        lines.append(f"- `{item['path']}`: {item['reason']}")

    lines.extend(["", "## Skipped", ""])
    if not skipped:
        lines.append("No files skipped by filters.")
    for item in skipped[:25]:
        lines.append(f"- `{item['path']}`: {item['reason']}")
    if len(skipped) > 25:
        lines.append(f"- ... {len(skipped) - 25} more skipped files")

    if not plan["applied"]:
        lines.extend(["", "No files were moved. Re-run with `--apply` after reviewing this plan."])

    return "\n".join(lines).rstrip() + "\n"


def matches_rules(path: str, include_patterns: list[str], exclude_patterns: list[str]) -> bool:
    if include_patterns and not any(fnmatch.fnmatch(path, pattern) for pattern in include_patterns):
        return False
    if exclude_patterns and any(fnmatch.fnmatch(path, pattern) for pattern in exclude_patterns):
        return False
    return True


def has_sensitive_keyword(path: Path) -> bool:
    lower_name = path.name.lower()
    return any(keyword in lower_name for keyword in SENSITIVE_KEYWORDS)


def unique_target(target: Path) -> Path:
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
