# skills

Agent skills I wrote. Each skill is a folder with a `SKILL.md` that Claude Code, Codex, and other agents that read the skill format can load.

| Skill | What it does |
|---|---|
| [how-to-prompt](skills/how-to-prompt/SKILL.md) | Write, review, and improve any text a model acts on: system prompts, per-request inputs, subagent briefs, tool descriptions, error feedback, and agent rules. It makes prompts self-sufficient, checks them sentence by sentence with a cold low-reasoning reader, renders input data instead of dumping JSON, improves prompts from counts over their runs, and measures changes with paired comparisons. |
| [how-to-write](skills/how-to-write/SKILL.md) | Write or revise any document another person or agent will read. It names the reader and what they already know, puts the context they lack on the page, leads with the point and a concrete example or diagram, and runs a loop in which a fresh subagent reads the draft cold, reports exactly what it couldn't follow, and the writer fills only those gaps. When changing an existing document, a bundled script compares it with the original to catch dropped, reworded, or moved content. |
| [how-to-route-judgment](skills/how-to-route-judgment/SKILL.md) | Decide what makes each judgment in software: plain code, a decision model such as TypeSafe's Jev, an LLM, or a person. It stops agents from guessing meaning with regexes and keyword lists, and from sending every closed yes-or-no or pick-one question to a slow LLM. It turns open questions into closed choices, routes on confidence by the cost of a wrong call, and includes a scanner that finds heuristics and closed-answer LLM calls in an existing codebase. |
| [how-to-run-llm-work](skills/how-to-run-llm-work/SKILL.md) | Decide where LLM work runs: on the coding harness's own subagents, or as an API call in code. Judging which solution is better, labeling or categorizing records, and extracting structure from documents run on subagents, as many in parallel as the harness allows, because the harness's subscription costs far less than API tokens and leaves no script or API key behind. API calls are for model calls the product, a scheduled job, or CI makes with no agent session, and for measuring a prompt the product will run. It covers sharding items across subagents, one brief for every shard, a pilot shard, judging with a panel, and a script that splits the input and checks the merged results. |

## Install

Clone the repository, then link each skill you want into your agent's skills directory:

```bash
git clone https://github.com/yahorbarkouski/skills.git ~/yahorbarkouski-skills
ln -s ~/yahorbarkouski-skills/skills/how-to-prompt ~/.claude/skills/how-to-prompt
ln -s ~/yahorbarkouski-skills/skills/how-to-write ~/.claude/skills/how-to-write
ln -s ~/yahorbarkouski-skills/skills/how-to-route-judgment ~/.claude/skills/how-to-route-judgment
ln -s ~/yahorbarkouski-skills/skills/how-to-run-llm-work ~/.claude/skills/how-to-run-llm-work
```

For Codex, link into `~/.codex/skills/` instead. A linked skill picks up changes with `git pull`.

## License

MIT
