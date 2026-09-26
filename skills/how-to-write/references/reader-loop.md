# Reader loop

The reader loop finds what a document assumes the reader knows. A fresh subagent plays the reader, reads only the page, and reports where it got lost. You add what is missing at exactly those spots, then check again with a new reader.

## Describe the reader

Write one short paragraph for the test reader to play. Say who it is, what it knows, what it hasn't seen, and what it will do after reading. For example:

> You are a backend engineer who joined the team this week. You know TypeScript and Postgres. You have not seen this repository, the design discussions, or any earlier version of this document. After reading it, you will implement the change it describes.

If the document has more than one kind of reader, such as reviewers and implementers, run one test reader for each kind.

## Write the check questions

Write three to six questions the document must answer, and write the expected answers before running any reader. Good questions ask:

- what the document decides or recommends
- what to do in one named case
- a limit, a value, or a name the reader will need
- what is out of scope
- one thing the document doesn't cover, whose right answer is "not stated"

## Reader instructions

Keep these unchanged across rounds. Changing them between rounds coaches the reader toward your rewrite.

```text
{reader description}

Below is a document written for you. You have no other context: no
conversation, no files, and no background beyond the description above.
Judge only the page.

<document>
{document}
</document>

Do five things, and do not rewrite the document.

1. In at most four sentences, say what the document tells you and what you
   would do next.
2. List every term, name, abbreviation, or reference that you could not
   resolve from the document and your background.
3. List every place where you had to guess to continue. Quote the passage
   and give your guess.
4. List every passage that told you something you already knew, given the
   background described above.
5. Answer the questions below using only the document. Write "not stated"
   if the document does not answer one.

<questions>
{numbered questions}
</questions>

Answer in this form:
RESTATEMENT: <your summary>
UNRESOLVED: <items, or "none">
GUESSES: "<quoted passage>" -> <your guess>; ... or "none"
ALREADY KNEW: "<quoted passage>"; ... or "none"
ANSWERS:
Q1: <answer> | <quote that supports it, or "none">
Q2: ...
```

## Act on the result

| Finding | What it means | What to do |
|---|---|---|
| The restatement differs from what you meant | The page doesn't say what you think it says | Find the passage it misread, often the opening, and rewrite it |
| An unresolved term | A missing definition | Define it where it first appears, or link to its definition |
| A guess that happens to be right | The passage works only for a reader who guesses | State it outright |
| A guess that is wrong | The passage has two readings | Rewrite it so that only your reading fits |
| An "already knew" passage | Over-explained for this reader | Cut it. In instructions for an agent, keep it if the agent knows the rule but still breaks it |
| A wrong answer, or "not stated" where the document should answer | The fact is missing or buried | Add it, or move it where the reader looks |
| "Not stated" where you expected it | The document is honest about its limits | Nothing |

Add each fix at the spot the reader flagged. Don't respond to a gap by adding background elsewhere or by rewriting the whole document.

## Rounds

Run a new reader each round with the same instructions and questions. Stop when a round finds no new gaps and the restatement matches what you meant.

A small, fast model finds the most gaps, because it guesses less than a strong model. For the last round of an important document, use the model, or the kind of person, closest to the real reader. If a flag comes only from the test reader's limits, such as a term every real reader knows, leave the text alone.
