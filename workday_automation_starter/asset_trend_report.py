from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AssetTrendItem:
    date: str
    asset: str
    category: str
    source: str
    title: str
    metric: str
    value: str
    summary: str
    url: str


def parse_asset_trends(path: Path) -> list[AssetTrendItem]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            AssetTrendItem(
                row.get("date", ""),
                row.get("asset", ""),
                row.get("category", ""),
                row.get("source", ""),
                row.get("title", "Untitled"),
                row.get("metric", ""),
                row.get("value", ""),
                row.get("summary", ""),
                row.get("url", ""),
            )
            for row in reader
        ]


def build_asset_trend_package(
    items_path: Path,
    output_dir: Path,
    watchlist: list[str] | None = None,
    limit: int = 5,
) -> dict[str, object]:
    package_dir = output_dir.expanduser()
    package_dir.mkdir(parents=True, exist_ok=True)

    all_items = parse_asset_trends(items_path)
    selected_items = select_asset_items(all_items, watchlist or [], limit)
    manifest = {
        "source": str(items_path.expanduser().resolve()),
        "package_dir": str(package_dir),
        "item_count": len(all_items),
        "selected_count": len(selected_items),
        "watchlist": watchlist or [],
        "files": {
            "market_digest": "market-digest.md",
            "portfolio_journal": "portfolio-journal.csv",
            "weekly_report": "weekly-report.md",
            "connector_checklist": "connector-checklist.md",
            "manifest": "asset-trend-manifest.json",
        },
        "disclaimer": "For tracking and review only. This is not investment, tax, legal, or financial advice.",
    }

    (package_dir / "market-digest.md").write_text(render_market_digest(selected_items), encoding="utf-8")
    (package_dir / "portfolio-journal.csv").write_text(render_portfolio_journal_csv(selected_items), encoding="utf-8")
    (package_dir / "weekly-report.md").write_text(render_weekly_asset_report(selected_items), encoding="utf-8")
    (package_dir / "connector-checklist.md").write_text(render_connector_checklist(), encoding="utf-8")
    (package_dir / "asset-trend-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def select_asset_items(items: list[AssetTrendItem], watchlist: list[str], limit: int) -> list[AssetTrendItem]:
    normalized = {item.lower() for item in watchlist}
    selected = items
    if normalized:
        selected = [
            item
            for item in items
            if item.asset.lower() in normalized or any(term in item.title.lower() for term in normalized)
        ]
    ranked = sorted(selected, key=lambda item: (-score_asset_item(item), item.date, item.asset, item.title))
    return ranked[: max(1, limit)]


def score_asset_item(item: AssetTrendItem) -> int:
    text = f"{item.asset} {item.category} {item.title} {item.summary}".lower()
    score = 1
    for term in ["rate", "inflation", "earnings", "guidance", "policy", "housing", "risk", "dividend", "fed"]:
        if term in text:
            score += 1
    if item.metric and item.value:
        score += 2
    if item.url:
        score += 1
    return min(score, 10)


def render_market_digest(items: list[AssetTrendItem]) -> str:
    lines = ["# Market Digest", "", f"Items: {len(items)}", ""]
    if not items:
        lines.extend(["No asset trend items matched the request.", ""])
    for item in items:
        lines.extend(
            [
                f"## {item.asset}: {item.title}",
                "",
                f"- Date: {item.date}",
                f"- Category: {item.category}",
                f"- Source: {item.source}",
                f"- Metric: {item.metric or 'not provided'}",
                f"- Value: {item.value or 'not provided'}",
                f"- Importance: {score_asset_item(item)}/10",
                f"- URL: {item.url}",
                f"- Summary: {item.summary or 'Review source manually.'}",
                "",
            ]
        )
    lines.extend(["## Review Boundary", "", "This digest is for personal tracking only. It is not investment advice."])
    return "\n".join(lines).rstrip() + "\n"


def render_portfolio_journal_csv(items: list[AssetTrendItem]) -> str:
    output = io.StringIO()
    fieldnames = [
        "date",
        "asset",
        "category",
        "source",
        "metric",
        "value",
        "importance",
        "summary",
        "action_status",
        "notes",
        "url",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in items:
        writer.writerow(
            {
                "date": item.date,
                "asset": item.asset,
                "category": item.category,
                "source": item.source,
                "metric": item.metric,
                "value": item.value,
                "importance": score_asset_item(item),
                "summary": item.summary,
                "action_status": "Review only",
                "notes": "No trade recommendation. Add personal notes after review.",
                "url": item.url,
            }
        )
    return output.getvalue()


def render_weekly_asset_report(items: list[AssetTrendItem]) -> str:
    categories = sorted({item.category for item in items if item.category})
    assets = sorted({item.asset for item in items if item.asset})
    lines = [
        "# Weekly Asset Trend Report",
        "",
        f"Tracked items: {len(items)}",
        f"Assets: {', '.join(assets) if assets else 'none'}",
        f"Categories: {', '.join(categories) if categories else 'none'}",
        "",
        "## Highlights",
        "",
    ]
    for item in items[:5]:
        lines.append(f"- {item.asset}: {item.title} ({item.metric or 'metric'} {item.value or 'n/a'})")
    lines.extend(
        [
            "",
            "## Spreadsheet Fields",
            "",
            "- date, asset, category, source, metric, value, importance, summary, action_status, notes, url",
            "",
            "## Review Notes",
            "",
            "- Verify figures against original sources.",
            "- Separate personal journal notes from public examples.",
            "- Do not treat this generated report as investment advice.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_connector_checklist() -> str:
    lines = [
        "# Asset Trend Connector Checklist",
        "",
        "Use this before connecting Gmail, Google Sheets, web search, or document export.",
        "",
        "- [ ] Use sanitized exports before connecting real accounts.",
        "- [ ] Preview every row before writing to Google Sheets.",
        "- [ ] Keep brokerage account numbers, balances, and tax data out of public repos.",
        "- [ ] Verify live prices and economic figures against trusted sources.",
        "- [ ] Export Word or document reports only after human review.",
        "- [ ] Keep all outputs as tracking notes, not investment recommendations.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_asset_trend_package_summary(manifest: dict[str, object]) -> str:
    files = manifest["files"]
    assert isinstance(files, dict)
    lines = [
        "# Asset Trend Report Package",
        "",
        f"Items reviewed: {manifest['item_count']}",
        f"Selected items: {manifest['selected_count']}",
        f"Folder: `{manifest['package_dir']}`",
        "",
        "## Files",
        "",
    ]
    for label, filename in files.items():
        lines.append(f"- {label}: `{filename}`")
    lines.extend(["", "## Disclaimer", "", str(manifest["disclaimer"])])
    return "\n".join(lines).rstrip() + "\n"
