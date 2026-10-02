# Examples

Each example shows how one kind of job runs small first, saves as it goes, and reports progress. Copy the reasoning. The numbers are illustrations.

## Profiles for auction lots: append, sample, then run

The first version of the script:

```python
profiles = []
for lot in lots:
    profiles.append(generate_profile(lot))
with open("profiles.json", "w") as f:
    json.dump(profiles, f)
```

Every profile lives in `profiles` until the loop ends. Stopping the script, a crash on lot 900, or a typo in the last two lines loses every call made so far, and nothing tells anyone how far it has got.

The rewritten script:

```python
import argparse, json
import anthropic
from runlog import Run, RunStopped

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
INPUT_PRICE = 3 / 1_000_000    # dollars per input token: set from the provider's pricing page
OUTPUT_PRICE = 15 / 1_000_000  # dollars per output token

parser = argparse.ArgumentParser()
parser.add_argument("items")
parser.add_argument("--run-dir", required=True)
parser.add_argument("--limit", type=int)
parser.add_argument("--max-cost", type=float, default=5.0)
args = parser.parse_args()

lots = [json.loads(line) for line in open(args.items)]
config = {"model": MODEL, "prompt_version": 4}
try:
    with Run(args.run_dir, config=config, max_cost=args.max_cost) as run:
        for lot in run.todo(lots, id_of=lambda lot: lot["lot_id"], limit=args.limit):
            try:
                response = client.messages.create(model=MODEL, max_tokens=500, messages=build_messages(lot))
            except Exception as error:
                run.fail(lot["lot_id"], error)
                continue
            usage = response.usage
            cost = usage.input_tokens * INPUT_PRICE + usage.output_tokens * OUTPUT_PRICE
            run.save(lot["lot_id"], {"profile": response.content[0].text, "raw": response.model_dump()}, cost=cost)
except RunStopped as reason:
    print(f"stopped: {reason}")
```

`build_messages` builds the prompt for one lot. The Anthropic client retries rate limits and server errors by itself, so an item reaches `run.fail` only after those retries. The agent runs the script on 3 lots, reads `results.jsonl`, and runs the step that builds the catalog from it. Then it draws 25 lots per category, plus the lots with the longest and shortest description, and runs the same script on those 102:

```bash
python3 runlog.py sample lots.jsonl --by category --per-group 25 --seed 1 --extremes description > sample.jsonl
python3 profiles.py sample.jsonl --run-dir runs/profiles-v4
```

The 105 lots so far cost $0.20, about $0.0019 per lot, so all 4,000 lots will cost about $7.60 in total and take about 50 minutes. The agent shows the user six profiles, two from the weakest category, and the projection. The projected total is over $5, so it waits for the user's go-ahead. The user approves $8, and the agent starts the full run in the background with the same run directory and `--max-cost 8`. The run skips the lots already saved and continues:

```bash
python3 profiles.py lots.jsonl --run-dir runs/profiles-v4 --max-cost 8 > runs/profiles-v4/job.log 2>&1 &
echo $! > runs/profiles-v4/job.pid
```

## A benchmark of two prompts: the smoke test catches the scorer

A team compares two prompts on 2,000 questions with known answers. A smoke test on three questions scores both prompts at 100%. Reading the three saved results shows that the scorer compared each answer with itself. After the fix, a sample of 40 questions per difficulty level gives plausible scores, and the agent projects the cost of the full run for both prompts. Each prompt gets its own run directory, because the prompt is a setting that affects results. The scorer reads the saved results, so it reruns over every saved answer without a single new call.

## A scrape of 30,000 product pages: stop when blocked

The site's sitemap lists 30,000 product URLs, which gives the total. The scraper saves each page's raw HTML under a file named after a hash of its URL, and appends one line per page to `results.jsonl` with the URL, the status, and the file name. Parsing runs as a separate step over the saved HTML. The first run fetches 20 pages from each of the site's five sections. When the site starts answering with 429 and then 403, the scraper stops after five failures in a row, at a cost of five requests, and rerunning it after a pause continues from the last saved page.

## A backfill of 4 million rows: commit in batches with a checkpoint

A migration fills a new column from an old one. The script works in batches of 1,000 rows ordered by ID. It commits each batch together with a checkpoint row that records the last ID processed, and it prints the rows done, the rate, and the time left every 15 seconds. The first run processes 1,000 rows on a copy of the table, and the agent checks those rows by hand. A restarted run reads the checkpoint and continues from the next ID.

## A batch API job: save the handle first

A job submits 20,000 requests to a batch API at half price. The moment the API accepts the batch, the script writes the batch ID to `batch.json` in the run directory. A separate command polls the batch's status and prints the counts the API reports, such as how many requests have succeeded, failed, or are still processing. When the batch ends, it downloads the results into `results.jsonl`. If the process dies at any point, the next run reads `batch.json` and reattaches, so the batch is never submitted and paid for twice. Before the 20,000-request batch, a batch of 50 requests checks the request format and the parsing of the results.

## A two-minute local script: the light version

A script resizes 600 images on the developer's machine. It is free and short, so it needs only the light version of the rules. It writes each resized image as soon as it's done, skips images whose output already exists, and prints a line every 100 images with the count and the time left.
