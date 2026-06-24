from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path


RECEIPT_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".pdf", ".heic", ".txt"}
CATEGORY_ALIASES = {
    "meal": "meals",
    "food": "meals",
    "식대": "meals",
    "교통": "transport",
    "taxi": "transport",
    "transport": "transport",
    "office": "office",
    "supplies": "office",
    "비품": "office",
    "meeting": "meeting",
    "회의": "meeting",
}


@dataclass
class ReceiptItem:
    path: str
    date: str
    month: str
    category: str
    vendor: str
    amount: int
    purpose: str
    target_folder: str


def build_receipt_report(path: Path, output_format: str) -> str:
    items = scan_receipts(path)
    report = {
        "root": str(path.expanduser().resolve()),
        "summary": {
            "receipt_count": len(items),
            "total_amount": sum(item.amount for item in items),
            "categories": category_totals(items),
        },
        "items": [item.__dict__ for item in items],
        "privacy_note": "Generated from local filenames/sample metadata. Review before submitting expense documents.",
    }

    if output_format == "json":
        return json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if output_format == "csv":
        return render_receipt_csv(items)
    return render_receipt_markdown(report)


def scan_receipts(path: Path) -> list[ReceiptItem]:
    root = path.expanduser().resolve()
    if not root.exists():
        return []

    items: list[ReceiptItem] = []
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in RECEIPT_SUFFIXES:
            continue
        rel = file_path.relative_to(root).as_posix()
        item = parse_receipt_filename(file_path.name, rel)
        items.append(item)
    return items


def parse_receipt_filename(filename: str, rel_path: str) -> ReceiptItem:
    stem = Path(filename).stem
    parts = re.split(r"[-_\s]+", stem)
    date = extract_date(stem)
    month = date[:7] if date != "unknown-date" else "unknown-month"
    category = infer_category(parts)
    amount = extract_amount(parts)
    vendor = infer_vendor(parts)
    purpose = infer_purpose(parts, category)
    target_folder = f"{month}_{category}"
    return ReceiptItem(rel_path, date, month, category, vendor, amount, purpose, target_folder)


def extract_date(text: str) -> str:
    match = re.search(r"(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?([0-2]\d|3[01])", text)
    if not match:
        return "unknown-date"
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"


def infer_category(parts: list[str]) -> str:
    lowered = [part.lower() for part in parts]
    for part in lowered:
        if part in CATEGORY_ALIASES:
            return CATEGORY_ALIASES[part]
    return "uncategorized"


def extract_amount(parts: list[str]) -> int:
    for part in reversed(parts):
        digits = re.sub(r"[^0-9]", "", part)
        if digits and len(digits) >= 3:
            return int(digits)
    return 0


def infer_vendor(parts: list[str]) -> str:
    ignored = {"receipt", "영수증", "expense", "photo", "image"}
    for part in parts:
        clean = part.strip()
        if not clean or clean.lower() in ignored:
            continue
        if any(char.isdigit() for char in clean) and extract_date(clean) != "unknown-date":
            continue
        if clean.lower() in CATEGORY_ALIASES:
            continue
        if re.fullmatch(r"[0-9,]+", clean):
            continue
        return clean
    return "unknown-vendor"


def infer_purpose(parts: list[str], category: str) -> str:
    if category == "meals":
        return "Meal or team food expense"
    if category == "transport":
        return "Transportation expense"
    if category == "office":
        return "Office supply expense"
    if category == "meeting":
        return "Meeting support expense"
    return "Review required"


def category_totals(items: list[ReceiptItem]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for item in items:
        totals[item.category] = totals.get(item.category, 0) + item.amount
    return totals


def render_receipt_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    items = report["items"]
    assert isinstance(summary, dict)
    assert isinstance(items, list)
    lines = [
        "# Expense Report Draft",
        "",
        f"Root: `{report['root']}`",
        "",
        "## Summary",
        "",
        f"- Receipts: {summary['receipt_count']}",
        f"- Total amount: {summary['total_amount']}",
        "",
        "## Category Totals",
        "",
    ]
    categories = summary["categories"]
    assert isinstance(categories, dict)
    if not categories:
        lines.append("- No receipt items found.")
    for category, total in categories.items():
        lines.append(f"- {category}: {total}")

    lines.extend(["", "## Organization Plan", ""])
    for item in items:
        lines.append(f"- `{item['path']}` -> `{item['target_folder']}/`")

    lines.extend(["", "## Expense Items", ""])
    for item in items:
        lines.extend(
            [
                f"### {item['date']} - {item['vendor']}",
                "",
                f"- Category: {item['category']}",
                f"- Amount: {item['amount']}",
                f"- Purpose: {item['purpose']}",
                f"- Source file: `{item['path']}`",
                "",
            ]
        )

    lines.extend(["## Privacy Note", "", str(report["privacy_note"])])
    return "\n".join(lines).rstrip() + "\n"


def render_receipt_csv(items: list[ReceiptItem]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date", "month", "category", "vendor", "amount", "purpose", "path", "target_folder"],
    )
    writer.writeheader()
    for item in items:
        writer.writerow(item.__dict__)
    return output.getvalue()
