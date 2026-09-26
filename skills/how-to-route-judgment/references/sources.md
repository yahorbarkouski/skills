# Sources

This file is for whoever maintains the skill. Each entry names a rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

SKILL.md and the other references state each rule's reason in plain words. The evidence belongs to the maintainer, so it stays in this file.

Strength labels:
- **measured**: a peer-reviewed or well-documented study
- **independent**: a report from someone other than the vendor, without a published method
- **vendor**: the vendor's own documentation or benchmark
- **practice**: reasoned practice with no direct study

Sources were read in September 2026. Jev launched that month, so most evidence about it comes from TypeSafe and its launch partners.

## The idea

- **Code owns the control flow, and a model sits only where the system needs judgment about unstructured input.** Vendor. TypeSafe, "How to build with System One", which contrasts traditional code, LLM agents, and "AI-powered software", where "code handles deterministic work and owns the control flow. The model appears only where the system needs programmable common sense or needs to interpret unstructured data." https://docs.typesafe.ai/concepts/how-to-build-with-system-one
- **"Use code when you can."** Vendor. The same page: "Keep deterministic work in code. It is reliable and cheap. Avoid agent `while` loops," because "every loop introduces another opportunity to go off the rails."
- **"Cheap by default, frontier on exception."** Independent. LangChain, "Building Prod with Jev and LangGraph" (Runkle and Lovell, 2026-09-25), quoting Jaya Gupta's "Great Unbundling of Intelligence". https://www.langchain.com/blog/building-prod-with-jev-and-langgraph
- **Heuristics that guess meaning don't generalize.** Practice. It rests on the maintainer's experience that agents default to keyword and regex rules that miss new phrasings. No study was consulted.

## What a decision model is

- **Three answer types, full probabilities, no text generation, no choosing its own next action.** Vendor. TypeSafe's API reference and "Introducing System One models and Jev". Noul returns the probability of yes, Choice supports up to 255 options, and Score supports 2 to 10 levels. https://typesafe.ai/blog/introducing-system-one-models-and-jev
- **Context limit of 64,000 tokens, with state plus the longest question capped at 32,000.** Independent. Browserbase, "What is Jev". TypeSafe's pages don't state a limit. https://www.browserbase.com/blog/what-is-jev
- **Speed and cost.** Vendor: 70 to 500 ms per call, $0.042 per million input tokens, and free output. Independent: Browserbase reports Jev as 20 to 200 times faster and 40 to 400 times cheaper than LLMs on its tasks.
- **Consistency.** Vendor. TypeSafe's consistency cookbook reports a mean per-question probability standard deviation of 0.0102 across repeated runs, below every LLM condition tested, and notes that LLM answers move between runs even at temperature 0. https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook LangChain's internal eval benchmark found Jev's variance 92 to 913 times lower than three LLM judges, and 100% agreement with a human oracle against 80% to 99.8% for the LLMs. It is labeled as LangChain's own benchmark, with the caveat that results may not carry over to other workflows. https://www.langchain.com/blog/jev-agent-evals-langsmith

## Turning open questions into closed ones

- **Choose from what exists.** Independent. Browserbase rebuilt Stagehand's `act()` so that Jev picks the action type and the element from the marked interactive elements, with anything below 0.7 confidence falling back to an LLM. Median latency fell from 1.97 s to 0.46 s.
- **Ask every question about the same state in one call.** Vendor. TypeSafe evaluates questions "independently and in parallel" and recommends batching them.
- **Split exact parts from judgment parts, and compare in pairs.** Practice. This follows from the component definitions; no source tests it directly.

## Routing on confidence

- **Tiers set by the cost of a wrong action, not one cutoff.** Vendor. TypeSafe's confidence page: high confidence acts, medium confidence asks for confirmation or review, and low confidence routes to a person or another system. "A confidence threshold is not one number." Their confidence-routing pattern uses a 0.6 floor to a person and 0.85 for a high-stakes action, as examples.
- **Set thresholds from labeled examples.** Vendor. The consistency cookbook: "Set production boundaries from labeled examples and from the cost of incorrect decisions and of review," and warns that its own example band is "neither a calibrated guarantee nor an optimized threshold."
- **Spot-check a cheap, consistent decider.** Independent. LangChain: "Low cost can amplify mistakes — a consistently wrong evaluator can produce bad feedback at scale."
- **Store decisions with the work item so a rerun reuses them.** Independent. The LangChain post's case for checkpointing: a rerun of model-driven steps "might not retrace the same path".

## The fallback when Jev isn't available

- **A shared `decide()` interface, a trained classifier, or a small LLM constrained to the options.** Practice. TypeSafe names no alternatives, so this section is the skill's own guidance.
- **Don't use a confidence number the model writes itself. Use log-probabilities, or agreement across several samples.** Measured. Xiong et al., "Can LLMs Express Their Uncertainty?" (ICLR 2024): models are overconfident when they state their confidence, and consistency across multiple sampled answers helps, though no method won everywhere. https://arxiv.org/abs/2306.13063

## Changing an existing system

- **Find sites with a scanner that over-reports, then review each hit.** Practice. `scripts/find_judgment_sites.py` was checked on a small fixture with planted positives, and exact regexes such as order-ID and UUID formats as negatives. It found every positive and none of the negatives.
- **Compare old and new on 50 to 200 labeled real inputs, and replace one judgment at a time.** Practice, consistent with TypeSafe's advice to set boundaries from labeled examples.

## Open questions

- No independent study compares a decision model with heuristics on the same task.
- Nobody has measured how Jev's calibration holds up outside its launch partners' workloads.
- The fallback backends are untested against Jev on the same questions.
