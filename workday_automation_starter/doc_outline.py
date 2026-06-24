from __future__ import annotations

import re
from pathlib import Path


def build_doc_outline(path: Path, slide_count: int) -> str:
    text = path.read_text(encoding="utf-8")
    title = first_heading_or_title(text, path)
    sentences = split_sentences(text)
    slides = build_slides(sentences, slide_count)

    lines = [f"# Presentation Outline: {title}", ""]
    for index, bullets in enumerate(slides, start=1):
        heading = bullets[0] if bullets else f"Slide {index}"
        lines.extend([f"## Slide {index}: {shorten(heading, 64)}", ""])
        for bullet in bullets[:3]:
            lines.append(f"- {shorten(bullet, 110)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def first_heading_or_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return shorten(clean, 72)
    return path.stem.replace("-", " ").replace("_", " ").title()


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.replace("#", " ")).strip()
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip() for part in parts if len(part.strip()) > 10]


def build_slides(sentences: list[str], slide_count: int) -> list[list[str]]:
    if slide_count < 1:
        slide_count = 1
    if not sentences:
        return [[f"Slide {index}"] for index in range(1, slide_count + 1)]

    slides: list[list[str]] = []
    chunk_size = max(1, (len(sentences) + slide_count - 1) // slide_count)
    for index in range(slide_count):
        chunk = sentences[index * chunk_size : (index + 1) * chunk_size]
        if chunk:
            slides.append(chunk)
    return slides


def shorten(text: str, max_length: int) -> str:
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."
