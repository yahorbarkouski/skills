# Distill a prompt from its runs

Improve a prompt from what its runs did, counted over every run. A coding agent computes the counts with code, reads the runs that the counts single out, and writes rules backed by the counts. One pass, no search loop.

## Preconditions

- The model, its settings, its tools, and its harness stay fixed. Only the prompt changes. Rules distilled for one model are not known to transfer to another, so re-distill when the model changes.
- A training pool of tasks where every run has an outcome: a reward, a pass or fail, a verifier verdict, or a human judgment. Without outcomes you can only find efficiency rules.
- Enough failures to learn from. A few dozen tasks, with failures in every category you want to improve, is a workable start. A very small or nearly failure-free corpus may leave nothing to distill.
- A held-out split that plays no part in distillation, and a validation split if you will pick between passes.
- The terms of the provider whose outputs form the corpus allow this use.

## Build the corpus

One directory, with one file per run or one JSONL row per run. Each run carries:

- task id and category (task type, or any input feature you can name)
- which prompt version produced it
- the full message sequence, with every tool call, its arguments, and its output
- the final answer or final state
- the outcome, plus the grader's reason when one exists
- how the run ended: answered, gave up, refused, escalated, hit a limit, errored
- token counts, step counts, wall time

Add the current prompt as `prompt.md` and the list of tools or allowed actions as `actions.md`. The action list is what makes absences visible. The corpus can only show that an action never happened if the distiller knows the action exists. Add nothing that summarizes the runs. Reasoning traces are optional, and runs without them carry enough signal.

## Isolate

Run the distiller in a fresh session whose working directory holds only the corpus, the prompt, and the action list. It must not reach the held-out split, its answer key, or earlier distilled prompts.

## The brief

Keep it this short. Do not prescribe a method. A capable coding agent finds the right one, and a prescribed pipeline narrows what it looks for.

```text
This directory holds <N> runs of an agent on <task family>, one per file in
./runs. Each has the full transcript, tool calls and outputs, outcome, and
metadata. The agent's current system prompt is ./prompt.md, and the actions it
can take are listed in ./actions.md. Analyze the runs directly, with no other
inputs and no precomputed summaries. Distill a file of behavioral rules that
would make a future instance of this agent more accurate and use fewer tokens
and steps on this task family. Use your own judgment on methodology. Write the
result to ./rules.md.
```

Append these sentences to the brief if the distiller is smaller or weaker than a frontier coding agent. Also append them if a first pass came back anecdotal, which you can tell because its rules cite a few transcripts instead of counts:

- "Compute corpus-wide counts with code before reading individual runs, and read runs to check what the counts suggest."
- "Back each rule with the count that justifies it."
- "Never name a specific task, entity, or answer from the runs."

## What a good distillation looks like

It opens with a short look at the corpus layout. It then alternates between counting with code and reading the runs that the counts single out. Each count raises a hypothesis, and reading either confirms it or kills it. It writes the rules once, at the end.

Red flags: it reads runs in order without computing anything. It writes rules before counting, or writes rules with no counts. It quotes strings from specific tasks. It produces a file several times longer than the prompt it improves.

## Counts to compute

- outcome rate, overall and per category
- run length in turns, steps, and tokens, and the outliers
- how runs end, split by outcome
- use of each tool or action, split by outcome and category
- exact duplicate calls within a run
- arguments that nothing earlier in the run supports, such as an ID the agent made up
- categories that fail every time
- actions that never happen, or never happen in failing runs
- checks the prompt, the policy, or the tool documentation requires before acting, which runs skip

## Hunt for absences

Some failures show up in every failed transcript, and any reviewer catches them. Others show up only as something that never happens anywhere, like a required step no run ever takes. No single transcript reveals those. Only a count over the corpus does.

1. Take each action from the action list.
2. Count its uses overall and per category, split by outcome.
3. For every action at or near zero in a failing category, read a few failed runs from that category and ask whether the action was needed.
4. Write the rule only when the reading confirms it.

## Rule format

Each rule has a trigger, an action, and the evidence:

- Check the device state before touching the account. 33 of 50 failed runs never checked it.
- Settle the outstanding balance before reactivating a service. No run ever called the payment action.
- Never pass an ID that no earlier tool output supplied. 16 of 50 runs made one up.
- Do not repeat an identical lookup. 123 of 284 lookups were exact duplicates.

Keep the evidence, either inline or in a sidecar file, because it is the rule's provenance. A sidecar file may cite run IDs. The rule itself stays general.

## Review the rules before measuring

- Every rule has a trigger, an action, and a count.
- Every rule corrects a behavior the runs show, or an action they show missing. None covers a situation the corpus never exercised.
- No rule names a task instance, entity, or answer from the pool.
- No rule contradicts the prompt's contract or another rule.
- Every rule is a decision that recurs across tasks. Case-by-case deduction stays out.
- The file is short. Every rule adds tokens to every future call, so each one must earn its place.
- The rules pass a cold read ([cold-read.md](cold-read.md)).

The rules become the policy section of the prompt. The contract sections stay as they were. Then measure ([measure.md](measure.md)).

## Variants and later rounds

- Distillation is cheap, so run about three independent passes. Rules that every pass produces are the robust core. How far the passes disagree tells you how reliable one pass is.
- If you pick one pass, pick it on the validation split, then measure the pick once on the held-out split.
- A second round needs a new corpus. Run the improved prompt on the training pool, then distill again. Never re-distill the same corpus to chase a score.
- A search loop proposes edits, re-runs each one, and keeps the edits that score better on a validation set. Use one only after distillation stops improving the validation score, and only when runs are cheap and the validation set is separate from both the pool and the test set. With a small validation set, the edits that happen to score better tend to fit that set's quirks instead of the task.
