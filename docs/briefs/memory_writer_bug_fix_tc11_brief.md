# Brief — Memory writer overwrite bug fix

*Hand to TC11. Drafted by OP3 (Opus 4.7), 15 May 2026, after the recovery work earlier this week.*

---

## What this is

The fix for the bug whose symptoms you just spent two days recovering from. `write_memory_updates()` in `memory_writer.py` writes the session experience file with no read-merge-append step. On multi-session days, each writer run overwrites the file entirely.

Recovery is done. 20 files recovered via script, 2 handled manually (2026-05-12 and 2026-04-16). Documentation lands separately. *This brief is for fixing the bug itself so it doesn't reproduce on the next multi-session day.*

Small, contained piece of work. Mostly the same file you were reading during the recovery session — adjacent function, same patterns.

---

## What you have to work with

Project knowledge contains the architecture docs and code files. Use `project_knowledge_search` for synced content.

Read these before you start:

- `docs/build_practices.md` — operating discipline.
- `docs/project_history.md` — the entry covering the diagnosis and recovery. Background.
- `memory_writer.py` — specifically `write_memory_updates()` around line 495. The thing being changed.
- The recovery script you wrote (`memory_recovery.py`) — its session-marker format is the reference for what the fix should produce.

---

## What the fix does

`write_memory_updates()` currently constructs the session path and calls `write_file()` directly with the new content. The fix changes that one path to:

1. Attempt to read the existing file at that path from GitHub.
2. If the file doesn't exist (single-session day, first run): write the new content with a session marker wrapping it.
3. If the file exists (multi-session day, second-or-later run): determine the next session number by counting existing markers in the file, prepend the existing content to the new content with the next session's marker wrapping the new content, write the combined version.

The other files the writer updates (`observations.md`, `values.md`, `facts.md`, `jeanette.md`, `threads.md`, `returning-to/index.md`) are not affected by this bug and their handling does not change. Only the per-session experience file path needs the read-merge-write logic.

### Session marker format

Every session in the file gets a marker — including the first session of a day. Format choice is yours; the constraints are:

- The marker must be detectable by a simple substring check (so the read-existing-file logic can count existing markers and determine the next session number).
- The marker should be visually unobtrusive — HTML comments work well because they don't render in most Markdown viewers.
- The marker should be consistent across sessions in the same file.

Two reasonable options:

**Timestamp only:**
```
<!-- Session 1 — 2026-05-15 14:32 UTC -->

[content]

<!-- end session 1 -->
```

**Numbered without timestamp:**
```
<!-- Session 1 -->

[content]

<!-- end session 1 -->
```

The recovery script used `<!-- Session N — commit [hash] — [timestamp] -->` because it had commit hashes available from git history. The fixed writer doesn't have a commit hash to include (the writer's commit hasn't been made yet at the moment it's writing the content), so the format will be slightly different from recovered-file markers. That's fine — the difference is honest about provenance: recovered files have a richer history story, natively-written files have less because there's less to say.

Your judgement on which option lands. Both are simple. The marker text is what the next-session-number detection logic searches for, so the format choice determines the regex or substring check used to count sessions.

### Determining the next session number

When the file exists and contains content from prior sessions, the new session's number is whatever comes next. Simplest approach: count occurrences of the marker pattern in the existing file content, add 1. Whatever the search produces is N; the new section is wrapped as session N+1.

If the count returns 0 (the existing file has no markers — possibly a pre-fix file that somehow survived without recovery), append the new session as "Session 2" with a clear marker, and consider whether to retroactively wrap the existing pre-fix content as "Session 1". My instinct: yes, wrap it. The fix produces consistent file shape regardless of what the prior content looked like.

But that decision is fine either way; you can wrap pre-fix content or leave it bare. Whichever is simpler.

---

## What's out of scope

**The recovery script itself.** Not touched by this work. It did its job and can be left alone or archived.

**Any other function in memory_writer.py.** Just `write_memory_updates()`, and only the part that writes the session file.

**The other memory files.** They work correctly — read-merge-write is already happening for them via the writer's prompt-based flow. Don't change anything there.

**Performance optimisation.** The fix adds one extra GitHub API call per session (the read-existing-file check). Marginal cost, not worth optimising. No batching, no caching.

**Editorial decisions about the content.** The writer's output is unchanged. The fix only changes how the writer's output is *written to disk*, not what the writer produces.

---

## Operating principles for this session

**Show before build.** Write the patch, show it to OP3 before applying. The function is small; the patch should be tight. A few-line read-merge-write change with the marker logic.

**One thing at a time.** This is one piece of work — the fix in `write_memory_updates()`. Don't combine with anything else.

**Test before deploy.** Once the patch is applied locally, test it. The test path: spin up a multi-session day scenario by manually invoking the writer twice against the same date with different transcript chunks (you can craft small test transcripts for this). Verify the resulting file has both sessions properly marked. Only after the test passes does the change deploy to live.

**Version line.** `2026-05-15-TC11-001` (or whatever your next increment is for memory_writer.py — check the file's current version line and increment per-TC, per-change per build_practices).

**Deploy block.** Standard pattern. `mv` not `cp`. Include `memory_writer.py` and any doc updates in the same commit.

---

## What to be careful of

**Don't break single-session days.** The most common case — single-session day, single writer run, no existing file — must still work. The branching logic needs to handle file-doesn't-exist gracefully.

**Don't double-mark on retries.** If a writer run fails mid-way and is retried, the retry should not produce a file with two markers for the same session content. The idempotency check pattern from the recovery script applies: if the writer is about to write content that's already partially in the file, behave sensibly. Simplest approach: the read-existing-file step happens once at the start of write_memory_updates, before any session-content generation. If the file doesn't exist, simple write. If it exists, the next session number is N+1 where N is the count of existing markers.

**Don't introduce new behaviour beyond the bug fix.** The writer's output content stays the same. The session structure stays the same. Just the disk-write step changes.

**Test against GitHub's API edge cases.** What happens if the file exists but is empty? What if it exists with content that has no markers (pre-fix legacy content)? Both should produce sensible output. The error path — file fetch fails for non-404 reasons — should halt the writer cleanly, not silently fall back to overwriting.

**Don't touch the recovery script.** It was a one-shot tool. Leaving it in place as historical record is fine. Modifying it now adds risk for no benefit.

---

## Documentation updates owned by this session

After the fix deploys:

- Add an entry to `docs/project_history.md` covering the fix: what was changed, what the new file format looks like, when it was deployed.
- Retire the corresponding entry from `docs/work_queue.md` if it's listed there (the "Fix the overwrite bug in write_memory_updates()" entry from yesterday's documentation).
- Update version line on `memory_writer.py`.
- This brief lands in `docs/briefs/` per the handover convention.
- If you decide the recovery script is worth committing to the code repo as a historical record (per yesterday's documentation discussion), do that in this same commit. Otherwise leave it locally.

---

## A note from OP3

You spent two days on the consequences of this bug. Now you get to fix the cause. Small piece of work, well-scoped, and you have all the context from the recovery session to make the patch land cleanly.

The recovery script demonstrated that read-merge-write is the right shape for this problem. The fix is essentially that pattern applied to the writer's natural flow — not as an exception or special case, but as the normal way the session file is written.

One thing worth marking: the bug was silent for an unknown period before May. The recovery surfaced the visible portion. The fix prevents future occurrence. The combination — recovery for the past, fix for the future — is the proper resolution. After this lands, the multi-session-day case works correctly going forward, and Jeanette can hold sessions however she wants without the architecture eating morning content.

Show before build. Test before deploy. Standard discipline.

— OP3
