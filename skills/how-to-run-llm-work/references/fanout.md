# Fan-out reference

This file has the brief template, how each harness starts subagents, and what `scripts/fanout.py` reads and writes.

## Brief template

Every shard gets the same brief, with only the two paths changed. This one labels support tickets. Replace the goal, the item description, the answers, and the fields for your task, and keep the parts that every brief needs: the goal and its reason, a description of the input, a definition for every allowed answer, a value for unclear items, exact output fields with the reasoning before the answer, the output path, and the short reply.

```text
You are labeling customer support tickets for a one-time report on what
customers contacted support about in July to September 2026. The report
decides which product areas get more engineering time next quarter, so
label what each customer needed, whatever words they used.

Input: {input_path}. It is a JSON Lines file with one ticket per line. Each
line has "ticket_id", a unique ID, and "body", the customer's first message
exactly as they wrote it.

Give each ticket one category:
- billing: charges, refunds, invoices, or payment methods
- bug: something in the product fails or behaves unexpectedly
- account: signing in, passwords, profile settings, or closing the account
- feature: asks for something the product doesn't do
- other: anything else
- unsure: fits two categories equally well, or is too short to tell

Write {output_path} as JSON Lines, one line per input ticket, in input
order, with exactly these fields:
- "ticket_id": copied from the input
- "reason": one sentence on what the customer needs
- "category": one of the six values above
Write a line for every ticket, including the unsure ones. Write no other
files.

When you finish, reply in a sentence or two: how many tickets you wrote,
and anything unusual, such as tickets in a language you couldn't read.
Leave the labels and any counts per category out of the reply.
```

For a panel, the brief carries the criteria, the candidates labeled A and B, and the order you chose for that judge. It asks for reasons that quote the code or text before the verdict, and for a verdict of A, B, or tie.

## How each harness starts subagents

Checked against each vendor's documentation in October 2026. Limits change, so check the current documentation when a number matters.

- **Claude Code.** The `Agent` tool starts a subagent, which was called the Task tool before version 2.1.63. Several `Agent` calls in one message run concurrently. Each subagent starts with a fresh context window, and a `model` parameter picks its model, such as `haiku` for simple labeling. Subagents can run in the background, and a subagent can start subagents of its own, up to three levels deep by default. By default a session runs at most 20 subagents at once, and a call beyond that fails with `Concurrent subagent limit reached`. The `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` environment variable changes the limit. The `Workflow` tool runs larger orchestrations, up to 16 agents at once by default, but only when the user has asked for multi-agent orchestration.
- **Codex** (CLI, IDE extension, and app). Subagents start through the `spawn_agent` tool, and `wait_agent` waits for them to finish. Codex starts subagents when the user asks directly or when a project or skill instruction applies, so this skill's instructions count. The `agents.max_concurrent_threads_per_session` setting caps how many run at once, and when it is unset Codex picks the cap itself. A subagent's model comes from its agent file, the `agents.default_subagent_model` setting, or the request.
- **Cursor.** The agent starts subagents with `Task` tool calls, and several calls in one message run at the same time. Each subagent has its own context window, a `model` field picks its model within the plan's limits, and `is_background` runs it in the background. A subagent can start subagents of its own, and those can't start any more. The documentation states no cap on how many run at once.
- **Other harnesses.** Look for a tool that starts another agent with its own context. If the harness has none, do the work inline in batches, and write each batch's results to a file as you go.

## fanout.py

`split` reads a CSV, JSON Lines, or JSON file, a plain text file with one item per line, or a directory with one item per file. For a directory, each item holds the file's path, and the subagents open the files themselves. Items keep their ID field, `id` by default or the one named with `--id-field`, and items without one get their position as the ID. It writes `input-001.jsonl`, `input-002.jsonl`, and so on, plus `manifest.json`, which records which IDs went into which shard. A shard closes at `--per-shard` items, 50 by default, or at `--max-chars` characters, 60,000 by default, whichever comes first. `--shards N` splits into N equal shards, which suits a harness that runs N subagents at once. It refuses a directory that already holds shard files.

Each subagent writes `output-NNN.jsonl` next to its input, with one JSON object per item and the item's ID under the same field name.

`merge` checks every output file against the manifest. Name each answer field with `--field`, as `--field topic=performance,pricing,other` to give its allowed values or `--field reason` to require the field alone, and repeat it for every field. It reports IDs that are missing, duplicated, or unknown, answers outside the allowed values, and lines that don't parse. It names the shards to rerun and prints how often each answer occurs, including allowed answers nobody chose. With `--out` it writes the valid records in input order. `--keep topic,sentiment` writes only the ID and those fields, which drops the subagents' `reason` field from a deliverable, and `--with-input` adds each input item's fields to its record. It exits with status 0 when every item merged cleanly, 1 when anything needs a rerun, and 2 on a usage error. After rerunning a shard, overwrite its output file and run `merge` again.
