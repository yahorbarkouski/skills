#!/usr/bin/env python3
"""Number every sentence of a prompt so a cold reader can judge each one.

Usage: number_sentences.py PROMPT_FILE [MORE_FILES...] > numbered.txt

Each prose sentence and each list item gets a marker such as [S12]. Lines that
are wrapped inside one paragraph or one list item are joined first, so a
sentence keeps one number. Headings and table rows count as one unit each. A
code fence counts as one unit and is copied unchanged. Each front-matter line is
numbered on its own, and horizontal rules and front-matter delimiters stay
unnumbered. With several files, each file starts
with a header line naming it, so the reader can tell the parts apart.
"""
import os
import re
import sys

ABBREVIATIONS = {"e.g.", "i.e.", "etc.", "vs.", "cf.", "dr.", "mr.", "mrs.", "ms.", "st.", "no.", "approx."}
BOUNDARY = re.compile(r"[.!?][)\"'\]*_`]*\s+(?=[A-Z0-9\"'(\[`*_])")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
TABLE_SEPARATOR = re.compile(r"^\s*\|[\s|:-]+\|?\s*$")


def split_sentences(text: str) -> list[str]:
    pieces, start = [], 0
    for match in BOUNDARY.finditer(text):
        words = text[start : match.start() + 1].split()
        if words and words[-1].lower() in ABBREVIATIONS:
            continue
        pieces.append(text[start : match.end()].strip())
        start = match.end()
    pieces.append(text[start:].strip())
    return [p for p in pieces if p]


def is_block_start(line: str) -> bool:
    s = line.strip()
    return (
        not s
        or s.startswith("#")
        or s.startswith("|")
        or bool(FENCE.match(line))
        or bool(RULE.match(line))
        or bool(LIST_ITEM.match(line))
    )


class Numberer:
    def __init__(self) -> None:
        self.n = 1

    def mark(self, text: str) -> str:
        out = []
        for sentence in split_sentences(text):
            out.append(f"[S{self.n}] {sentence}")
            self.n += 1
        return " ".join(out)

    def unit(self) -> str:
        marker = f"[S{self.n}]"
        self.n += 1
        return marker

    def number(self, text: str) -> list[str]:
        lines = text.splitlines()
        out: list[str] = []
        i = 0
        if lines and RULE.match(lines[0]) and lines[0].strip().startswith("---"):
            end = next((j for j in range(1, len(lines)) if lines[j].strip() == "---"), None)
            if end is not None:
                out.append(lines[0])
                for fm_line in lines[1:end]:
                    out.append(self.mark(fm_line) if fm_line.strip() else fm_line)
                out.append(lines[end])
                i = end + 1
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            fence = FENCE.match(line)
            if fence:
                char, length = fence.group(1)[0], len(fence.group(1))
                out.append(self.unit())
                out.append(line)
                i += 1
                while i < len(lines):
                    out.append(lines[i])
                    close = FENCE.match(lines[i])
                    i += 1
                    if close and close.group(1)[0] == char and len(close.group(1)) >= length and not lines[i - 1].strip()[len(close.group(1)):].strip():
                        break
                continue
            if not stripped or RULE.match(line) or TABLE_SEPARATOR.match(line):
                out.append(line)
                i += 1
                continue
            if stripped.startswith("#") or stripped.startswith("|"):
                out.append(f"{self.unit()} {line}")
                i += 1
                continue
            item = LIST_ITEM.match(line)
            if item:
                indent, bullet, body = item.groups()
                i += 1
                while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]) and len(lines[i]) - len(lines[i].lstrip()) > len(indent):
                    body += " " + lines[i].strip()
                    i += 1
                out.append(f"{indent}{bullet} {self.mark(body)}")
                continue
            indent = line[: len(line) - len(line.lstrip())]
            body = stripped
            i += 1
            while i < len(lines) and not is_block_start(lines[i]):
                body += " " + lines[i].strip()
                i += 1
            out.append(indent + self.mark(body))
        return out


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    numberer = Numberer()
    several = len(sys.argv) > 2
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if several:
            print(f"===== {os.path.basename(path)} =====")
        print("\n".join(numberer.number(text)))
        if several:
            print()


if __name__ == "__main__":
    main()
