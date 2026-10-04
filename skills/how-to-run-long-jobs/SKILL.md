---
name: how-to-run-long-jobs
description: Run a long or costly job so that it runs on a small sample first, saves each result the moment it arrives, shows its progress at any time, resumes without losing or repaying work, and stops itself when it breaks or reaches its budget. Use when you write, launch, or fix a script or command that loops over many items, calls a paid API more than a few times, or may run longer than about a minute, such as LLM or API calls over a dataset, benchmarks and evaluations, scrapes, embeddings, backfills, and migrations. Skip it for builds, test suites, package installs, and servers.
---

# How to run long jobs

An agent writes a script that generates an LLM profile for every lot in four auction categories. The script collects the profiles in a list and writes them to a file after the loop. Partway through, the user stops it to change the prompt. The calls so far cost $0.23, nothing was saved, and while it ran nobody could say how many lots were done. Written the way this skill asks, the script appends each profile to `results.jsonl` the moment it arrives and prints a progress line with the count, the spend, and the time left. It first runs on 25 lots from each category, 100 in all, and the full run starts after those 100 profiles look right. Stopping it then loses at most the profile in flight, and running it again skips every lot already saved.

Every long or costly job follows four rules:
1. It runs on a small sample before it runs on everything.
2. It saves each result as soon as it has it. Work that cost money never exists only in memory.
3. It shows how far it has got, at any moment, to anyone who looks.
4. It can stop and resume without losing work or paying for it twice, and it stops itself when it breaks or reaches its budget.

Scale the effort to the job. A two-minute local loop needs results appended as they arrive and a progress line. A paid run over thousands of items needs every section. A job that breaks one of these rules has a bug. Fix it when you see it, in your own code or in code you are asked to run.

## 1. Run it small first

1. **Use the same code at every size.** Give the script a `--limit N` option or a sample file as input, so the small run exercises exactly the code the full run will use. A separate test script proves only that the test script works.
2. **Smoke-test on one to three items.** Run the whole pipeline end to end: the calls, the saved results, and every step that reads them afterwards, such as scoring, aggregation, or the report. Read the results file back. Many bugs sit in the last step, and a job that writes only at the end hides them until everything has been paid for.
3. **Run a sample that covers every kind of item.** Draw it at random with a fixed seed from every category or segment, such as 25 items per category, and add the hardest cases you know: the longest input, an empty field, another language. This command draws 25 items per category, adds the items with the longest and shortest description, and adds two items you picked by ID:

   ```bash
   python3 <this skill's directory>/scripts/runlog.py sample items.jsonl --by category --per-group 25 --seed 1 --extremes description --include L-0042,L-1913 --id-field lot_id > sample.jsonl
   ```
4. **Check the sample before going on.** Read a handful of results. Check the error rate, and check that the numbers are plausible: a benchmark score of 0% or 100%, or every item getting the same answer, usually means a bug in the job or the scorer. Measure the cost and the time per item.
5. **Project the full run, and tell the user.** Multiply the measured cost and time per item by the number of items left, add what the small runs already spent, and tell the user the projected total cost and the time before the full run starts. If the user set a budget, stay inside it. If not, wait for their go-ahead before any job whose projected total is more than $5. For a very large job, run about a tenth of it as a middle step and check it the same way.
6. **Then run everything.** If nothing that affects the results has changed since the sample, the full run picks up the sample's results and continues (section 3). If the prompt, the model, the parameters, or the code that produces results changed, use a new run directory and run a new sample.

## 2. Save every result as it arrives

- Write each result to durable storage the moment it completes: append one line to a JSON Lines file and flush it, or insert and commit one database row. Never collect results in a list, a dictionary, or a dataframe to write after the loop. A stopped or crashed run may lose the item in flight and nothing more.
- Save the raw response next to anything you parse from it. A parsing bug can then be fixed and the parsing rerun from the saved responses, with no new calls.
- Save failures as records too, with the item's ID and the error, so they are counted, visible, and retried on the next run. A failed call that returned no usage may still be billed, so record an estimate from the input you sent, and the spend never reads low.
- When work runs in threads or async tasks, send every write through one lock or one writer, or give each worker its own file, so that lines never interleave.
- When work finishes in units bigger than one item, save the smallest unit you can. Commit a database backfill every few hundred rows, together with the last ID it processed. Save a batch API's job ID the moment the job is accepted, so a restarted process fetches the results and never submits and pays a second time.
- Build summaries, tables, and reports in a separate step that reads the saved results. That step can run at any time, including halfway through a run.

## 3. Make it resumable

- Give every item a stable ID. On start, read the saved results and skip every ID already there. A stopped run then continues where it stopped, and rerunning a finished run does nothing.
- Retry failed items on the next run. Within a run, retry timeouts, rate limits, and server errors a few times with growing waits. Official API SDKs already retry these errors, the Anthropic SDK twice by default. Record an item as failed once, after its retries are used up.
- Keep each run in its own directory, and save in it the settings that affect results: the model, the parameters, a prompt version, and a code version. Raise the prompt or code version yourself whenever you change something that changes results, and leave it alone for changes that don't, such as logging. A change to any setting means a new directory, so results made with different settings never mix.

## 4. Show progress at all times

- Count the total before starting, so progress is a fraction of a known number. A job whose total can't be known in advance, such as a crawl, reports the count done and the rate.
- Print one plain line at a fixed interval, such as every 15 seconds, and when the job ends. It gives items done out of the total, failures, the rate, the time left, and the money spent with the projected total:

  ```text
  [profiles-v2] 340/1200 (28%) · 3 failing · 1.90/s · ~7m32s left · $0.41 spent, ~$1.45 projected
  ```

  Use plain lines because they stay readable in a log file and to an agent. A progress bar that redraws one line with carriage returns turns into noise in a log.
- Compute spend from the token usage the API returns with each response, multiplied by the model's price per token from the provider's pricing page.
- Make progress readable from outside the process. The results file's line count is the number done, and a small progress file, rewritten at each interval, holds the total, the counts, the spend, and whether the job is running, finished, or stopped and why.
- A job with several stages reports which stage it is in and the progress within that stage.

`python3 <this skill's directory>/scripts/runlog.py status RUN_DIR` prints the progress of any run directory in this layout. It also says how long ago the last result was saved, which tells a live run from a dead one.

## 5. Stop by itself when it breaks or reaches its budget

- Stop after five failures in a row, or fewer when each call is expensive. A job whose every call fails should cost five calls.
- Give every paid job a spending cap, such as a `--max-cost` option, and stop when the spend reaches it. Set the cap to the budget the user gave or approved. With no budget, set it to $5, the most a job may spend without the user's go-ahead. The cap covers the whole run directory, including the small runs.
- When a job stops, record why in the log and in the progress file.

## 6. Launch and watch it from an agent

- Start any job that may run longer than about a minute in the background, with its output going to a log file in the run directory, and save its process ID. Then keep working, or check on it at intervals. A job running in the foreground blocks you, and its output stays unreadable until it ends.

  ```bash
  python3 job.py items.jsonl --run-dir runs/profiles-v2 > runs/profiles-v2/job.log 2>&1 &
  echo $! > runs/profiles-v2/job.pid
  ```
- When the user asks how a job is going, read its progress with the status command or the end of its log, and report the numbers.
- Stop a job with `kill $(cat RUN_DIR/job.pid)`, which sends SIGTERM. A job using the helper records `stopped: terminated` and exits, and saved results are safe even if it doesn't. Use `kill -9` only when the job ignores SIGTERM. Then report how many items are saved and that running it again continues from there.

## 7. The runlog helper

`scripts/runlog.py` handles saving, resuming, progress, and stopping for Python jobs, with no dependencies. Retries stay in your code or the API's SDK. Copy it next to the job script, or put this skill's `scripts` directory on `PYTHONPATH`:

```python
from runlog import Run, RunStopped

with Run("runs/profiles-v2", config={"model": MODEL, "prompt": PROMPT_VERSION}, max_cost=args.max_cost) as run:
    for lot in run.todo(lots, id_of=lambda lot: lot["lot_id"], limit=args.limit):
        try:
            response = client.messages.create(model=MODEL, max_tokens=500, messages=build_messages(lot))
        except Exception as error:
            run.fail(lot["lot_id"], error)
            continue
        usage = response.usage
        cost = usage.input_tokens * INPUT_PRICE + usage.output_tokens * OUTPUT_PRICE
        run.save(lot["lot_id"], {"profile": response.content[0].text, "raw": response.model_dump()}, cost=cost)
```

`client` is an `anthropic.Anthropic()` client, `build_messages` builds the prompt for one lot, and `INPUT_PRICE` and `OUTPUT_PRICE` are the model's dollars per token. `Run` refuses to reuse a directory started with a different `config`. `todo()` skips the items already saved, and progress counts the items passed to it, so a run over a sample file reports the sample's size. With `limit`, the run ends as `finished: limit of 3 reached, 1997 left`, and the projected cost covers all the items. `save()` and `fail()` append and flush one line each and are safe to call from several threads. Every 15 seconds and at the end, `Run` prints the progress line, with the cost per item, and rewrites `progress.json`. It raises `RunStopped` after five failures in a row or when the directory's total spend reaches `max_cost`. Inside the `with` block, SIGTERM and Ctrl+C stop the run cleanly and record why, even for a job started in the background. For a job in another language, follow the same files, described in [references/layout.md](references/layout.md), and the status command works on it too.

Worked examples are in [references/examples.md](references/examples.md). Before changing this skill, check the basis for each rule in [references/sources.md](references/sources.md).
