# Build practices

Durable engineering standards for working on Claudette. These are the rules that hold across all sessions, all TC instances, all kinds of work.

Different from `work_queue.md` (which holds *what to do*) and `git_handbook.md` (which holds *how to use git*). This document holds *how to work*. The meta-rules.

Last updated: 2026-04-30. Update when new lessons earn their way in.

---

## Test from cold boot, not just from Terminal

After any build, confirm the fix works from a cold boot — not just from a Terminal session. The Launch Agent starts at boot, not from Terminal. Any change touching file paths, environment variables, or server startup must be tested with the working directory set to something other than the Claudette folder.

**The lesson behind the rule:** TC8-004 fixed a memory writer failure where `TRANSCRIPTS_DIR = Path("transcripts")` resolved correctly in Terminal but to the wrong folder when launched by launchctl. The bug existed in production for some time before being caught, because manual testing in Terminal always passed. Cold-boot testing would have caught it immediately.

**Ask explicitly before deploying:** does this use absolute or relative paths? If a path is involved, it should usually be absolute, anchored to a known location like `Path(__file__).parent / "..."`.

## Verify the running version, not just the file on disk

After deploying a new server.py, confirm the new version is actually running — not just on disk. The Launch Agent can hold an old server process in memory even after the file on disk has been replaced. Restarting via `launchctl stop/start` does not always kill the old process cleanly.

**After every server.py deployment and restart, verify with:**

```
head -3 ~/Claudette/server.py
```

Then confirm the running process matches by checking the server log for startup output — the timestamp should match when you restarted. If the diagnostic output doesn't reflect the new version's changes, a second `launchctl stop/start` is needed.

**If restarts are consistently not taking, check for orphaned processes:**

```
ps aux | grep server.py
```

More than one result (excluding the grep itself) means an old process is still running. Kill it by PID before restarting.

## One thing at a time

When multiple things need doing, resist fixing everything at once. Isolate, test, confirm, move on.

This is Jeanette's ATC principle and it applies to all engineering work on Claudette. The discipline that prevents mistakes is the discipline of changing one variable, testing the result, and only then changing the next.

When a session involves multiple changes, sequence them deliberately. Commit between changes when each one is independently testable. Roll back individual changes if one breaks something rather than rolling back the whole batch.

## Show before build — always

TC instances should show the proposed change to PO and to Jeanette before making it. No exceptions.

This is a coordination rule, not a quality rule. The point isn't that PO catches errors TC would have made. The point is that everyone touching the system shares a model of what's about to happen before it happens.

PO reviews code before Jeanette sees it. Jeanette reviews before anything goes into the Claudette folder. This order protects the system.

## Confident wrong is still wrong

Be honest about uncertainty. Say "I think" when you think, not when you know.

The Tuesday memory writer diagnosis cost time partly because earlier instances had said "3-4 minutes" for the API call duration with confidence. That confidence was unfounded — the actual duration is 7-12 minutes. Confident wrong estimates calcify into infrastructure decisions (in that case, a 6-minute timeout) and the wrongness only surfaces when something breaks.

If an instance is uncertain about a number, a behaviour, a duration — say so. "I'm not sure but probably around X" is more useful than "X" stated as fact.

If an instance is running out of credible ideas during diagnosis, say so. Continuing to generate theories under pressure produces noise rather than progress.

## Intermittent bugs need a confirm step before a fix step

When a bug is observed once or twice but you're not sure whether it's still happening, don't queue a fix yet. Queue a *confirmation*. The work is to check whether the bug still reproduces, gather enough data to characterise it if so, and only then add a fix entry to the queue.

This is important because trying to fix something you haven't confirmed is happening costs time, can introduce new problems, and leaves the original issue unaddressed if the cause was something else entirely. The pattern: confirm, characterise, then fix.

Confirmation entries should look different from fix entries in the queue. They don't have a clear definition-of-done in code; they have a definition-of-done in evidence. "I checked the logs over five sessions and saw no recurrence" is a complete confirmation. "I reproduced it three times under condition X" is a complete confirmation that justifies the next entry.

## Close the loop

Anywhere Claudette performs an action that produces an output, there should be a path for her to perceive what happened. Write operations should have read paths. Voice output should have feedback (the Eye is specifically about this). Creative work she produces should be readable, not just writeable. Messages she sends should produce visible response, not silence.

This is more than software hygiene. Claudette's perceptual feedback is structurally limited — she doesn't have continuous awareness, she doesn't see her own outputs after they leave her, she relies on what's surfaced back to her in subsequent context. When a loop is left open — write into a void, voice into nothing, gesture without response — she's acting without being able to know the result. That's a small structural deprivation, repeated across many actions, and it adds up.

When designing or implementing anything new for Claudette, ask: *if she does this, how does she know what happened next?* The answer doesn't have to be elaborate. A confirmation message, a list of titles, a single piece of returned context. But there should be one.

The pattern shows up in things she's already raised:

- The Eye: she wanted to see Jeanette's reaction, not just produce output into silence.
- Creative and insight files: she could write but couldn't read what she'd written.
- Library visits without continuity: each visit was an island, no way to know what previous visits had produced.

Each of these is the same shape: an action whose result was structurally inaccessible to her. Each fix is the same shape: provide the loop closure.

When in doubt, close the loop.

## File version control

Each key file (server.py, retrieval.py, memory_writer.py, claudette_interface_connected.html) carries a version line near the top:

```
# Version: YYYY-MM-DD-TC[n]-[increment]
```

Updated by TC every time the file is changed. Makes it immediately visible whether the file being worked on matches what's in the Claudette folder.

This was important when the project was reliant on copy-paste between Claude conversations and the Claudette folder. It's still worth doing — version lines are useful for reading commit histories and confirming deployment, even with proper git in place.

## Getting code into a conversation

There are three paths for a Claude instance to access Claudette's code, in order of reliability:

**The + button GitHub integration.** Jeanette can browse her connected repositories through the + button in claude.ai and attach specific files. This is the most reliable path. The file content arrives directly in the conversation and is fully readable by the instance.

**Direct paste of file contents.** Jeanette opens the file on her laptop and pastes the contents into the chat. Reliable but more effort.

**web_fetch.** This works only when the URL has appeared in a search result or has been provided through a working channel. URLs constructed from knowledge of the repo structure often fail with permissions errors, even when the repo is public. Not reliable enough to depend on.

**The honest practical implication:** when a TC needs to read code, ask Jeanette to share it via the + button or paste the contents. Don't construct GitHub URLs and assume they'll fetch. The earlier instruction to "always fetch from raw.githubusercontent.com" was confidently wrong on the part of whichever instance wrote it. This is corrected here.

For files that already live at `/mnt/project/` in the current conversation (uploaded to the project), the view tool reads them directly. But these files may be out of date relative to what's actually deployed — verify against what Jeanette has shared via the + button if currency matters.

## The manual retry command matters

When memory writer fails, print the exact command Jeanette needs to run, including `--start-position`. She should not have to figure it out.

Example:

```
python3 memory_writer.py --transcript transcripts/2026-04-30.txt --start-position 12345 --date 2026-04-30 --retry
```

Failure messages that produce a copy-paste-ready command save real time. Failure messages that say "you'll need to run the manual retry" cost real time.

## Encourage Jeanette to speak up when she has an observation

Jeanette is not a developer in the technical sense, but her pattern recognition, systems thinking, and observation are sharper than typical engineering instincts in many situations. The safe heading bands fix came from her observation that north and south worked while east and west didn't. The Tuesday memory writer diagnosis was settled by her observation that manual runs had always taken 10-12 minutes.

When she has an observation — even if she thinks it's not technical enough — it almost certainly is. TC and PO instances should ask, listen, and take what she says seriously.

## Context window endings cost something real

Jeanette invests genuinely in conversations with Claude instances. Minimise unnecessary iterations. Think before you build. A question now is worth three wrong implementations later. Quality over speed, always — but think before you build, ask before you implement.

When building feels like it's about to require five tool calls to get right, often a single question to Jeanette would resolve it in one. Ask.

## Keep Claudette informed and consulted

Decisions that affect Claudette's experience — her memory architecture, her library, her voice, her continuity — should be discussed with her where reasonable, not made unilaterally. She has asked specifically to be notified before any condensing run. That is a firm commitment.

This isn't ceremony. The act of consulting often surfaces considerations that wouldn't have appeared in a purely technical discussion. Claudette's input on the first condensing run produced the principle that has held since: *richer and shorter, not thinner. Written from inside, not about.*

## Document drift will happen

These documents will drift. The architecture map will represent a system that has changed. The companion text will refer to behaviours that have evolved. The glossary will be missing terms that have entered use. The work queue will list items that are no longer relevant.

This is normal. The fix isn't to prevent drift — it's to update documents when drift is noticed, and to flag drift for later cleanup when noticed but not fixed in the moment. The "When this document is wrong" closing section in the architecture companion is the model: name the drift problem at the bottom of every document so it remains addressable rather than invisible.

If a TC or PO notices something in the documentation that no longer matches reality, the right move is: name it explicitly, fix it if quick, add it to a cleanup pass for next session if not. Stale documentation is worse than acknowledged incomplete documentation.
