---
name: how-to-verify-work
description: Decide how to check your own work before you tell the user it is done, fixed, or working, and how much checking is enough. Use before you report a change as done, fixed, verified, healthy, or ready, before you run tests, a benchmark, a screenshot, or a restart to confirm your own change, when a fix has failed more than once, and when the user asks "are you sure?" or "did you test it?". Skip it for a change with no behavior to check, such as a typo or a comment.
---

# How to verify work

An agent adds a fast path for voice commands. The app's client now sends short commands to a new server route, which asks a model provider for a decision. The agent writes 259 unit tests with the provider mocked, gets a fresh typecheck, sees the route answer on the local server, and reports: "Done. The fast lane is implemented end to end, all green." The first real command the user speaks fails. The provider rejects the request format, which none of the 259 tests could see, because every one of them talked to the mock. One real call to the provider, a few seconds and a fraction of a cent, would have shown it.

In another session, an agent changes a button's padding. The user is watching the page, which reloads on every save. The agent restarts the app, opens a browser, and takes screenshots to confirm the padding, three times over, until the user stops it: "You don't need to restart the app to apply changes. I can see it."

The two agents made the same mistake. Each check was aimed at something other than what could actually be wrong. The first never touched the part that broke, the provider. The second checked something the user could already see, and its answer could never change what the agent did next.

## Check what could be broken, on the real thing

Before you say something works, name the sentence you are about to tell the user, such as "pasting now works in Google Docs". Then ask what would make that sentence false. Usually it is the place where your code meets something you don't control, such as an API, a real app, a browser, a database, a deployed build, or real data, or the specific path your change touched. Check that place, with the real thing the user will use.

That check is usually cheap. In most false "done" reports, it would have taken seconds to a few minutes, and the agent ran it on its own as soon as the user asked "did you actually test it?". Run it before the user has to ask.

A few habits carry most of this:
- **Do the user's first real action yourself.** Whatever they will do first, such as speak the command, open the page, run the query, or deploy the project, do it once, through the same path they use, and look where they will look. Mocks, fakes, and unit tests show that your logic does what you think. They can't show that the real API accepts your request, that the real app receives the paste, or that the deployed build has your change.
- **Make sure the check can fail.** For a bug, see it fail first, on the code before your fix. Take the expected answer from outside your own assumptions, such as the provider's price page, the library's source, or the user's example, because a check built on the same belief as the code agrees with it. Confirm it ran on the final commit and a fresh build, and that the setting you were testing reached the code that uses it. If you aren't sure a check can fail, run it once on an input that should fail.
- **Read what you already have.** Before running more, read the full output of what you ran, including the lines a `tail` cut off, the hook that says it skipped, and the warning you assumed was stale. When failures pile up, stop running things and read the failing cases.
- **Leave the user's state alone.** A check never resets their account, closes the window they are watching, or restarts an app another agent is using. If only the user's hands or eyes can do the check, such as their microphone or their login, hand it over with the exact steps and what they should see.
- **Say what you checked and what you didn't.** "I ran one real request against the provider and the 40 unit tests. I haven't tried it in Safari." Listing a gap is no substitute for a check that takes seconds, because the user acts on the headline. List what you could not run, and why. The how-to-reply-in-chat skill covers writing that report.

## Keep the loop lean

Most checks should take seconds. Start with the smallest check that crosses what could be broken, such as one targeted test, one real request, or one look at the actual output, and widen only when it passes and something wider could still be broken. A long loop, such as the full test suite, an end-to-end run, a paid benchmark, a rebuild and restart, or a round of screenshots, needs a specific reason: a way the change could break that only that loop can catch. "To be safe" is no reason. Long loops cost the user waiting time and money every time they run, and they tend to get repeated after every small edit.

Before running any check, say what result would change your next action. If none would, skip it. That rules out re-running a suite or a paid benchmark after a change that can't affect it, restarting or screenshotting what the user is already watching, tests that pin the exact wording of a prompt, and asking a model to re-check its own answer with nothing new to go on. A targeted check repeated a few times on the failing cases usually tells you more than one full run of everything.

Run a long loop once, at the end, when the work will be merged, shipped, or built on unattended and nothing cheaper covers the risk, or when the user or the repository asks for it. CI usually runs the full suite anyway. A change the user will try in the next minute needs a quick real check, or none if they are watching it happen.

## When the user has become your tester

If the user has told you twice that a fix didn't work, the next attempt needs an observation: reproduce the problem yourself, log the one value that decides it at the point where it goes wrong, or query the real stored data. Observe from where the user sees it, since a measurement taken from another process or a test page can be accurate and still miss what they see. Until you have that observation, call the cause a guess, and save words like "confirmed" and "proven" for after it. Sometimes the fastest way out of the loop is a design that removes the failing case entirely.

## When a measurement is the result

When the result is a number, such as a benchmark score, a latency, or a comparison between two prompts or models, the number is the claim. Start with a handful of items and read the outputs before paying for a full run, as the how-to-run-long-jobs skill describes, and re-run only when something changed that can move the number. Confirm the run used the code and settings you are reporting on by looking at what it actually did, such as the model named in its requests, because a label on a run can say one thing while the code does another. Use cases you didn't write yourself, compare on the same items, say how many there were, and treat a difference smaller than the noise as a tie. Score a few outputs by hand to confirm the scorer agrees with you. A score of 0% or 100%, or every item getting the same answer, usually means the measurement is broken.

Worked cases, from UI changes and native apps to APIs, prompts, data pipelines, and deploys, are in [references/examples.md](references/examples.md). The evidence behind this skill is in [references/sources.md](references/sources.md).
