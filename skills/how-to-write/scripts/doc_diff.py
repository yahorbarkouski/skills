#!/usr/bin/env python3
"""List what a document states, and what an edit dropped, reworded, moved, or added.

Usage:
  doc_diff.py inventory FILE
  doc_diff.py compare ORIGINAL EDITED [--sentences]

inventory prints the items the script finds in FILE, grouped by kind, with line
numbers and the section each item sits in.

compare matches items between two versions of a Markdown or plain-text document.
It prints the items of ORIGINAL that are missing from EDITED, the ones EDITED
rewords, the ones that now sit under a different heading, checkboxes whose state
changed, the items EDITED adds, the hedge-word totals of both versions, and the
sections that lost more than a third of their words. With --sentences it also
lists every ordinary sentence that has no exact match.

Kinds of item:
  heading      a Markdown heading
  frontmatter  one line of YAML front matter
  rule         a sentence with must, never, always, shall, should, only, do not, ...
  hedge        a sentence with may, might, likely, unclear, TBD, assume, ..., or
               one that ends in a question mark
  checkbox     a task-list item and its state
  table-row    one table row
  code-block   a fenced code block, compared as a whole
  id           a token such as FR-001, SC-2, U-12, or T014
  link         a Markdown link target or a bare URL
  code         an inline code span: commands, paths, identifiers
  number       a number with its unit, such as 200 ms, 32 KiB, or 40%

The script matches text, not meaning. A missing item is something to account
for, not proof of a loss, since a requested change also shows up as missing.
A claim reworded until it shares no tracked token with the original is invisible
to the script, so read every changed passage as well.

Exit status is 0 on success and 2 on a usage or file error.
"""
import argparse
import difflib
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

ABBREVIATIONS = {"e.g.", "i.e.", "etc.", "vs.", "cf.", "approx.", "no.", "fig."}
BOUNDARY = re.compile(r"[.!?][)\"'\]*_`]*\s+(?=[A-Z0-9\"'(\[`*_])")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
CHECKBOX = re.compile(r"^\[([ xX~-])\]\s+(.*)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HORIZONTAL_RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
TABLE_SEPARATOR = re.compile(r"^\s*\|[\s|:-]+\|?\s*$")

RULE_WORDS = re.compile(
    r"\b(must|never|always|shall|should|required|requires?|forbidden|prohibited|only|"
    r"cannot|can't|do not|don't|does not|doesn't|may not|must not|should not|shouldn't)\b",
    re.I,
)
HEDGE_WORDS = re.compile(
    r"\b(may|might|could|likely|unlikely|probably|possibly|perhaps|maybe|unclear|unknown|"
    r"unverified|undecided|uncertain|tbd|tbc|todo|open question|not sure|we think|we believe|"
    r"seems?|assum(?:e|ed|es|ing|ptions?)|approximately|roughly|estimated?)\b",
    re.I,
)
ID = re.compile(r"\b[A-Z][A-Z0-9]*-\d+(?:\.\d+)*[a-z]?\b|\b[A-Z]{1,3}\d{2,}\b")
MD_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
BARE_URL = re.compile(r"https?://[^\s)>\]]+")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")
NUMBER = re.compile(
    r"(?<![\w.])(\d+(?:[.,]\d+)*)"
    r"(\s?%|\s?(?:ms|s|sec|seconds?|min|minutes?|h|hours?|days?|weeks?|months?|[KMGT]i?B|bytes?|"
    r"tokens?|lines?|words?|characters?|chars?|px|x|k|pts?|points?)\b)?"
)

SENTENCE_KINDS = ("rule", "hedge")
TOKEN_KINDS = ("id", "link", "code", "number")


@dataclass
class Item:
    kind: str
    key: str
    text: str
    line: int
    section: int  # index of the enclosing heading in Doc.headings, or -1 before the first heading
    state: str = ""


class Doc:
    def __init__(self, path: str) -> None:
        self.path = path
        self.items: list[Item] = []
        self.sentences: list[Item] = []  # every prose sentence, tracked kinds included
        self.headings: list[Item] = []
        self.words: Counter = Counter()  # section index -> word count
        self.hedge_words = 0
        self._stack: list[tuple[int, int]] = []  # (level, heading index)
        try:
            with open(path, encoding="utf-8") as f:
                self._parse(f.read().splitlines())
        except OSError as error:
            print(f"doc_diff.py: {error}", file=sys.stderr)
            sys.exit(2)

    def section(self) -> int:
        return self._stack[-1][1] if self._stack else -1

    def section_name(self, index: int) -> str:
        if index < 0:
            return "(top)"
        names, current = [], index
        while current >= 0:
            names.append(self.headings[current].text)
            current = self.headings[current].section
        return " > ".join(reversed(names))

    def add(self, kind: str, text: str, line: int, state: str = "", key: str | None = None) -> Item:
        item = Item(kind, key if key is not None else normalize(text), text.strip(), line, self.section(), state)
        self.items.append(item)
        return item

    def _parse(self, lines: list[str]) -> None:
        i = 0
        if lines and lines[0].strip() == "---":
            end = next((j for j in range(1, len(lines)) if lines[j].strip() == "---"), None)
            if end is not None:
                for j in range(1, end):
                    if lines[j].strip():
                        self.add("frontmatter", lines[j], j + 1)
                i = end + 1
        while i < len(lines):
            line, number = lines[i], i + 1
            stripped = line.strip()
            fence = FENCE.match(line)
            if fence:
                marker = fence.group(1)
                body = [line]
                i += 1
                while i < len(lines):
                    body.append(lines[i])
                    i += 1
                    if lines[i - 1].strip().startswith(marker[0] * len(marker)) and not lines[i - 1].strip().strip(marker[0]):
                        break
                content = "\n".join(l.rstrip() for l in body)
                label = next((l.strip() for l in body[1:] if l.strip()), "(empty)")
                self.add("code-block", f"{body[0].strip()} {label}", number, key=content)
                continue
            if not stripped or HORIZONTAL_RULE.match(line) or TABLE_SEPARATOR.match(line):
                i += 1
                continue
            heading = HEADING.match(stripped)
            if heading:
                level = len(heading.group(1))
                while self._stack and self._stack[-1][0] >= level:
                    self._stack.pop()
                item = self.add("heading", heading.group(2), number)
                self.headings.append(item)
                self._stack.append((level, len(self.headings) - 1))
                self._tokens(heading.group(2), number)
                i += 1
                continue
            if stripped.startswith("|"):
                self.add("table-row", " | ".join(c.strip() for c in stripped.strip("|").split("|")), number)
                self._tokens(stripped, number)
                self._count_words(stripped)
                self.hedge_words += len(HEDGE_WORDS.findall(CODE_SPAN.sub(" ", stripped)))
                i += 1
                continue
            listed = LIST_ITEM.match(line)
            if listed:
                indent, body = listed.group(1), listed.group(3)
                i += 1
                while i < len(lines) and lines[i].strip() and not starts_block(lines[i]) and indent_of(lines[i]) > len(indent):
                    body += " " + lines[i].strip()
                    i += 1
                box = CHECKBOX.match(body)
                if box:
                    self.add("checkbox", box.group(2), number, state=box.group(1).lower())
                    self._tokens(box.group(2), number)
                    self._count_words(box.group(2))
                    self.hedge_words += len(HEDGE_WORDS.findall(CODE_SPAN.sub(" ", box.group(2))))
                else:
                    self._prose(body, number)
                continue
            body = stripped
            i += 1
            while i < len(lines) and not starts_block(lines[i]):
                body += " " + lines[i].strip()
                i += 1
            self._prose(body, number)

    def _prose(self, text: str, line: int) -> None:
        self._count_words(text)
        self._tokens(text, line)
        for sentence in split_sentences(text):
            plain = CODE_SPAN.sub(" ", sentence)
            self.hedge_words += len(HEDGE_WORDS.findall(plain))
            kinds = [k for k, pattern in (("rule", RULE_WORDS), ("hedge", HEDGE_WORDS)) if pattern.search(plain)]
            if sentence.rstrip("*_)\"' ").endswith("?"):
                self.hedge_words += 1
                if "hedge" not in kinds:
                    kinds.append("hedge")
            kind = "+".join(kinds) if kinds else "sentence"
            item = Item(kind, normalize(sentence), sentence, line, self.section())
            self.sentences.append(item)
            if kinds:
                self.items.append(item)

    def _tokens(self, text: str, line: int) -> None:
        for match in CODE_SPAN.finditer(text):
            self.add("code", match.group(2), line, key=match.group(2).strip())
        rest = CODE_SPAN.sub(" ", text)
        for match in MD_LINK.finditer(rest):
            self.add("link", match.group(1), line, key=match.group(1))
        rest = MD_LINK.sub(" ", rest)
        for match in BARE_URL.finditer(rest):
            url = match.group(0).rstrip(".,;:")
            self.add("link", url, line, key=url)
        rest = BARE_URL.sub(" ", rest)
        for match in ID.finditer(rest):
            self.add("id", match.group(0), line, key=match.group(0))
        rest = ID.sub(" ", rest)
        rest = re.sub(r"^\s*\d+[.)]\s", " ", rest)
        for match in NUMBER.finditer(rest):
            value = re.sub(r"\s+", " ", match.group(0))
            self.add("number", value, line, key=value)

    def _count_words(self, text: str) -> None:
        self.words[self.section()] += len(text.split())

    def of_kind(self, *kinds: str) -> list[Item]:
        return [item for item in self.items if item.kind in kinds]


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip())


def starts_block(line: str) -> bool:
    s = line.strip()
    return (
        not s
        or s.startswith("#")
        or s.startswith("|")
        or bool(FENCE.match(line))
        or bool(HORIZONTAL_RULE.match(line))
        or bool(LIST_ITEM.match(line))
    )


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


def normalize(text: str) -> str:
    text = re.sub(r"[*_]{1,3}(?=\S)|(?<=\S)[*_]{1,3}", "", text)
    return re.sub(r"\s+", " ", text).strip().rstrip(".;:,").lower()


def is_sentence(item: Item) -> bool:
    return item.kind == "sentence" or any(k in item.kind.split("+") for k in SENTENCE_KINDS)


def family(item: Item) -> str:
    return "sentence" if is_sentence(item) else item.kind


def similarity(a: str, b: str, threshold: float) -> float:
    """Edit similarity, or 0.8 when the shorter text appears whole inside the longer one."""
    shorter, longer = sorted((a, b), key=len)
    if len(shorter) >= 4 and re.search(rf"(?<!\w){re.escape(shorter)}(?!\w)", longer):
        return 0.8
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if matcher.real_quick_ratio() < threshold or matcher.quick_ratio() < threshold:
        return 0.0
    return matcher.ratio()


def match_items(original: list[Item], edited: list[Item], threshold: float = 0.7):
    """Pair items exactly first, then by similarity. Returns (exact, reworded, missing, unmatched edited)."""
    pool: dict[str, list[Item]] = defaultdict(list)
    for item in edited:
        pool[item.key].append(item)
    exact, leftover = [], []
    for item in original:
        if pool[item.key]:
            exact.append((item, pool[item.key].pop(0)))
        else:
            leftover.append(item)
    remaining = [item for items in pool.values() for item in items]
    reworded, missing = [], []
    for item in leftover:
        scored = [(similarity(item.key, other.key, threshold), n) for n, other in enumerate(remaining) if family(other) == family(item)]
        best = max(scored, default=(0.0, -1))
        if best[0] >= threshold:
            reworded.append((item, remaining.pop(best[1])))
        else:
            missing.append(item)
    return exact, reworded, missing, remaining


def label(item: Item) -> str:
    return item.kind if len(item.kind) <= 10 else item.kind[:10]


def inventory(path: str) -> None:
    doc = Doc(path)
    print(f"{path}: {len(doc.headings)} headings, {len(doc.sentences)} sentences, {doc.hedge_words} hedge words\n")
    for kind in ("frontmatter", "heading", "rule", "hedge", "checkbox", "table-row", "code-block"):
        items = [item for item in doc.items if kind in item.kind.split("+")]
        if not items:
            continue
        print(f"{kind.upper()} ({len(items)})")
        for item in items:
            state = f"[{item.state}] " if item.kind == "checkbox" else ""
            print(f"  L{item.line:<5} [{doc.section_name(item.section)}] {state}{item.text}")
        print()
    for kind in TOKEN_KINDS:
        counts = Counter(item.key for item in doc.of_kind(kind))
        if counts:
            print(f"{kind.upper()} ({sum(counts.values())} occurrences, {len(counts)} distinct)")
            print("  " + ", ".join(f"{key} x{n}" if n > 1 else key for key, n in counts.items()))
            print()


def compare(original_path: str, edited_path: str, list_sentences: bool) -> None:
    old, new = Doc(original_path), Doc(edited_path)
    old_whole = [i for i in old.items if i.kind not in TOKEN_KINDS]
    new_whole = [i for i in new.items if i.kind not in TOKEN_KINDS and not is_sentence(i)] + new.sentences

    headings_exact, headings_reworded, _, _ = match_items(old.headings, new.headings)
    section_map = {-1: -1}
    for a, b in headings_exact + headings_reworded:
        section_map[old.headings.index(a)] = new.headings.index(b)

    exact, reworded, missing, added = match_items(old_whole, new_whole)
    moved = [(a, b) for a, b in exact + reworded if section_map.get(a.section, -2) != b.section]
    flipped = [(a, b) for a, b in exact if a.kind == "checkbox" and a.state != b.state]
    added = [i for i in added if i.kind != "sentence"]

    print(f"original: {original_path} ({len(old.sentences)} sentences)   edited: {edited_path} ({len(new.sentences)} sentences)\n")

    token_missing, token_added = [], []
    for kind in TOKEN_KINDS:
        before = Counter(i.key for i in old.of_kind(kind))
        after = Counter(i.key for i in new.of_kind(kind))
        for key, n in before.items():
            if after[key] < n:
                lines = ",".join(f"L{i.line}" for i in old.of_kind(kind) if i.key == key)
                token_missing.append(f"  {lines:<12} {kind:<10} {key}  ({n} in original, {after[key]} in edited)")
        for key, n in after.items():
            if before[key] < n:
                token_added.append(f"  {kind:<10} {key}  ({before[key]} in original, {n} in edited)")

    if missing or token_missing:
        print(f"MISSING: {len(missing) + len(token_missing)} items in the original have no match in the edited version.")
        print("Account for each one: changed as requested, moved elsewhere, or removed for a stated reason.")
        for item in missing:
            print(f"  L{item.line:<11} {label(item):<10} [{old.section_name(item.section)}] {item.text}")
        for row in token_missing:
            print(row)
        print()
    if reworded:
        print(f"REWORDED: {len(reworded)} items changed wording. Check that each still means what it meant.")
        for a, b in reworded:
            print(f"  L{a.line} -> L{b.line}  {label(a)}")
            print(f"    was: {a.text}")
            print(f"    now: {b.text}")
        print()
    if moved:
        print(f"MOVED: {len(moved)} items now sit under a different heading.")
        for a, b in moved:
            print(f"  L{a.line} -> L{b.line}  {label(a):<10} {a.text[:70]}")
            print(f"    from [{old.section_name(a.section)}] to [{new.section_name(b.section)}]")
        print()
    if flipped:
        print(f"CHECKBOX STATE: {len(flipped)} changed.")
        for a, b in flipped:
            print(f"  L{a.line} -> L{b.line}  [{a.state}] -> [{b.state}]  {a.text}")
        print()
    if added or token_added:
        print(f"ADDED: {len(added) + len(token_added)} items appear only in the edited version.")
        for item in added:
            print(f"  L{item.line:<11} {label(item):<10} [{new.section_name(item.section)}] {item.text}")
        for row in token_added:
            print(row)
        print()

    print(f"HEDGE WORDS: {old.hedge_words} in the original, {new.hedge_words} in the edited version.")
    shrunk = []
    for old_index, count in old.words.items():
        new_index = section_map.get(old_index)
        if count >= 40 and new_index is not None and new.words[new_index] < count * 2 / 3:
            shrunk.append(f"  [{old.section_name(old_index)}] {count} -> {new.words[new_index]} words")
    if shrunk:
        print("SHRUNK: sections that lost more than a third of their words")
        print("\n".join(shrunk))

    plain = [s for s in old.sentences if s.kind == "sentence"]
    new_keys = {s.key for s in new.sentences}
    lost_plain = [s for s in plain if s.key not in new_keys]
    print(f"OTHER SENTENCES: {len(lost_plain)} of {len(plain)} ordinary sentences have no exact match"
          + ("." if list_sentences or not lost_plain else " (rerun with --sentences to list them)."))
    if list_sentences:
        for s in lost_plain:
            print(f"  L{s.line:<11} [{old.section_name(s.section)}] {s.text}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("inventory", help="list the items in one document")
    one.add_argument("file")
    two = commands.add_parser("compare", help="compare an original and an edited version")
    two.add_argument("original")
    two.add_argument("edited")
    two.add_argument("--sentences", action="store_true", help="also list ordinary sentences with no exact match")
    args = parser.parse_args()
    if args.command == "inventory":
        inventory(args.file)
    else:
        compare(args.original, args.edited, args.sentences)


if __name__ == "__main__":
    main()
