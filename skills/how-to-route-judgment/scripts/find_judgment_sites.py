#!/usr/bin/env python3
"""List places in a codebase where software may be guessing meaning from fuzzy input.

Usage: find_judgment_sites.py ROOT [ROOT ...]

Scans Python, JavaScript, and TypeScript files and prints candidate judgment
sites, grouped by kind, each with its file and line:

  regex over text     a regex with word alternatives, such as /refund|chargeback/
  keyword check       lowercased text tested with `in`, includes, or startswith,
                      or any()/some() over a word list
  keyword list        a list or set assigned to a name like KEYWORDS or TRIGGER_PHRASES
  fuzzy match         string-similarity or sentiment-lexicon libraries
  llm closed answer   an LLM prompt or parser that expects yes/no, a label, or a
                      score, or an enum schema in a file that calls an LLM SDK

The scan over-reports on purpose. Read each hit and keep the ones that guess
what text means. A regex over a format the system itself defines, such as an
order ID, is exact work that belongs in code. Exit status is 0, or 2 on a
usage error.
"""
import os
import re
import sys
from collections import defaultdict

EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "dist", "build", "__pycache__",
    ".next", ".nuxt", "vendor", "site-packages", "coverage", ".mypy_cache", ".pytest_cache",
}

WORD_ALTERNATION = re.compile(r"[A-Za-z][A-Za-z ']{2,}\|[A-Za-z][A-Za-z ']{2,}")
REGEX_CONTEXT = re.compile(r"\bre\.(search|match|fullmatch|findall|finditer|sub|compile)\(|RegExp\(|/[^/\n]{4,}/[a-z]*\s*\.\s*(test|exec)\(|\.match\(\s*/|\.replace\(\s*/")
CASEFOLD = re.compile(r"\.(lower|casefold)\(\)|\.toLowerCase\(\)|\.toLocaleLowerCase\(\)")
SUBSTRING_TEST = re.compile(r"\sin\s|\.includes\(|\.startswith\(|\.startsWith\(|\.endswith\(|\.endsWith\(|\.indexOf\(|\.find\(")
WORD_LOOP = re.compile(r"\bany\(\s*\w+\s+in\s+\w+|\.some\(\s*\(?\s*\w+\s*\)?\s*=>\s*[\w.]+\.includes\(")
KEYWORD_LIST = re.compile(
    r"\b[\w]*(keyword|phrase|pattern|trigger|term|word|blocklist|blacklist|allowlist|whitelist|signal|indicator|synonym|spam|profan|slang)s?[\w]*\s*(:\s*[\w\[\], ]+)?\s*=\s*[\[\({]",
    re.I,
)
FUZZY = re.compile(
    r"fuzzywuzzy|rapidfuzz|thefuzz|\bfuzz\.\w*ratio\(|\bprocess\.extract\w*\(|SequenceMatcher|get_close_matches|\bLevenshtein\b|jellyfish|jaro_winkler|"
    r"vaderSentiment|SentimentIntensityAnalyzer|\bTextBlob\b|textblob|string-similarity|compareTwoStrings|"
    r"fuse\.js|new Fuse\(|fast-levenshtein|['\"]leven['\"]|natural\.(JaroWinklerDistance|LevenshteinDistance|SentimentAnalyzer)"
)
CLOSED_PROMPT = re.compile(
    r"\b(yes or no|\"yes\" or \"no\"|'yes' or 'no'|true or false|one of the following|one of these (labels|categories|options)|"
    r"classify (this|the|each)|which (category|label|team|department|class)|on a scale (of|from) \d|"
    r"(rate|score) (it|this|the \w+) (from|between) \d|respond with only|answer with only|reply with only|"
    r"return only the (label|category|class|number|score))\b",
    re.I,
)
CLOSED_PARSE = re.compile(r"""(==|===)\s*['"]yes['"]|\.(startswith|startsWith)\(\s*['"]yes['"]|\.includes\(\s*['"]yes['"]|['"]yes['"]\s+in\s""", re.I)
ENUM_SCHEMA = re.compile(r"\bz\.enum\(|\bLiteral\[|['\"]enum['\"]\s*:")
LLM_SDK = re.compile(
    r"\bopenai\b|anthropic|@ai-sdk|\bfrom ['\"]ai['\"]|langchain|google\.generativeai|google\.genai|@google/genai|"
    r"\bcohere\b|mistralai|litellm|\bollama\b|\bgroq\b|llama_index|\bdspy\b|\binstructor\b|pydantic_ai|"
    r"generateObject|generateText|chat\.completions|messages\.create"
)

KINDS = ["regex over text", "keyword check", "keyword list", "fuzzy match", "llm closed answer"]


def is_comment(stripped: str) -> bool:
    return stripped.startswith(("#", "//", "*", "/*"))


def scan_file(path: str) -> list[tuple[str, int, str]]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    calls_llm = any(LLM_SDK.search(line) for line in lines)
    hits = []
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or is_comment(stripped):
            continue
        if REGEX_CONTEXT.search(line) and WORD_ALTERNATION.search(line):
            hits.append(("regex over text", number, stripped))
        elif WORD_LOOP.search(line) or (CASEFOLD.search(line) and SUBSTRING_TEST.search(line)):
            hits.append(("keyword check", number, stripped))
        if KEYWORD_LIST.search(line):
            hits.append(("keyword list", number, stripped))
        if FUZZY.search(line):
            hits.append(("fuzzy match", number, stripped))
        if CLOSED_PROMPT.search(line) or CLOSED_PARSE.search(line) or (calls_llm and ENUM_SCHEMA.search(line)):
            hits.append(("llm closed answer", number, stripped))
    return hits


def walk(root: str):
    if os.path.isfile(root):
        yield root
        return
    for directory, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in sorted(files):
            if os.path.splitext(name)[1] in EXTENSIONS:
                yield os.path.join(directory, name)


def main() -> None:
    roots = sys.argv[1:]
    if not roots or any(r in ("-h", "--help") for r in roots):
        print(__doc__)
        sys.exit(0 if roots else 2)
    by_kind: dict[str, list[str]] = defaultdict(list)
    files_with_hits = set()
    for root in roots:
        if not os.path.exists(root):
            print(f"find_judgment_sites.py: no such path: {root}", file=sys.stderr)
            sys.exit(2)
        for path in walk(root):
            for kind, number, text in scan_file(path):
                shown = text if len(text) <= 140 else text[:137] + "..."
                base = root if os.path.isdir(root) else os.path.dirname(root) or "."
                by_kind[kind].append(f"  {os.path.relpath(path, base)}:{number}  {shown}")
                files_with_hits.add(path)
    total = sum(len(v) for v in by_kind.values())
    print(f"{total} candidate judgment sites in {len(files_with_hits)} files.")
    if total:
        print("Read each hit and keep the ones that guess what text means.\n")
    for kind in KINDS:
        if by_kind[kind]:
            print(f"{kind.upper()} ({len(by_kind[kind])})")
            print("\n".join(by_kind[kind]))
            print()


if __name__ == "__main__":
    main()
