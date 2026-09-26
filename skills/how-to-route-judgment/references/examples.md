# Examples

Each example names the component that should make each judgment and why it fits. Copy the reasoning, not the domain or the numbers. The Jev calls follow TypeSafe's SDK as described in [decision-models.md](decision-models.md).

## Routing support tickets: use Jev

A support inbox routes tickets with keywords:

```python
def route(ticket: str) -> str:
    text = ticket.lower()
    if any(w in text for w in ["refund", "money back", "chargeback", "invoice"]):
        return "billing"
    if any(w in text for w in ["crash", "error", "bug", "broken"]):
        return "technical"
    return "general"
```

"There's an error on my invoice" goes to technical, and "you took my money twice" goes to general.

**This is a job for Jev.** The input is free text, the answer is one of three teams, the question runs on every ticket, and the same ticket should always land with the same team. Keywords can't read meaning. An LLM can, but it would add seconds and real cost to every ticket, and could route the same ticket differently on a rerun.

```python
from typesafe_sdk import Choice, Noul, TypeSafeClient

client = TypeSafeClient()
answers = client.system_one(
    state=ticket,
    questions={
        "team": Choice(
            instructions="Which team should handle this ticket",
            criteria={
                "billing": "Charges, refunds, invoices, or payment methods",
                "technical": "Something in the product fails or behaves unexpectedly",
                "general": "Anything else",
            },
        ),
        "urgent": Noul(instructions="The customer says they are blocked or facing a deadline"),
    },
).answers

team = answers["team"]
if team.confidence >= 0.8:
    assign(ticket, team.choice, priority="high" if answers["urgent"].noul >= 0.5 else "normal")
else:
    queue_for_triage(ticket, suggestion=team.choice, probabilities=team.probabilities)
```

A misrouted ticket costs little, so the threshold is modest. The uncertain tickets go to a person, with Jev's suggestion and probabilities attached.

## Merging duplicate customers: code finds candidates, Jev decides, a person checks the unsure ones

A CRM merges customers whose names are more than 85% similar by string distance. It merges "Jon Smith" with "John Smith" at a different company, and misses "Katherine O'Neil" and "Kate Oneil" at the same address.

**Code finds the candidates.** Records that share an email, a phone number, or a postcode and street are exact matches on exact fields, so a database query finds them.

**Jev decides each pair.** "Are these two records the same person?" is a yes-or-no judgment about fuzzy data: nicknames, typos, a changed surname. It runs once per candidate pair, often thousands of times, so it needs to be cheap and consistent.

**A person checks the unsure ones.** A wrong merge is hard to undo, so Jev's yes is enough only above 0.95.

```python
same = client.system_one(
    state={"record_a": a.to_dict(), "record_b": b.to_dict()},
    questions={"same_person": Noul(instructions="Both records describe the same real person")},
).answers["same_person"].noul

if same >= 0.95:
    merge(a, b)
elif same >= 0.5:
    review_queue.add(a, b, probability=same)
```

## Browser actions: Jev picks the element, an LLM handles what Jev isn't sure about

A browser agent sends the whole page to an LLM and asks what to do next, which takes seconds per step.

**Jev fits the normal case.** A page offers a finite set of interactive elements, so "what to click next" is a choice from a list that code builds by marking those elements. Jev returns the element and the action type with a confidence.

**An LLM handles the rest.** Below 0.7 confidence, the step goes to an LLM, which can reason about an unusual page. Browserbase, which runs browsers for AI agents, rebuilt the `act()` step of its open-source automation library Stagehand this way, and the step's median latency fell from 1.97 seconds to 0.46.

## Legal document review: Jev classifies, an LLM redacts, an attorney decides privilege

Every page of a production set gets three questions in one Jev call:

- **"Is this page responsive to the request?"** Jev, as a yes-or-no. Pages that aren't responsive are set aside.
- **"Does it contain personal information?"** Jev decides, and an LLM does the redaction, because redacting means rewriting the text and Jev doesn't generate text.
- **"Might it be privileged?"** Jev flags it, and an attorney makes the call, because a wrong privilege decision can't be taken back.

Jev makes every classification on hundreds of thousands of pages. The LLM does the one writing task, and a person makes the one irreversible call.

## Pulling an address out of an email: use an LLM

A customer writes, "please send the replacement to my office instead, it's the third floor of the Hansen building, Kongensgade 14, 5000 Odense."

**This is a job for an LLM**, with structured output for the address fields. The answer is a value, not a choice from a known list, and Jev doesn't produce text. Code then validates what the LLM returns, for example that the postcode matches the city.

## A return request: code, Jev, and an LLM on one message

A return request reads: "Order ORD-48213, bought on March 3. The mug arrived cracked. Can I get a new one?"

- **The order number: code.** The system itself issues numbers as `ORD-` plus five digits, so a regex is exact and complete.
- **Whether the order is inside the 30-day return window: code.** It's date arithmetic.
- **"Does the customer say the item arrived damaged?": Jev.** It's a yes-or-no judgment about free text.
- **The reply to the customer: an LLM.** It's open-ended writing.
