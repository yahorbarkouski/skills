# Decision models

A decision model takes fuzzy input and a set of questions, and returns a typed answer with probabilities for each question. It never writes text. This file covers TypeSafe's Jev, how to set confidence thresholds, and what to use when a project can't call Jev.

Everything about Jev below comes from TypeSafe's documentation and launch post as of September 2026. Check https://docs.typesafe.ai before writing code against it, because the API may have changed.

## Jev

TypeSafe describes Jev as a "System One" model: "unstructured state in, typed probabilistic decisions out".

**Input.** A `state`, which can be a string, an object, or an array of text and structured data, and a named map of `questions`. Jev reads text and structured data only, not images. It evaluates the questions independently and in parallel, so put every question about the same state in one call.

**Question types.**

| Type | Asks | Returns |
|---|---|---|
| `Noul` | a yes-or-no question | `noul`, the probability from 0 to 1 that the answer is yes |
| `Choice` | pick one of up to 255 named options, each described in `criteria` | `choice`, `probabilities` for every option, and `confidence` |
| `Score` | place the state on an ordered scale of 2 to 10 levels | `score`, `legend`, `probabilities` for every level, and `confidence` |

**Confidence.** TypeSafe computes confidence from the probability distribution: probability concentrated on one option means a confident answer, and probability spread across options means an uncertain one. The full `probabilities` always come back, so code can see a close second choice.

**What it doesn't do.** It doesn't generate text or code, and it doesn't choose its own next action. TypeSafe says it isn't meant for chatbots, copilots, or coding agents, where an LLM belongs.

**Limits.** Up to 255 options per `Choice`, and 2 to 10 levels per `Score`. Browserbase reports a 64,000-token context window, with the state plus the longest question capped at 32,000 tokens. TypeSafe's own pages don't state a context limit.

**Speed and cost**, as TypeSafe reports them: 70 to 500 milliseconds per call, $0.042 per million input tokens, and no charge for output. Repeated calls on the same input return nearly the same probabilities.

**A call**, as shown in TypeSafe's documentation:

```python
# pip install typesafe-sdk
from typesafe_sdk import Choice, Noul, TypeSafeClient

client = TypeSafeClient()  # reads TYPESAFE_API_KEY
response = client.system_one(
    state="Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing.",
    questions={
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "technical": "Bugs or integration problems",
                "billing": "Charges, refunds, invoices, or payment methods",
                "general": "Anything else",
            },
        ),
        "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
    },
)
response.answers["department"].choice          # "technical"
response.answers["department"].probabilities   # a probability for each option
response.answers["is_urgent"].noul             # probability of yes, such as 1.0
```

Over HTTP, send `POST https://api.typesafe.ai/v1/systemone` with `Authorization: Bearer <key>`. The response holds `answers`, `model`, and `usage`, and errors come back as 401, 422, 429, or 529. The model defaults to `jev-latest`.

## Set the thresholds

TypeSafe recommends tiers rather than one cutoff:

- **High confidence:** act automatically.
- **Medium confidence:** ask the user to confirm, flag the case for review, or gather more information.
- **Low confidence:** don't act. Send the case to a person or an LLM, or ask for clarification.

Their worked example sends anything below 0.6 to a person and requires more than 0.85 before a high-stakes action such as approving a transfer. They say plainly that these numbers are examples, not calibrated values.

To set real thresholds for one action:

1. Run the decision model on 50 to 200 labeled inputs.
2. For each candidate threshold, count two things: how often the decisions at or above it are wrong, and what share of cases fall below it and so need an LLM or a person.
3. Pick the lowest threshold whose error rate the action can tolerate, given what one wrong action costs and what one review costs.
4. Repeat for each action. An action that sends an email and an action that refunds money need different thresholds.

## When a project can't use Jev

This section is this skill's own guidance. TypeSafe's documentation names no alternatives.

Keep one interface in the code, so the backend can change without touching the routing:

```python
from dataclasses import dataclass

@dataclass
class Decision:
    answer: str                      # the chosen option, or "yes" / "no"
    probabilities: dict[str, float]  # one entry per option
    confidence: float                # from the backend, or the top probability


def decide(state: str, questions: dict) -> dict[str, Decision]:
    ...  # Jev, a classifier, or a small LLM behind the same signature
```

Then choose a backend:

- **A trained classifier.** Use it when you have a few hundred labeled examples per question and the options rarely change. Embeddings with logistic regression, or a fine-tuned small model, both give probabilities. Check them against held-out labels before trusting them as confidence.
- **A small, fast LLM whose answer is constrained to the options.** Use structured output with an enum, or ask for a single-token answer. For confidence, use the log-probability of each option if the API returns log-probabilities. If it doesn't, ask the same question five times at a nonzero temperature and use the share of answers that agree. Never ask the model to write down its own confidence: models state confidence too high. Sampling five times costs five calls, so put several questions in each call.

Whichever backend you use, set its thresholds with the procedure above. A switch to Jev later only changes what runs inside `decide`.
