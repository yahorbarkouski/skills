#!/usr/bin/env python3
"""Split items into shards for parallel subagents, then merge and check their results.

Usage:
  fanout.py split INPUT --out DIR [--per-shard N | --shards N] [--max-chars N] [--id-field NAME]
  fanout.py merge DIR [--field NAME[=A,B,C] ...] [--out FILE] [--keep NAMES] [--with-input]

split reads INPUT and writes DIR/input-001.jsonl, DIR/input-002.jsonl, and so on,
plus DIR/manifest.json, which records which item IDs went into which shard.
INPUT can be:

  file.jsonl   one JSON object per line
  file.json    a JSON array of objects or strings
  file.csv     one object per row, keyed by the header
  directory    one item per file: {"id": relative path, "path": absolute path},
               for documents the subagents open themselves
  other file   one item per non-empty line: {"id": line number, "text": line}

Each item keeps its ID field (default "id"). Items without one get their
1-based position as the ID. A shard closes at --per-shard items (default 50)
or at --max-chars characters of input (default 60000, about 15k tokens),
whichever comes first. --shards N splits into N shards of equal size instead,
still capped by --max-chars. Each subagent reads input-NNN.jsonl and writes
output-NNN.jsonl in the same directory: one JSON object per item, with the
item's ID under the same field name.

merge reads every output-NNN.jsonl in DIR and checks it against the manifest:
every input ID appears exactly once, no unknown IDs, every line parses, and,
for each --field, every record has that field, with one of the listed values
when the field is written NAME=A,B,C. Repeat --field for each answer field. It
prints the problems, the shards to rerun, and the distribution of each field's
values. With --out, it writes the valid records in input order. --keep lists
the fields to write, besides the ID, and --with-input adds the input item's
fields under the output fields.

Exit status is 0 when every item merged cleanly, 1 when anything is missing,
duplicated, unknown, or invalid, and 2 on a usage error.
"""
import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter

MANIFEST = "manifest.json"
OUTPUT_NAME = re.compile(r"^output-(\d+)\.jsonl$")


def fail(message: str) -> None:
    print(f"fanout.py: {message}", file=sys.stderr)
    sys.exit(2)


def load_items(path: str, id_field: str) -> list[dict]:
    if os.path.isdir(path):
        items = []
        for directory, dirs, files in os.walk(path):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for name in sorted(files):
                if name.startswith("."):
                    continue
                full = os.path.join(directory, name)
                items.append({id_field: os.path.relpath(full, path), "path": os.path.abspath(full)})
        return items
    extension = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8", newline="") as f:
        if extension == ".jsonl":
            rows = []
            for number, line in enumerate(f, 1):
                if line.strip():
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        fail(f"{path}:{number}: not valid JSON: {e.msg}")
        elif extension == ".json":
            rows = json.load(f)
            if not isinstance(rows, list):
                fail(f"{path}: expected a JSON array at the top level")
        elif extension == ".csv":
            rows = list(csv.DictReader(f))
        else:
            rows = [{"text": line.rstrip("\n")} for line in f if line.strip()]
    items = []
    for position, row in enumerate(rows, 1):
        item = row if isinstance(row, dict) else {"text": row}
        if item.get(id_field) in (None, ""):
            item = {id_field: position, **item}
        items.append(item)
    return items


def plan_shards(items: list[dict], per_shard: int, max_chars: int) -> list[list[dict]]:
    shards, current, chars = [], [], 0
    for item in items:
        size = len(json.dumps(item, ensure_ascii=False))
        if "path" in item and os.path.isfile(str(item["path"])):
            size += os.path.getsize(item["path"])
        if current and (len(current) >= per_shard or chars + size > max_chars):
            shards.append(current)
            current, chars = [], 0
        current.append(item)
        chars += size
    if current:
        shards.append(current)
    return shards


def split(args: argparse.Namespace) -> None:
    if not os.path.exists(args.input):
        fail(f"no such path: {args.input}")
    items = load_items(args.input, args.id_field)
    if not items:
        fail(f"no items in {args.input}")
    seen = Counter(str(item[args.id_field]) for item in items)
    duplicates = [key for key, count in seen.items() if count > 1]
    if duplicates:
        fail(f"duplicate IDs in input: {', '.join(duplicates[:10])}")
    per_shard = math.ceil(len(items) / args.shards) if args.shards else args.per_shard
    shards = plan_shards(items, per_shard, args.max_chars)
    os.makedirs(args.out, exist_ok=True)
    stale = [n for n in os.listdir(args.out) if n.startswith(("input-", "output-")) or n == MANIFEST]
    if stale:
        fail(f"{args.out} already holds shard files; use an empty directory")
    width = max(3, len(str(len(shards))))
    manifest = {"id_field": args.id_field, "source": os.path.abspath(args.input), "shards": {}}
    for index, shard in enumerate(shards, 1):
        name = str(index).zfill(width)
        with open(os.path.join(args.out, f"input-{name}.jsonl"), "w", encoding="utf-8") as f:
            for item in shard:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        manifest["shards"][name] = [str(item[args.id_field]) for item in shard]
    with open(os.path.join(args.out, MANIFEST), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    sizes = [len(s) for s in shards]
    print(f"{len(items)} items in {len(shards)} shards ({min(sizes)} to {max(sizes)} items each) in {args.out}")
    print(f"Each subagent reads input-NNN.jsonl and writes output-NNN.jsonl, keyed by \"{args.id_field}\".")


def merge(args: argparse.Namespace) -> None:
    manifest_path = os.path.join(args.dir, MANIFEST)
    if not os.path.isfile(manifest_path):
        fail(f"no {MANIFEST} in {args.dir}; run split first")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    id_field = manifest["id_field"]
    shard_of = {key: shard for shard, keys in manifest["shards"].items() for key in keys}
    order = [key for keys in manifest["shards"].values() for key in keys]
    checks: dict[str, set[str] | None] = {}
    for spec in args.field or []:
        name, _, values = spec.partition("=")
        checks[name.strip()] = {v.strip() for v in values.split(",") if v.strip()} or None

    records: dict[str, dict] = {}
    duplicate, unknown, invalid, unparsed = [], [], [], []
    invalid_keys = set()
    names = sorted(n for n in os.listdir(args.dir) if OUTPUT_NAME.match(n))
    for name in names:
        with open(os.path.join(args.dir, name), encoding="utf-8") as f:
            for number, line in enumerate(f, 1):
                if not line.strip():
                    continue
                where = f"{name}:{number}"
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    unparsed.append(where)
                    continue
                if not isinstance(record, dict) or record.get(id_field) in (None, ""):
                    unparsed.append(f"{where} (no \"{id_field}\")")
                    continue
                key = str(record[id_field])
                if key not in shard_of:
                    unknown.append(f"{where} {key}")
                    continue
                if key in records:
                    duplicate.append(key)
                    continue
                problems = []
                for field, allowed in checks.items():
                    values = record.get(field)
                    values = values if isinstance(values, list) else [values]
                    if values == [None] or (allowed and any(str(v) not in allowed for v in values)):
                        problems.append(f"{field}={record.get(field)!r}")
                if problems:
                    invalid.append(f"{key} ({', '.join(problems)})")
                    invalid_keys.add(key)
                    continue
                records[key] = record

    missing = [key for key in order if key not in records and key not in invalid_keys]
    bad_keys = set(missing) | set(duplicate) | invalid_keys
    rerun = sorted({shard_of[key] for key in bad_keys if key in shard_of})
    print(f"{len(records)} of {len(order)} items merged from {len(names)} output files.")
    for label, entries in [
        ("missing", missing),
        ("duplicate IDs", duplicate),
        ("unknown IDs", unknown),
        ("invalid values", invalid),
        ("unparseable lines", unparsed),
    ]:
        if entries:
            shown = ", ".join(entries[:20]) + (f", and {len(entries) - 20} more" if len(entries) > 20 else "")
            print(f"{label} ({len(entries)}): {shown}")
    if rerun:
        print(f"Rerun shards: {', '.join(rerun)}")
    for field, allowed in checks.items():
        if not records:
            break
        counts = Counter()
        for record in records.values():
            values = record[field]
            for value in values if isinstance(values, list) else [values]:
                counts[str(value)] += 1
        print(f"\n{field}:")
        for value, count in counts.most_common():
            print(f"  {value:<24} {count:>6}  {100 * count / len(records):5.1f}%")
        for value in sorted((allowed or set()) - set(counts)):
            print(f"  {value:<24} {0:>6}    0.0%")

    if args.out:
        keep = [field.strip() for field in args.keep.split(",") if field.strip()] if args.keep else []
        inputs: dict[str, dict] = {}
        if args.with_input:
            for shard in manifest["shards"]:
                with open(os.path.join(args.dir, f"input-{shard}.jsonl"), encoding="utf-8") as f:
                    for line in f:
                        item = json.loads(line)
                        inputs[str(item[id_field])] = item
        with open(args.out, "w", encoding="utf-8") as f:
            for key in order:
                if key in records:
                    row = {**inputs.get(key, {}), **records[key]}
                    if keep:
                        row = {field: row[field] for field in [id_field, *keep] if field in row}
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"\nWrote {len(records)} records to {args.out}")

    clean = not (missing or duplicate or unknown or invalid or unparsed)
    sys.exit(0 if clean else 1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fanout.py",
        description="Split items into shards for parallel subagents, then merge and check their results.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("split", help="split INPUT into shard files")
    p.add_argument("input")
    p.add_argument("--out", required=True, help="directory for shard files (must hold no earlier shards)")
    size = p.add_mutually_exclusive_group()
    size.add_argument("--per-shard", type=int, default=50, help="items per shard (default 50)")
    size.add_argument("--shards", type=int, help="split into this many shards of equal size")
    p.add_argument("--max-chars", type=int, default=60000, help="input characters per shard (default 60000)")
    p.add_argument("--id-field", default="id", help="field that holds each item's ID (default id)")

    m = commands.add_parser("merge", help="merge and check output-NNN.jsonl files")
    m.add_argument("dir")
    m.add_argument("--field", action="append", metavar="NAME[=A,B,C]",
                   help="answer field every record must have, with its allowed values; repeat for each field")
    m.add_argument("--keep", help="comma-separated fields to write to --out, besides the ID")
    m.add_argument("--out", help="file for the merged records, in input order")
    m.add_argument("--with-input", action="store_true", help="add each input item's fields to its record")

    args = parser.parse_args()
    if args.command == "split":
        if (args.shards is not None and args.shards < 1) or args.per_shard < 1 or args.max_chars < 1:
            fail("--per-shard, --shards, and --max-chars must be at least 1")
        split(args)
    else:
        if args.keep and not args.out:
            fail("--keep needs --out")
        merge(args)


if __name__ == "__main__":
    main()
