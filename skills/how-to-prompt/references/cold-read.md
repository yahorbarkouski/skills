# Cold read

A cold read shows a prompt to a reader that has none of the author's context. It then checks two things. Can the reader act on every sentence? Does its idea of the task match the author's?

## Choose the reader

Use the smallest model you can run, with reasoning off or at its lowest setting, such as a Haiku, mini, nano, or Flash-class model. Start it fresh, with no conversation history, no file access, and no project instructions. A strong model tends to fill gaps by guessing, and the guess hides the gap. A weak reader is more likely to stop where the page is thin. No study has validated this, so treat the cold read as a cheap way to find gaps.

For a prompt that will run in production, add a second reader: the real target model with the same reasoning setting, temperature, and output limit it runs with in production. The weak reader finds unclear sentences. The target reader shows how the actual executor interprets them.

## Build the page

The reader gets exactly what the executor will get, and nothing else:

- the system prompt
- a real rendered input, taken from a capture or produced by the production renderer. Never a template with placeholders.
- the descriptions of any tools the executor can call

If inputs come in several shapes (empty, long, error case, the hardest real example), cold-read each shape. Number the sentences so every verdict points at one:

```bash
python3 <directory containing this skill>/scripts/number_sentences.py system.md input.md > page.txt
```

## Reader instructions

Freeze these for the whole review. Changing them between rounds coaches the reader toward your rewrite.

```text
You are reading instructions written for another model. You have no other
context: no conversation, no files, no background. Judge only the page below.
It is exactly what the other model will receive. Its sentences are numbered
[S1], [S2], and so on.

<page>
{numbered page}
</page>

Do not rewrite the page. Do four things.

1. Give every numbered sentence one verdict, judging it with everything else
   on the page in view:
   CLEAR: you know exactly what it states or asks and could act on it.
   PARTIAL: you get the gist but would have to guess. Say what you would guess.
   UNCLEAR: you could not act on it. Say why.
2. In at most three sentences, say what task the page asks for and what a
   finished result looks like.
3. List every name, term, code, abbreviation, label, or reference that you
   cannot resolve from the page alone.
4. List the questions you would ask the author before starting, most
   important first.

Answer in exactly this form:
S1: CLEAR
S2: PARTIAL: <what you would have to guess>
...
TASK: <your restatement>
UNRESOLVED: <items, or "none">
QUESTIONS: <items, or "none">
```

## Read the result

1. Compare TASK with your intent. Every difference is context that only exists in your head.
2. For every PARTIAL, UNCLEAR, UNRESOLVED item, or question, decide what it points to. A missing fact, an undefined term, or a sentence with two readings gets fixed on the page. Fix the page, never the reader. A flag that reflects only the small reader's limits, on a sentence the target model reads correctly, leaves the sentence as it is.
3. Check that the fix kept the meaning. A clearer sentence must force the same decision as before: no branch dropped, no hard rule softened into advice, no exact value replaced by a vague synonym. If the meaning has to change, that is a behavior change, and it needs a measurement.
4. If a sentence deliberately leaves a choice to the executor, say so in the sentence ("use your judgment on X"). A choice stated as open reads as CLEAR, and a vague one does not.
5. Run a fresh reader with the same instructions. A reader that has already seen the page has learned it. Stop when a round turns up no missing facts, no undefined terms, and no sentence with two readings, and the restatement matches your intent. That usually takes two or three rounds.

## Scale it to the prompt

| Prompt | Check |
|---|---|
| One-off brief to another agent | Restatement, unresolved terms, and questions. Per-sentence verdicts are optional. |
| Prompt that runs repeatedly, tool description, skill, agent rule | Everything, every sentence |
| Production prompt | Everything, with the weak reader and the target model, on each input shape |

A cold read proves the page can be understood. Whether the executor then behaves well is a separate question, answered by runs ([measure.md](measure.md)).
