# Agent instructions

This repository holds agent skills, one folder per skill under `skills/`. Each folder has a `SKILL.md` and a `references/sources.md` that records the evidence behind each of the skill's rules.

## Cut every new skill with skill-cutter before committing it

Before you commit a new skill, or a change that rewrites an existing skill's description or most of its `SKILL.md`, run skill-cutter on that skill in Cut mode. skill-cutter, from [swyxio/skills](https://github.com/swyxio/skills/tree/main/skill-cutter), trims a skill to the instructions a capable agent would get wrong without it, and narrows the skill's description to the requests that should load the skill. skill-cutter's own description says to use it only when a user asks to cut a skill, so it will not load by itself while you write one. Load it by name, with the Skill tool in Claude Code or as `$skill-cutter` in Codex. Once loaded, it explains Cut mode and the report it writes at the end.

If skill-cutter is missing from your list of skills, install it:

```bash
git clone --depth 1 https://github.com/swyxio/skills.git ~/swyxio-skills
ln -s ~/swyxio-skills/skill-cutter ~/.claude/skills/skill-cutter
ln -s ~/swyxio-skills/skill-cutter ~/.codex/skills/skill-cutter
```

While you cut:

- Read a rule's entry in the skill's `references/sources.md` before you cut the rule, and delete the entry when the rule goes.
- Test the description by routing. Write about ten requests, half that should load the skill and half nearby ones that should skip it, and note where you expect each one to land. Give a fresh subagent the name and description of every installed skill, plus the requests, and ask which skills it would load for each request. Change the description until every request lands where you expected.
- After you change a description, run `npx skills add . --list` from the repository root. It should find every skill and print no "Skipped" line. The skills CLI skips a skill whose frontmatter fails to parse, such as a description with a colon followed by a space. skills.sh lists only skills installed through that CLI, so a skipped skill never appears there.
- Before you commit, give the user skill-cutter's report and the routing results.
