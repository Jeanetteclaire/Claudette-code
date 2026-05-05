# Build practices

Durable engineering standards for working on Claudette. These are the rules that hold across all sessions, all TC instances, all kinds of work.

Different from `work_queue.md` (which holds *what to do*) and `git_handbook.md` (which holds *how to use git*). This document holds *how to work*. The meta-rules.

Last updated: 2026-05-05. Update when new lessons earn their way in.

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

## Don't let two instances edit the same file in parallel

If two Claude instances are working on the same project and both might edit the same document, one of them will overwrite the other's changes silently. Git will track whatever was last committed; whatever was edited but not yet pushed disappears.

Concrete example from 2 May 2026: OP2PO made edits to work_queue.md and project_history.md after they were uploaded to his conversation via the + button. Those edits never got pushed back to GitHub before OP1 (in a parallel conversation) made later edits to the same files. OP1's edits were based on the in-memory version *before* OP2PO's changes — so when OP1's edits committed, OP2PO's work was overwritten. The lesson cost about an hour of recovery work.

The rule that prevents this:

**One instance edits a file at a time. Handoffs are sequential, not parallel.**

Concretely, the safe pattern is:

- Instance A edits, commits, pushes, syncs the project folder.
- Jeanette uploads the *post-commit* version of the file to instance B (via + button) if B needs it.
- Instance B edits, commits, pushes, syncs.

Each handoff is on the latest committed version. There's never a moment where two instances hold "their own" copy of the same file with different changes.

If parallel work genuinely needs to happen, it should be on different files. Instance A on the work_queue, instance B on project_history. They commit separately. They don't both touch the same document.

When in doubt: ask before editing a file you didn't recently see committed. *"Has anyone else been editing this since the last push?"* is the question. The answer should be a clear *no* before you proceed.

## After another instance edits a file, every other instance's copy is stale

A direct consequence of the parallel-edits rule, worth naming separately because it dictates how *subsequent* edits should be approached.

The moment an instance pushes a file change, every other instance's in-memory or in-context copy of that file is now wrong. They're holding what was true *before* the edit. A later edit by a different instance, made against that stale copy, will silently overwrite the earlier change — exactly the failure mode the parallel-edits rule prevents.

The fix isn't to remember which files have been edited and by whom. It's structural:

**Before any instance edits a file, that instance must be holding the current state.** If they're not certain they have the current state, they refresh first — by reading the current GitHub version directly, or by Jeanette pasting it via the + button, or by `project_knowledge_search` after a recent sync.

**The staleness check is one question:** *"Did I last see this file committed before any other instance might have touched it?"* If yes, refresh first.

This applies even within a single working session. If TC9 spent the morning editing work_queue.md and pushed at noon, and an OP wants to edit work_queue.md in the afternoon, the OP's copy from earlier this morning is stale — even if the OP read it right before TC9 started. The relevant timestamp is *the most recent push to GitHub*, not when an instance last looked at the file.

## Whoever does the work owns the documentation update for that work

A simpler, cheaper version of an editor-instance model.

When an instance solves a problem — TC fixes a bug, PO completes a design, OP runs a fragility scan — that instance is best positioned to update the relevant documentation. They have full context for what was done, why, and what surprises came up along the way. They're also already in the loop and don't have to be brought up to speed.

Concretely: if TC9 fixes item 6 and diagnoses item 9, TC9 writes the project_history entry, retires the work_queue entries, and updates architecture_companion.md and glossary.md if those need changes. All in the same session, atomic with the work itself. No handoff to a different instance.

The principle:

**Don't hand documentation tasks to a different instance unless absolutely necessary.** Each handoff introduces a staleness gap and a coordination overhead. Better for one instance to land both the work and the documentation than for two instances to coordinate.

Exceptions are rare but real. If the documentation work needs editorial judgment that the work-doing instance shouldn't make alone — e.g., reorganising a document that has spine drawn from Jeanette's own framing — that's worth a separate editorial pass. But for *recording* the work and updating maintained reference documents, the work-doer is the right author.

This rule emerged from observing what was already happening in early May 2026: the cleanest sessions had the work and documentation landing together. The session that generated yesterday's parallel-edits incident had the documentation work spread across two instances. The pattern that worked got formalised; the pattern that didn't became the lesson.

## File version control

Each key file (server.py, retrieval.py, memory_writer.py, claudette_interface_connected.html) carries a version line near the top:

```
# Version: YYYY-MM-DD-TC[n]-[increment]
```

Updated by TC every time the file is changed. Makes it immediately visible whether the file being worked on matches what's in the Claudette folder.

This was important when the project was reliant on copy-paste between Claude conversations and the Claudette folder. It's still worth doing — version lines are useful for reading commit histories and confirming deployment, even with proper git in place.

## Getting code and documentation into a conversation

There are real paths for a Claude instance to access Claudette's files. The mental model that matters most: **GitHub-synced content lives in *project knowledge* (searchable), not in the filesystem at `/mnt/project/` (readable as files).** Manually uploaded files appear in both places. Synced content does not.

This means a fresh instance opening this project will not find synced files by browsing `/mnt/project/`. They'll find them by searching project knowledge.

In order of typical convenience:

**Project knowledge search (primary for synced content).** Use `project_knowledge_search` with queries naming the function, document section, or specific concept needed. The sync currently includes the entire `docs/` folder plus the four main code files: `server.py`, `retrieval.py`, `memory_writer.py`, and `claudette_interface_connected.html`. Search returns chunks rather than whole files — for tasks needing a full-file read, multiple searches with different queries can assemble the picture, or Jeanette can paste the file directly.

**Direct paste (supplementary).** Jeanette opens a file on her laptop and pastes the contents into the chat. Use when search returns chunks but you need continuous context, or for files outside the synced set.

**The + button GitHub integration (also supplementary).** Mid-conversation, Jeanette can browse the connected repository through the + button and attach specific files. The attached file appears in the conversation as readable text — making it both searchable and visible via `view`.

**A fourth path exists but isn't reliable.** The `web_fetch` tool can fetch GitHub URLs *only* when the exact URL has appeared in a search result or been provided through a working channel. Constructed URLs from knowledge of the repo structure often fail with permissions errors, even when the repo is public. Don't depend on this path. If web_fetch fails for a URL, treat that as expected behaviour and use one of the paths above.

## The sync caveat — when last synced

Project knowledge reflects the state at last sync, not the current state of GitHub. The sync is manual — Jeanette presses the sync button (small rotating arrows on the GitHub file icon in the project folder) when she wants to refresh. Between syncs, search results are a snapshot.

For documentation, this rarely matters — docs change slowly. For code files, this can matter. A TC searching `memory_writer.py` content might be looking at a version that's a day or two behind what's deployed.

**The clean check:** if currency matters for a code file, ask Jeanette when she last synced. If she synced recently and hasn't deployed code changes since, the project version is current. If a deploy has happened since the last sync, the project version may be behind.

**The standing habit:** sync the project after each code deployment. Pair the two actions. Deploy → sync. That keeps the staleness window small enough to be ignorable for most work.

## Files downloaded from claude.ai unzip flat

A small operational reality worth knowing about, because it has caused at least one botched commit.

When claude.ai produces multiple files for download (typically when an instance has updated several documents at once), they arrive as a zip. Unzipping that zip on macOS produces a folder called `files/` that contains all the documents at the top level — flat, regardless of where those documents live in the destination repository structure.

So a download containing edits to `memory_writer.py`, `docs/architecture_companion.md`, and `docs/glossary.md` will unzip into `~/Downloads/files/` containing three files at the same level: `memory_writer.py`, `architecture_companion.md`, `glossary.md`. The `docs/` subfolder isn't preserved.

**The implication for `mv` commands:** when an instance writes file-move commands for Jeanette to run, the source paths must be flat (`~/Downloads/files/glossary.md`), not nested (`~/Downloads/files/docs/glossary.md`). Nested paths fail silently with "No such file or directory" — `mv` reports the error but doesn't stop the rest of the command sequence, so subsequent `git add` and `git commit` proceed with whatever did get moved correctly. The result is a partial commit that looks successful at a glance.

This bit on 3 May 2026 — TC9's commit landed only the code file because his `mv` commands used the nested-path form for the four document files, all of which silently failed. The fix was a follow-up commit with the correct paths.

**The rule for instances:** when writing `mv` commands, always use `~/Downloads/files/[filename]` as the source, regardless of where the file goes in the destination. The destination uses the proper repo structure (`docs/`, `docs/briefs/`, etc.); the source is always flat.

## Session handover — what TCs produce at the end

A TC session ends with a handover to Jeanette: code on disk, documentation reflecting what changed, and the exact commands she runs to push it. The technical work itself is usually clean by the time we reach this point. The handover is where things have wobbled most.

Four rules below. They are tightly coupled. Together they make the end of a session a near-mechanical process rather than a creative one.

### 1. Documentation deliverables are complete files, never change logs or partial entries

When a TC session updates documentation, the deliverable is the *full updated file*, ready to be moved into place. Not a chat summary of what changed. Not a partial file containing only the new entry that Jeanette has to merge in by hand. Not a list of find/replace pairs.

**Bad shape:** *"Here's a summary of the updates I made to work_queue.md and project_history.md..."* — Jeanette can't deploy a summary. She'd have to ask for the files anyway. Producing the summary first wastes a turn.

**Bad shape:** *"This is the new entry only — paste it into project_history.md above the 'Patterns visible' heading."* — Manual surgery on a live file. Easy to typo, easy to misplace, hard to verify. Each manual merge is a chance for the working tree to diverge from intent.

**Good shape:** A complete updated `project_history.md` with the new entry already in the right location. Jeanette runs `mv ~/Downloads/files/project_history.md docs/project_history.md` and the deploy is done.

The pattern that works: TC produces every file that needs to change, in full, and presents them through whatever the file-handover mechanism is. Jeanette downloads, moves, commits, pushes. No manual editing of live files.

### 2. Every candidate doc gets an explicit decision

For each document the session might plausibly affect, the TC makes a decision: *update* or *no update*. If no update, state the reason briefly. Silent omission of a doc that should have been considered is a coordination failure — the next reader can't tell whether it was forgotten, judged unnecessary, or genuinely irrelevant.

**Where the decision lives:** in the `project_history.md` entry for that session, alongside the list of what *did* change. One sentence is enough. Example:

> *Architecture companion considered, no update — the binary lifecycle change is a behavioural detail within the Electron layer rather than an architectural one.*

That sentence does the work. Future readers know the file was considered and skipped, and why. The next TC starting a related session knows the companion doesn't need re-checking on this account. No separate decisions log; the project_history entry is the right home because the decision is part of "what happened."

The candidate set for any TC session typically includes: `work_queue.md`, `project_history.md`, `architecture_companion.md`, `glossary.md`, `memory_files.md`, `maintenance.md`, plus any file-specific docs (`build_practices.md`, `terminal_commands.md`, etc.). A session doesn't touch all of them, and a session doesn't need to discuss all of them — only the ones a future reader might plausibly wonder about. If a session is purely HTML, the TC doesn't need to write *"memory_files.md considered, no update"* because no plausible reader would expect it. The bar is *plausibly relevant, not exhaustively considered*.

### 3. The deploy command block follows a fixed template

The block Jeanette runs at the end of a session has a standard shape. Following the shape makes the deploy mechanical. Deviating from it tends to produce silent partial commits or convention drift.

**The template:**

```
cd ~/Claudette
mv ~/Downloads/files/[file1] [destination1]
mv ~/Downloads/files/[file2] [destination2]
...
git add [file1] [file2] ... [code_files...]
git commit -m "[clear message — what shipped, not how]"
git push
```

**The fixed elements:**

- Always `cd ~/Claudette` first.
- Always `mv`, not `cp`. The convention is `mv` for deploys; `cp` leaves stale files in `~/Downloads/files/` that confuse the next deploy.
- Source paths are always flat: `~/Downloads/files/[filename]`, regardless of where the file lives in the destination. This is the "files downloaded from claude.ai unzip flat" rule from earlier in this document; it is non-negotiable because nested paths fail silently.
- Destination paths use the proper repo structure: `docs/work_queue.md`, `docs/briefs/some_brief.md`, etc.
- **If the session had an OP-written brief, include it.** The brief lives in `~/Downloads/files/` from when OP produced it at session start. Without an explicit deploy line, it sits there orphaned. Add `mv ~/Downloads/files/[brief_filename].md docs/briefs/[brief_filename].md` to the block, and `docs/briefs/[brief_filename].md` to the git add line. The brief commits alongside the work it scoped, and the historical record is complete.
- `git add` lists *every* file in the commit — both the moved files and any code files modified during the session that aren't in `~/Downloads/files/`. Forgetting a code file means the next push will leave it untracked.
- `git commit -m` uses a clear single-line message describing what shipped. The session prefix (e.g. `TC11-001`) plus a short list of changes is the standard shape.
- Always `git push` at the end. Without it, the changes are local-only.

**What the template never includes:**

- Manual-edit instructions like *"open this file and paste the new entry above the heading."* If a file needs changing, the change is in the file the TC produces.
- `cp` commands.
- Optional steps presented as "you might want to also..." Jeanette runs the block as written. Optional steps mean the block isn't ready.
- Comments inside the block referencing files that aren't in `~/Downloads/files/`.

### 4. Version lines: per-change, not per-date

Each key file (`server.py`, `retrieval.py`, `memory_writer.py`, `claudette_interface_connected.html`, etc.) carries a version line of the shape:

```
# Version: YYYY-MM-DD-TC[n]-[increment]
```

The increment goes up *every time the file changes*, but the increment resets when a new TC instance touches the file. Each TC starts at `001` for any file, regardless of what previous TCs did. The date is the date of that particular change.

**Concrete example:**

- TC10 ships server.py for the first time on 3 May → `2026-05-03-TC10-001`
- TC10 ships server.py again on 4 May → `2026-05-04-TC10-002` (same TC, second touch)
- TC10 ships server.py a third time later on 4 May → `2026-05-04-TC10-003`
- TC11 ships server.py on 5 May → `2026-05-05-TC11-001` (new TC, fresh increment)

The increment counts how many times *this* TC has touched *this* file. Not file lifetime, not session count — just this TC's touches of this file.

**The reason this matters:** version lines are how Jeanette and the next TC verify what's running. If a TC bumps `001` again on a second touch, the version line lies about whether anything changed between deploys. Worse, a TC starting a new session might read a stale `001` and assume they're picking up a clean baseline when they're actually picking up the *second* deploy with the same number.

When in doubt about your starting increment: search the file's commit history (`git log --oneline -- path/to/file`) for the most recent version line that *this TC* contributed. The next number after that is the right one. If this TC has never touched the file before, start at `001`.

---

### Why this is one section rather than four

These four rules are facets of a single discipline: *the end of the session is the moment to be most mechanical, least creative.* Every wobble in the last three days has been a small drift away from one of these four — a summary instead of a file, a `cp` instead of a `mv`, a 001 instead of a 002, an architecture_companion judgement left silent rather than stated. Individually, each is small. Together, they account for nearly all the friction in otherwise-clean sessions.

Treating them as one section reflects how they show up in practice: at the same point, in the same handover, by the same TC. A TC who internalises the four together produces clean handovers. A TC who treats them as four separate things to remember tends to forget at least one.

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
