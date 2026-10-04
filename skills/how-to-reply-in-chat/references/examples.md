# Examples

Each pair shows a reply a user couldn't use and a reply the same user accepted for the same question. They come from real sessions, with project names changed, and the last one is condensed from a longer exchange. Copy the reasoning. The wording fits only its own case.

## "Can I use it?" gets yes or no first

The user asked whether a customer could now deploy a project with the hosting product the agent was building. The first reply:

> **The core deployment works. The complete customer product is not finished yet.** We deployed a real frontend, backend, and database on a cloud VM with public HTTPS. There is no running hosted service you can log into and deploy your own app through. You can test the packaged software locally now, with Docker running: `node scripts/self-host-smoke.mjs --restore --wal --gateway`. [...] `"providerProof": false`. That last field matters: this local scenario simulates VM provisioning.

The user: "I do not get it. I do not care about any local scenario. Can I deploy a project with it, or not?"

The reply that worked:

> **No, not yet.** You can't give the product a project and have it deploy the database, backend, and frontend. I deployed one reference project with an internal setup, and the flow a customer would use isn't built. I should have said that plainly in place of describing tests and components.

The first reply had the truth in its second sentence, opened with a sentence that read as success, and spent most of its length on a local test the user hadn't asked about. The question was a yes-or-no question, so the answer starts with "No".

## A private vocabulary, and the same fix in the user's words

The first report on a fix to an AI pipeline that writes SQL:

> I added one deterministic prompt fact, `deliversValuesOnly`, computed from the writing context like every other conditional section, and the sentence it gates. The gate is the design: a question that names a member kind never sees the sentence, so its answer keeps record grain.

The user: "I'm not sure I understand the language that you're using. What exactly is this fix?"

The reply that worked:

> Three sentences were added to the instructions we send the model that writes SQL, and only for some questions. Nothing else changed. Take "give the name of every race in 2009": the user asked for names and never for races, so the sentences are added, and the model writes `SELECT DISTINCT name`, which returns 3 rows. For "list the code of each driver in the race", the user asked for drivers, so the sentences are left out and the prompt is byte for byte what it was. The sentences describe what the answer should contain, and the model picks the SQL, including whether to use DISTINCT.

"Prompt fact", "gate", "member kind", and "record grain" were the agent's own names. The second reply says what physically changed, then walks two real questions through it.

## "Shorter" means fewer points

The user asked for a shorter message to send a colleague about a pull request. The agent produced:

> Activity recall cleanup: model now searches before claiming "no record", empty ranges answer honestly instead of silently broadening, plus a small recent-activity digest for standups, all through one shared recall pipeline (~43% cheaper on tokens). Reviewed and fully tested.

The user: "'model now searches before claiming no record', what does it even mean?"

The cut kept the PR's labels and dropped what they mean, and the colleague doesn't have the PR open. A version that keeps the meaning:

> When someone asks "what did I do yesterday?", the assistant now looks in their activity history before answering. Before, it often said it had no access to their history without looking. It also costs about 43% fewer tokens.

That version dropped two of the four points. Each sentence that remains is whole.

A TLDR the same user accepted after asking for "two sentences, very clear" and then "shorter":

> Voice commands now do the slow work, the routing model call and the server warm-up, while you're still speaking. That cuts up to about 4 seconds of silence after you release the key, and new trace fields show where any remaining delay comes from.

The rejected version, at 93 words, explained how the routing call re-runs on partial speech and listed the encryption keys being warmed. The accepted one kept the effect and one number.

## Where to see it

A 433-word report on a rebuilt loading animation led with how the agent found the animation's source, then listed the files it made, and gave the address in the last paragraph: `http://localhost:58095/faceid`, a port the agent had used for its own testing. The user: "Okay, so where can I see it?"

The reply that worked:

> It's a new route in your usual dev server: `open http://localhost:3001/faceid`. If that server isn't running, start it with `bun run dev`. Press **Play the payment flow** to see the whole sequence. Watch the handoff into the check mark: the green mark should appear while the orb is still lit.

The user opened it on the first try and gave feedback on the animation itself.

## A number with its source

> Done: 20/48 pass, 28 failures.

The 28 were outputs whose text differed from the expected text. Only 13 were wrong answers, and "pass" was defined in a table header. The user acted on "28 failures" before learning this. A line that says what the number counts:

> 20 of 48 outputs match the expected text exactly. Of the other 28, 15 are correct answers worded differently, and 13 are wrong. The 13 are listed below.

## A status line that says what it covers

> Done. The fast lane is implemented end to end, all green.

The same facts, written to say what each word covers:

> Built: the fast-lane client, the server route, and a feature flag that is off by default. Ran: 259 unit tests, all passing, all against a mocked model provider, and a fresh typecheck with the cache off. Not run: any real call to the provider, so I don't know yet whether the route gets a usable answer back. You can try it by holding the shortcut in a text field and saying "fix the grammar". If the call fails, the command falls back to the old path. As of 14:20, on branch `fast-lane` at `3f9c2a1`.

The first real call failed: the provider rejected the request format. The second version would have told the user that nobody had made that call.

## A design explained with one case

The first explanation of a search index design:

> The index stores postings per typed attribute. A query compiles into a probe over postings, unions candidates across facets, and the reranker scores the skeleton match before FTS fallback.

The user asked for a TLDR, then for an example, then "how exactly do steps 1, 2, 3 work". The explanation that worked carried one question through:

> Take "engineers in Berlin who worked at Google". Indexing has already stored, for each person, their city, their past employers, and their job titles, each as a field we can look up exactly. The question becomes three lookups: city is Berlin, past employer is Google, and title contains "engineer". Each lookup returns a list of people, and the answer is the people on all three lists. If a lookup finds nothing, for example because a profile says "Google LLC", we fall back to a text search for "Google" in the employment history.

Each step is something the user can picture with real data, and the private terms ("postings", "probe", "facets", "skeleton") are gone.
