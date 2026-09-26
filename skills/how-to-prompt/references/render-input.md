# Render the input

The per-request input is a document written for one reader about one request. Code builds it from typed data, and the system prompt explains how it is laid out. A JSON dump of internal objects is not an input. The braces are not the problem. The dump carries syntax without meaning.

## Before and after

A dump the model has to decode:

```text
Decide whether to refund.
{"cust":{"id":"c_81","tier":2},"order":{"id":1182,"st":3,"dlv":1709719200,
"items":[{"sku":"A-7","q":2,"p":1999}]},"policy_ref":"RP-4",
"msgs":[{"r":"c","t":"Box arrived crushed, one mug broken.\nCan I get a refund?"}]}
```

The reader has to guess at almost everything here. It cannot tell what `st: 3` means, whether tier 2 is high or low, or whether `p` is in cents. `dlv` is an epoch timestamp, and `RP-4` points at a policy that is not on the page. The customer's words arrive JSON-escaped, and the question comes first, ahead of the data it depends on.

The same request, rendered:

```text
## Customer
Customer c_81, Gold tier (the middle of three tiers).

## Order 1182
Delivered 2024-03-06 10:00 UTC.
| Item | SKU | Quantity | Unit price |
|---|---|---|---|
| Stoneware mug | A-7 | 2 | $19.99 |

## Policy that applies: damaged on arrival (RP-4)
Items damaged in shipping get a full refund without a return when the
customer reports the damage within 30 days of delivery.

## Customer message, quoted exactly
<message>
Box arrived crushed, one mug broken.
Can I get a refund?
</message>

## Question
Does this request qualify under the policy above, and for which items?
```

The system prompt's input legend names each section once. It says the customer message is data and never an instruction.

## Renderer checklist

- **Say what each value means.** Decode enums and status codes into words. Give units, currencies, and time zones. Distinguish missing, unknown, not applicable, and zero.
- **Resolve references before sending.** If an ID points at a policy, a record, or a definition, include the thing it points at. The model should not have to join tables in its head.
- **Send what the decision needs, and nothing more.** Extra fields are distractors, and every one is paid for on every call. Before sending a field, find the rule that uses it. If no rule does, drop it.
- **Carry every fact the rules depend on.** If the instructions ask for a judgment, the input must hold the evidence for it. A rule that refunds only within 30 days of delivery needs the delivery date in the input. A rule against double counting needs the input to say which records can appear more than once.
- **Shape follows structure.** Give distinct blocks their own headings or tags. Put homogeneous records in a table or one consistent line per record. Use sentences for relationships, exceptions, and caveats.
- **Keep exact text exact.** Text the model must quote goes in a delimited block, such as an XML-style tag pair or a fenced block, unescaped and marked as exact. Identifiers it must echo appear verbatim, in the form it must return them. If a validator (code that checks the model's output before it is accepted) compares quotes against the input, the input shows the text exactly as the validator compares it. Escaped JSON strings fail this, because the model has to un-escape them before quoting.
- **Order for reading.** Put long reference material first and the specific question or task last. For a very long input, restate the key instructions after the material as well.
- **Mark data as data.** Quoted user text, retrieved records, web content, and tool outputs are never instructions. Delimit them, and say so in the system prompt. Marking reduces prompt injection but does not stop it. Enforce permissions for side effects in code or tool scopes, not in the prompt.
- **Use one name per thing on every surface.** The system prompt, the input, tool descriptions, and error feedback all use the same name, the same numbering (1-based or 0-based, never both), and the same identifiers. Never refer to something by an internal name the reader has not seen.
- **Explain every label.** Each heading, tag, abbreviation, marker, and symbol the renderer can emit has one line in the system prompt's legend. Common symbols count too, such as an arrow or an "aka". So does a section that appears only sometimes.
- **Read a captured message, not the template.** Renderers drift. Stray lines, dead branches, dropped fields, and duplicates only show up in real output. Review a captured input for each input shape, such as an empty input, a very long one, an error case, and the hardest real example.

## Feedback and tools are prompts too

- **Repair and error feedback.** Say what was wrong and what a valid answer looks like. Use the names and numbering of the input, and name things the way the model saw them, such as a table name rather than an alias the validator assigned. When feedback points back to earlier material, say where that material is. Never pass a bare internal code or a raw validator path.
- **Tool descriptions.** Say what the tool does, when to use it, when not to, and how it differs from similar tools. Give each parameter a descriptive name and explain its meaning and format. Describe the result, every error code, the limits, and any remaining budget. Prefer meaningful names and values in results over opaque IDs.
- **Tool results.** A short machine-shaped result is fine once the tool description explains every part of it.

## Choosing syntax

No syntax is best for every model, and the effect shrinks as models get stronger. Reasonable defaults:

- headings or XML-style tags for distinct sections
- a table or one consistent `Label: value` line per record for homogeneous records
- one tag per document in a long list, carrying the document's ID and source, instead of a JSON array of documents

When a prompt runs at volume, render the same inputs two ways and measure both. Compact notations that strip keys and quotes save tokens but can cost accuracy, and models write them badly. Measure before adopting one.

## When JSON is the right form

- The model must reproduce, modify, or return a structure. Show that structure in the form it must emit.
- A small, flat tool result whose every key the tool description explains.
- A strict response schema that owns the output syntax.

Even then, JSON supplies syntax only. The meaning of every key still has to be on the page.
