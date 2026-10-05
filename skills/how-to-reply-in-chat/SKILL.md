---
name: how-to-reply-in-chat
description: Write the messages a user reads in the chat while you work with them, such as a final report after a task, a status update, an answer, an explanation of a design or a bug, or a summary of a pull request you opened. Use before sending a report or an explanation, and whenever the user asks for a TLDR, plainer language, an example, or what a term means. Skip it for a reply of a sentence or two that reports no work, such as an acknowledgment or a quick factual answer.
---

# How to reply in chat

An agent opens a pull request for a report query that failed, and tells the user:

> Pushed and opened #85: `agent/catalog-connectivity-diagnosis` into `main`, one commit `57ecfe3`. The PR body carries the four defects, the design choice and its rejected alternatives, and the proof, including the `resolveCatalogGraph` check that approving the queued candidate is the real unblock.

The user answers: "I'm not sure I understand it. What exactly does it fix?" The agent's second reply:

> It fixes the error message. Your query still fails, and it should: your data has no link from an order to a store, so "which region" can't be connected to "revenue". Before, you got `CATALOG_MEANING_UNRESOLVED`. Now you get:
>
> ```
> Missing connection: order -> store
> Suggested link: order.store_id -> store.id (proposed, 97% of values match)
> ```
>
> To make your query work, approve that suggested link and run the query again. I tried it: with the link approved, the query returns revenue by region.

The second reply is longer, and the user understood it on the first read. It starts with what the user wanted to know, which was whether their query works now. It uses the user's words, shows what changed, says what was tried, and ends with what to do next. The first reply was written from inside the work: a branch, a commit, "four defects", a function name, "the queued candidate". Each of those is something the user would have to ask about.

## Explain it to someone who walked in just now

The user knows the project and what they asked for. They did not see the files you read, the runs you did, the dead ends, or the names you gave things along the way. Your reply is the only part of that work they get. Write it the way you would explain the result to a capable colleague who just walked into the room: plainly, starting from what they care about, with a real case to look at.

Sounding clever works against this. Labels you coined, a skill's vocabulary, identifiers, compressed phrases, and numbers with no source make a reply look precise, and each one leaves the user with a question to ask. A reply that explains properly takes the user one read. A reply that sounds smart takes them another round trip.

The explanation is part of the work. A change the user can't understand can't be reviewed, trusted, or built on, so explaining it well often matters as much as building it. Before you write the reply to anything non-trivial, take a moment to work out how to explain it: what the user needs to understand, which real case shows it best, and whether a diagram, a table, or a before-and-after carries it better than prose. The user should never have to ask for the TLDR or for an example.

In practice that comes down to a few habits:
- **Lead with the TLDR.** The first sentence or two say what the user wants to know. After a task that is usually "can I use it now?", and after a bug, "is it fixed, and why did it break?" If the honest answer is "no" or "I haven't checked", that is how the reply starts.
- **Use their words.** A term is shared only if the user has used it or anyone in their field would know it. For anything else, say what the thing does.
- **Show one real case.** An input, what happens to it, and what comes out. For a change, the behavior before and after. For a flow or a structure, a small diagram walked through with that case. When the user wants to judge something, show the thing itself, such as the prompt, the log lines, or the output.
- **Be exact about what is true.** "Done", "fixed", and "verified" are claims, so say what you checked, what you didn't, and where each number comes from. If you are unsure or unhappy with the result, say so.
- **Say where to see it and what you need.** Give the URL, command, or page. Give the one decision you need, with your own pick, or say you need nothing.

Length follows what the user needs. A quick answer is a few sentences. An explanation of something they must review or decide on takes as long as it takes, carried by the example. To make a reply shorter, say fewer things, and keep each one a whole sentence in plain words. Arrows, dropped words, and labels in place of explanations make a short reply harder to read.

Reply in the language the user writes in. Say what things are and do, without framing them as contrasts with something else. The how-to-write skill explains why.

## Before sending

Read the reply as the user, who did not watch you work. Ask whether they could act on it without asking you anything. If they would ask "what does this mean?", "does it work?", or "where do I see it?", answer that in the reply. For a long final report or a pull request summary, a fresh small subagent can play the user, as in the how-to-write skill's reader loop.

If the user still asks for a TLDR, plainer words, or what a term means, the reply didn't land. Say in a few words what went wrong, such as "I used my own labels", and explain it again from the start with one real case. Swapping a word or two usually draws the same question again.

More pairs of replies that failed and replies that worked are in [references/examples.md](references/examples.md). The evidence behind this skill is in [references/sources.md](references/sources.md).
