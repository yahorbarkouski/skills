# Measure a prompt change

A change to what a prompt asks the model to do ships with a measurement. A plausible argument is not one.

## Splits

- **Training pool.** It produces the runs you learn from. The prompt author, and any agent that rewrites the prompt from runs, may read all of it.
- **Held-out test.** It measures, and nobody writes rules from it. Once someone reads its failures to change the prompt, it has become training data, and you need fresh items.
- **Validation.** You need it only to pick between candidates. Set it aside before any experiment starts, and keep it separate from both of the above.

## Noise

- One score over n items at pass rate p has a standard error of sqrt(p(1-p)/n). At n = 50 and p near 0.5 that is about 7 points, and at n = 100 about 5.
- The difference between two independent scores is noisier, about 10 points at n = 50. Run both variants on the same items and compare them item by item. Report the mean per-item difference and its standard error. Pairing usually shrinks the error, because both variants see the same easy and hard items.
- Call a difference real only when it exceeds about two standard errors. Anything smaller is a tie. Report it as one.
- Spread across seeds is not the whole noise. Three seeds on the same 50 items can agree closely and still say little about the next 50 items. Seeds measure sampling randomness, and items measure how the result generalizes. When the model samples with temperature above zero, run at least three seeds, and always report n.
- Say which variance you measured. Re-running one prompt with new seeds is one source of spread. Producing the prompt again independently, by a second rewrite or a second distillation, is another.
- Expect the same recipe to drift by a few points between sessions.

## Report

- Accuracy against the prompt being replaced, as the paired difference with its standard error and n.
- Tokens and steps per run. Efficiency counts as well as accuracy.
- Prompt tokens per call. Every word of a long prompt is paid on every call.
- Latency, when it matters.
- If the prompt's decision rules are meant to replace model reasoning, report the same model with reasoning on, and the share of that gap the prompt recovers: (with rules - without) / (with reasoning - without).
- What producing the prompt cost.

## Selection

Keeping an edit because a small validation batch approved it overfits that batch. The best of several noisy scores overstates the winner. If you must pick, pick on the validation split, then re-measure the pick once on the held-out test.

## Judging

- The model that produced an answer does not grade it alone. Prefer deterministic checks, meaning code that verifies the answer, such as an exact match, a schema check, or a test. Otherwise use a judge model from a different vendor or model family, and do not tell it which variant produced which answer.
- When comparing agent variants, keep the setup blind. Candidates get an ordinary task with no hint that they are being evaluated or compared.

## Tests

Tests prove the parts of a prompt that code can check. Examples decode and pass the validator, request assembly uses the production code path, and limits reject bad responses. Tests never assert prompt wording: no pinned sentences, banned-word lists, section-order checks, or snapshots of rendered prompts. Such tests fail on every edit and pass on every wrong prompt, so they catch edits, not errors. Runs measure behavior, and a person reviews the wording and reads captured rendered inputs.
