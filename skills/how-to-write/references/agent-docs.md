# What a document agents act on should say

Agents do what these documents say, so every line changes behavior and costs tokens in every session. Write the lines that prevent real mistakes, and cut the rest.

## The file every session loads

This covers AGENTS.md, CLAUDE.md, and rules files that load at the start of every session.

- Make it a map. It holds what is true across the whole project and points to the rest. Aim for under 200 lines. The reason is cost and upkeep: every line costs tokens in every session, and a stale line misleads. Length by itself doesn't seem to make agents ignore rules, so don't cut a needed rule just to hit a line count.
- Test each line by asking whether removing it would cause a mistake an agent actually makes. If it wouldn't, cut the line.
- Keep:
  - the commands to build, test, lint, and run
  - conventions an agent would get wrong
  - pitfalls, and where things live when that isn't obvious
  - what must not be touched, and why
- Cut:
  - directory tours and dependency lists
  - restatements of the README
  - generic advice such as "write clean code"
  - rules a linter already enforces
- Check each new rule against the existing ones. Given two rules that contradict each other, an agent may follow either.
- Review a generated version line by line before you keep it. A model writing about a repository tends to repeat what the repository already says, which adds cost without helping.
- When the model changes, try removing instructions written for the older model. Instructions that were once needed are often too prescriptive for newer models.

## Specs and requirements

- Besides the problem, state the behavior you expect and the constraints. Include what must keep working. Given only the problem, an agent tends to fix it and break what worked before.
- Name exact targets: which files, services, and environments are in scope, and what must not change. Vague targets are a common cause of out-of-scope changes, and warnings about possible damage don't make up for them.
- Write acceptance criteria as checks. A check can be a command and its expected output, a test that fails before the change and passes after it, or a Given/When/Then statement.
- Give each requirement one testable statement and a stable ID.
- Mark unknowns as unknown, for example in a short list of open questions. Record any guess you make as an assumption, so a reader can find and overturn it.
- Specify what must be true, at the level of detail you are sure of. A wrong plan does more harm than no plan, and wrong low-level details cascade into the implementation.

## Plans that change as work proceeds

A plan should hold enough for someone to restart the work from the plan alone. It needs these sections:

- **Goal and context.** Say what the work is, why it is needed, and for whom. Define every term and give full paths.
- **Progress.** Use checkboxes with dates, updated at every stopping point.
- **Discoveries.** Record what turned out different from what you expected, with the evidence.
- **Decision log.** Record each decision with its reason and its date.
- **Failed approaches.** Record what was tried and why it failed. Without this, the next session tries the same dead ends.
- **Remaining work.** List each piece, with how to check that it works.

Update it like this:

- Update the plan at every stopping point.
- When a decision changes, update every section it affects. Add a dated line to the decision log saying what changed and why. Don't leave the old plan text next to the new text.
- Before you mark an item done, check it against a tool result, such as a test run or a command's output. A status written from memory is where false "done" marks come from.
- Some status must be updated by agents but never rewritten, such as a list of features with pass or fail flags. Keep it in a structured file such as JSON, and say which fields may change. Models are less likely to rewrite JSON than Markdown.
- Let one agent write to the plan at a time.
- In a long run, have the agent reread the plan periodically. Agents tend to drift from a plan they read only once.

## Handoff and progress notes

When a session ends, or before context is compacted, write a note the next agent can start from with nothing else. It holds:

- the goal, and the user's constraints in the user's own words, in a section of their own
- the current state: what works, what has been checked, and how
- the decisions made and their reasons, and the approaches that failed and why
- the open items and the next step
- details that are hard to rebuild, such as exact error messages, IDs, and commands, copied verbatim

Summaries keep facts and drop restrictions, and each further round of summarizing drops more. Keep hard rules in a file loaded from disk every session.

## When length rules conflict

- A task plan should be self-contained, so put what the task needs in the plan. A standing document, such as AGENTS.md or a design doc, should link to details, because copies go stale.
- Long specs are hard to review, and reading a plan is not the same as checking it. Keep a spec to what its reviewer can check.
