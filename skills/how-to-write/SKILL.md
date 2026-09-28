---
name: how-to-write
description: Write or revise any document another person or agent will read, such as design docs, specs, plans, READMEs, explanations, reports, pull request descriptions, runbooks, handoff notes, and AGENTS.md files. Covers naming the reader and what they already know, putting the context they lack on the page, leading with the point and a concrete example or diagram before the abstract explanation, staying concise without leaving gaps, and a feedback loop in which a fresh subagent reads the draft cold, reports exactly what it could not follow, and you elaborate only those points. Use whenever you write a document, or change one, for a reader who was not inside your session.
---

# How to write

Here is a sentence an agent might write at the end of a long session:

> Switched retries to the new queue as discussed, so the TTL issue is gone.

To the writer it is complete. The reader doesn't know which queue is new, what was discussed, which TTL, or what the issue was. Written for the reader, it says:

> Payment retries moved from the main job queue to the `payments-retry` queue. The main queue deletes messages after 15 minutes, which silently dropped any retry scheduled later than that. The new queue keeps messages for 24 hours.

The writer can't see the gap, because after working on something you no longer remember what it was like not to know it. This is the main way documents fail, and agents fail this way more often than people, because everything in the session is context the reader never saw. So decide who will read, write for what they don't know, give the draft to a reader who has none of your context, and fill exactly the gaps it finds.

## 1. Name the reader

Before you write, answer four questions, if only for yourself:

- Who reads this: a person or an agent, and in what role?
- What do they already know: the field, this project, its vocabulary, its history, the conversation that led here?
- What will they do after reading: decide, build, review, follow steps, or look up one fact?
- How will they read: skim for the conclusion, follow it step by step, or search for one section?

If you can't answer, ask whoever requested the document. If there is no one to ask, write for a capable newcomer: someone who knows the field but has never seen this project or this conversation.

The answers decide what goes in. A reviewer on the same team needs the decision, the reasons, and what changed. A newcomer also needs the terms and the background. An agent that will act on the document needs exact paths, commands, values, and a way to check that it is done.

## 2. Put the missing context on the page

Find everything the reader needs that exists only in your head or your session:

- names you coined, abbreviations, codenames, and ticket numbers
- references to things the reader never saw, such as "the bug", "as discussed", "the new approach", or "the earlier run"
- relative time, such as "yesterday" or "now", and file paths the reader can't open
- decisions made in conversation, and the options that were ruled out and why
- the reason behind each rule or choice

For each one, define it where it first appears, link to where it is defined, or cut it. Use one name for each thing throughout the document. Leave out what the reader already knows, because explaining the obvious buries the part they need.

## 3. Lead with the point, then show it

- Put what the reader most needs in the first two or three sentences: the conclusion, the decision, or what the thing does and why it exists. Details follow, in the order the reader will need them.
- Explain a new idea with a concrete example before the general rule. Use one real, typical case with real names and numbers, small enough to hold in mind. Then state the rule the example illustrates.
- When the idea is a structure, a flow, a sequence, or how parts connect, draw it before you explain it in prose. In Markdown, use a Mermaid diagram or a small text sketch. Label every part with the name the text uses, show only what the text discusses, and follow the diagram with prose that walks through it. Skip the diagram when one sentence says the same thing.

Short before-and-after examples of each are in [references/examples.md](references/examples.md).

## 4. Be concise without leaving gaps

Concise means that every word does work. The reader still gets every explanation they need.

- Cut what does no work: filler, restatement, generic advice, and explanations of what the reader already knows.
- Never cut context the reader lacks to save space. A short document the reader can't follow costs more than a longer one, because the reader has to ask, guess, or go read the code.
- Write whole sentences with their articles and verbs. Don't compress them into arrows, fragments, or private shorthand, which only you can decode.
- Say what a thing is and does, concretely: name the behavior, the mechanism, or the number. Never frame it as a contrast with something else, as in "It is not X, it is Y", "It does not stop at X: it does Y", "not just X but Y", "not only X but also Y", "Y rather than X", or "No X, no Y, just Z". The reader has to picture the denied claim before discarding it, and the pattern reads as machine-written. Write a limit the reader needs as its own plain sentence, such as "The cache never stores passwords." To find these patterns, search the draft for "not", "just", "only", "rather than" and "instead of". An example is in [references/examples.md](references/examples.md#say-what-it-does).

## 5. Test it with a cold reader and fill what it couldn't follow

Run this loop after every draft, and after every change to an existing document. A short message or a one-line change needs one round. A document that others will build on or act on needs rounds until no gaps remain.

1. Start a fresh subagent with none of your context. Give it the reader description from section 1 and the document, and nothing the real reader wouldn't have. A small, fast model, such as a Haiku, mini, or Flash-class model, works well, because it guesses less than a strong one and so stops where the page is thin.
2. Ask it to restate what the document says and what it would do next, to list every term or reference it couldn't resolve, to quote every place it had to guess along with its guess, and to answer a few questions the document must answer. Write the answers you expect before you run it. Model readers often miss the biggest problem in a text, and a wrong answer shows you what the reader's own list left out.
3. For each gap, add what is missing at exactly that spot: a definition, a missing step, a reason, an example, or a diagram. Don't rewrite the document, and don't add general background around the gap.
4. For each wrong guess, the passage allows two readings. Rewrite it so that only yours fits.
5. If the reader says a passage told it what it already knew, cut the passage.
6. Run a new reader on the result, since a reader that has seen a draft has learned it. A round that led to any fix is never the last round. Stop when a round finds no new gaps and the restatement matches what you meant, which usually takes two or three rounds.

If a flag comes only from the test reader's limits, such as a term that every real reader of this document knows, leave the text as it is. The loop checks clarity. A reader without your sources can't catch a wrong fact, so check every claim against your sources yourself. The reader instructions and how to act on each kind of finding are in [references/reader-loop.md](references/reader-loop.md).

## 6. When you change an existing document

- Write the changed part for someone reading this version cold. Don't narrate the change with words like "now", "updated to", or "instead of before" unless the history matters to the reader. Keep history in a changelog or decision log.
- Change a fact everywhere the document states it: the summary, other sections, tables, examples, and other documents that link here. Replace the old statement where it stands, and never append a correction below it.
- Keep what the request doesn't cover: rules, numbers, exceptions, reasons, open questions, and how certain each statement is. Rewrites tend to turn "may" into "will" and to drop the reasons behind rules.
- When asked to shorten, reach the requested length. Cut filler, repetition, and restated background first, then say each rule, number, exception, reason, and open question in fewer words. The compare step will list those sentences as reworded; check that each still means the same, and don't restore the old wording. Propose removing a whole item only if the length still can't be reached.
- Before you finish, run `python3 <this skill's directory>/scripts/doc_diff.py compare ORIGINAL EDITED` against a copy of the original. It lists what is missing, reworded, or moved, and whether hedges were lost. Account for each item.
- Run the loop in section 5 on the changed document.
- Tell the owner what you changed, what you removed and why, and anything that needs their decision, such as two statements that conflict or a fact you couldn't check.

## 7. When the reader is an agent

An agent acts on the page literally and usually can't ask you. Give it exact file paths, commands, and values. Say what done looks like as a check it can run. State constraints as requirements it can verify, and write only what it can't find in the repository. More on documents that agents act on is in [references/agent-docs.md](references/agent-docs.md).

Before changing this skill, check the evidence for each rule in [references/sources.md](references/sources.md).
