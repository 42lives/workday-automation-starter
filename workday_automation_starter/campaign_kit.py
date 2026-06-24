from __future__ import annotations

import json
import re
from pathlib import Path


def build_campaign_package(topic: str, output_dir: Path, cards: int = 4) -> dict[str, object]:
    package_dir = output_dir.expanduser().resolve()
    package_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(topic)
    proposal = render_proposal(topic)
    slides = render_slides(topic)
    card_news = render_card_news(topic, cards)
    manifest = {
        "topic": topic,
        "package_dir": str(package_dir),
        "files": {
            "proposal": "proposal.md",
            "slides": "slides-outline.md",
            "card_news": "card-news.md",
            "manifest": "campaign-manifest.json",
        },
        "workflow": [
            "Review proposal draft.",
            "Review slide outline.",
            "Review card-news copy and image prompts.",
            "Export to Word, PPT, or image tools only after review.",
        ],
        "privacy_note": "This package is generated locally and uses no live web search or image service by default.",
        "slug": slug,
    }

    (package_dir / "proposal.md").write_text(proposal, encoding="utf-8")
    (package_dir / "slides-outline.md").write_text(slides, encoding="utf-8")
    (package_dir / "card-news.md").write_text(card_news, encoding="utf-8")
    (package_dir / "campaign-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def render_package_summary(manifest: dict[str, object]) -> str:
    files = manifest["files"]
    assert isinstance(files, dict)
    lines = [
        "# Campaign Package",
        "",
        f"Topic: {manifest['topic']}",
        f"Folder: `{manifest['package_dir']}`",
        "",
        "## Files",
        "",
    ]
    for label, filename in files.items():
        lines.append(f"- {label}: `{filename}`")
    lines.extend(["", "## Review Workflow", ""])
    workflow = manifest["workflow"]
    assert isinstance(workflow, list)
    for item in workflow:
        lines.append(f"- {item}")
    lines.extend(["", "## Privacy Note", "", str(manifest["privacy_note"])])
    return "\n".join(lines).rstrip() + "\n"


def render_proposal(topic: str) -> str:
    return f"""# Proposal Draft: {topic}

## Objective

Create a practical campaign package for `{topic}` that can be reviewed, edited, and exported into office documents or marketing assets.

## Target Audience

- Working professionals who need a fast planning draft.
- Teams preparing an internal proposal or lightweight marketing test.
- Non-professional builders who want a structured starting point.

## Core Message

{topic} should be explained through a clear problem, a practical benefit, and a low-risk next step.

## Proposed Package

- Proposal draft for Word or Markdown review.
- Presentation outline for PPT export.
- Card-news copy and image prompts for SNS review.

## Review Checklist

- Confirm facts and dates before external use.
- Replace sample claims with verified source material.
- Review brand, copyright, and privacy risks.
- Export only after a person approves the package.
"""


def render_slides(topic: str) -> str:
    slides = [
        ("Campaign Goal", f"Define why `{topic}` matters now and what decision the audience should make."),
        ("Audience and Problem", "Clarify who this helps and what repeated work, cost, or confusion it reduces."),
        ("Proposed Message", "Turn the topic into one clear promise with supporting proof points."),
        ("Execution Plan", "List document, presentation, and card-news assets to create first."),
        ("Review and Next Step", "Check facts, approve copy, then export to Word, PPT, or image tools."),
    ]
    lines = [f"# Presentation Outline: {topic}", ""]
    for index, (title, body) in enumerate(slides, start=1):
        lines.extend([f"## Slide {index}: {title}", "", f"- {body}", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_card_news(topic: str, cards: int) -> str:
    lines = [f"# Card News Draft: {topic}", ""]
    for index in range(1, max(1, cards) + 1):
        lines.extend(
            [
                f"## Card {index}",
                "",
                f"- Headline: {card_headline(topic, index)}",
                f"- Body: {card_body(topic, index)}",
                f"- Image prompt: {card_image_prompt(topic, index)}",
                "",
            ]
        )
    lines.append("Review all copy and image prompts before using a generation tool.")
    return "\n".join(lines).rstrip() + "\n"


def card_headline(topic: str, index: int) -> str:
    templates = [
        f"Why {topic} matters now",
        f"The practical problem behind {topic}",
        f"A safer workflow for {topic}",
        f"Next step: test {topic} with a small campaign",
    ]
    return templates[(index - 1) % len(templates)]


def card_body(topic: str, index: int) -> str:
    templates = [
        "Start with a clear trend, not a vague claim.",
        "Show the audience what changes in their daily work.",
        "Keep the first version reviewable before exporting assets.",
        "Package the proposal, slides, and visual prompts in one folder.",
    ]
    return templates[(index - 1) % len(templates)].replace("the proposal", f"the {topic} proposal")


def card_image_prompt(topic: str, index: int) -> str:
    return (
        f"Clean editorial card-news image for {topic}, card {index}, "
        "office workflow context, realistic documents and presentation materials, no logos, no private data"
    )


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9가-힣]+", "-", text.strip()).strip("-").lower()
    return slug or "campaign"
