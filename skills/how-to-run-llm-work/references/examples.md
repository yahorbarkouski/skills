# Examples

Each example names where the LLM work runs and why. Copy the reasoning. The domains and numbers are illustrations.

## Labeling 1,000 support tickets: fan out

A product manager exports 1,000 tickets to `tickets.csv` and wants each one tagged as billing, bug, account, feature request, or other, to see what customers complain about this quarter.

**This is harness work.** The labels are needed once, for one analysis, and nothing in the product will ask the question again.

```bash
python3 <this skill's directory>/scripts/fanout.py split tickets.csv --out "$SCRATCH/tickets" --per-shard 50 --id-field ticket_id
```

That writes 20 shards. The agent writes one brief and runs shard 001 alone on a small model as a pilot. Its labels look right, so the agent starts the other 19 subagents in one message, and each writes its own `output-NNN.jsonl`. The merge reports that shard 017 skipped two tickets and gave a third the category `refund`, which isn't on the list. The agent reruns shard 017 with the same brief, merges again, and the run is clean. The distribution shows 41% `other`, so the agent reads 15 of those tickets. Most are about shipping delays, which none of the categories covers. The agent tells the product manager and offers to add a `shipping` category and rerun all 20 shards with the revised brief, so that one brief labeled every ticket.

## Choosing between three fixes: code first, then a panel

Three subagents each wrote a fix for a race condition in a job scheduler, on three branches.

**This is harness work, as a panel.** The choice is made once.

The agent runs the test suite and the reproduction script from the bug report on each branch. Branch B fails the reproduction, so it is out. For A and C, the agent writes the criteria: the fix holds under the reproduction run 200 times, it changes no public API, and a reviewer can see why it is correct. It strips the branch names, calls the candidates X and Y, and starts four judges in one message, two with X shown first and two with Y shown first. Each judge reasons first and then gives a verdict. Three of four prefer X, and their reasons cite the same lock ordering. The agent reports the choice with those reasons.

## Pulling terms out of 40 vendor contracts: fan out over files

Legal wants a table of renewal date, notice period, liability cap, and governing law for 40 PDF contracts in `contracts/`.

**This is harness work.** The table is needed once.

```bash
python3 <this skill's directory>/scripts/fanout.py split contracts/ --out "$SCRATCH/contracts" --per-shard 2
```

Each item is a file path, and the subagents open the PDFs themselves. Contracts are long and the terms are easy to misread, so the agent uses a strong model and two contracts per shard. The brief asks for each field with the page it came from, and `not stated` when the contract has no such clause. The agent checks five contracts against their sources before handing over the table.

## Summarizing each new ticket for support staff: API call in code

The support tool should show a two-line summary at the top of every new ticket.

**This belongs in the product.** It runs for every ticket, around the clock, with no agent session. Write it as an API call in the ticket service, and first use the how-to-route-judgment skill to check whether each part of it needs an LLM.

## Measuring a change to the product's classifier prompt: API call

The product classifies incoming emails with a prompt on a specific model, and a developer wants to know whether a new wording is more accurate.

**This needs the API.** The measurement is about the product's call: its model, settings, and prompt. A subagent would run on the harness's model, with the harness's system prompt, and its accuracy would say nothing about production. The agent can still use subagents for the parts that are one-off work, such as drafting correct labels for the test set for a person to review.

## Tagging 300,000 reviews for one analysis: sample first

An analyst wants to know which product issues come up most often in 300,000 reviews.

At about 150 tokens per review, all the reviews come to roughly 45 million tokens of input, which would use far more of the plan than the question is worth. The question is about proportions, and a random sample of 3,000 reviews estimates each proportion to within about two percentage points, at 95% confidence. The agent samples 3,000 reviews, fans them out to 60 subagents in waves the harness can run at once, and reports the proportions with their margins. If the analyst later needs a tag on every review, for example to filter them in a dashboard, the agent proposes a script on a batch API and states its cost before running it.

## Sorting 15 commit messages: do it inline

The user asks which of the last 15 commits are features, fixes, or chores.

**Do it inline.** The messages are short and the list fits in a few lines. A subagent would take longer to start than the work takes.
