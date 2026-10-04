# skills

Agent skills I wrote. Each skill is a folder with a `SKILL.md` that Claude Code, Codex, and other agents that read the skill format can load.

| Skill | What it does |
|---|---|
| [how-to-prompt](skills/how-to-prompt/SKILL.md) | Write, review, and improve any text a model acts on: system prompts, per-request inputs, subagent briefs, tool descriptions, error feedback, and agent rules. It makes prompts self-sufficient, checks them sentence by sentence with a cold low-reasoning reader, renders input data instead of dumping JSON, improves prompts from counts over their runs, and measures changes with paired comparisons. |
| [how-to-write](skills/how-to-write/SKILL.md) | Write or revise any document another person or agent will read. It names the reader and what they already know, puts the context they lack on the page, leads with the point and a concrete example or diagram, and runs a loop in which a fresh subagent reads the draft cold, reports exactly what it couldn't follow, and the writer fills only those gaps. When changing an existing document, a bundled script compares it with the original to catch dropped, reworded, or moved content. |
| [how-to-route-judgment](skills/how-to-route-judgment/SKILL.md) | Decide what makes each judgment in software: plain code, a decision model such as TypeSafe's Jev, an LLM, or a person. It stops agents from guessing meaning with regexes and keyword lists, and from sending every closed yes-or-no or pick-one question to a slow LLM. It turns open questions into closed choices, routes on confidence by the cost of a wrong call, and includes a scanner that finds heuristics and closed-answer LLM calls in an existing codebase. |
| [how-to-run-llm-work](skills/how-to-run-llm-work/SKILL.md) | Decide where LLM work runs: on the coding harness's own subagents, or as an API call in code. Judging which solution is better, labeling or categorizing records, and extracting structure from documents run on subagents, as many in parallel as the harness allows, because the harness's subscription costs far less than API tokens and leaves no script or API key behind. API calls are for model calls the product, a scheduled job, or CI makes with no agent session, and for measuring a prompt the product will run. It covers sharding items across subagents, one brief for every shard, a pilot shard, judging with a panel, and a script that splits the input and checks the merged results. |
| [how-to-run-long-jobs](skills/how-to-run-long-jobs/SKILL.md) | Run any long or costly job, such as LLM or API calls over a dataset, a benchmark, a scrape, or a backfill, so that it runs on a small sample before the full dataset, saves every result the moment it arrives, and shows how far it has got at any time. A stopped or crashed run keeps everything it paid for and resumes where it stopped, and a run stops itself when every call fails or it reaches its budget. It includes a dependency-free Python helper that appends each result, resumes, prints progress with spend and time left, enforces a budget, draws stratified samples, and reports any run's status from its files. |
| [how-to-verify-work](skills/how-to-verify-work/SKILL.md) | Decide how to check your own work before telling the user it is done, and how much checking is enough. Before claiming, the agent does the user's first real action itself, such as one real API call, one run in the real app, or one query on the real data, with a check that can fail. Checks stay lean: a long loop such as a full test suite, an end-to-end run, or a paid benchmark runs only for a specific reason, checks whose result couldn't change the next step are skipped, and the report says what was and wasn't checked. |
| [how-to-reply-in-chat](skills/how-to-reply-in-chat/SKILL.md) | Write the messages a user reads in the chat: reports, status updates, answers, explanations, and pull request summaries. The user knows the project and didn't watch the agent work, so every reply leads with the TLDR, uses the user's words in place of names the agent made up, explains with a real example and a diagram or table where it helps, and says honestly what is done and checked. |

## Install

Clone the repository, then link each skill you want into your agent's skills directory:

```bash
git clone https://github.com/yahorbarkouski/skills.git ~/yahorbarkouski-skills
ln -s ~/yahorbarkouski-skills/skills/how-to-prompt ~/.claude/skills/how-to-prompt
ln -s ~/yahorbarkouski-skills/skills/how-to-write ~/.claude/skills/how-to-write
ln -s ~/yahorbarkouski-skills/skills/how-to-route-judgment ~/.claude/skills/how-to-route-judgment
ln -s ~/yahorbarkouski-skills/skills/how-to-run-llm-work ~/.claude/skills/how-to-run-llm-work
ln -s ~/yahorbarkouski-skills/skills/how-to-run-long-jobs ~/.claude/skills/how-to-run-long-jobs
ln -s ~/yahorbarkouski-skills/skills/how-to-verify-work ~/.claude/skills/how-to-verify-work
ln -s ~/yahorbarkouski-skills/skills/how-to-reply-in-chat ~/.claude/skills/how-to-reply-in-chat
```

For Codex, link into `~/.codex/skills/` instead. A linked skill picks up changes with `git pull`.

## License

MIT
