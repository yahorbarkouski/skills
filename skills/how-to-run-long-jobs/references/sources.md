# Sources

This file is for whoever maintains the skill. Each entry names a rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

SKILL.md and the other references give each rule's reason in plain words. The evidence stays in this file.

Strength labels:
- **measured**: a peer-reviewed or well-documented study, or a test of this skill's own code
- **independent**: a report from someone other than the vendor, without a published method
- **vendor**: the vendor's own documentation
- **practice**: reasoned practice with no direct study

Sources were read on 2026-10-02.

## Why the skill exists

- **Writing results only at the end loses paid work.** Practice. The skill comes from a run in the maintainer's own work that generated an LLM profile per auction lot, wrote its output only after the loop, and was stopped after spending $0.23 with nothing saved. The fix saved each profile as it arrived and ran on 25 lots per category across all four categories first.

## Running small first

- **Same code at every size, a smoke test, a stratified sample, a check, and a projection before the full run.** Practice, and measured in the end-to-end test below. The $5 point at which the agent waits for the user's go-ahead is the maintainer's default, and a budget the user sets replaces it. The default cap of $5 for a job with no budget follows from it, so the cap and the go-ahead point never disagree.
- **A sample of 25 per category.** Practice, from the incident above. For estimating a proportion, 25 items give a 95% margin of about ±20 percentage points, which catches broken output and gross errors. It can't tell close variants apart, which is the job of the full run.
- **A score of 0% or 100% usually means a bug.** Practice.

## Saving as results arrive

- **A flushed line survives the process being killed.** Vendor and practice. Python's `flush()` writes the file object's buffer to the operating system, and data the operating system already holds survives the death of the process, which is standard operating-system behavior. A power loss can still lose it, which needs `os.fsync`. The skill accepts that risk because jobs are far more often stopped or crashed than cut off by power loss. https://docs.python.org/3/library/io.html#io.IOBase.flush
- **Rewrite the progress file through a temporary file and a rename.** Vendor. Python's `os.replace` documentation says a successful rename "will be an atomic operation (this is a POSIX requirement)", so a reader never sees a half-written progress file. https://docs.python.org/3/library/os.html#os.replace
- **Save raw responses, save failures as records, and build reports in a separate step.** Practice.
- **Save a batch job's ID the moment it's accepted.** Vendor, in part. Anthropic's Message Batches API returns a batch ID that is used to poll for status and fetch results, and a batch can run for up to 24 hours, so a process that loses the ID can't reattach. https://platform.claude.com/docs/en/build-with-claude/batch-processing

## Resuming and retrying

- **Retry timeouts, rate limits, and server errors with growing waits.** Vendor. Anthropic's errors page says to retry a 500 "with exponential backoff", and its SDKs retry connection errors, rate limits, and 5xx errors twice by default (https://platform.claude.com/docs/en/api/errors). The OpenAI cookbook recommends retrying "with a random exponential backoff" (https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits).
- **Skip saved IDs on start, and keep each set of settings in its own directory.** Practice. Versions are raised by hand because hashing the job's own source file invalidates the run directory on harmless edits, which the end-to-end test agent pointed out.
- **Record an item as failed once, after its retries.** Practice. With one failure recorded per attempt, a single flaky item used three of the five failures that stop a run in the end-to-end test.
- **Record an estimated cost for failed calls.** Practice. A timed-out call returns no usage, and the provider may still have processed it.

## Progress

- **Plain progress lines at an interval, readable from outside the process.** Practice. A redrawn progress bar writes carriage returns that a log file keeps as one long line.
- **Compute spend from the usage each response returns.** Vendor. The Anthropic and OpenAI APIs return token counts with every response and price per million tokens (https://platform.claude.com/docs/en/about-claude/pricing, https://developers.openai.com/api/docs/pricing).

## Stopping by itself

- **Stop after five failures in a row.** Practice. Anthropic's errors page notes that a 429 caused by reaching a tier's spend cap "keeps failing until access resumes", a case where retrying forever only adds failures (https://platform.claude.com/docs/en/api/errors).
- **A spending cap per paid job.** Practice.
- **Stop a background job with SIGTERM.** Practice, and measured. A job started with `&` from a non-interactive shell ignores SIGINT, so Ctrl+C sent with `kill -INT` does nothing unless the job restores the handler, which the end-to-end test agent found and `runlog.py` now does. SIGTERM is what `kill PID` sends.

## The helpers

- **`scripts/runlog.py`.** Measured, on this skill's own tests on 2026-10-02:
  - A 20-item run with `--limit` resumed into a full 200-item run.
  - A run killed with SIGKILL kept its 115 saved results.
  - A partial last line was cut off on restart, and the finished file held 200 lines with 200 unique IDs.
  - A $0.005 budget stopped the run after 5 items.
  - A job whose every call failed stopped after 5 calls.
  - A changed config was refused.
  - 16 threads saving 2,000 results produced 2,000 parseable lines.
  - Ctrl+C recorded `stopped: interrupted` in `progress.json`.
  - `sample` drew 25 per group, or all of a group smaller than 25.
  - After the end-to-end test's findings: a background job stopped with `kill` exited with status 143 and recorded `stopped: terminated`, and one stopped with `kill -INT` exited with 130 and recorded `stopped: interrupted`; both resumed to 200 unique results. A `--limit 3` run ended as `finished: limit of 3 reached, 197 left`. A 20-item sample file run in a directory that already held 3 other items reported 20/20, in the job and in `status`. `status` no longer shows errors for items that later succeeded. `sample --extremes --include` added the expected items and refused an unknown ID.
- **The Node version in `layout.md`.** Measured. Killed with SIGKILL and restarted after a partial line was appended, it finished with 300 lines and 300 unique IDs. The budget and failure stops worked, SIGTERM and Ctrl+C sent to it in the background recorded their reasons and exited with 143 and 130, and `runlog.py status` read its run directory.

## End-to-end test

- On 2026-10-02, a fresh Sonnet agent in Claude Code got this skill and a task: generate a profile for each of 2,000 auction lots with a stand-in for a paid LLM API that charged by token, took about 50 ms per call, and timed out on 2% of calls, with no budget set. It ran 3 lots, then a sample of 25 per category plus the longest and shortest lot, and checked them. It projected $4.61 for the job, below the $5 point, and started the full run in the background with a $6 cap. It stopped the run with Ctrl+C at 628 saved, restarted it, and finished with 2,000 profiles for $4.62, paying for no lot twice. Its report led to the cost computed from usage in the code example, the rules on retries, failed-call cost, versions, the cap, and stopping a background job, and the helper's signal handling, scoped progress, limit status, and sample options.

## Open questions

- No study gives a sample size that reliably catches a broken pipeline before a full run. The skill's numbers are practice.
- The $5 default for waiting on the user has not been tuned against how often users want to be asked.
