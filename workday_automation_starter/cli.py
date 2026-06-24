from __future__ import annotations

import argparse
from pathlib import Path

from .doc_outline import build_doc_outline
from .email_digest import build_email_digest
from .file_plan import build_file_plan, render_file_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="workday-automation-starter",
        description="Local-first starter workflows for office automation.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    file_plan = subparsers.add_parser("file-plan", help="Create a dry-run file organization plan.")
    file_plan.add_argument("path", type=Path)
    file_plan.add_argument("--format", choices=["markdown", "json"], default="markdown")

    doc_outline = subparsers.add_parser("doc-outline", help="Create a presentation outline from a text document.")
    doc_outline.add_argument("path", type=Path)
    doc_outline.add_argument("--slides", type=int, default=6)

    email_digest = subparsers.add_parser("email-digest", help="Create a Notion-ready digest from sample email text.")
    email_digest.add_argument("path", type=Path)
    email_digest.add_argument("--format", choices=["markdown", "csv"], default="markdown")

    args = parser.parse_args(argv)

    if args.command == "file-plan":
        print(render_file_plan(build_file_plan(args.path), args.format), end="")
        return 0

    if args.command == "doc-outline":
        print(build_doc_outline(args.path, args.slides), end="")
        return 0

    if args.command == "email-digest":
        print(build_email_digest(args.path, args.format), end="")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
