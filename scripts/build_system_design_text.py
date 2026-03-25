#!/usr/bin/env python3
from __future__ import annotations

import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "system-design-mastery"
OUTPUT_ROOT = ROOT / "system-design-text"

MERMAID_STARTERS = ("flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram")


def wrap_text(text: str, *, initial: str = "", subsequent: str = "") -> str:
    return textwrap.fill(
        " ".join(text.split()),
        width=96,
        initial_indent=initial,
        subsequent_indent=subsequent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def clean_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("\\*", "*")
    return " ".join(text.split()).strip()


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def format_mermaid(lines: list[str], label: str) -> list[str]:
    output = [f"[DIAGRAM: {label.upper()}]"]
    output.append("This diagram summarizes the system flow or relationship described in the chapter.")
    participants: dict[str, str] = {}

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(MERMAID_STARTERS):
            continue
        if line.startswith("participant "):
            participant_match = re.match(r"participant\s+([A-Za-z0-9_]+)(?:\s+as\s+(.+))?", line)
            if participant_match:
                key = participant_match.group(1)
                label_text = participant_match.group(2) or key
                participants[key] = clean_inline(label_text.strip('"'))
            continue

        human = (
            line.replace("-->>", " -> ")
            .replace("->>", " -> ")
            .replace("-->", " -> ")
            .replace("==>", " => ")
            .replace("---", " - ")
        )
        human = re.sub(r"\[(.*?)\]", r" \1 ", human)
        human = re.sub(r"\((.*?)\)", r" \1 ", human)
        for key, value in participants.items():
            human = re.sub(rf"\b{re.escape(key)}\b", value, human)
        human = clean_inline(human.replace('"', ""))
        if human:
            output.append(wrap_text(human, initial="  ", subsequent="    "))

    return output


def markdown_to_text(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    output: list[str] = []
    in_code_block = False
    code_language = ""
    code_lines: list[str] = []
    current_h3 = ""
    current_h4 = ""
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_language = stripped[3:].strip()
                code_lines = []
            else:
                if code_language == "mermaid":
                    label = current_h3 or "System Diagram"
                    output.extend(format_mermaid(code_lines, label))
                    output.append("")
                else:
                    output.append("[CODE BLOCK]")
                    for code_line in code_lines:
                        output.append(code_line)
                    output.append("")
                in_code_block = False
                code_language = ""
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        if stripped.startswith("# "):
            title = clean_inline(stripped[2:])
            chapter_match = re.match(r"(\d+)\.\s+(.+)", title)
            if chapter_match:
                number = int(chapter_match.group(1))
                heading = f"CHAPTER {number}: {chapter_match.group(2).upper()}"
            else:
                heading = title.upper()
            output.extend(["=" * 36, heading, "=" * 36, ""])
            i += 1
            continue

        if stripped.startswith("## "):
            current_h3 = ""
            current_h4 = ""
            title = clean_inline(stripped[3:])
            output.extend([title, "-" * len(title), ""])
            i += 1
            continue

        if stripped.startswith("### "):
            current_h3 = clean_inline(stripped[4:])
            current_h4 = ""
            output.extend([f"{current_h3}:", ""])
            i += 1
            continue

        if stripped.startswith("#### "):
            current_h4 = clean_inline(stripped[5:])
            output.extend([f"{current_h4}", "~" * len(current_h4), ""])
            i += 1
            continue

        if stripped.startswith("##### "):
            title = clean_inline(stripped[6:])
            output.extend([f"{title}:", ""])
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                headers = split_table_row(table_lines[0])
                rows = [split_table_row(row) for row in table_lines[2:]]
                for row in rows:
                    if not row:
                        continue
                    title = clean_inline(row[0])
                    output.append(f"{title}:")
                    for header, value in zip(headers[1:], row[1:]):
                        output.append(wrap_text(f"{clean_inline(header)}: {clean_inline(value)}", initial="  ", subsequent="    "))
                    output.append("")
            continue

        bullet_match = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if bullet_match:
            indent = "  " + ("  " if bullet_match.group(1) else "")
            output.append(wrap_text(clean_inline(bullet_match.group(2)), initial=f"{indent}- ", subsequent=f"{indent}  "))
            i += 1
            continue

        ordered_match = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if ordered_match:
            indent = "  " + ("  " if ordered_match.group(1) else "")
            marker = ordered_match.group(2)
            output.append(wrap_text(clean_inline(ordered_match.group(3)), initial=f"{indent}{marker}. ", subsequent=f"{indent}{' ' * (len(marker) + 2)}"))
            i += 1
            continue

        if not stripped:
            if output and output[-1] != "":
                output.append("")
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        output.append(wrap_text(clean_inline(stripped)))
        i += 1

    text = "\n".join(output)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def chapter_files() -> list[Path]:
    files = [path for path in SOURCE_ROOT.glob("*/*.md") if path.is_file()]
    return sorted(files, key=lambda path: int(path.stem.split("-", 1)[0]))


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for old_file in OUTPUT_ROOT.glob("*.txt"):
        old_file.unlink()

    for source_path in chapter_files():
        target_path = OUTPUT_ROOT / f"{source_path.stem}.txt"
        markdown_text = source_path.read_text(encoding="utf-8")
        target_path.write_text(markdown_to_text(markdown_text), encoding="utf-8")

    print(f"Generated {len(list(OUTPUT_ROOT.glob('*.txt')))} text chapters in {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
