from __future__ import annotations

import argparse
from pathlib import Path

from .asset_trend_report import build_asset_trend_package, render_asset_trend_package_summary
from .campaign_kit import build_campaign_package, render_package_summary
from .doc_outline import build_doc_outline
from .email_digest import build_email_digest
from .email_reply_assistant import build_email_reply_package, render_email_reply_package_summary
from .file_plan import build_file_plan, render_file_plan
from .report_draft import build_report_draft
from .receipt_report import build_receipt_report
from .research_pack import build_research_package, render_research_package_summary
from .smart_clean import (
    SmartCleanOptions,
    apply_smart_clean_plan,
    build_smart_clean_plan,
    render_smart_clean_plan,
    write_manifest,
)
from .trend_digest import build_trend_digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workday-automation-starter",
        description="Local-first starter workflows for office automation.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    file_plan = subparsers.add_parser("file-plan", help="Create a dry-run file organization plan.")
    file_plan.add_argument("path", type=Path)
    file_plan.add_argument("--format", choices=["markdown", "json"], default="markdown")

    smart_clean = subparsers.add_parser("smart-clean", help="Plan or apply a safe file cleanup workflow.")
    smart_clean.add_argument("path", type=Path)
    smart_clean.add_argument("--include", action="append", default=[], help="Only include paths matching this glob.")
    smart_clean.add_argument("--exclude", action="append", default=[], help="Exclude paths matching this glob.")
    smart_clean.add_argument("--destination", type=Path, help="Folder for organized files. Defaults to PATH/Organized.")
    smart_clean.add_argument("--apply", action="store_true", help="Move files after generating the reviewed plan.")
    smart_clean.add_argument("--manifest", type=Path, help="Write the cleanup plan or applied move manifest as JSON.")
    smart_clean.add_argument("--format", choices=["markdown", "json"], default="markdown")

    doc_outline = subparsers.add_parser("doc-outline", help="Create a presentation outline from a text document.")
    doc_outline.add_argument("path", type=Path)
    doc_outline.add_argument("--slides", type=int, default=6)

    email_digest = subparsers.add_parser("email-digest", help="Create a Notion-ready digest from sample email text.")
    email_digest.add_argument("path", type=Path)
    email_digest.add_argument("--format", choices=["markdown", "csv"], default="markdown")

    email_reply = subparsers.add_parser("email-reply-assistant", help="Create reply drafts and a Notion archive package.")
    email_reply.add_argument("--emails", type=Path, required=True, help="Sample Gmail-like text export.")
    email_reply.add_argument("--output-dir", type=Path, required=True, help="Folder where package files will be written.")
    email_reply.add_argument("--important-sender", action="append", default=[], help="Sender that should always be reviewed.")
    email_reply.add_argument("--status", default="Pending review", help="Status value for the Notion-ready CSV.")
    email_reply.add_argument("--since-hours", type=int, help="Only include emails received within this many hours.")
    email_reply.add_argument("--now", help="Reference time for --since-hours, for example '2026-06-27 10:00'.")

    daily_report = subparsers.add_parser("daily-report", help="Create a daily or weekly report draft from sample inputs.")
    daily_report.add_argument("--emails", type=Path, required=True, help="Sample Gmail-like text export.")
    daily_report.add_argument("--calendar", type=Path, required=True, help="Sample calendar CSV export.")
    daily_report.add_argument("--period", choices=["daily", "weekly"], default="weekly")
    daily_report.add_argument("--format", choices=["markdown", "json"], default="markdown")

    trend_digest = subparsers.add_parser("trend-digest", help="Create a trend digest from sanitized news items.")
    trend_digest.add_argument("--items", type=Path, required=True, help="CSV file with sanitized trend/news items.")
    trend_digest.add_argument("--topic", help="Optional topic filter such as AI, IT, or finance.")
    trend_digest.add_argument("--limit", type=int, default=10)
    trend_digest.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown")

    asset_report = subparsers.add_parser("asset-trend-report", help="Create a personal asset trend report package.")
    asset_report.add_argument("--items", type=Path, required=True, help="CSV file with sanitized asset trend items.")
    asset_report.add_argument("--output-dir", type=Path, required=True, help="Folder where package files will be written.")
    asset_report.add_argument("--watchlist", action="append", default=[], help="Asset ticker, keyword, or topic to include.")
    asset_report.add_argument("--limit", type=int, default=5)

    campaign_kit = subparsers.add_parser("campaign-kit", help="Create a local campaign package from one topic.")
    campaign_kit.add_argument("--topic", required=True, help="Campaign topic or planning keyword.")
    campaign_kit.add_argument("--output-dir", type=Path, required=True, help="Folder where package files will be written.")
    campaign_kit.add_argument("--cards", type=int, default=4, help="Number of card-news drafts to create.")

    receipt_report = subparsers.add_parser("receipt-report", help="Create an expense report draft from receipt files.")
    receipt_report.add_argument("path", type=Path, help="Receipt staging folder.")
    receipt_report.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown")

    research_pack = subparsers.add_parser("research-pack", help="Create a research summary and presentation package.")
    research_pack.add_argument("--topic", required=True)
    research_pack.add_argument("--sources", type=Path, required=True, help="Folder containing PDF placeholders or extracted text notes.")
    research_pack.add_argument("--output-dir", type=Path, required=True)
    research_pack.add_argument("--images", type=int, default=3)

    args = parser.parse_args(argv)

    if args.command == "file-plan":
        print(render_file_plan(build_file_plan(args.path), args.format), end="")
        return 0

    if args.command == "smart-clean":
        options = SmartCleanOptions(
            include=args.include,
            exclude=args.exclude,
            destination=args.destination,
            apply=args.apply,
            manifest=args.manifest,
        )
        plan = build_smart_clean_plan(args.path, options)
        if args.apply and "error" not in plan:
            plan = apply_smart_clean_plan(plan)
        if args.manifest:
            write_manifest(plan, args.manifest)
        print(render_smart_clean_plan(plan, args.format), end="")
        return 0 if "error" not in plan else 1

    if args.command == "doc-outline":
        print(build_doc_outline(args.path, args.slides), end="")
        return 0

    if args.command == "email-digest":
        print(build_email_digest(args.path, args.format), end="")
        return 0

    if args.command == "email-reply-assistant":
        manifest = build_email_reply_package(
            args.emails,
            args.output_dir,
            args.important_sender,
            args.status,
            args.since_hours,
            args.now,
        )
        print(render_email_reply_package_summary(manifest), end="")
        return 0

    if args.command == "daily-report":
        print(build_report_draft(args.emails, args.calendar, args.period, args.format), end="")
        return 0

    if args.command == "trend-digest":
        print(build_trend_digest(args.items, args.topic, args.limit, args.format), end="")
        return 0

    if args.command == "asset-trend-report":
        manifest = build_asset_trend_package(args.items, args.output_dir, args.watchlist, args.limit)
        print(render_asset_trend_package_summary(manifest), end="")
        return 0

    if args.command == "campaign-kit":
        manifest = build_campaign_package(args.topic, args.output_dir, args.cards)
        print(render_package_summary(manifest), end="")
        return 0

    if args.command == "receipt-report":
        print(build_receipt_report(args.path, args.format), end="")
        return 0

    if args.command == "research-pack":
        manifest = build_research_package(args.topic, args.sources, args.output_dir, args.images)
        print(render_research_package_summary(manifest), end="")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
