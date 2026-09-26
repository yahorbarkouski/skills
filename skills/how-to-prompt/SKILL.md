---
name: how-to-prompt
description: Write, review, and improve any text a model acts on, such as system prompts, per-request inputs, subagent briefs, tool descriptions, error and repair feedback, skills, and agent rules. Covers making a prompt self-sufficient, checking it sentence by sentence with a cold low-reasoning reader, rendering input data instead of dumping JSON, choosing between a goal brief and explicit policy, specifying output and examples, improving a prompt from its runs, and measuring changes. Use whenever you write or change a prompt, hand work to another agent, build an LLM call, or see an agent fail the same way twice.
---

# How to prompt

The reader of a prompt has only the page. It never saw your conversation, your code, your earlier attempts, or why you chose what you chose. Write for that stranger, check the prompt with a stranger, and change it based on what its runs show.

Scale the effort to the prompt. A one-off brief to another agent needs sections 1 and 2 and a quick cold read. A prompt that runs many times needs every section.

## 1. Know the reader

- **A capable agent with tools.** Give it the goal, why the goal matters, the materials and where they are, and the boundaries: what is out of scope, and what others are already doing. Leave the method to it unless the method is itself a requirement. A prescribed procedure narrows what a strong agent looks for.
- **A cheap or no-reasoning model on a hot path.** Give it policy, meaning explicit rules for the decisions it would otherwise re-derive on every call. Examples: which check comes first, when an input is insufficient, when not to give up, what never to repeat. Rules like these can stand in for much of what reasoning would work out. Deduction specific to one case cannot be written down in advance, so leave that to reasoning or to code.
- **A production call checked by a validator.** Layer the policy on a contract. Open with what the model produces, for whom, and what happens before and after this call. Describe every block of the input. State every validator rule the model can break, and what a violation costs. Keep tuned policy in its own section so rewrites keep it.

If the project has its own prompt-authoring rules, in its agent instructions, contributing guide, or recorded decisions, they take precedence over this skill.

## 2. Put everything on the page

After hours inside a task, you stop noticing what you know, and the reader knows none of it. Every prompt carries:

- the goal, and the reason behind it, so the reader can handle cases no rule mentions
- what the reader is looking at, and where it came from
- a definition for every name, code, abbreviation, and label it will meet
- what is already settled or ruled out, so the reader does not redo it
- the constraints, and what breaking each one costs
- what to return, in what form, at what length, and when to stop

Before sending, hunt for context only you have. That includes:
- references to things only you saw ("the bug", "as discussed", "the new approach", "last run")
- internal component names, codenames, and ticket numbers
- file paths the reader cannot open, and relative dates
- a term the instructions use that the input never uses, or a label the input uses that the instructions never define

Every decision the prompt asks for must be decidable from the page. If a rule depends on a fact, the input carries that fact.

Self-sufficient does not mean exhaustive. Requirements you leave unstated are the ones that break when the model or the prompt changes. But every added requirement competes with the others, and a long list lowers compliance with each item. State what the reader cannot infer on its own, and let the cold read and the runs show you which requirements those are.

Deliver it as one message. The same content spread over several turns performs markedly worse. If the executor can ask questions, say when it should, because models rarely ask unprompted. Put hard constraints where they survive, in the instructions that are never summarized or trimmed, not only in early turns of a long conversation.

## 3. Check it with a cold reader

Give the exact page the executor will see to a fresh agent on the smallest, lowest-reasoning model available, with no other context. That might be a Haiku, mini, or Flash-class model, or whatever your smallest model is. It judges every numbered sentence CLEAR, PARTIAL, or UNCLEAR. It restates the task, lists every term it cannot resolve, and lists the questions it would ask you. Each mismatch between its restatement and your intent is missing context. Fix the page, never the reader, and run a fresh reader on the result.

Fix a flag when it points to a missing fact, an undefined term, or a sentence with two readings. If a flag reflects only the small reader's limits, and the target model reads that sentence correctly, keep the sentence. Stop when a round turns up no missing facts and the restatement matches your intent. Treat the cold read as a cheap way to find gaps, not as proof that the prompt works. Runs decide that.

Clarity must never cost meaning. Do not drop a branch, soften a hard rule into advice, or swap an exact value for a vague synonym. The procedure, the reader instructions (reused unchanged every round), and how deep to go for each kind of prompt are in [references/cold-read.md](references/cold-read.md).

## 4. Render inputs for the reader

The per-request input is a document written for one reader about one request, and code builds it from typed data. Do not send a JSON dump of internal objects, unless the model must reproduce or return that exact structure. The braces are not the problem. What goes wrong is lost meaning: key names are the author's shorthand, codes stay undecoded, IDs point at things that are not on the page, fields the task never needs distract, and quoted text arrives escaped.

- Say what each value means: decode codes, give units and time zones, and tell missing apart from unknown, not applicable, and zero.
- Resolve references. Include the thing an ID points to.
- Send what the decision needs and nothing more.
- Keep exact text exact, delimited, and unescaped. If a validator compares the model's quotes or echoed IDs against the input, show them in exactly the form the validator compares.
- Put long reference material first and the question last. For a very long input, restate the key instructions after the material too.
- Mark quoted and retrieved content as data, never instructions. Marking reduces prompt injection but does not stop it, so enforce permissions for side effects in code or tool scopes.
- Use one name for each thing across the instructions, the input, the tool descriptions, and the feedback.
- Review a captured message, never the template.

No syntax is best for every model, and strong models care less than weak ones. Use headings or tags for sections, a table or one consistent line per record for records, and a tag with ID and source for each document in a long list. When the prompt runs at volume, measure two renderings instead of guessing.

A tool description is a prompt too. Say what the tool does, when to use it and when not to, and how it differs from similar tools. Explain each parameter's meaning and format, the result it returns, every error code, and its limits. Error and repair feedback uses the input's names and numbering, says what was wrong, and says what a valid answer looks like. The before-and-after example and the full checklist are in [references/render-input.md](references/render-input.md).

## 5. Specify the output and the examples

- Let a strict schema or parser own syntax, and spend prompt words on meaning. Never list outputs the schema already makes impossible.
- When the answer needs reasoning, the reasoning comes before the answer. Put the reasoning field first in the schema, turn reasoning on, or let the model reason in free text and format afterwards. A schema that puts the answer before the reasoning costs accuracy, and small models pay the most.
- Models copy examples, including their length, wording, and entities. Use several examples that differ in whatever should vary, or describe the target instead when outputs should not look alike. Caption each example with the one behavior it shows, and run it through the real parser so it cannot drift from the contract.

## 6. Improve it from its runs

Once a prompt has runs with outcomes, base changes on counts over every run, not on a few transcripts you happened to read. Hand a coding agent (any agent that can write and run code over files) the raw runs, the prompt, the list of actions the agent under study can take, and the short brief in [references/distill.md](references/distill.md). A good distillation first counts outcomes, run lengths, endings, tool use, duplicate calls, unsupported arguments, and actions that never happen. Then it reads the runs that the counts single out. Each rule it writes has a trigger, an action, and the count behind it. It names behaviors and tools, never a specific task or answer from the runs.

Distill each set of runs once, with no loop that edits, re-scores, and keeps the winners on the same runs. Set the held-out items aside before anyone reads a run, and keep them away from the prompt author and from any agent that rewrites the prompt.

## 7. Measure changes

A change to what the prompt asks the model to do ships with a measurement on held-out items. Rewording or restructuring needs a cold read, and also a measurement when the prompt runs at volume, because layout alone can shift results. Run both variants on the same items, and report the paired difference with its standard error, n, and cost in tokens and in steps (tool calls or turns).

A difference smaller than about two standard errors is a tie. On 50 items at a pass rate near 50%, binomial noise alone gives one variant's score about 7 points of standard error, and an unpaired difference between two variants about 10. Tests check what code can check and never assert prompt wording. The details are in [references/measure.md](references/measure.md).

## 8. Keep it lean

- Delete every rule that does not change behavior. Each word is paid for on every call, and it dilutes the rules that matter.
- Contradictions do more damage than gaps. When adding a rule, check it against every existing rule on inputs it was not written for.
- State rules calmly. All-caps warnings and words like CRITICAL make current models over-apply a rule. Give the reason instead.
- One concern per sentence. Say the decision, not the vibe.

Before changing this skill, check the evidence for each rule in [references/sources.md](references/sources.md).
