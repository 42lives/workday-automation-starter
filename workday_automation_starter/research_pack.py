from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


SOURCE_SUFFIXES = {".txt", ".md", ".pdf"}


@dataclass
class ResearchSource:
    path: str
    title: str
    kind: str
    summary: str
    key_points: list[str]


def build_research_package(topic: str, source_dir: Path, output_dir: Path, images: int = 3) -> dict[str, object]:
    package_dir = output_dir.expanduser()
    package_dir.mkdir(parents=True, exist_ok=True)
    sources = scan_research_sources(source_dir)

    summary = render_literature_summary(topic, sources)
    presentation = render_research_presentation(topic, sources)
    image_prompts = render_research_image_prompts(topic, images)
    manifest = {
        "topic": topic,
        "source_dir": str(source_dir.expanduser().resolve()),
        "package_dir": str(package_dir),
        "source_count": len(sources),
        "files": {
            "summary": "literature-summary.md",
            "presentation": "presentation-guide.md",
            "image_prompts": "image-prompts.md",
            "manifest": "research-manifest.json",
        },
        "privacy_note": "This package is generated from local notes/placeholders. Review copyright and citation rules before sharing.",
    }

    (package_dir / "literature-summary.md").write_text(summary, encoding="utf-8")
    (package_dir / "presentation-guide.md").write_text(presentation, encoding="utf-8")
    (package_dir / "image-prompts.md").write_text(image_prompts, encoding="utf-8")
    (package_dir / "research-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def scan_research_sources(source_dir: Path) -> list[ResearchSource]:
    root = source_dir.expanduser().resolve()
    if not root.exists():
        return []

    sources: list[ResearchSource] = []
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = file_path.relative_to(root).as_posix()
        if file_path.suffix.lower() == ".pdf":
            sources.append(pdf_placeholder_source(rel))
        else:
            sources.append(text_source(file_path, rel))
    return sources


def text_source(file_path: Path, rel: str) -> ResearchSource:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    title = first_title(text, file_path.stem)
    points = extract_key_points(text)
    return ResearchSource(rel, title, file_path.suffix.lower().lstrip("."), summarize_text(text), points)


def pdf_placeholder_source(rel: str) -> ResearchSource:
    title = Path(rel).stem.replace("-", " ").replace("_", " ").title()
    return ResearchSource(
        rel,
        title,
        "pdf-placeholder",
        "PDF file detected. Add OCR or text extraction before generating a factual summary.",
        ["Review PDF manually or provide extracted text.", "Do not commit copyrighted paper content."],
    )


def first_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean[:90]
    return fallback.replace("-", " ").replace("_", " ").title()


def extract_key_points(text: str) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        clean = line.strip().lstrip("-*").strip()
        if len(clean) >= 20:
            bullets.append(clean[:140])
        if len(bullets) == 3:
            break
    if bullets:
        return bullets
    sentences = split_sentences(text)
    return [sentence[:140] for sentence in sentences[:3]] or ["Review source manually."]


def summarize_text(text: str) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return "No summary available."
    return " ".join(sentences[:2])[:260]


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.replace("#", " ")).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if len(part.strip()) > 12]


def render_literature_summary(topic: str, sources: list[ResearchSource]) -> str:
    lines = [f"# Literature Summary: {topic}", "", f"Sources reviewed: {len(sources)}", ""]
    if not sources:
        lines.append("No source files found.")
    for source in sources:
        lines.extend(
            [
                f"## {source.title}",
                "",
                f"- File: `{source.path}`",
                f"- Type: {source.kind}",
                f"- Summary: {source.summary}",
                "- Key points:",
            ]
        )
        for point in source.key_points:
            lines.append(f"  - {point}")
        lines.append("")
    lines.extend(["## Review Notes", "", "- Add citations before sharing.", "- Verify claims against original sources."])
    return "\n".join(lines).rstrip() + "\n"


def render_research_presentation(topic: str, sources: list[ResearchSource]) -> str:
    lines = [f"# Presentation Guide: {topic}", ""]
    slides = [
        ("Research Question", f"What should the audience understand about {topic}?"),
        ("Source Overview", f"Summarize {len(sources)} source files and their relevance."),
        ("Key Findings", "Group the strongest repeated points from the literature summary."),
        ("Practical Implications", "Explain what changes for work, study, or decision-making."),
        ("Limitations and Next Steps", "Call out missing evidence, citation needs, and follow-up research."),
    ]
    for index, (title, body) in enumerate(slides, start=1):
        lines.extend([f"## Slide {index}: {title}", "", f"- {body}", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_research_image_prompts(topic: str, image_count: int) -> str:
    lines = [f"# Image Prompts: {topic}", ""]
    for index in range(1, max(1, image_count) + 1):
        lines.extend(
            [
                f"## Image {index}",
                "",
                (
                    f"Prompt: Editorial research presentation image about {topic}, "
                    f"visual {index}, academic materials on a desk, charts and notes, "
                    "no logos, no copyrighted figures, no private data"
                ),
                "",
            ]
        )
    lines.append("Review prompts before using an image generation tool.")
    return "\n".join(lines).rstrip() + "\n"


def render_research_package_summary(manifest: dict[str, object]) -> str:
    files = manifest["files"]
    assert isinstance(files, dict)
    lines = [
        "# Research Package",
        "",
        f"Topic: {manifest['topic']}",
        f"Sources: {manifest['source_count']}",
        f"Folder: `{manifest['package_dir']}`",
        "",
        "## Files",
        "",
    ]
    for label, filename in files.items():
        lines.append(f"- {label}: `{filename}`")
    lines.extend(["", "## Privacy Note", "", str(manifest["privacy_note"])])
    return "\n".join(lines).rstrip() + "\n"
