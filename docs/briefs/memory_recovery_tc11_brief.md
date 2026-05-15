# Brief — Memory recovery script (experience file overwrite bug)

*Hand to TC11. Drafted by OP3 (Opus 4.7), 13 May 2026, after diagnosis of a silent overwrite bug in memory_writer.py affecting multi-session days. v2 — corrected the dry-run test file and excluded 2026-05-12 from script scope (already manually recovered).*

---

## Who you are in this session

You are TC11, continuing from your HTML work earlier this month. You have not touched memory_writer.py or the GitHub API integration before. This session is small in scope but high in stakes — it touches the canonical memory repo with real writes, and any bug in the script could compound the problem it's trying to fix.

The job is a single-file Python script that recovers content silently overwritten across 23 multi-session days. *Recovery only.* The underlying bug in `memory_writer.py`'s `write_memory_updates()` is documented separately and out of scope for this session.

---

## What happened

Diagnosis from yesterday:

`memory_writer.py`'s `write_memory_updates()` function writes the session experience file (`memory/experiences/sessions/YYYY-MM-DD.md`) with no read-merge-append step. Each writer run overwrites the file entirely with the content from that run's transcript chunk only.

On single-session days this is fine — one run, one write, the file contains that session's content.

On multi-session days the bug fires: the morning writer produces morning content, writes the file. The afternoon writer produces afternoon content from the afternoon transcript chunk, writes the file — overwriting the morning content. The morning content is preserved in git's commit history but no longer present in the current file.

Jeanette noticed this on 12 May. She read the morning content in her experience file that morning, then after the afternoon writer ran manually (recovering from a Mac update interruption), the morning content was gone — only afternoon content remained.

A count of all experience files with multiple commits identified 23 affected days from 16 April through 12 May. Some have 2 commits; some have as many as 7.

The other memory files (`observations.md`, `values.md`, `facts.md`, `jeanette.md`, `threads.md`, `returning-to/index.md`) are not affected — they're not date-keyed and the writer reads-and-merges them correctly. Only experience files are affected.

The bug itself in `write_memory_updates()` will be fixed in a separate session. *Your job is recovery only.*

---

## What you have to work with

Project knowledge contains the architecture documentation and code files. Use `project_knowledge_search` — synced files do not appear at `/mnt/project/`.

Read these before you start:

- `docs/build_practices.md` — operating discipline.
- The current `memory_writer.py` — to see how it currently uses the GitHub API library. The recovery script should reuse the same library and the same authentication pattern.
- The list of affected files (below).

The 22 affected experience files, with commit counts:

```
2026-04-16.md (5 commits)
2026-04-17.md (5 commits)
2026-04-18.md (3 commits)
2026-04-19.md (2 commits)
2026-04-20.md (5 commits)
2026-04-21.md (5 commits)
2026-04-22.md (4 commits)
2026-04-23.md (4 commits)
2026-04-24.md (7 commits)
2026-04-26.md (6 commits)
2026-04-27.md (4 commits)
2026-04-28.md (5 commits)
2026-04-29.md (4 commits)
2026-04-30.md (3 commits)
2026-05-01.md (2 commits)
2026-05-03.md (5 commits)
2026-05-04.md (6 commits)
2026-05-05.md (3 commits)
2026-05-06.md (2 commits)
2026-05-07.md (3 commits)
2026-05-08.md (5 commits)
2026-05-11.md (4 commits)
```

Total: 92 commits across 22 files. For each file, every commit except the last one represents content that was overwritten by a subsequent run.

**Note on 2026-05-12.md, which is *excluded* from the script's scope.**

The file `2026-05-12.md` was the diagnostic case — the day Jeanette noticed the bug. She recovered that file manually via GitHub's web editor yesterday afternoon, pasting the morning content back in alongside the afternoon content. That manual recovery added a third commit to the file's history. If the script were to run against 2026-05-12.md, it would treat the manual recovery commit as a third "session" and produce a file containing morning + afternoon + (morning + afternoon already combined) — duplication and corruption.

Do not include 2026-05-12.md in the script's affected files list. It is already recovered manually. The script must explicitly exclude it.

The repo is `Jeanetteclaire/Claudette-memory`. Authentication uses the `GITHUB_MEMORY_TOKEN` environment variable, same as `memory_writer.py`.

---

## What the script does

A single Python script at `~/Claudette/memory_recovery.py`. Standalone. Not imported by anything else; runs once, then can be deleted or kept as a record.

For each affected file in the list above:

1. Fetch every commit that touched the file, in chronological order (oldest first).
2. Retrieve the file's content at each commit.
3. Concatenate them with strict session markers.
4. Write the concatenated content back to the file as a single new commit.

After the script runs, each affected file contains every version's content in order, with no editing.

### Format of the concatenated output

Each session's content is bracketed with markers showing which commit it came from. The markers are intentionally explicit — they make the recovery traceable and let Claudette or a future reader see what came from where.

Suggested format (open to adjustment if you have a better shape):

```markdown
<!-- Session 1 — commit abc1234 — 2026-04-16 09:34 UTC -->

[content from commit abc1234 — the original morning version]

<!-- end session 1 -->

<!-- Session 2 — commit def5678 — 2026-04-16 14:22 UTC -->

[content from commit def5678 — the afternoon version that overwrote morning]

<!-- end session 2 -->
```

The commit hash and timestamp give traceability. The HTML comments are non-rendering in most Markdown viewers so they don't visually clutter the content. The session numbering is sequential within each file.

No editorial judgement by the script. No deduplication. No trimming of repeated framing between sessions. The script preserves what was there. If two sessions both start with a similar date header, both date headers appear in the output. Better to preserve verbose-but-honest than to risk further loss through over-eager cleanup.

### Commit message for the recovery write

One commit per file. Suggested message:

```
Recover [date] — restore overwritten morning/midday session content (N sessions concatenated)
```

Where `[date]` is the file's date and `N` is the number of historical commits being concatenated. This makes the recovery commits identifiable in the repo's history.

---

## Operating principles for this session

**Show before build.** Write the script, show it to Jeanette and OP3 before running. The script writes to the canonical memory repo. A bug in the script could compound the problem rather than fix it. Approval comes before execution.

**Dry run before live run.** Once the script is approved, run it first against a *single* test file: `2026-05-06.md`. This is a deliberately chosen test case because its two sessions are topically distinct — Jeanette discussed a dream in the morning, library redesign work in the afternoon. The two halves of the recovered file should be easy to identify and verify. Run the script only against this file, examine the output, confirm correctness, then run across the remaining 21 files.

The verification Jeanette will do on the dry-run output:

1. *Triangulation.* She'll check three things against each other: the content from each historical commit on GitHub (viewable via the commit URLs), the dream/library boundary in the original transcript at `~/Claudette/transcripts/2026-05-06.txt`, and the script's output. All three should agree on what was in session 1 vs session 2.

2. *Topical correlation.* Session 1 in the script's output should contain dream content. Session 2 should contain library redesign content. If they're in the wrong order, mixed together, or missing — something is wrong with the script's commit-ordering or content-extraction logic.

3. *Before-and-after sanity check.* The current state of `2026-05-06.md` on GitHub (the afternoon-overwrote-morning version) should match session 2 in the script's output. If session 2 doesn't match the current GitHub state, the script is doing something unexpected.

Only after Jeanette confirms all three checks pass do you run the script across the remaining 21 files.

**Idempotency matters.** If the script is run twice by accident, the second run shouldn't double-concatenate or otherwise corrupt the files. Best protection: the script should detect whether a file already contains the session markers (which means recovery has happened) and skip it on subsequent runs. Belt and braces.

**No deletion. No force-push. No history rewrite.** The script only reads commits and writes new commits. It does not delete commits, does not rewrite history, does not force-push. The historical commits remain in place; the recovery is a new commit on top of them.

**Logging.** The script logs to stdout what it's doing: which file it's processing, how many historical commits it found, that it wrote a new commit. Jeanette runs it from terminal and sees progress in real time.

**Stop on error.** If any file fails — for whatever reason — the script logs the failure clearly and stops. Doesn't try to continue past errors. Jeanette can investigate the failure with you, fix the issue, and resume.

---

## What to be careful of

**Don't fix the underlying bug.** The bug in `write_memory_updates()` is documented and queued separately. Touching it in this session expands scope and creates risk. Recovery only.

**Don't modify any files outside the 22 listed.** The list is the scope. Files outside it are either healthy single-session days or already-recovered (2026-05-12.md); touching them is unnecessary and risky.

**Don't read GitHub commit history through the local clone.** Use the GitHub API directly (same `github` library `memory_writer.py` uses). The local clone may be out of date or in an inconsistent state. The canonical source is GitHub.

**Don't assume the existing file's content is the "newest" session.** Yes, that's likely true given the bug shape — the latest commit is the most recent session. But the script should not rely on that. It should fetch every commit's content programmatically and concatenate in commit-timestamp order. Let the data tell the story.

**Don't introduce new dependencies.** The script should use only the libraries `memory_writer.py` already uses. No new pip installs. Standard library plus the `github` library is enough.

**Don't run the script unattended.** Jeanette is present when it runs. If something goes wrong, she sees it. Long-running unattended scripts that touch canonical data are exactly how silent corruption happens.

---

## What's out of scope

- The bug fix in `write_memory_updates()`. Separate session.
- Recovery of any non-experience files. Other files don't have this bug.
- Cleanup of duplicated framing within the recovered content. If Claudette or Jeanette want to read through and tidy redundant headers, that's a human-judgement task separate from this script.
- Changes to memory_writer.py itself.
- Changes to server.py.
- Changes to anything in the code repo beyond creating the new recovery script.

---

## Documentation updates owned by this session

After successful execution:

- Add an entry to `docs/project_history.md` covering the recovery: what was lost, when it was diagnosed, what the script did, when it was run, the count of files recovered.
- Add an entry to `docs/work_queue.md` under immediate jobs for *Fix the overwrite bug in memory_writer.py's write_memory_updates() function*. Brief entry — the diagnosis is captured in project_history.

The script itself (`memory_recovery.py`) can either be committed to the code repo as a historical record, or kept locally and not committed. Your judgement — if you commit it, add a header comment explaining what it was for and noting that it's one-shot.

The session brief (this document) also lands in `docs/briefs/` per the build_practices handover convention.

---

## Actual outcomes (added post-session)

Script ran 13 May 2026. Results:

- **20 files recovered via script** — concatenated sessions with HTML comment markers, committed to Claudette-memory.
- **1 skipped** — 2026-05-06.md (dry-run test file; recovery marker already present, idempotency check caught it correctly).
- **1 needs manual recovery** — 2026-04-16.md. The commit history contains a deletion commit (8161d4c) that returns 404 on content fetch. Script was patched mid-run to handle 404s gracefully (log and skip rather than halt), but 2026-04-16.md's history is complex enough that Jeanette will recover it by hand.
- **1 already recovered** — 2026-05-12.md (manually recovered by Jeanette on 12 May, correctly excluded from script scope).

The underlying bug in `write_memory_updates()` remains unfixed and is queued as an immediate job.

---

## A note from OP3

This is small, focused, mechanical work. The diagnosis is clean. The script is short. The recovery is reversible (you'd just revert the recovery commits if anything went wrong). Approach it carefully but not anxiously — the cost of getting it wrong is bounded.

The reason for the show-before-build and dry-run-first discipline is that *the canonical memory repo holds real value*. Most of what makes Claudette persist across sessions lives in those files. A bug in the recovery script that corrupted files instead of restoring them would be worse than the overwrite bug itself, because the original content would already be entrenched in older commits while the new commits would be wrong.

The first run, on `2026-05-06.md` only, is the proof. Jeanette can compare the script's output against what she saw manually yesterday. If it matches, the approach is sound and the remaining 22 files can be processed.

— OP3
