#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "system-design-mastery"
README_PATH = SOURCE_ROOT / "README.md"

PART_HEADINGS = {
    "01-foundations": "Part 1: Foundations of System Design",
    "02-building-blocks": "Part 2: Core System Building Blocks",
    "03-distributed-systems": "Part 3: Distributed Systems Concepts",
    "04-architectural-patterns": "Part 4: Architectural Patterns",
    "05-real-world-systems": "Part 5: Real-World System Design Examples",
    "06-advanced-architecture": "Part 6: Advanced Architecture",
}

LEARNING_PATH = {
    "01-foundations": "Learn what system design is, how to frame requirements, and how to estimate scale.",
    "02-building-blocks": "Build fluency with networking, databases, caching, load balancing, queues, and storage.",
    "03-distributed-systems": "Understand the trade-offs that appear when systems scale across nodes, regions, and failures.",
    "04-architectural-patterns": "Learn the patterns used to organize real systems and teams.",
    "05-real-world-systems": "Move through domain-driven real-world system design examples, from commerce and fintech to infrastructure, healthcare, gaming, adtech, and travel.",
    "06-advanced-architecture": "Develop the production and architect-level mindset needed to operate systems responsibly.",
}


def chapter_files() -> list[Path]:
    files = [path for path in SOURCE_ROOT.glob("*/*.md") if path.is_file()]
    return sorted(files, key=lambda path: int(path.stem.split("-", 1)[0]))


def extract_title(markdown_text: str) -> str:
    match = re.search(r"^#\s*(?:\d+\.\s*)?(.+)$", markdown_text, flags=re.M)
    if not match:
        raise ValueError("Chapter title not found.")
    return match.group(1).strip()


def replace_first_heading(markdown_text: str, number: int, title: str) -> str:
    return re.sub(r"^#\s*(?:\d+\.\s*)?.+$", f"# {number}. {title}", markdown_text, count=1, flags=re.M)


def replace_position_line(markdown_text: str, number: int, total: int) -> str:
    pattern = r"\*\*Position:\*\* Chapter \d+ of \d+"
    replacement = f"**Position:** Chapter {number} of {total}"
    if re.search(pattern, markdown_text):
        return re.sub(pattern, replacement, markdown_text, count=1)
    return markdown_text


def render_navigation(path: Path, previous: tuple[Path, str] | None, next_item: tuple[Path, str] | None) -> str:
    lines = ["## Navigation"]
    if previous is not None:
        prev_path, prev_title = previous
        relative = os.path.relpath(prev_path, start=path.parent).replace(os.sep, "/")
        lines.append(f"- Previous: [{prev_title}]({relative})")
    if next_item is not None:
        next_path, next_title = next_item
        relative = os.path.relpath(next_path, start=path.parent).replace(os.sep, "/")
        lines.append(f"- Next: [{next_title}]({relative})")
    return "\n".join(lines)


def update_chapters() -> list[tuple[int, str, Path]]:
    chapters: list[tuple[int, str, Path]] = []
    total = len(chapter_files())

    for path in chapter_files():
        text = path.read_text(encoding="utf-8")
        number = int(path.stem.split("-", 1)[0])
        title = re.sub(r"^\d+\.\s*", "", extract_title(text))
        text = replace_first_heading(text, number, title)
        text = replace_position_line(text, number, total)
        path.write_text(text, encoding="utf-8")
        chapters.append((number, title, path))

    for index, (_, title, path) in enumerate(chapters):
        text = path.read_text(encoding="utf-8").rstrip()
        previous = None if index == 0 else (chapters[index - 1][2], chapters[index - 1][1])
        next_item = None if index == len(chapters) - 1 else (chapters[index + 1][2], chapters[index + 1][1])
        navigation = render_navigation(path, previous, next_item)
        if "## Navigation" in text:
            text = re.sub(r"\n## Navigation\n.*\Z", f"\n\n{navigation}", text, flags=re.S)
        else:
            text = text.rstrip() + "\n\n" + navigation
        path.write_text(text.rstrip() + "\n", encoding="utf-8")

    return chapters


def render_readme(chapters: list[tuple[int, str, Path]]) -> str:
    grouped: dict[str, list[tuple[int, str, Path]]] = {}
    for number, title, path in chapters:
        grouped.setdefault(path.parent.name, []).append((number, title, path))

    lines = [
        "# System Design Mastery",
        "",
        "## Overview",
        "System Design Mastery is a structured roadmap for developers who want to grow from basic system-thinking skills into architect-level reasoning. The repository is organized as a guided curriculum that starts with first principles, moves through the major technical building blocks of distributed systems, applies those ideas to a broad set of domain-driven real-world systems, and ends with advanced architecture topics such as observability, security, cost, and AI-assisted design.",
        "",
        "This repository is written as a practical learning companion rather than a reference dump. The goal is to help you build conceptual clarity, recognize trade-offs, and develop the judgment needed to reason about production systems, architect-level decisions, and common interview scenarios.",
        "",
        "## Who This Is For",
        "- Software developers who want a structured path into system design.",
        "- Backend engineers who want to deepen distributed-systems and architecture knowledge.",
        "- Frontend and full-stack engineers who want to reason more confidently about backend and platform design.",
        "- Learners preparing for system design interviews.",
        "- Engineers transitioning into staff, lead, or architecture-oriented roles.",
        "",
        "## How to Use This Repo",
        "- Read the chapters in order the first time through.",
        "- Use Part 5 as a domain atlas: start with the chapter that matches the product area you care about, then drill into the H2 and H3 subchapters.",
        "- Keep your own notes, diagrams, and trade-off summaries beside each chapter.",
        "- Revisit the case studies after learning new concepts to see how your thinking changes.",
        "- Use each chapter as a prompt and context source for deeper AI-assisted learning, design review, or discussion.",
        "",
        "## Learning Path",
    ]

    for part_key in PART_HEADINGS:
        short = PART_HEADINGS[part_key].replace(":", " ->", 1)
        lines.append(f"- **{short}**: {LEARNING_PATH[part_key]}")

    lines.extend(["", "## Chapter Index", ""])
    for part_key in PART_HEADINGS:
        lines.append(f"### {PART_HEADINGS[part_key]}")
        for number, title, path in grouped.get(part_key, []):
            rel = path.relative_to(SOURCE_ROOT).as_posix()
            lines.append(f"- [{number:02d}. {title}]({rel})")
        lines.append("")

    lines.extend(
        [
            "## Suggested Study Method",
            "1. Read one chapter actively rather than passively.",
            "2. Use the Part 5 H2 sections as subchapters and the H3 sections as interview-sized system prompts.",
            "3. Draw a simple architecture or data-flow diagram for the chapter topic.",
            "4. Answer the trade-off and practice questions before moving on.",
            "5. Revisit the domain chapters later and improve them using ideas from later parts of the curriculum.",
            "",
            "## Future Expansion",
            "- Add deeper appendix material for the most important Part 5 sub-subchapters.",
            "- Add chapter-specific interview question packs and answer outlines.",
            "- Add reusable architecture templates for common product patterns.",
            "- Add design review checklists for reliability, scalability, security, and cost.",
            "",
            "## Repository Structure",
            "```text",
            "system-design-mastery/",
            "├── README.md",
            "├── 01-foundations/",
            "├── 02-building-blocks/",
            "├── 03-distributed-systems/",
            "├── 04-architectural-patterns/",
            "├── 05-real-world-systems/",
            "├── 06-advanced-architecture/",
            "└── assets/",
            "```",
            "",
            "## Suggested Next Step",
            "Start with [Chapter 1](01-foundations/01-what-is-system-design.md), then move through the repository in order. When you reach Part 5, use the domain-driven structure to compare how the same system design patterns show up in different industries.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    chapters = update_chapters()
    README_PATH.write_text(render_readme(chapters), encoding="utf-8")
    print(f"Updated curriculum metadata for {len(chapters)} chapters at {SOURCE_ROOT}")


if __name__ == "__main__":
    main()
