#!/usr/bin/env python3
"""Save each result as it arrives, resume stopped runs, and report progress.

Use it as a module in a Python job:

    from runlog import Run

    with Run("runs/profiles-v2", config={"model": MODEL, "prompt": 3}, max_cost=5.0) as run:
        for lot in run.todo(lots, id_of=lambda lot: lot["lot_id"], limit=args.limit):
            try:
                response = generate_profile(lot)
            except Exception as error:
                run.fail(lot["lot_id"], error)
                continue
            run.save(lot["lot_id"], {"profile": response.text}, cost=response.cost)

A run directory holds:

  config.json     the settings that affect results; a different config refuses to
                  reuse the directory
  results.jsonl   one line per finished item, appended and flushed as it arrives:
                  {"id", "at", "cost", ...your fields}
  errors.jsonl    one line per failed attempt: {"id", "at", "cost", "error"}
  progress.json   counts, rate, time left, spend, and status, rewritten at every
                  progress report

todo() skips items already in results.jsonl, so rerunning resumes, and progress
then counts only the items passed to it. Failed items are retried on the next
run; retry within a run in your own code, and call fail() once per item when
the retries are used up. Every `report_every` seconds, and when the run ends, a
progress line goes to stderr. The run stops itself, raising RunStopped, after
`max_consecutive_failures` failures in a row or once the run directory's total
spend reaches `max_cost`. Inside a `with` block in the main thread, SIGTERM
(plain `kill PID`) and Ctrl+C stop the run cleanly, even when it was started in
the background, and record why in progress.json. Run is safe to share between
threads.

Use it from the command line:

  runlog.py status RUN_DIR
      Print a run's progress from its files, including how long ago it last
      saved a result. Works while the job runs and after it has died.
  runlog.py sample INPUT --by FIELD --per-group N [--seed S]
                   [--extremes FIELD ...] [--include ID,ID --id-field NAME]
      Print a random sample of N items from each value of FIELD, as JSON Lines,
      in input order. --extremes adds the items with the longest and shortest
      value of a field, and --include adds items by ID. INPUT is a .jsonl,
      .json (array), or .csv file.

Exit status is 0, or 2 on a usage error.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import random
import signal
import sys
import threading
import time
import traceback
from collections import defaultdict


class RunStopped(Exception):
    """The run stopped itself: too many failures in a row, or the budget was reached."""


class _Terminated(KeyboardInterrupt):
    """Raised in the main thread when the process receives SIGTERM."""


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _duration(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m{seconds % 60:02d}s"
    return f"{seconds // 3600}h{seconds % 3600 // 60:02d}m"


def _money(amount: float) -> str:
    return f"${amount:,.2f}" if amount >= 0.1 or amount == 0 else f"${amount:.4f}"


def _read_lines(path: str, repair: bool = False) -> list[dict]:
    """Read a JSON Lines file, ignoring a partial last line.

    With repair, cut the partial line off the file, as a killed process leaves
    it, so the next appended line starts on a line of its own.
    """
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        data = f.read()
    if data and not data.endswith(b"\n"):
        cut = data.rfind(b"\n") + 1
        if repair:
            with open(path, "r+b") as f:
                f.truncate(cut)
        data = data[:cut]
    records = []
    for line in data.decode("utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _write_json_atomic(path: str, value: dict) -> None:
    temporary = f"{path}.tmp"
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=1)
    os.replace(temporary, path)


class Run:
    def __init__(
        self,
        path: str,
        config: dict | None = None,
        total: int | None = None,
        max_cost: float | None = None,
        max_consecutive_failures: int = 5,
        report_every: float = 15.0,
        name: str | None = None,
    ):
        self.path = path
        self.name = name or os.path.basename(os.path.normpath(path))
        self.total = total
        self.max_cost = max_cost
        self.max_consecutive_failures = max_consecutive_failures
        self.report_every = report_every
        self._lock = threading.Lock()
        os.makedirs(path, exist_ok=True)

        config_path = os.path.join(path, "config.json")
        if config is not None:
            config = json.loads(json.dumps(config, default=str))
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    saved = json.load(f)
                if saved != config:
                    raise ValueError(
                        f"{path} was started with a different config ({saved}); "
                        "use a new run directory for new settings"
                    )
            else:
                _write_json_atomic(config_path, config)

        results = _read_lines(os.path.join(path, "results.jsonl"), repair=True)
        errors = _read_lines(os.path.join(path, "errors.jsonl"), repair=True)
        self._done = {str(r["id"]) for r in results if "id" in r}
        self._failing = {str(e["id"]) for e in errors if "id" in e} - self._done
        self.spent = sum(float(r.get("cost") or 0) for r in results + errors)
        self._done_before = len(self._done)
        self._saved_now = 0
        self._consecutive_failures = 0
        self._started = time.monotonic()
        self._last_report = self._started
        self._results = open(os.path.join(path, "results.jsonl"), "a", encoding="utf-8")
        self._errors = open(os.path.join(path, "errors.jsonl"), "a", encoding="utf-8")
        self.status = "running"
        self._scope: set[str] | None = None
        self._limit_reached: int | None = None
        self._old_handlers: dict = {}
        if self._done:
            print(f"[{self.name}] resuming: {len(self._done)} items already saved, {_money(self.spent)} spent", file=sys.stderr)

    def done(self, item_id) -> bool:
        return str(item_id) in self._done

    def todo(self, items, id_of=lambda item: item["id"], limit: int | None = None):
        """Yield the items not yet saved, at most `limit` of them.

        Progress counts only these items, so a run over a sample file reports
        the sample's size, and items saved by earlier runs outside it don't count.
        """
        items = list(items)
        self._scope = {str(id_of(item)) for item in items}
        if self.total is None:
            self.total = len(items)
        yielded = 0
        for item in items:
            if self.done(id_of(item)):
                continue
            if limit is not None and yielded >= limit:
                self._limit_reached = limit
                return
            yielded += 1
            yield item

    def save(self, item_id, record: dict | None = None, cost: float = 0.0) -> None:
        line = {"id": item_id, "at": _now(), "cost": cost, **(record or {})}
        line["id"] = item_id
        with self._lock:
            self._results.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
            self._results.flush()
            self._done.add(str(item_id))
            self._failing.discard(str(item_id))
            self._saved_now += 1
            self.spent += cost
            self._consecutive_failures = 0
            self._maybe_report()
            if self.max_cost is not None and self.spent >= self.max_cost:
                self._stop(f"budget of {_money(self.max_cost)} reached")

    def fail(self, item_id, error, cost: float = 0.0) -> None:
        text = error if isinstance(error, str) else "".join(traceback.format_exception_only(type(error), error)).strip()
        line = {"id": item_id, "at": _now(), "cost": cost, "error": text}
        with self._lock:
            self._errors.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
            self._errors.flush()
            self._failing.add(str(item_id))
            self.spent += cost
            self._consecutive_failures += 1
            self._maybe_report()
            if self._consecutive_failures >= self.max_consecutive_failures:
                self._stop(f"{self._consecutive_failures} failures in a row; last: {text[:200]}")
            if self.max_cost is not None and self.spent >= self.max_cost:
                self._stop(f"budget of {_money(self.max_cost)} reached")

    def progress(self) -> dict:
        elapsed = time.monotonic() - self._started
        rate = self._saved_now / elapsed if elapsed > 0 else 0.0
        scope = self._scope if self._scope is not None else self._done
        done = len(self._done & scope)
        remaining = (self.total - done) if self.total is not None else None
        per_item = self.spent / len(self._done) if self._done else None
        value = {
            "name": self.name,
            "status": self.status,
            "done": done,
            "total": self.total,
            "failing": len(self._failing & scope) if self._scope is not None else len(self._failing),
            "spent": round(self.spent, 4),
            "cost_per_item": round(per_item, 6) if per_item is not None else None,
            "rate_per_second": round(rate, 3),
            "seconds_left": round(remaining / rate) if remaining and rate > 0 else None,
            "projected_cost": round(self.spent + per_item * remaining, 4) if per_item is not None and remaining is not None else None,
            "done_outside_scope": len(self._done - scope),
            "updated_at": _now(),
        }
        return value

    def report(self) -> None:
        value = self.progress()
        _write_json_atomic(os.path.join(self.path, "progress.json"), value)
        print(format_progress(value), file=sys.stderr, flush=True)
        self._last_report = time.monotonic()

    def finish(self, status: str = "finished") -> None:
        with self._lock:
            if self.status == "running":
                if status == "finished" and self._limit_reached is not None:
                    done = len(self._done & self._scope)
                    status = f"finished: limit of {self._limit_reached} reached, {self.total - done} left"
                self.status = status
            self.report()
            self._results.close()
            self._errors.close()

    def _maybe_report(self) -> None:
        if time.monotonic() - self._last_report >= self.report_every:
            self.report()

    def _stop(self, reason: str) -> None:
        self.status = f"stopped: {reason}"
        self.report()
        raise RunStopped(reason)

    def __enter__(self) -> "Run":
        if threading.current_thread() is threading.main_thread():
            def terminate(signum, frame):
                raise _Terminated()

            self._old_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, terminate)
            # A job started with `&` from a script ignores SIGINT; restore Ctrl+C.
            if signal.getsignal(signal.SIGINT) is signal.SIG_IGN:
                self._old_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, signal.default_int_handler)
        return self

    def __exit__(self, kind, error, trace) -> bool:
        for signum, handler in self._old_handlers.items():
            signal.signal(signum, handler)
        if kind is not None and issubclass(kind, KeyboardInterrupt):
            reason = "terminated" if issubclass(kind, _Terminated) else "interrupted"
            self.finish(f"stopped: {reason}")
            print(f"[{self.name}] stopped. Everything saved so far is kept; run the same command again to continue.", file=sys.stderr)
            raise SystemExit(143 if reason == "terminated" else 130)
        if kind is not None and not isinstance(error, RunStopped):
            self.finish(f"stopped: {kind.__name__}: {error}")
        else:
            self.finish()
        return False


def format_progress(value: dict) -> str:
    done, total = value["done"], value.get("total")
    parts = [f"{done}/{total} ({100 * done / total:.0f}%)" if total else f"{done} done"]
    parts.append(f"{value['failing']} failing")
    if value.get("rate_per_second"):
        parts.append(f"{value['rate_per_second']:.2f}/s")
    if value.get("seconds_left") is not None and value.get("status", "running") == "running":
        parts.append(f"~{_duration(value['seconds_left'])} left")
    money = f"{_money(value['spent'])} spent"
    if value.get("cost_per_item"):
        money += f" ({_money(value['cost_per_item'])}/item)"
    if value.get("projected_cost") is not None:
        money += f", ~{_money(value['projected_cost'])} projected"
    parts.append(money)
    line = f"[{value['name']}] " + " · ".join(parts)
    if value.get("status") and value["status"] != "running":
        line += f" · {value['status']}"
    return line


def status(path: str) -> None:
    if not os.path.isdir(path):
        print(f"runlog.py: no such run directory: {path}", file=sys.stderr)
        sys.exit(2)
    results_path = os.path.join(path, "results.jsonl")
    results = _read_lines(results_path) if os.path.exists(results_path) else []
    errors = _read_lines(os.path.join(path, "errors.jsonl"))
    done = {str(r["id"]) for r in results if "id" in r}
    failing = {str(e["id"]) for e in errors if "id" in e} - done
    saved = {}
    progress_path = os.path.join(path, "progress.json")
    if os.path.exists(progress_path):
        with open(progress_path, encoding="utf-8") as f:
            saved = json.load(f)
    spent = sum(float(r.get("cost") or 0) for r in results + errors)
    value = {
        **saved,
        "name": saved.get("name") or os.path.basename(os.path.normpath(path)),
        "done": len(done) - int(saved.get("done_outside_scope") or 0),
        "failing": len(failing),
        "spent": spent,
        "cost_per_item": spent / len(done) if done else None,
    }
    if value.get("total") is not None and value["cost_per_item"] is not None:
        value["projected_cost"] = spent + value["cost_per_item"] * (value["total"] - value["done"])
    print(format_progress(value))
    if os.path.exists(results_path):
        print(f"last result saved {_duration(time.time() - os.path.getmtime(results_path))} ago")
    still_failing = [e for e in errors if str(e.get("id")) in failing]
    if still_failing:
        print(f"last error on an unfinished item: {still_failing[-1].get('error', '')[:300]}")


def load_items(path: str) -> list[dict]:
    extension = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8", newline="") as f:
        if extension == ".jsonl":
            return [json.loads(line) for line in f if line.strip()]
        if extension == ".json":
            return json.load(f)
        if extension == ".csv":
            return list(csv.DictReader(f))
    print(f"runlog.py: can't read {path}: use .jsonl, .json, or .csv", file=sys.stderr)
    sys.exit(2)


def sample(path: str, by: str, per_group: int, seed: int, extremes=(), include=(), id_field: str = "id") -> None:
    items = load_items(path)
    groups = defaultdict(list)
    for index, item in enumerate(items):
        groups[str(item.get(by))].append(index)
    rng = random.Random(seed)
    chosen = set()
    for key in sorted(groups):
        indexes = groups[key]
        chosen.update(indexes if len(indexes) <= per_group else rng.sample(indexes, per_group))
        print(f"{by}={key}: {min(len(indexes), per_group)} of {len(indexes)}", file=sys.stderr)
    drawn = len(chosen)
    for field in extremes:
        lengths = [(len(str(item.get(field) or "")), index) for index, item in enumerate(items)]
        chosen.update({min(lengths)[1], max(lengths)[1]})
    wanted = {value.strip() for value in include if value.strip()}
    found = set()
    for index, item in enumerate(items):
        if str(item.get(id_field)) in wanted:
            chosen.add(index)
            found.add(str(item.get(id_field)))
    if wanted - found:
        print(f"runlog.py: no item with {id_field} {', '.join(sorted(wanted - found))}", file=sys.stderr)
        sys.exit(2)
    if len(chosen) > drawn:
        print(f"added {len(chosen) - drawn} items from --extremes and --include", file=sys.stderr)
    for index in sorted(chosen):
        print(json.dumps(items[index], ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(prog="runlog.py", description="Report on run directories and draw samples.")
    commands = parser.add_subparsers(dest="command", required=True)
    s = commands.add_parser("status", help="print a run directory's progress")
    s.add_argument("run_dir")
    p = commands.add_parser("sample", help="print a stratified random sample as JSON Lines")
    p.add_argument("input")
    p.add_argument("--by", required=True, help="field to group by")
    p.add_argument("--per-group", type=int, required=True, help="items to draw from each group")
    p.add_argument("--seed", type=int, default=1, help="random seed (default 1)")
    p.add_argument("--extremes", action="append", default=[], metavar="FIELD",
                   help="also add the items with the longest and shortest value of FIELD; repeatable")
    p.add_argument("--include", default="", metavar="ID,ID", help="also add these items by ID")
    p.add_argument("--id-field", default="id", help="field that holds each item's ID, for --include (default id)")
    args = parser.parse_args()
    if args.command == "status":
        status(args.run_dir)
    else:
        if args.per_group < 1:
            parser.error("--per-group must be at least 1")
        sample(args.input, args.by, args.per_group, args.seed, args.extremes, args.include.split(","), args.id_field)


if __name__ == "__main__":
    main()
