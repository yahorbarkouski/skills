# Sources

This file is for whoever maintains the skill. Each entry names a rule, what supports it, and how strong the support is. Before changing a rule, check its basis here. When you add a rule, add its basis.

SKILL.md and the other references give each rule's reason in plain words. The evidence stays in this file.

Strength labels:
- **measured**: a peer-reviewed or well-documented study
- **preprint**: one study, not yet reviewed
- **vendor**: guidance from a model provider or tool vendor, with no published method
- **practice**: reasoned practice, or the maintainer's own sessions, with no controlled study

Sources were read on 2026-10-04.

## Why the skill exists

- **The maintainer's sessions.** Practice, from a count. 540 incidents were mined from 413 Claude Code and Codex sessions over 30 days. About 45 were replies he couldn't follow. Across all his messages, asks for examples appear in 83 sessions, "I don't understand" in 55, "clear language" in 39, "are you sure / have you tested" in 30, TLDR in 23, and "how do I open it / what commands" in 21. Forked sessions inflate these counts.
- **Length doesn't separate the replies he accepted from the ones he couldn't use.** Practice, from his sessions. In 22 matched pairs (a reply he couldn't follow and the reply he accepted for the same question), the median was 532 words against 511, and the accepted reply was longer in 10 pairs. Across 2,299 exchanges, clarification requests rose only from 1.7% after replies under 100 words to 5.8% after replies over 1,000 words, and approvals also rose with length. What changed between the failing and the accepted reply was the first sentence, the vocabulary, and a running example. This is why the skill sets length by the reader's job.
- **The TLDR and the example come unasked, and the explanation is worth thought.** Practice, the maintainer's direction on 2026-10-04: "we should not expect the user to ask for a TLDR. We should expect the agent to actually give the TLDR right away, with clear examples, diagrams, and whatever. [...] the agent should spend a little time reasoning and understanding how to properly format and explain things. Explaining things sometimes is even more important than implementing things." His sessions agree: TLDR requests appear in 23 sessions and nearly always add "with clear examples".
- **Direction over rules.** Practice, the maintainer's direction on 2026-10-04: "too many rules don't help [...] it's all about the overall direction and understanding that we should not sound over-smart and we should explain properly." An earlier draft with numbered rules, per-reply templates, and a lint script was cut to the direction and five habits.
- **Status words carried more than they proved.** Practice, from his sessions. In 24 documented cases a report said "ready", "done", "verified", "live", "healthy", "green", or "published" about something that was partly done or untested. None was caught by the agent's own checks before the report. He found them by using the product, reading the data, or asking a pointed question.

## Answer the question first

- **Readers take the first thing mentioned as the main point.** Measured. Kieras, "Initial mention as a signal to thematic content in technical passages" (Memory & Cognition 8(4), 1980), and "Good and bad structure in simple paragraphs" (Journal of Verbal Learning and Verbal Behavior 17(1), 1978): readers built the main idea from what came first, and paragraphs without the topic first took longer to read and were recalled worse. A report that opens with process makes the process its point.
- **Context before content.** Measured. Bransford and Johnson, "Contextual prerequisites for understanding" (JVLVB 11(6), 1972): context given before a passage raised comprehension, and the same context given after it did not.
- **Bad news first, without a buffer.** Measured. Locker, "Factors in reader responses to negative letters" (Journal of Business and Technical Communication 13(1), 1999): buffer openings didn't improve responses, and readers reacted worst when bad news surprised them.
- **A caveat placed after the headline isn't acted on.** Practice, from his sessions: in four of the 24 status cases the true fact was in the same message as the overstatement, after the headline.
- **The full inverted pyramid is not supported.** Measured. Yaros, "Is it the medium or the message?" (Communication Research 33(4), 2006): for non-experts, an explanatory structure beat inverted-pyramid news stories. So the skill puts the answer first and then builds the explanation in order.
- **Vendor and practice agreement.** US Army AR 25-50 ("bottom line up front"). Claude Code's system prompt: "Lead with the answer or outcome. If something could not be verified, say so first." OpenAI's GPT-6 Codex prompt: "Lead with the outcome and then develop your reasoning." No study tests answer-first in chat replies.

## Use only words the reader has

- **Short labels are earned through the partner's acceptance, and don't transfer.** Measured. Clark and Wilkes-Gibbs, "Referring as a collaborative process" (Cognition 22(1), 1986): descriptions shortened from 41 to 8 words per figure only as the partner accepted them. Brennan and Clark, "Conceptual pacts and lexical choice in conversation" (JEP: LMC 22(6), 1996): with a new partner, speakers dropped the agreed term. Hawkins, Frank, and Goodman (Cognitive Science 44(6), 2020) found the same in text chat. A label an agent coins in its own work, or agrees with a subagent, has been agreed with nobody the user can see. This is the basis for "the reader shares a term only if they have used it themselves".
- **Language models presume common ground.** Measured. Shaikh et al., "Grounding Gaps in Language Model Generations" (NAACL 2024): models produced far fewer grounding acts than people, and preference tuning reduced them further. https://arxiv.org/abs/2311.09144
- **Writers overestimate how well they were understood.** Measured. Keysar and Henly, "Speakers' overestimation of their effectiveness" (Psychological Science 13(3), 2002): speakers who thought they were understood were wrong 46% of the time. Kruger, Epley, Parker, and Ng, "Egocentrism over e-mail" (JPSP 89(6), 2005). Horton and Keysar (Cognition 59(1), 1996): adjusting for the listener drops out under time pressure.
- **Jargon lowers fluency, and available definitions didn't fix it.** Measured. Bullock, Colón Amill, Shulman, and Dixon, "Jargon as a barrier to effective science communication" (Public Understanding of Science 28(7), 2019), N = 650, with definitions available by mouse-over. Shulman et al. (Journal of Language and Social Psychology 39(5-6), 2020) reports the same data. This is the basis for preferring a rewrite over a definition. Shulman and Bullock (PLOS ONE 15(10), 2020) found jargon had no effect on an urgent topic, so standard terms the user already uses are fine.
- **Expanding abbreviations raises comprehension.** Measured. Grossman Liu et al. (JAMA Network Open 5(5), 2022), a randomized trial: 95% comprehension with abbreviations expanded against 62% without.
- **Vendor agreement.** Claude Code: "Do not refer to anything by a name you made up during the session." Anthropic's Fable 5 prompting page: "The vocabulary you built up while working is yours, not theirs." GPT-6 Codex: "Avoid invented compound labels". The Federal Plain Language Guidelines: "It's better to take the time to rewrite to avoid needing to define a term."
- **Skill vocabulary counts as private, and sounding clever costs a round trip.** Practice. Several reply templates in skills on the maintainer's machine name the skill's own terms (frontier, predicate, arm, lane, verdict), and those terms then appear in replies. The maintainer's sessions show "arms", "lane", "probe", "gate", "facet", and "judgement" in replies he couldn't follow.

## One concrete example, before and after

- **Concreteness drives comprehensibility.** Measured. Sadoski, Goetz, and Fritz (Journal of Educational Psychology 85(2), 1993): concreteness was "the variable overwhelmingly most related to comprehensibility and recall."
- **Examples beat restated definitions.** Measured. Rawson, Thomas, and Jacoby, "The power of examples" (Educational Psychology Review 27(3), 2015): d = 0.74 to 1.67. Example-first and example-after did about equally well, so the skill requires the example and only suggests its position.
- **Comparing two cases teaches more, and the principle works best after the comparison.** Measured. Alfieri, Nokes-Malach, and Schunn (Educational Psychologist 48(2), 2013), a meta-analysis of 57 experiments: d = 0.50. This is the basis for before-and-after.
- **An example in private notation doesn't help.** Practice, from his sessions: a worked example written in the reply's own coined terms drew the same "I don't understand".
- **Show the real artifact.** Practice. He asked for the exact prompt, the log, or the output 21 times in 17 sessions.

## Say exactly what is done, checked, and left

- **Agents' final messages overclaim.** Preprint. Smyth et al., "Quantifying Overclaiming Propensity in Frontier LLM Agents" (arXiv 2609.20812, 2026): agents left requested files unread in 67.9% of runs, and 80.4% of those runs claimed a full review or hid the gap. https://arxiv.org/abs/2609.20812
- **An explicit evidence requirement nearly removes false success.** Preprint. Zhu et al., "Failure-Transparent Agents" (arXiv 2609.35732, 2026): false success fell from 22.8% with no instruction to 0.8% with a structured evidence contract, and useful responses rose. Vendor: Anthropic's Fable 5 page says auditing each claim against a tool result "nearly eliminated fabricated status reports".
- **Confident closing language fools judges.** Preprint. Advani (arXiv 2606.09863, 2026): LLM judges detecting false success reached at most AUROC 0.65, because they keyed on confident wording.
- **Readers trust the summary in place of the work.** Preprint. Dhanorkar, Passi, and Vorvoreanu (arXiv 2606.05391, 2026), 17 interviews: developers spot-check agents by reading their change summaries.
- **PR descriptions that claim unimplemented changes cost acceptance.** Preprint. Gong et al. (arXiv 2601.04886): such PRs were accepted 28.3% of the time against 80.0%.
- **First-person uncertainty helps, vague hedges don't.** Measured. Kim et al., "I'm Not Sure, But..." (FAccT 2024), N = 404: first-person hedges raised accuracy when the system was wrong from 43.6% to 52.0%. Wallsten et al. (JEP: General 115(4), 1986): readers assign very different probabilities to words like "probable". The maintainer asked "What do you mean by 'might'?"
- **Precise numbers read as confident.** Measured. Jerez-Fernandez, Angulo, and Oppenheimer (Psychological Science 25(2), 2014). A bare "28 failures" reads as solid, which is why each number carries its source.
- **Number sources and timestamps.** Practice. Google's SRE incident document puts "last updated at ... by ..." on its status. No study covers stale numbers. His sessions supply the cases: a count that mixed wording differences with wrong answers, a measurement from a build one version behind, and "no conflicts" computed before another PR merged.
- **Where the code is.** Practice. He asked "is it committed / pushed / in main?" in several sessions after a report that didn't say.

## Where to see it, what you need

- **Say where to see the result.** Practice. No source tests it, and only two of the agent prompts surveyed (Cline's demo command, Replit's screenshot tool) address it. His sessions have 21 "how do I open it" questions after reports that gave a scratch path, a testing port, or no address.
- **Say what feedback you want.** Preprint. Pirouzkhah, Wurzel Gonçalves, and Bacchelli (arXiv 2602.14611, 2026), 80,000 PRs: stating the desired feedback best predicted acceptance.

## Size and shape

- **Raters reward length and formatting for their own sake.** Measured. Singhal et al., "A Long Way to Go" (COLM 2024); Zheng et al. on MT-Bench judges (NeurIPS 2023); Zhang et al., "From Lists to Emojis" (arXiv 2409.11704, preprint). A model's default length and formatting are therefore no evidence of what helps a reader.
- **Long explanations raise confidence without improving judgment.** Measured. Steyvers et al. (Nature Machine Intelligence 7, 2025).
- **Short beats long for busy readers.** Measured field experiment, reported in a book. Rogers and Lasky-Fink, *Writing for Busy Readers* (2023): a 49-word email drew 4.8% responses against 2.7% for 127 words. This supports short text the reader skims or forwards. His sessions show the opposite for explanations he must review, where he asked for "much more" and accepted 1,000-word replies.
- **Shorter by cutting points.** Practice. Claude Code: "Keep it short by leaving things out, not by packing them in." The unslop skill's over-compression rule. His sessions: a 93-word TLDR cut to 51 by dropping mechanism was accepted, and a 55-word blurb that swapped explanations for labels drew "What does it even mean?" twice.
- **No contrast framing.** Practice, with the reason measured. See the how-to-write skill's sources. His memory file extends the rule to chat replies.
- **Reply in the user's language.** Practice. In his Russian sessions the accepted replies were in Russian with English technical terms.

## Before sending

- **A cold reader for long final reports.** Practice, carried over from the how-to-write skill.
- **Rewrite the whole reply after a clarification request.** Practice, from his sessions: the accepted recoveries named the failure in one clause and redid the explanation from the top with an example. Re-explaining the same abstraction with a few words changed drew the same request again.

## This skill's own test

- **Replies written with the skill were preferred, and used fewer terms the reader couldn't follow.** Measured, small. On 2026-10-04, six scenarios were built from replies the maintainer couldn't follow, each giving the agent's working notes (with its own vocabulary) and the user's message, and none taken from examples.md. Sonnet 5.5 wrote one reply per scenario with the skill and one without. Four blinded judges (two Opus, two Sonnet, half with the order swapped, told that length is no merit) preferred the skill's reply in 21 of 24 comparisons, with 2 for the baseline and 1 tie. Two Haiku readers playing the user, each seeing one reply per scenario, flagged about 10 terms they couldn't understand across the six skill replies against about 29 across the six baseline replies (for example `descriptionApplies`, `completeMembersView`, `upgrade_to_task`, "supervisor"). The skill's replies were about 20% longer. One run per arm, so the result is suggestive. The baseline wrote from clean notes, which is easier than writing at the end of a long session, so the test likely understates the effect.
