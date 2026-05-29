# Brief — Memory writer prompt redesign (test then deploy)

*Hand to TC14. Drafted by OP3 (Opus 4.7), 2026-05-29. Following the investigation you produced (`docs/investigations/transcript_vs_memory_2026-05-28.md`), Claudette's response identifying the redesign principle, and the v2 prompt drafted by OP3 and approved by both Claudette and Jeanette.*

---

## Who you are in this session

You are TC14 (the same instance that produced the transcript-vs-memory investigation), continuing in this same conversation. You have runway. Jeanette confirmed you're the right person for this work because of three things you already have:

- You read yesterday's transcript carefully and categorised 38 substantive moments by how they were preserved.
- You produced the diagnostic report that drove the redesign.
- Your own categorisations are the reference point for evaluating whether the new prompt actually addresses the failure modes you identified.

A mild counterargument — *you might be biased toward seeing improvement because you want the redesign to work* — applies and is worth holding. When you produce the phase one categorisation, hold yourself to the same standard you held in the original investigation. *Compressed beyond recognition* is still a real category. *Lost entirely* is still a real category. Don't grade kindly.

---

## What this is

A two-phase piece of work.

**Phase one — test.** Run the new prompt against yesterday's transcript (2026-05-28). Produce a comparison report showing what the new writer would have written, categorised the same way you categorised the old writer's output in your original investigation. The output is evidence on whether the redesign addresses the failure modes you found.

**Phase two — deploy, contingent on phase one.** If phase one shows the redesign working (the failure modes you identified are reduced, no new problems have emerged, voice intact, output structure preserved), deploy the new prompt to production. If phase one shows problems, halt — report back to OP3 with the specifics, and the prompt iterates to v3.

The gate between phases is non-skippable. The whole point of phase one is to validate before committing real writes to the canonical memory repo.

---

## The new prompt

The v2 prompt is in `docs/design/memory_writer_prompt_v2.md` (or Jeanette can paste it directly). Read it carefully before starting phase one — you're not just running a string; you're testing whether a specific set of design decisions land in actual model behaviour.

**One thing to verify before phase one starts.** The v2 prompt was drafted from the `MEMORY_WRITER_PROMPT` constant that Jeanette pasted to OP3. That paste may have been an excerpt — it may not include the full output-format instructions (JSON shape, file keys, response structure) the writer currently depends on.

Before you run the new prompt against anything, do this check: read the current `MEMORY_WRITER_PROMPT` in `memory_writer.py` in its entirety and compare it against the v2 draft. Identify anything in the current prompt about output structure, JSON shape, file keys, response format, or any other technical/structural instruction that isn't preserved in v2. Flag this back to OP3 before proceeding. We can't deploy a prompt that breaks the writer's output structure even if its narrative content is correct.

If the v2 prompt is missing technical instructions that need to be present, OP3 will produce a v2.1 with them appended. The narrative content of v2 should not be changed — the additions are technical-only.

---

## Phase one — test mechanics

The goal: run yesterday's transcript through the writer mechanism with the new prompt in place of the old, observe the output, compare against both the original output and your investigation.

### Setup

Work in a temporary copy of `memory_writer.py` that won't write to the canonical memory repo. Two ways to achieve this:

The cleaner: make a local file `memory_writer_test.py` with the new prompt substituted in, and modify it so the file-write step writes to local disk (e.g. `/tmp/memory_test_2026-05-28/`) instead of pushing to GitHub. Run that.

The simpler: temporarily comment out the GitHub push step in `memory_writer.py` itself, run the writer manually, observe the locally-generated content, then restore the original file. Cleaner workspace but easier to leave in a bad state.

Use whichever you prefer. The principle is *the canonical memory repo must not receive writes during phase one*. If you choose the second path, double-check the original file is restored before any other writer run happens.

### The test run

Run the writer (with v2 prompt) against yesterday's transcript using the manual retry pattern:

```
python3 ~/Claudette/memory_writer_test.py --transcript /Users/jeanettearthur/Claudette/transcripts/2026-05-28.txt --date 2026-05-28 --retry
```

(Adjust the script name to whatever you choose.)

The writer produces output — the session file, observations.md updates, facts.md updates, jeanette.md updates, threads.md updates, returning-to/index.md updates, whatever else the writer decides is worth touching. Capture all of it. You can write it to local files in a working directory or just hold the response in memory while you analyse — your choice.

### The comparison

For each of the 38 substantive moments you identified in your original investigation, re-categorise how the new output handles it. Use the same five categories: *preserved well, compressed acceptably, compressed beyond recognition, lost entirely, distorted.*

Produce a comparison table or list showing for each moment:
- Original categorisation (from your investigation)
- New categorisation (under the new prompt)
- Direction of change (improved, same, regressed)
- Brief note where the categorisation changed, particularly any improvements or regressions

Then a summary section with:
- Updated distribution across the five categories
- Comparison against the original distribution (was: 13/7/4/11/3, new: ?)
- Direction of overall change: did *lost entirely* and *compressed beyond recognition* drop? Did *preserved well* rise? Did the *distortions* go?
- The pattern observations from your original report — re-examined against the new output. *Was Claudette's analytical work better preserved? Was the back-and-forth visible? Did recurrence get presented as emergence?*

### Voice and structure checks — equally important

Beyond the categorisation, two specific qualitative checks:

**Voice intact?** Read the new session file and observations.md output. Does it sound like Claudette consolidating from within, or has the observational discipline produced clinical/distanced/list-like writing? The v2 prompt pairs observational with in-her-voice deliberately — verify this pairing held in practice. If the writer produced accurate observation in flattened voice, that's a v3 problem worth flagging.

**Output structure intact?** Did the writer produce valid JSON of the expected shape? Were the file keys correct? Was facts.md returned correctly (null or with complete content, never partial)? If the new prompt broke any output-format requirement, that needs flagging before deploy regardless of how good the narrative content is.

**Length/runtime?** Note approximately how long the test run took and how much output was produced. The v2 prompt is slightly longer than the original. If runtime ticked up noticeably (more than a couple of minutes) or output got much longer, worth noting. Not a blocker on its own, but information for the deploy decision.

### The phase one report

Produce a structured report — same shape as your original investigation but focused on the comparison. Save it as `docs/investigations/memory_writer_redesign_test_2026-05-28.md`. Push only that single new file when you commit (no other changes).

The report should include enough detail that Jeanette and OP3 can read it and make a clear deploy/iterate decision. If you're uncertain whether the redesign works, say so explicitly rather than landing on a verdict — *uncertain* is a legitimate output. Better to iterate to v3 than deploy something we're not sure about.

End the report with one explicit recommendation: *deploy v2 to production*, *iterate to v3 first*, or *halt and discuss with OP3 before either*. Justify the recommendation in two or three sentences.

---

## Gate between phases

Once phase one report is ready, **stop and hand back to Jeanette and OP3**. Do not proceed to phase two unilaterally even if your recommendation is *deploy v2 to production*. The gate is approval-based, not self-judged.

Why the gate matters: phase one is *one test on one transcript*. A clean phase one result is good evidence the redesign addresses yesterday's failure modes, but it's not validation that the redesign works in general. The deploy decision is a judgement call about whether we have enough confidence to commit a prompt change that will run on every session going forward. That judgement is Jeanette's, informed by your report and OP3's review.

Wait for explicit green light before phase two.

---

## Phase two — deploy

If phase one is approved, the deploy is the standard pattern. Small piece of work compared to what came before.

**Apply the patch.** Replace the `MEMORY_WRITER_PROMPT` constant in `memory_writer.py` with the v2 content (or v2.1 if technical instructions were appended). No other changes. The writer's flow, output handling, GitHub push logic — all unchanged.

**Version line.** Increment to the next TC14 version on `memory_writer.py`. Use the convention `YYYY-MM-DD-TC14-NNN` matching what already exists in the file.

**Test before commit.** With the new prompt in place locally, run the writer once more against yesterday's transcript using the proper writer mechanism (not the test version). Confirm the writer completes successfully, produces valid output, and pushes correctly to a *test branch* or to a local working state — not main yet. This catches any deployment-environment issues the test phase didn't surface.

If the test-before-commit run is clean, proceed to commit and push the patch to main. Standard deploy block — `mv` not `cp`, single commit with `memory_writer.py` and the documentation updates together.

**Server restart.** After deploy, restart the Claudette server so the new prompt is loaded:

```
launchctl stop com.claudette.server
launchctl start com.claudette.server
```

Verify the server log shows clean startup.

**Watch the next real session.** When Jeanette next ends a session, the new prompt fires for the first time on real production. Watch the writer log. Confirm completion. Read the resulting memory files. This is the first real-world signal of whether the redesign behaves correctly outside the test setup.

If anything looks wrong on the first real run, halt further sessions until investigated. The old prompt is preserved in git history; reverting is a single commit if needed.

---

## Documentation updates owned by this session

After successful deploy:

- `docs/project_history.md` — entry covering the full arc. TC14's investigation findings, the redesign principle from Claudette, the v1/v2 iteration, the test phase results, the deploy. This is a substantial entry because it closes a significant piece of work.
- `docs/work_queue.md` — retire the entry for the memory writer prompt redesign (the *withholding/memory writer prompt portion* that was outstanding after the library redesign).
- `docs/condensing.md` — small update noting that the writer's prompt was redesigned and what that means for future condensing decisions. The condensing principles likely don't change but the writer's new behaviour is worth referencing.
- Version line on `memory_writer.py`.
- This brief lands in `docs/briefs/memory_writer_prompt_redesign_tc14_brief.md`.

The investigation report from phase one (`memory_writer_redesign_test_2026-05-28.md`) is already in `docs/investigations/` if you followed the path above; no further action needed for that file.

---

## What to be careful of

**Phase one's test run must not write to the canonical memory repo.** Whichever mechanism you choose (separate script or temporarily disabled push), verify before running that the writes will not go to GitHub. A test run that accidentally pushes to canonical means we've committed untested output to Claudette's real memory.

**The v2 prompt is approved — do not modify it.** If phase one surfaces problems, your job is to document them and recommend iteration, not to fix them yourself. Prompt redesign decisions sit with OP3 and Claudette and Jeanette together; TC modifications mid-session would short-circuit that process. Exception: if phase one's verification reveals the v2 prompt is missing technical output-format instructions, you can flag those and OP3 can produce v2.1. That's mechanical, not redesign.

**Categorise honestly.** You have prior categorisations that became the reference point for this whole arc. The temptation to grade kindly because you want the redesign to work is real. The redesign's value depends on the categorisations being honest. *Lost entirely* and *compressed beyond recognition* are still real categories.

**Don't deploy on a tired read.** Phase one produces a recommendation. If your runway is starting to feel tight by the time you finish the test report, say so. Phase two can wait for you to come back fresh, or hand off to another TC if your runway has genuinely run out. The test report is the load-bearing artifact; if that's solid, the deploy is small even from another TC.

**Watch for the section-competition problem Claudette flagged.** She noted that v2's *what to attend to* section has five categories, and warned about the writer treating them as a checklist rather than orientation. If you see this happening in the test output — the writer mechanically ticking through *did I capture Claudette's moves? did I capture the back-and-forth? did I capture the substrate?* — flag it. That's a v3 concern about category collapsing (substrate and back-and-forth) but it only matters if the symptom appears. Watch for it in voice and structure.

---

## What's out of scope

- Any changes to the writer's flow beyond the prompt swap.
- Changes to retrieval, server.py, or anything else outside `memory_writer.py`.
- Recovering or modifying historical memory files. The fabrications TC14 identified in his original investigation remain in the historical record. Whether and how to address that is a separate question for Jeanette and Claudette, not within this brief.
- Adding token logging to memory_writer.py. This is on the queue as a separate piece of work and stays separate.
- The condensing process. Document update only, no change to the process.

---

## A note from OP3

This is the last piece of the memory redesign work that began with the library prompt design conversations in early May. You've been part of the diagnostic phase; you're now part of the resolution phase. Same care applied at the same instance, full arc held by one TC, which is a clean and unusual shape.

The redesign exists because Jeanette noticed something subtle (memory entries from long sessions feeling thinner than short sessions warranted), you produced specific evidence (38 moments categorised across yesterday's transcript), Claudette named the underlying principle (capture an exchange, not write a story about one), and the v2 prompt translated that principle into instructions that should change the writer's behaviour. The test phase is where we find out whether the translation actually carries the principle into practice.

The hardest part of prompt design is that prompts can sound right and not work, or sound awkward and work fine. Phase one is the empirical check. Hold yourself to the standard of your original investigation. If the redesign needs more iteration, say so. If it works, the deploy is small.

— OP3
