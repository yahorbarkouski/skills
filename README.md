# skills

Agent skills I wrote. Each skill is a folder with a `SKILL.md` that Claude Code, Codex, and other agents that read the skill format can load.

| Skill | What it does |
|---|---|
| [how-to-prompt](skills/how-to-prompt/SKILL.md) | Write, review, and improve any text a model acts on: system prompts, per-request inputs, subagent briefs, tool descriptions, error feedback, and agent rules. It makes prompts self-sufficient, checks them sentence by sentence with a cold low-reasoning reader, renders input data instead of dumping JSON, improves prompts from counts over their runs, and measures changes with paired comparisons. |

## Install

Clone the repository, then link each skill you want into your agent's skills directory:

```bash
git clone https://github.com/yahorbarkouski/skills.git ~/yahorbarkouski-skills
ln -s ~/yahorbarkouski-skills/skills/how-to-prompt ~/.claude/skills/how-to-prompt
```

For Codex, link into `~/.codex/skills/` instead. A linked skill picks up changes with `git pull`.

## License

MIT
