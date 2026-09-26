# Sources

This file is for whoever maintains the skill. Each entry names the rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

Strength labels:
- **measured**: a peer-reviewed or well-documented study
- **preprint**: one study, not yet reviewed
- **vendor**: guidance from a model provider with no published method
- **practice**: reasoned practice with no direct study

## Knowing the reader

- **Give a capable agent the goal and leave the method to it.** Practice, with one observation behind it. In Singh et al. (arXiv 2609.26261, 2026), a coding agent given a one-paragraph goal with no procedure arrived at the same sound analysis workflow across independent runs. Nobody has compared this against prescribing the method.
- **Contract layer for validated production calls.** Practice. It comes from maintaining prompts whose responses a strict validator checks. Every validator rule the model can break has to be on the page, or the model cannot avoid breaking it.

## Self-sufficiency

- **Leaving requirements unstated makes prompts fragile, and stating too many at once also costs.** Measured. Yang et al., "What Prompts Don't Say" (arXiv 2505.13360, 2025/2026). Unstated requirements regressed about twice as often across model and prompt changes. Stating many requirements together lowered compliance with each one. https://arxiv.org/abs/2505.13360
- **Deliver context in one message.** Measured. Laban et al., "LLMs Get Lost in Multi-Turn Conversation" (ICLR 2026). A request split across turns lost about 39% of its performance, and merging the pieces into one prompt recovered most of it. https://arxiv.org/abs/2505.06120
- **Authors leave out background when they write prompts for other agents.** Preprint. PerspectiveGap (arXiv 2606.08878, 2026) found models omitting shared background from worker-role prompts. HiddenBench (ICML 2026) found agents do not notice when information is split between them. https://arxiv.org/abs/2606.08878, https://arxiv.org/abs/2505.11556
- **Say when the executor should ask.** Measured. Ambig-SWE (ICLR 2026) showed that agents rarely ask unless prompted, and that asking recovers much of the lost performance. Grounding Gaps (NAACL 2024) showed that models presume common ground. https://arxiv.org/abs/2502.13069, https://arxiv.org/abs/2311.09144
- **Keep hard constraints where they are never summarized away.** Preprint. "Governance Decay" (arXiv 2606.22528, 2026) found that constraints lost during context compaction stopped being obeyed. https://arxiv.org/abs/2606.22528
- **A brief states the objective, output format, tools, and boundaries.** Vendor. Anthropic, "How we built our multi-agent research system" (2025). https://www.anthropic.com/engineering/multi-agent-research-system

## Cold read

- **Show the prompt to a reader with no context.** Vendor. This is Anthropic's "colleague" test.
- **Use a weak model as that reader, sentence by sentence.** Practice. No study validates weak models as clarity testers. The rule stands because it is cheap and finds gaps, and because runs, not the cold read, decide whether a prompt works.

## Input rendering

- **No syntax is best for every model.** Measured. He et al., arXiv 2411.10541 (2024); Sclar et al., FormatSpread (ICLR 2024). Both were run on older models, and strong models show smaller effects. https://arxiv.org/abs/2411.10541, https://arxiv.org/abs/2310.11324
- **Meaningful names and descriptions help.** Measured. Wretblad et al. (arXiv 2408.04691, 2024) and SNAILS (SIGMOD 2025) on text-to-SQL. Anthropic, "Writing effective tools for agents" (2025), on replacing opaque IDs with meaningful language (vendor). https://arxiv.org/abs/2408.04691, https://www.anthropic.com/engineering/writing-tools-for-agents
- **Irrelevant content hurts.** Measured, by a vendor. Chroma, "Context Rot" (2025), covering 18 models. https://www.trychroma.com/research/context-rot
- **Long material first, the question last, and the key instructions restated after very long material.** Vendor, plus measured on older models. Anthropic's prompting docs; OpenAI's GPT-4.1 prompting guide; Liu et al., "Lost in the Middle" (TACL 2024). https://arxiv.org/abs/2307.03172
- **Marking content as data reduces injection but does not stop it.** Measured. Hines et al., "Spotlighting" (arXiv 2403.14720, 2024); Debenedetti et al., AgentDojo (NeurIPS 2024 Datasets and Benchmarks). https://arxiv.org/abs/2403.14720, https://arxiv.org/abs/2406.13352
- **Tool descriptions say when to use the tool, and parameters and results carry meaning.** Vendor. Anthropic, "Writing effective tools for agents" (2025).
- **Tag each document instead of using a JSON array of documents.** Vendor. OpenAI's GPT-4.1 guide reports JSON doing poorly for long document lists but publishes no data.
- **Measure compact notations before adopting one.** Preprint. "Notation Matters" (arXiv 2605.29676, 2026) found token savings at an accuracy cost, and poor results when models had to write the notation. https://arxiv.org/abs/2605.29676

## Output

- **Reasoning comes before the answer, and schema design matters more than JSON itself.** Measured, and contested. "Let Me Speak Freely?" (Tam et al., 2024) found large drops, but those came from a schema in the prompt and from answer-before-reasoning key order. Later work finds structured output at or near parity for strong models when reasoning comes first: JSONSchemaBench (2025), CRANE (ICML 2025), and "Capacity, Not Format" (arXiv 2606.09410, 2026). https://arxiv.org/abs/2501.10868, https://arxiv.org/abs/2502.09061, https://arxiv.org/abs/2606.09410

- **Models copy examples, so vary them.** Measured on older models. Zhao et al., "Calibrate Before Use" (ICML 2021) found majority-label and recency bias from examples. Min et al., "Rethinking the Role of Demonstrations" (EMNLP 2022) found that format and label space carry much of an example's effect. Both Anthropic's and OpenAI's prompting guides give the same advice (vendor). https://arxiv.org/abs/2102.09690, https://arxiv.org/abs/2202.12837

## Keeping it lean

- **Contradictions do more damage than gaps.** Vendor. OpenAI's GPT-5 prompting guide warns that contradictory instructions waste reasoning and degrade results. Yang et al. (above) found that piling on requirements lowers compliance with each one.
- **State rules calmly, without all-caps emphasis.** Vendor. Anthropic's prompting docs for recent Claude models say that aggressive emphasis now causes over-application.

## Improving from runs

- **Distill rules from corpus-wide counts in one pass, with no search loop.** Preprint. Singh et al., "Coding Agents are Strong Prompt Optimizers" (arXiv 2609.26261, 2026). That paper covers one target model, small test sets, and no ablation isolating the counting. https://arxiv.org/abs/2609.26261
- **Explicit rules can replace much of the reasoning a cheap model would need.** Preprint. Same paper, from its comparison against the same model with reasoning turned on.
- **Gating on a small validation set overfits it.** Measured. The optimizer's curse (Smith and Winkler, 2006); the reusable holdout (Dwork et al., 2015).

## Measurement

- **Binomial noise sets the smallest difference worth reporting.** Calculation: sqrt(p(1-p)/n).
- **Compare variants on the same items, report paired differences with standard errors, and separate seed noise from item noise.** Measured. Miller, "Adding Error Bars to Evals" (arXiv 2411.00640, 2024). https://arxiv.org/abs/2411.00640
- **Tests never assert prompt wording.** Practice. A wording assertion fails on every edit and passes on every wrong prompt. Behavior is measured with runs.
