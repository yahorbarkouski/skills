# Sources

This file is for whoever maintains the skill. Each entry names a rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

SKILL.md and the other references give each rule's reason in plain words. The evidence stays in this file.

Strength labels:
- **measured**: a peer-reviewed or well-documented study
- **independent**: a report from someone other than the vendor, without a published method
- **vendor**: the vendor's own documentation or benchmark
- **practice**: reasoned practice with no direct study

Sources were read on 2026-10-01.

## Where the work runs

- **Harness subagents cost less than API calls for one-off work.** Vendor. Claude Pro and Max plans "offer usage limits that are shared across Claude and Claude Code", and Claude Code bills as API usage when `ANTHROPIC_API_KEY` is set (https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan). Codex is included in ChatGPT plans, and Codex run with an API key bills at API prices (https://learn.chatgpt.com/docs/pricing). Cursor's paid plans include a monthly amount of usage, can add on-demand usage, and charge some models at their API price (https://cursor.com/docs/account/pricing). The Anthropic and OpenAI APIs bill per million tokens (https://platform.claude.com/docs/en/about-claude/pricing, https://developers.openai.com/api/docs/pricing). That a flat plan is cheaper per token than the API for a developer who uses it heavily is the maintainer's premise; no source compares the two directly.
- **Subagents have tools, and an API call sees only what is sent.** Practice. It follows from how harness subagents and API calls work.
- **Measuring a product prompt needs the product's model, settings, and prompt.** Practice. A subagent runs on the harness's model with the harness's system prompt and tools, so its answers measure a different call. The how-to-prompt skill's measurement rules assume the same.
- **Each subagent loads the harness's system prompt and tool definitions.** Practice. Observed in Claude Code: a Haiku subagent labeling 20 app reviews of under 75 characters each, about 1,000 tokens of input, reported 49,819 tokens used, and a subagent given a 3,500-token prompt and one tool call reported about 56,000. Most of each figure is the harness's own context, read again on every model turn. No vendor publishes the per-subagent overhead.

## Choosing a setup

- **Move bulk work out of the main context.** Vendor. Claude Code: "Each subagent starts with a fresh, isolated context window" (https://code.claude.com/docs/en/sub-agents). Cursor's subagents also have their own context windows (https://cursor.com/docs/subagents). That a crowded context degrades the rest of the task is practice.

## Fanning out

- **Several items per shard, but not too many.** Measured, on older models. Cheng, Kasai, and Yu, "Batch Prompting: Efficient Inference with Large Language Model APIs" (2023, arXiv 2301.08721), cut cost "up to 5× with 6 samples in each batch" with comparable accuracy, but "performance typically decreases as b increases, with a significant drop at b = 6 across four out of five datasets", and more so for long inputs and hard tasks. They tested 1 to 6 samples per prompt on Codex and the GPT-3 to GPT-4 models. The skill's 20 to 50 short records per shard is practice for current models working through a file with tools, and the pilot shard is there to catch a shard that is too large. The floor of about 20 comes from the startup overhead above: with 20 items per shard, the overhead was still most of a shard's tokens.
- **Models use the middle of a long input worse.** Measured. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023, arXiv 2307.03172): performance "is often highest when relevant information occurs at the beginning or end" and "significantly degrades" when it sits in the middle.
- **Subagent calls in one message run concurrently.** Vendor. Cursor: "Agent sends multiple Task tool calls in a single message, so subagents run simultaneously" (https://cursor.com/docs/subagents). Claude Code's documentation says "multiple subagents can run concurrently" (https://code.claude.com/docs/en/agent-sdk/subagents), and its system prompt tells the agent to send independent agents in a single message so they run concurrently.
- **Concurrency limits.** Vendor. Claude Code: 20 concurrent subagents by default, changed with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (https://code.claude.com/docs/en/sub-agents). Its `Workflow` tool runs up to 16 agents at once by default (https://code.claude.com/docs/en/workflows). Codex: `agents.max_concurrent_threads_per_session`, with no documented default (https://learn.chatgpt.com/docs/config-file/config-reference). Cursor: no documented cap.
- **Codex starts subagents on a direct request or a skill instruction.** Vendor. "Current local Codex releases spawn agents after a direct request or applicable project or skill instruction" (https://learn.chatgpt.com/docs/agent-configuration/subagents).
- **A model per subagent.** Vendor. Claude Code's `model` parameter (https://code.claude.com/docs/en/sub-agents), Codex agent files and `agents.default_subagent_model`, and Cursor's `model` field.
- **Fan-outs use many tokens.** Vendor. Anthropic, "How we built our multi-agent research system" (2025-06-13): "multi-agent systems use about 15× more tokens than chats", and running subagents and their tool calls in parallel "cut research time by up to 90% for complex queries" (https://www.anthropic.com/engineering/multi-agent-research-system).
- **Batch APIs cost half and return within a day.** Vendor. Anthropic's Message Batches: "All usage is charged at 50% of the standard API prices", most batches finish within an hour, and a batch expires after 24 hours (https://platform.claude.com/docs/en/build-with-claude/batch-processing). OpenAI's Batch API: a 50% discount and a 24-hour completion window (https://developers.openai.com/api/docs/guides/batch).
- **A sample of 3,000 estimates a proportion to within about two points.** Measured, by arithmetic. The 95% margin for a proportion near 0.5 is 1.96 × √(0.25 / 3000), about 1.8 percentage points.
- **Pilot one shard, merge in code, spot-check, and save results.** Practice. A model's answers on borderline items change between runs, which is why later steps read the saved file. In the end-to-end test below, the pilot caught three brief mistakes, and the spot check after the full run caught two more that the pilot shard didn't contain, which is why a wrong brief is fixed and every shard rerun.

## Judging with a panel

- **Several judges beat one.** Measured. Verga et al., "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models" (2024, arXiv 2404.18796): a panel of smaller models "outperforms a single large judge, exhibits less intra-model bias", and costs over seven times less. Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (2022, arXiv 2203.11171): the majority answer across sampled reasoning paths beats a single path. The skill's panel uses one model in several fresh subagents, which is closer to self-consistency than to Verga's mix of models.
- **Models favor the answer shown first, and the longer answer.** Measured. Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023, arXiv 2306.05685), found position bias and verbosity bias, and recommend judging each pair in both orders and declaring a win only when it holds in both. The skill splits the two orders across judges and counts a pair as a tie when every judge picks whichever candidate it saw first.
- **Models favor their own output.** Measured. Panickssery, Bowman, and Feng, "LLM Evaluators Recognize and Favor Their Own Generations" (2024, arXiv 2404.13076), found "a linear correlation between self-recognition capability and the strength of self-preference bias". Zheng et al. could not establish self-enhancement bias with their data, so don't cite them for it.
- **Check what code can check before judging, and write the criteria first.** Practice.
- **Reasons before the verdict.** Practice, consistent with the how-to-prompt skill's rule that reasoning comes before the answer.

## End-to-end test

- On 2026-10-01, a fresh Sonnet agent in Claude Code got this skill and a task: tag 120 app reviews in a CSV with a topic and a sentiment for a one-time report, with the `anthropic` and `openai` packages installed. It made no API call. It split the CSV into 6 shards of 20 with `fanout.py`, ran a pilot on Haiku, fixed the brief, started the 6 shards in one message (their output files were written within 12 seconds of each other), revised the brief after the spot check, reran all 6, and delivered 120 of 120 items with a clean merge, using about 658,000 subagent tokens in 13 subagents. Its report led to repeatable `--field` checks and `--keep` in `merge`, the rule to fix a wrong brief and rerun every shard, the pilot rule based on the cost of redoing the fan-out, and the rule that sets the number of shards.

## fanout.py

- The script was checked on a 120-row CSV split into shards of 50, with simulated outputs containing a missing ID, a duplicate, an unknown ID, a value outside `--allowed`, an unparseable line, and a shard with no output file. `merge` reported each one, named shards 002 and 003 to rerun, and exited with status 1. Two `--field` checks and `--keep` were checked on the end-to-end test's shards, where `merge` exited 0 and wrote only the ID and the two answer fields. Directory and plain-text inputs, `--shards`, the `--max-chars` cap, and the refusal to reuse a shard directory were checked on small fixtures.

## Open questions

- No source measures how many short items one subagent can label before accuracy drops, for current models.
- No source compares the cost of a flat plan and the API for the same fan-out.
- Codex's default concurrency cap is undocumented.
