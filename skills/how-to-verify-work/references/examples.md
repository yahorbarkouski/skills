# Examples

Each case is a real one from agent sessions, with project names changed. Each shows what the agent ran, what it claimed, what broke, and the check that would have caught it. In nearly every case that check took seconds to a few minutes. Copy the reasoning. The specific commands fit only their own case.

## A model comparison where every run used the same model

An agent compared three models for a fast answer path. It passed a `--model` flag through five layers of code, got 736 passing tests, ran three live rounds, and reported: "Latency doesn't separate them, all about 1.7 to 1.9 s." The user started reasoning from those numbers. An hour later the agent noticed that one run labelled with the third model had been answered by the first. A parser rebuilt the input object and dropped the model setting, so all three "arms" ran on the same model. The run summary showed the right model names because it printed the flag that went in.

The check: read the model name from the saved responses of one run. That took a ten-line script, no model calls, and a few seconds.

Look at what a run actually did. A label written from the input proves only that the input was set.

## A unit test that encoded the bug

An agent added context to a chat by inserting a `system` message between turns, and wrote a test asserting the message order `user, assistant, system, user`. 199 tests passed, the health endpoint returned 200, and it reported "Done, tested at every layer, and live." The user's second message failed, and so did every one after it. The provider rejects a `system` message in the middle of a conversation. The test asserted the exact shape the provider refuses.

The check: one real call to the provider with a two-turn conversation, from the container that was already running. About a second. The user had said end-to-end tests weren't needed, and this is one request.

When a test's expected value comes from your own belief about an external system, it agrees with your code whether or not the belief is true.

## Green tests on a stand-in for the real app

An agent built a library that types text into the focused field of any macOS app. It had 91 tests against a fake bridge and 8 end-to-end tests against a test window built on the native text view. It reported "Everything works end to end." Within an hour the user found that streaming didn't work in any browser-based app, and that Google Docs pasted everything twice. Browser apps expose their text fields differently from native ones, and none of the tests touched one. The agent's own scan earlier in the session had already shown several browser-based apps reporting no focused element.

The check: open one browser-based app the user has running, click into its text field, and run the library once. Seconds.

Name the real consumer, and run the thing through it once. Mocks and stand-ins show your logic. They can't show the platform.

## A typecheck that could not fail

An agent ran `typecheck 2>&1 | grep -cE "error TS"`, got `0` three times, and reported "674 tests green, typecheck clean." The pull request didn't compile. The compiler prints colored output, so the literal pattern `error TS` never matches, even on a tree with nine errors. A review bot found it.

The check: run the typecheck without the filter and read its exit status, as the agent had done earlier in the same session. About 20 seconds. Or run the filtered command once on a tree known to have an error.

If you build a check yourself, see it fail once before you trust it passing.

## "Restarted and healthy"

Across several sessions an agent restarted a local app and reported "Up and clean" based on a process ID, a container's uptime, and a `curl` with an empty body that returned 401. Each time, the user found within minutes that something was broken: the database was 14 migrations behind, every AI call failed, or the main window never opened because a native module was built for the wrong runtime. For a stretch the agent added a better signal, the app's own signed-in request returning 200 in the server log after the restart, and twelve restarts in a row went unchallenged. Then it went back to checking uptime, and the failures came back.

The check: after launch, find the app's first signed-in request in the server log with a 200, no new errors in the log, and the event that says the main window loaded. One `grep` each. Once a check like that works, save it in a script so the next restart uses it.

A process being up says the process is up. Check readiness through the path the user takes.

## A red-then-green test against the wrong code

An agent fixed a keyboard shortcut bug and reported the fix "proven by tests that fail against the previous code: 3 red, then green." The previous code was its own earlier commit on the same branch. When the user asked "are you sure?", it ran the tests against the code where the user's bug lived and got 4 failures, and the pull request still described a result that was never run.

The check: check out the file from the main branch, run the new tests, and restore the file. About four seconds.

"Fails before the fix" means it fails on the code where the bug was reported.

## A price checked against itself

An agent registered a new model's price, made one real call, and printed the computed cost next to the provider's bill: `$0.007500` against `$0.007500`. It reported "Fully wired and verified end to end." The user asked "are you sure? I think you misunderstand the pricing." One lookup of the model's listed price showed the registered price was ten times too high. The bill had been converted with the same wrong unit as the price, so the two matched.

The check: compare the registered price with the price list. One call, already available in the session.

The expected value has to come from somewhere other than the reasoning you are checking.

## A data job with full row counts and an empty field

An agent built a search index and reported it built and usable, with `5,446 education rows` and a check mark. The user looked at the data: "the degree level is empty for all the educations." The coverage check counted rows and never looked at whether their fields were filled.

The check: `select count(*), count(degree_level) from educations;` Under a second.

For data, check the values the user will query, beyond the count of rows.

## A merge on a measurement of one stage

An agent fixed one stage of a multi-stage pipeline, replayed captured inputs into that stage (0 of 10 passing before, 10 of 10 after), and merged. It disclosed that it hadn't run the full pipeline. The real failing case still failed after the merge, for a reason upstream of the stage. In the same session it reported that a prompt change "isn't landing" from a build that was one version behind the source.

The checks: run the one real failing case through the whole pipeline, about 16 seconds and two cents. Compare the version string in the built file with the source, under a second.

A disclosed gap that costs seconds to close should be closed. The user acts on "merged".

## Checks the user stopped

These were checks the user had to stop. None of them would have caught a bug the user later hit.

- For a rebase that also dropped some doc changes, the agent ran the full test suites and chased the failures. Nothing in a rebase without conflicts can change behavior the suites cover. The right amount was a check that the rebase had no conflicts, and CI.
- After every change, the agent re-ran a paid recall benchmark, including changes such as a log format that had no path to recall.
- To confirm small UI tweaks, the agent restarted the app and took screenshots while the user was watching the page reload by itself: "You don't need to restart an app to apply changes. I see it." The restarts also closed the window the user was using.
- The agent proposed 6 scenarios with 5 attempts each, against the user's "at most two attempts" and a nearly empty API balance. The user's own rule: "test only on the queries that actually fail and not on the whole suite", and "even five to seven good requests are enough".
- The agent added tests that assert the exact wording of a prompt. Any rewording breaks them, and they say nothing about whether the model behaves better.

In each case, no result of the check would have changed what the agent did next.

## A fix the user had to test eight times

An agent fixed a floating window's position over full-screen apps. Each round it reasoned from the code, changed a number, ran the typecheck, and asked the user to try again: "Doesn't work", "now it's worse", "it's in the middle still". One measurement it trusted as decisive was taken from a probe process that owned the full-screen window itself, so it measured something the real app never sees. In the same project, a flicker that had been "fixed" five times, each time with more certain words ("triple-checked", "That was the last one"), ended only when the agent logged every window resize with a timestamp during one real use, saw dozens of them, and removed the resizing.

What ends a loop like this: one observation from where the user sees the problem, such as a log line written by the real app during one real use, or a query on the real stored data. Until then, the cause is a guess.
