---
name: how-to-run-llm-work
description: Decide where LLM work runs, on the coding harness's own subagents or as an API call in code, and run harness work as a wide parallel fan-out. Use whenever a task needs model judgment over material you have now, such as judging which of several solutions is better, reviewing, categorizing or labeling records, extracting fields or structure from documents, summarizing sources, or drafting labels for a person to check, and before writing a script that imports an LLM SDK (Anthropic, OpenAI, Gemini, OpenRouter, LiteLLM) or asking the user for an API key. Covers telling one-off work from calls the product needs, why harness subagents cost less, choosing between inline work, one subagent, a fan-out, and a panel of judges, sharding items so that many subagents run at once, writing one brief for every shard, and merging and checking the results in code. Works in Claude Code, Codex, Cursor, and any harness that can start subagents.
---

# How to run LLM work

An agent asked to sort 1,000 support tickets from a CSV export into five categories writes `label_tickets.py`. The script loops over the rows and calls the Anthropic API once per ticket. To run it, the developer has to find an API key, the project gains an SDK dependency, every token is billed at API prices, and the repository keeps a script that will never run again. The harness the agent runs in can do the same work. The agent splits the tickets into 20 files of 50 and starts 20 subagents in one message. Each subagent writes its labels to its own file, and a few lines of code merge the files and check them. The subagents run on the harness subscription the developer already pays for, and the labeled tickets are all that is left behind.

LLM work that only the current task needs runs on the harness's own subagents, as many at once as the harness allows. LLM work becomes an API call in code when it has to run where no agent session is running: in the product, for its users, on a schedule, or in CI.

## 1. Decide where the work runs

Ask one question: after this task ends, will this LLM call have to run again with no agent session to run it?

If not, run it on the harness. That covers any result you need during the task, as data or as a decision:
- judging which of several implementations or designs is better
- reviewing code, a document, or a plan
- categorizing, labeling, or scoring a batch of records
- extracting fields or structure from documents, web pages, or transcripts
- summarizing, comparing, or deduplicating sources
- drafting labels for a person to review, such as the labeled examples an evaluation needs

Write an API call in code when one of these holds:
- The product calls the model at runtime, for example in a feature its users trigger.
- A scheduled job, a data pipeline, or CI calls the model with no agent session behind it.
- You are measuring how well a prompt the product runs performs, by running it on test inputs and scoring the outputs. Those outputs have to come from the product's model, settings, and prompt, and a subagent runs on the harness's model, with the harness's own system prompt and tools. Subagents can still do the one-off parts, such as drafting the test set's correct answers for a person to review.
- The volume would exhaust the plan's usage limits (step 4 in section 3).
- The user asks for a script that calls the API.

A result that has to last is still harness work, because the result is what lasts and the call never has to run again. If 2,000 products each need a category stored in the database, subagents produce the categories, and code loads the file into the database. Work a developer repeats by hand, such as a monthly relabeling, stays on the harness too. Save its brief and steps in the repository, for example as a skill or a markdown note, so the next session can repeat it.

The reasons:
- **Cost.** A harness on a subscription, such as Claude Code on a Claude plan, Codex on a ChatGPT plan, or Cursor on a paid plan, charges a flat fee with usage limits, so subagent tokens cost nothing extra until a limit is reached. An API bills every token. When the harness itself bills per token through an API key, subagents cost about as much as direct calls, plus the harness's system prompt and tool definitions, which every subagent reads before its first item. The next two reasons still hold.
- **Tools.** A subagent can open files, run code, search, and check its own answer. An API call sees the text the script sends and nothing else.
- **Nothing to maintain.** Harness work needs no API key, no SDK, and no code that outlives the task.

When the call does belong in the product, the how-to-route-judgment skill, if you have it, decides whether an LLM should make that judgment at all.

## 2. Choose the smallest setup that does the job

- **Inline.** A few short items, such as 20 commit messages to categorize: do it yourself in the current context. Starting a subagent costs more than the work.
- **One subagent.** One large piece of work that benefits from a fresh context, such as reviewing a long design document against its spec.
- **A fan-out.** Many items, or many independent parts of one job: split the work and run subagents in parallel (section 3).
- **A panel.** A judgment that one model's verdict can't settle reliably, such as choosing between solutions: several independent subagents judge the same candidates (section 4).

Move bulk work out of the main context even when it would fit. The rest of the task runs on that context, and a thousand labeled rows in it crowd out everything else.

## 3. Fan out wide

1. **Give every item a stable ID, and split the items into shards.** Each subagent handles one shard, so the number of shards sets how much runs in parallel. Aim for as many shards as the harness runs at once, while keeping at least about 20 short records, or one long document, in each. Below that, the fixed cost of starting a subagent outweighs the time saved, because every subagent reads the harness's system prompt and tools first. When the items fill more shards than the harness runs at once, grow the shards up to about 50 short records or 5 long documents, and only then add waves. Use smaller shards when each item needs careful judgment, since models use material in the middle of a long input worse than material at its start and end, and accuracy drops as more items share one prompt. A comparison between candidates gets a shard of its own.
2. **Write one brief, and use it unchanged for every shard.** Only the input path and the output path differ between shards. The brief is all the subagent sees, so it carries the goal and why it matters, what the items are and where they came from, every allowed answer with its definition, what to do with an unclear item (give it an explicit `unsure` value), the exact output fields, and the output path. Ask each subagent to write its results to its own file and to reply in a sentence or two: how many items it wrote and anything odd it noticed, with no per-item results. Everything a subagent replies is added to your own context, where it takes up room the rest of the task needs. A template is in [references/fanout.md](references/fanout.md), and the how-to-prompt skill covers briefs in depth.
3. **Choose the model.** Use the cheapest model that does the job reliably: a small one for clear-cut labeling or extraction, a strong one for judging quality or drawing subtle lines.
4. **Run a pilot shard, and check the volume.** Unless the whole fan-out is cheap to redo, as with three or fewer shards, run one shard alone first, read its output, and fix the brief before the other shards repeat its mistakes. A pilot catches the brief's commonest mistakes, and the checks in step 6 catch the rest. Then estimate the total as the number of shards times the tokens the pilot used. Most harnesses report a finished subagent's token count. If yours doesn't, count about four characters of input per token, which gives a lower bound. Subagent tokens count against the plan's usage limits, so if the total runs into millions of tokens, tell the user before starting the rest, since they know how much of their limit is left. If a one-off analysis has more items than the plan can cover, check whether a random sample of a few thousand answers the question. If every item is needed, propose a script on a batch API, which costs half the normal price and returns within a day, and give the user its cost before running it.
5. **Start every remaining subagent in one message.** Subagent calls sent in one message run at the same time, and calls sent one per message run one after another. If there are more shards than the harness runs at once, start them in waves of that size. Run them in the background when you have other work for the meantime. How each harness starts subagents, and how many it runs at once, is in [references/fanout.md](references/fanout.md).
6. **Merge and check in code.** Confirm that every input ID appears exactly once, that every answer is one of the allowed values, and that every line parses. Rerun the shards with missing or invalid items, using the same brief. Then look at how the answers are distributed, and read 10 to 20 items yourself, spread across the answers. One answer covering nine items in ten, an allowed answer nobody chose, or the same input getting different answers in different shards, usually means the brief drew a line in the wrong place. Fix the brief and rerun every shard with it, so that one brief judged every item. Last, decide the `unsure` items yourself, or send them to one more subagent on a stronger model, because the final result usually has no `unsure` value.
7. **Save the merged result with a note of how it was made.** Write it to a file the user or code can use, and record the brief, the model, and the date in a note file next to it. A rerun gives different answers on borderline items, so later steps read the saved file and never judge the same items again.

`scripts/fanout.py` does the splitting and the checking. Put the shard directory in a scratch directory outside the repository, written `$SCRATCH` below, or in one the repository ignores:

```bash
python3 <this skill's directory>/scripts/fanout.py split tickets.csv --out "$SCRATCH/tickets" --per-shard 50 --id-field ticket_id
# one subagent per input-NNN.jsonl, each writing output-NNN.jsonl beside it
python3 <this skill's directory>/scripts/fanout.py merge "$SCRATCH/tickets" --field category=billing,bug,account,feature,other,unsure --out tickets.labeled.jsonl --keep category
```

Repeat `--field` once for each answer field. `merge` lists missing, duplicate, unknown, and invalid IDs, names the shards to rerun, prints the distribution of each field's answers, and exits with status 1 until every item has merged cleanly. `--keep` limits the written file to the ID and the named fields.

## 4. Judge with a panel

When subagents choose between solutions, designs, or outputs:
- Check everything code can check first, such as tests, type checks, benchmarks, and lint. The judges decide what is left.
- Write the criteria before anyone looks at the candidates, and give every judge the same criteria. Say what "better" means for this task, such as "handles every failing input in the bug report" or "a new contributor could follow it".
- Use three to five judges, each in a fresh subagent, and take the majority. If they tie, add a judge. One model's verdict can flip on a rerun, and the majority of a panel moves less.
- Hide where each candidate came from. Remove author, model, and branch names, and label the candidates A, B, and C. Models favor output they recognize as their own.
- Compare two candidates at a time. Show half the judges A first and the other half B first, because models favor the answer shown first, and the longer answer. If every judge picks whichever candidate it saw first, count the pair as a tie. With more than four candidates, have each judge rank all of them, shuffle the order for every judge, and add up the ranks.
- Ask each judge for its reasons before its verdict, quoting the code or text that decided it.

## 5. Traps

- A one-off script that imports an LLM SDK.
- Asking the user for an API key for work that subagents could do.
- Independent subagents started one after another.
- One subagent for each short item.
- Subagents sending their full results back as text.
- Two subagents writing to the same file.
- A subagent standing in for the product's model when measuring the product's prompt.
- Merged results used without checking IDs and values.
- One judge choosing between solutions.

Worked examples, including cases where an API call is the right answer, are in [references/examples.md](references/examples.md). Before changing this skill, check the evidence for each rule in [references/sources.md](references/sources.md).
