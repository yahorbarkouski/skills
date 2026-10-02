# Run directory layout

A run directory holds one job run made with one set of settings. `scripts/runlog.py` writes this layout, and `runlog.py status` reads it. A job in any other language that writes the same files gets the same resume behavior and the same status command.

| File | Written | Contents |
|---|---|---|
| `config.json` | once, at the start | The settings that affect results, such as the model, the prompt version, and the parameters. A run started with different settings uses a new directory. |
| `results.jsonl` | one line per finished item, appended and flushed when the item finishes | `{"id": ..., "at": "<UTC ISO time>", "cost": <dollars>, ...result fields}`. Keep the raw response in a field next to anything parsed from it. |
| `errors.jsonl` | one line per failed attempt | `{"id": ..., "at": ..., "cost": ..., "error": "<message>"}`. An ID that later appears in `results.jsonl` no longer counts as failing. |
| `progress.json` | rewritten at each progress report, through a temporary file and a rename | `name`, `status` (`running`, `finished`, `finished: limit of N reached, M left`, or `stopped: <reason>`), `done` and `total` for the items this run was given, `failing`, `spent` for the whole directory, `cost_per_item`, `rate_per_second`, `seconds_left`, `projected_cost` (what is spent plus the cost of the items left), `done_outside_scope` (saved items that weren't in this run's input, such as a smoke test's), and `updated_at` |
| `job.log` | by the shell, when you start the job with its output redirected | the progress lines and anything else the job prints |
| `job.pid` | by the shell, when you start the job in the background | the process ID, for `kill $(cat job.pid)` |

On start, a job reads `results.jsonl`, skips every ID in it, and adds up `cost` to know what the directory has already spent. If the file doesn't end with a newline, the process that wrote it was killed partway through a line. Cut the file back to its last newline before appending.

## The same in Node

This is the minimum for a Node job, in plain JavaScript. Add types to use it in TypeScript. It appends and resumes, reports progress every 15 seconds, stops at a budget or after five failures in a row, and records why it stopped when it gets SIGTERM or Ctrl+C.

```js
import fs from "node:fs";
import path from "node:path";

export function openRun(dir, { config, total, maxCost, name = path.basename(dir) }) {
  fs.mkdirSync(dir, { recursive: true });
  const file = (n) => path.join(dir, n);
  const configText = JSON.stringify(config);
  if (fs.existsSync(file("config.json"))) {
    if (JSON.stringify(JSON.parse(fs.readFileSync(file("config.json"), "utf8"))) !== configText)
      throw new Error(`${dir} was started with a different config; use a new run directory`);
  } else fs.writeFileSync(file("config.json"), configText);

  const read = (n) => {
    if (!fs.existsSync(file(n))) return [];
    let text = fs.readFileSync(file(n), "utf8");
    if (text && !text.endsWith("\n")) {
      text = text.slice(0, text.lastIndexOf("\n") + 1);
      fs.truncateSync(file(n), Buffer.byteLength(text));
    }
    return text.split("\n").filter(Boolean).map((line) => JSON.parse(line));
  };
  const results = read("results.jsonl"), errors = read("errors.jsonl");
  const done = new Set(results.map((r) => String(r.id)));
  const failing = new Set(errors.map((e) => String(e.id)).filter((id) => !done.has(id)));
  let spent = [...results, ...errors].reduce((sum, r) => sum + (r.cost || 0), 0);
  let savedNow = 0, inARow = 0, status = "running";
  const started = Date.now();

  const report = () => {
    const rate = savedNow / Math.max((Date.now() - started) / 1000, 0.001);
    const progress = {
      name, status, done: done.size, total, failing: failing.size, spent,
      rate_per_second: rate,
      seconds_left: total && rate ? Math.round((total - done.size) / rate) : null,
      projected_cost: total && done.size ? (spent / done.size) * total : null,
      updated_at: new Date().toISOString(),
    };
    fs.writeFileSync(file("progress.json.tmp"), JSON.stringify(progress));
    fs.renameSync(file("progress.json.tmp"), file("progress.json"));
    console.error(`[${name}] ${done.size}/${total} · ${failing.size} failing · ${rate.toFixed(2)}/s · $${spent.toFixed(2)} spent · ${status}`);
  };
  const timer = setInterval(report, 15_000);
  for (const [signal, reason, code] of [["SIGTERM", "terminated", 143], ["SIGINT", "interrupted", 130]]) {
    process.once(signal, () => { status = `stopped: ${reason}`; clearInterval(timer); report(); process.exit(code); });
  }
  const stop = (reason) => { status = `stopped: ${reason}`; clearInterval(timer); report(); throw new Error(reason); };
  const checkBudget = () => { if (maxCost !== undefined && spent >= maxCost) stop(`budget of $${maxCost} reached`); };

  return {
    done: (id) => done.has(String(id)),
    save(id, record, cost = 0) {
      fs.appendFileSync(file("results.jsonl"), JSON.stringify({ ...record, id, at: new Date().toISOString(), cost }) + "\n");
      done.add(String(id)); failing.delete(String(id)); spent += cost; savedNow++; inARow = 0;
      checkBudget();
    },
    fail(id, error, cost = 0) {
      fs.appendFileSync(file("errors.jsonl"), JSON.stringify({ id, at: new Date().toISOString(), cost, error: String(error) }) + "\n");
      failing.add(String(id)); spent += cost;
      if (++inARow >= 5) stop(`${inARow} failures in a row; last: ${error}`);
      checkBudget();
    },
    finish() { if (status === "running") status = "finished"; clearInterval(timer); report(); },
  };
}
```

`appendFileSync` hands each line to the operating system before it returns, so a killed process loses at most the item in flight. In a job with many concurrent requests, this is still safe, because Node runs the callbacks one at a time and each call writes a whole line.
