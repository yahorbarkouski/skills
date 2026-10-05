# Skills

[![skills.sh](https://skills.sh/b/yahorbarkouski/skills)](https://skills.sh/yahorbarkouski/skills)

These are the failures I keep running into, over and over, when I work with LLMs and coding agents. Each skill teaches an agent to avoid one of them.

## Install

```bash
npx skills@latest add yahorbarkouski/skills
```

Or clone the repository and link the skills you want into your agent's skills directory:

```bash
git clone https://github.com/yahorbarkouski/skills.git ~/yahorbarkouski-skills
ln -s ~/yahorbarkouski-skills/skills/how-to-verify-work ~/.claude/skills/how-to-verify-work
```

For Codex, link into `~/.codex/skills/`. A linked skill picks up changes with `git pull`.

## Reference

- **[how-to-verify-work](skills/how-to-verify-work/SKILL.md)**: Check your own work before saying it's done. Do the user's first real action once, with a check that can fail, keep checks lean, and say what was and wasn't checked.
- **[how-to-reply-in-chat](skills/how-to-reply-in-chat/SKILL.md)**: Write reports, answers, and explanations the user understands on the first read. Lead with the TLDR, use the user's words, and show one real example.
- **[how-to-write](skills/how-to-write/SKILL.md)**: Write documents for a reader who wasn't in your session. A fresh subagent reads each draft cold and reports what it couldn't follow.
- **[how-to-prompt](skills/how-to-prompt/SKILL.md)**: Write prompts, subagent briefs, and tool descriptions a model can act on with only the page, and improve them from their runs.
- **[how-to-route-judgment](skills/how-to-route-judgment/SKILL.md)**: Decide whether code, a decision model such as Jev, an LLM, or a person makes each judgment, so the agent stops guessing meaning with regexes and keyword lists.
- **[how-to-run-llm-work](skills/how-to-run-llm-work/SKILL.md)**: Run one-off LLM work, such as labeling, reviewing, or extracting, on the harness's own subagents in parallel, with no API key and no script left behind.
- **[how-to-run-long-jobs](skills/how-to-run-long-jobs/SKILL.md)**: Run long or paid jobs on a small sample first, save every result as it arrives, show progress, resume after a stop, and stop at a budget.

## License

MIT
