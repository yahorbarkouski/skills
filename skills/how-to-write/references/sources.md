# Sources

This file is for whoever maintains the skill. Each entry names a rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

SKILL.md and the other references state each rule's reason in plain words, with no study names or numbers. The agent following the skill needs the reason to handle cases no rule covers. The evidence belongs to the maintainer, so it stays in this file.

Strength labels:
- **measured**: a peer-reviewed or well-documented study
- **preprint**: one study, not yet reviewed
- **vendor**: guidance from a model provider or tool vendor, with no published method
- **practice**: reasoned practice, or a technique from another skill, with no direct study

Sources were checked in September 2026.

## Why writers leave gaps

- **Writers can't see what their reader lacks.** Measured. Camerer, Loewenstein, and Weber, "The Curse of Knowledge in Economic Settings" (Journal of Political Economy 97(5), 1989): better-informed people could not set aside what they knew when predicting less-informed people's judgments, and market incentives only halved the bias. Newton, "The Rocky Road from Actions to Intentions" (Stanford PhD dissertation, 1990): people tapping a song's rhythm predicted listeners would name 50% of the songs; listeners named 3 of 120, or 2.5%. https://gwern.net/doc/psychology/cognitive-bias/illusion-of-depth/1990-newton.pdf
- **People overestimate how much of their own state others can see.** Measured. Gilovich, Savitsky, and Medvec, "The Illusion of Transparency" (Journal of Personality and Social Psychology 75(2), 1998).
- **Experts can't correct this by trying harder, which is why the check uses an outside reader.** Measured. Hinds, "The Curse of Expertise" (Journal of Experimental Psychology: Applied 5(2), 1999): experts underestimated how long novices take, and debiasing interventions did little. An exact percentage circulates online without a source, so don't cite one.
- **Language models presume shared context too.** Measured. Shaikh et al., "Grounding Gaps in Language Model Generations" (NAACL 2024): model generations were 77.5% less likely than human ones to contain grounding acts such as clarifying questions and acknowledgments, and instruction tuning reduced them further. https://arxiv.org/abs/2311.09144
- **Agents fail to reason about what other agents know.** Preprint. HiddenBench (arXiv 2505.11556): with information split between agents, groups reached 30.1% accuracy, against 80.7% for one agent given everything. https://arxiv.org/abs/2505.11556 PerspectiveGap (arXiv 2606.08878, 2026) found orchestrator models rarely gave each sub-agent the right information: pass rates averaged 15% to 17%. Its failures include over-sharing as well as omitting, so it supports "calibrate to the reader" more than "always add context". https://arxiv.org/abs/2606.08878

## Name the reader, and put the missing context on the page

- **Decide who reads and what they know before writing.** Practice, following from the evidence above. No study compares writing with and without an explicit reader profile.
- **The list of things only the writer knows** (coined names, "as discussed", relative dates, unopenable paths). Practice. It is the same list the how-to-prompt skill uses for prompts.
- **Leave out what the reader already knows.** Measured, for instructional material. Mayer's coherence principle: removing extraneous material improved learning in 18 of 19 tests (median d = 0.86). Mayer, "143 Research-Based Principles for Designing Multimedia Instruction" (2023), summarizing *Multimedia Learning*, 3rd edition (2021).

## Lead with the point, then show it

- **Put the conclusion first.** Practice. US Army Regulation 25-50 requires "bottom line up front" in Army writing, and the Minto pyramid principle says the same. No controlled study of the ordering was found.
- **Concrete worked examples help readers learn.** Measured. Sweller and Cooper (Cognition and Instruction 2(1), 1985): students who studied worked examples solved similar problems in about half the time with about a fifth of the errors. Atkinson, Derry, Renkl, and Wortham (Review of Educational Research 70(2), 2000) review the design principles, including using several varied examples.
- **Give the example before the rule.** Practice. The worked-example evidence supports examples, but no clean study compares example-first with rule-first ordering.
- **Draw structures and flows.** Measured. Mayer's multimedia principle: words with graphics beat words alone in 13 comparisons, median d = 1.35 in Mayer's studies. Cromley and Chen (Educational Research Review 49, 2025), across 181 studies, found a smaller but real effect, g ≈ 0.39.
- **Show only what the text discusses, and put the prose right after the diagram.** Measured. Mayer's coherence principle (above), spatial contiguity (9 of 9 tests, d = 0.82), and Chandler and Sweller's split-attention effect (Cognition and Instruction 8(4), 1991): integrating text and diagram beats presenting them apart.
- **Skip the diagram when a sentence says the same thing.** Practice, loosely supported by Mayer's redundancy findings, whose effect is small (d = 0.10) and can reverse.

## Concise without gaps

- **Cut what does no work, never the context the reader lacks.** Practice. A systematic review of plain-language summaries (PMC9170105, 90 studies) found mixed, heterogeneous effects, and little evidence for specific formatting rules. Don't claim "shorter is better" as a measured result.
- **Don't compress into arrows, fragments, or shorthand.** Practice. It is rule 33 of the unslop skill, and the example at the top of SKILL.md shows the failure.

## The reader loop

- **Test the draft with a fresh reader that has none of the writer's context.** Vendor. Anthropic's doc-coauthoring skill runs a fresh Claude on the document to catch "things that make sense to the authors but might confuse others". https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring
- **Check questions with expected answers, not only the reader's own list of problems.** Measured. Rashkin, Clark, Huot, and Lapata, "Help Me Write a Story" (ACL 2025): models gave plausible, specific feedback but were weak at error detection, often missing the biggest problem in a text. https://arxiv.org/abs/2507.16007
- **Simulated readers can drive improvement.** Measured, adjacent. Nair et al., "Closing the Loop" (EMNLP 2024) trained a feedback generator against simulated student revisions (arXiv 2410.08058). It is not the same loop, but it shows simulated readers can steer revision.
- **Use a small, fast model as the test reader, and a new reader each round.** Practice, carried over from the how-to-prompt skill's cold read. A strong model fills gaps by guessing, and a reader that has seen a draft has learned it. No study validates either choice.
- **The loop improves clarity, and it doesn't check facts.** Practice, from this skill's own test. Four Sonnet agents wrote a handoff note from the same terse session notes for a new engineer (two per arm). A fresh reader playing that engineer, given only the note, answered 11 of 11 questions for both notes written with this skill, and 10 and 9 of 11 for the two written without it. The misses were an undefined provider name and "Thursday" left without a date. The skill's notes were also shorter (about 1,300 to 1,400 words against about 1,500) and both included a state diagram, but took three to four times as long to write. One skill-written note opened by calling the bug a double charge when the notes described a charge with no booking, and the reader loop couldn't catch it. With two runs per arm this is suggestive, not measured.
- **Stop after two or three rounds with no new gaps.** Practice. In building this skill, two rounds on SKILL.md found one real gap (whether a shortening request allows removing a rule), and the second round found none.

## Changing an existing document

- **Every model pass over a document damages it, mostly by altering text rather than deleting it.** Preprint. Laban, Schnabel, and Neville, "LLMs Corrupt Your Documents When You Delegate" (DELEGATE-52, arXiv 2604.15597, 2026): frontier models corrupted about 25% of content over long editing workflows. https://arxiv.org/abs/2604.15597
- **Change a fact everywhere it is stated.** Preprint and measured. EditPropBench (arXiv 2605.02083): the best editor missed about 30% of dependent updates. LEDGER (arXiv 2606.28379, ACL 2026): a dependency map raised cross-reference consistency from 56% to 76%.
- **Rewrites raise certainty and flatten voice.** Measured. "From 'May' to 'Is'" (arXiv 2606.07951, EMNLP 2026): certainty changed in up to 75% of rewrites, 1.5 to 2 times more often upward. "Voice Under Revision" (arXiv 2604.22142, preprint): voice-preserving prompts reduced but did not remove the flattening.
- **Replace a superseded statement instead of appending a correction.** Vendor and practice. Claude Code's memory docs say contradictory rules get followed arbitrarily. GitHub Spec Kit's `/clarify` replaces invalidated text and leaves no contradiction behind.
- **A request to shorten means reaching the length by rewording, not by refusing.** Practice, from this skill's own test. On a 1,640-word design document edited in four sequential requests (two runs per arm, Sonnet), agents without guidance cut it by 30% while keeping all 36 checked rules and values, but dropped two or three hedges each. Agents following an earlier, preservation-heavy version of this skill kept every hedge but cut only 5% to 11%, and proposed removals instead of meeting the request. The shortening rule now puts the target first.
- **Compare with the original using `scripts/doc_diff.py`.** Practice. It follows the idea of the docx skill's validation against the original file.

## Documents that agents act on

The evidence for [agent-docs.md](agent-docs.md), in brief:

- Agents follow what context files say, and generated context files add cost without helping. Preprint. Gloaguen et al., "Evaluating AGENTS.md" (arXiv 2602.11988, 2026): named tools were used 1.6 to 2.5 times per task against almost never when unnamed; LLM-generated files changed success by −0.5 to −2 points and raised cost over 20%.
- Skills models wrote for themselves scored 8 to 11.5 points below no skill at all, and focused skills beat exhaustive ones. Preprint. SkillsBench (arXiv 2602.12670).
- Stating expected behavior and constraints mostly prevents collateral damage. Preprint. SWE-Chain (arXiv 2605.14415): precision, which penalizes breaking passing tests, rose from 7.8% to 88.1%, while resolving rose from 62.6% to 66.1%.
- Vague targets cause out-of-scope actions, and damage warnings barely help. Preprint. "Coding Agents Are Guessing" (arXiv 2607.02294).
- Prohibitions fade over long sessions while requirements hold. Preprint, one author. arXiv 2604.20911.
- Summaries drop rules. Measured. "The Compaction Cliff" (arXiv 2608.22752, CIKM 2026): Claude Code's compaction kept 53% of safety rules after one round and 10% after five.

## Open questions

- No study tests whether a model-reader loop improves documents for human readers, or how well a model reader's confusion matches a person's.
- No study compares example-first with rule-first explanations directly.
- No study compares writing with and without an explicit reader profile.
