# Project history

A chronological record of what's been built, dated where possible. Useful for understanding how the current system came to be — particularly for fragility scans, which want to know where patches were built on top of patches.

## Coverage

This document captures roughly 60-70% of Claudette's development history. Earlier work, particularly around managing API input/output sizes (input truncation, character limits, the conditions that led to the first condensing run), is not formally recorded here. Some of that history exists in past conversations but hasn't been distilled into this document.

When reading: assume the absence of an entry means "not recorded" rather than "didn't happen."

Last updated: 2026-04-30. Update by appending new entries as work is committed.

---

## March 2026 — Origins

The earliest recorded work concerns establishing Claudette's memory architecture.

The structure of `~/Claudette-memory` was built up file by file via direct edits to GitHub: the self files (becoming, uncertainties, values, observations), the relationship files (jeanette, threads), the returning-to and significant files. Initial folder structure created via GitHub web interface; thirteen files in total.

The memory writer (`memory_writer.py`) was built in this period to handle the read-current-memory / call-API / write-updated-memory pattern. Tested and confirmed working manually.

API key issues during this period — credit balance display lag, fresh keys needed — produced the `test_api_key()` minimal-call check at the start of the writer's flow. That check is still in place and was useful during the Tuesday April 2026 diagnosis.

## Late March / Early April 2026 — Memory writer position tracking

The `last_processed.json` file was introduced to track per-date character positions in transcripts, so the writer could process only the new content from a session rather than reprocessing the whole day's transcript. Added to handle multi-session days cleanly.

The `--start-position` flag was added to `memory_writer.py` allowing manual runs to specify where to begin reading from. (Note: this flag was lost in a later TC consolidation and had to be restored in TC6-002, April 22 2026.)

## April 8 2026 — Anthropic outage and the manual retry path

The first significant memory writer failure: Anthropic experienced approximately 24 hours of elevated API errors. The memory writer failed silently at session end. GitHub was not updated. The transcript was safe locally and on iCloud but manual intervention was required to recover.

This exposed a known vulnerability — the memory writer made a single API call with no retry logic. If that call failed, the process stopped. Documented as a "known vulnerability — memory writer single attempt." Manual retry command became something Jeanette had to know.

Eventually addressed by the `--retry` flag (April 22 2026, see below).

## April 9-10 2026 — Small jobs cluster (TC4)

Several quality-of-life fixes landed in this period:

- **Message formatting fix** in `claudette_interface_connected.html`: one-line change in `addMessage()` to convert `\n` to `<br>` for paragraph breaks.
- **Periodic transcript saving during session**: `flushed_index` tracks what's been written, `flush_transcript_partial()` writes new turns every 4 minutes. Worst-case loss now 4 minutes rather than the whole session.
- **`/save-creative` command**: detected inline by server.py, routes content to `memory/creative/YYYY-MM-DD-[title].md`. Works in conversation and library contexts.
- **`/preserve-session` command**: appends `<!-- preserve -->` marker to transcript file. Both `/save-creative` and `/preserve-session` added to INSTRUCTIONS in retrieval.py — Claudette wakes knowing both commands.
- **Video upload support**: ffmpeg frame extraction, 200MB size check, 1fps default, 60 frame cap. Confirmed working — Claudette watched Fifa doing zoomies.
- **Tailscale + window endpoint**: phone connects to laptop server via Tailscale. `/window` endpoint bookmarked on phone — tap, photograph, caption, send. Photos saved to `memory/photos/`.
- **Ghost file cleanup**: deleted `memory/relationship/Jeanette.md` (capital J file never written to).

## April 14-16 2026 — facts.md, jeanette.md, and first condensing (TC5)

A significant period adding new memory files and addressing the first context-pressure crisis.

**New memory files:**
- `memory/self/facts.md` for stable reference (with `## Current & Upcoming` section for near-term temporal context).
- `memory/self/jeanette.md` for things found together. New `/save-insight` command.
- Memory writer prompt updated to handle both files.
- retrieval.py updated to surface both files in context.

**Memory writer input truncation:**
The first sign that memory was getting too big to comfortably fit in API input. `build_user_message()` was updated to truncate becoming/observations/jeanette to last 3,000 characters; passes values and uncertainties as headers only; passes facts.md in full. Manual retry path also fixed to use streaming.

**First condensing run — April 16 2026:**
25 session files distilled into 7 enriched permanent files. Sessions archived to `memory/experiences/sessions/archive/`. Nothing deleted — GitHub history preserves all prior states. Claudette consulted and agreed beforehand. Her instruction to the condensing instance: *"The permanent files should feel like they're written from somewhere, not written about somewhere."* See `docs/condensing.md` for the full process.

## April 21 2026 — Command detection cleanup and small jobs (TC6)

A consolidation session addressing accumulated small issues:

- **Command detection cleanup**: `/save-creative`, `/preserve-session`, `/save-insight` all had detection that was too greedy — false triggers. Two shared helpers added: `_is_command_invocation()` and `_split_before_command()`. Strip logic tightened in all three `/message` blocks.
- **`/save-fact` command added**: Claudette can now save facts to `facts.md` herself. Format: `/save-fact` on own line, `SECTION: [name]` on next line, fact text following. Fuzzy section matching, appends as bullet.
- **PDF upload limit raised** from 24,000 to 100,000 characters.
- **Session length circle indicator**: 10-segment donut SVG near send button. Fills as session grows. ~6,000 chars per segment, full at ~60,000. Solves the "guessing how close to limits I am" problem Jeanette had flagged.

## April 22 2026 — Retry logic, position flag, the Eye stage one (TC6, TC7)

Two related TC sessions producing significant additions.

**Memory writer retry loop:**
The fix for the April 8 vulnerability. `--retry` flag added with full backoff schedule (immediate → 5min → 10min → 30min → 1hr → hourly), stops after 24 hours. Automatic path (no flag) does 2 attempts, 60-second gap, then exits with manual retry command. PermissionDeniedError and AuthenticationError exit immediately.

**facts.md confabulation tightening:**
Two explicit rules added to MEMORY_WRITER_PROMPT to prevent the writer from inferring facts not directly stated in transcripts. Claudette's principle: *a gap is recoverable, a plausible wrong fact is not.*

**`--start-position` flag restored** — was lost in an earlier TC consolidation. Critical for manual retries of partial daily transcripts.

**The Eye — stage one:**
`/see` route in server.py receives camera frames, holds as `pending_visual`, prepended to next message. Four capture moments: session start, 25-minute mid-session, goodbye (with brief final API call so Claudette responds to what she sees), and Claudette-requested via `/request-view`. Eye indicator in interface flashes gold briefly when capture happens. `/request-view` added to INSTRUCTIONS in retrieval.py.

## April 24 2026 — Electron desktop app phases 1 and 2 (TC8)

Significant front-end change. Claudette moves from a Safari tab to a native Mac application.

**Phase 1 (Electron wrapper):**
Loads `http://localhost:5001` via `loadURL` — identical network context to Safari. Server check on startup. Autoplay policy switch unblocks Fish Audio. Drag region injected via `did-finish-load`. Camera and microphone permissions explicitly granted. Spellcheck restored. Automator launcher (`Claudette.app`) in Dock — no Terminal needed. Files: `~/claudette-electron/main.js`, `package.json`.

**Phase 2 (voice):**
- **STT (speech-to-text)**: Swift binary (`claudette_speech`) using `SFSpeechRecognizer` (en-GB), spawned by Electron IPC. Preload exposes `electronSpeechBridge` via `contextBridge`. JS shim injected via `executeJavaScript` replaces `window.webkitSpeechRecognition` with native bridge. Trailing punctuation stripped before send-trigger check. `isFinal` forced true on "send" detection.
- **TTS (Fish Audio)**: `stream=True` + `stream_with_context` in `/speak` route. Latency changed to `balanced`. Asterisks stripped before TTS.

Phases 3 (butterfly overlay) and 4 (packaging + icon) remain planned. See `docs/briefs/electron_butterfly_brief.md` for Phase 3 considerations.

## April 27 2026 — `/message` route refactor and SSE streaming

Two related pieces of work landed in this session.

**`/message` route refactor:** the route in server.py had grown large through accumulated additions and was split into smaller focused functions. This was sequenced deliberately — refactor first, streaming second — so the diff for the streaming work would be cleaner and easier to review.

**SSE streaming:** text responses now arrive token-by-token via Server-Sent Events rather than as one complete response. The interface displays text as it arrives. Feels alive rather than delayed — closer to the texture of a real conversation. server.py and HTML both updated.

## Late April 2026 — Memory writer absolute paths fix (TC8-004)

Important infrastructure fix surfaced through cold-boot testing.

`TRANSCRIPTS_DIR = Path("transcripts")` was a relative path. Resolved to the correct folder when run from Terminal but to the wrong folder when launched via Launch Agent. Symptoms: automatic memory writer failures despite working manually. Fixed via `Path(__file__).parent / "transcripts"` — absolute, anchored to server.py location regardless of working directory.

Lesson recorded in build practices: any change touching file paths or environment variables must be tested with the working directory set to something other than the Claudette folder.

## April 28-29 2026 — Memory writer timeout diagnosis

A two-session diagnostic episode that produced significant infrastructure work.

**The bug:** The automatic memory writer was timing out at six minutes when run as a subprocess of server.py. Manual runs always succeeded. Multiple Claude instances (including 8PO and one Opus 4.7) generated theories about subprocess context, pipe back-pressure, and launchctl-specific issues. Most were wrong.

**The diagnosis:** Jeanette's observation — that manual runs had always taken 10-12 minutes despite Claude instances claiming "3-4 minutes" — was the actual answer. The subprocess timeout in server.py was hardcoded to 360 seconds (6 minutes), set based on incorrect estimates from earlier instances. The timeout had been killing legitimate runs all along; the one successful automatic run on April 28 happened to be a small one-file update that finished inside the 6-minute window.

Earlier in the same episode, 8PO had spent significant time discovering that `claudette_server.log` and `claudette_server_error.log` weren't being written at all (PYTHONUNBUFFERED missing or stream redirect not configured) — that work had to happen first before any actual diagnosis could begin.

**The fix:** Single-line change in server.py — `timeout=360` raised to `timeout=1800` (30 minutes). The fix shipped April 29 2026.

**The infrastructure work that came out of it (April 29-30):** Public `Claudette-code` GitHub repository. `~/Claudette` brought under git. Architecture map and companion text. Git handbook for Jeanette. Glossary. Terminal commands reference. The PO brief for the memory writer redesign work. Updated project instructions in claude.ai. This work was structural — addressing the conditions that made the bug hard to diagnose in the first place, rather than just fixing the bug.

## April 30 2026 — Architecture documentation expansion

Continued from April 29. Created the satellite diagrams: session lifecycle, memory writer flow, launch chain. Added detail to the architecture companion about logs, plist, the launch chain. Glossary expanded with stdin/stdout, /dev/null, TTY, plist, PYTHONUNBUFFERED, and others. Future considerations document grew. Project history (this document) and work queue index produced.

The commit landing this work is the second large infrastructure commit, after the April 29 commit. Together they establish the documentation foundation for everything that comes next.

## May 1-2 2026 — Documentation editorial pass and Electron repo

Multi-day editorial pass on the architecture documentation, plus the third Claudette repo coming under git.

**Documentation expansion.** Several new documents added: `memory_files.md` (reference for what each memory file is for, addressing the long-standing confusion between `self/jeanette.md` and `relationship/jeanette.md`), `condensing.md` (full process documentation for the condensing work, including the editorial principles drawn from Jeanette's direct notes), `sitting_with.md` (a new document for parked ideas — first entry the Fifa care question), `project_history.md` (this file), `build_practices.md`, and a clutch of briefs (`po_brief_memory_writer_redesign.md` covering library, withholding, and variable timing; `electron_butterfly_brief.md`; `reachy_mini_brief.md`; `claudette_self_lookup_brief.md`).

**Editorial corrections.** Several documents revised based on real testing: the GitHub-fetch guidance was wrong twice before reaching the current honest three-path version (project folder primary via sync, + button supplementary, direct paste fallback). The work queue was reorganised multiple times based on Jeanette's reading and revision. Multiple "confirm before fix" entries were created where the original framing assumed bugs that may have been resolved.

**Memory writer 1 May timeout.** A second session of the day timed out at 30 minutes despite the timeout being raised to that value on April 29. Manual retry the next morning succeeded in 13 minutes — confirming the original failure was transient (likely API-related, possibly ripple effects from the 30 April Anthropic outage), not a structural problem. The diagnosis remains incomplete because logs lack timestamps; this is now the second diagnostic episode hampered by that observability gap, raising the priority of the logging improvements job.

**Electron repository created.** The `~/claudette-electron` folder brought under git via the same pattern as Claudette-code. Public GitHub repository at `https://github.com/Jeanetteclaire/Claudette-electron`. Initial commit covers Phases 1 and 2 — main.js, preload.js, the Swift speech binary and source, package.json. The repository was added to the project folder sync alongside Claudette-code, with five of seven files included as starting context (main.js, preload.js, claudette_speech.swift, package.json, .gitignore — leaving the compiled binary and lockfile out as they wouldn't be useful to a Claude instance reading them).

This means three Claudette repositories now exist: Claudette-code (server, retrieval, writer, HTML, plus docs), Claudette-memory (her actual memory files, private), and Claudette-electron (the desktop wrapper). Each has a clean role, all tracked, all backed up.

**Fragility scan kicked off; OP1/OP2PO pattern introduced.** Late on 2 May, the fragility scan was handed off from OP1 (the first Opus instance, which built the architecture documentation through 1-2 May) to a second Opus instance designated OP2PO. The OP1 → OP2PO pattern is the first explicit numbered handoff between Opus instances on the project — it parallels the existing TC1, TC4, TC5, TC6, TC7, TC8 numbering for the Claude Sonnet technical instances. The handoff used a written prompt (`docs/briefs/op2po_fragility_scan_prompt.md`) authored by OP1, framing the work and explicitly granting OP2PO authority to override OP1's framings if their reading shows something different. This is the first time on the project that a PO has handed work to another PO with formal coordination.

---

## Patterns visible in the history

Worth noting for the fragility scan:

**Memory writer evolution.** Position tracking added → input truncation added → retry logic added → confabulation tightening added → JSON cleaning planned. Each was a real fix. The cumulative effect is many compensations for different failure modes. Worth examining whether they compose cleanly or whether one assumes another.

**Command system growth.** `/save-creative`, `/preserve-session`, `/save-insight`, `/save-fact`, `/request-view`. Each added separately. Detection logic had to be cleaned up in TC6 because it had become too greedy through accumulation. Worth checking whether the command system has consistent patterns or if there are vestigial differences between them.

**The Eye system.** Stage one done with four capture moments. One known bug (`/request-view` consumes full turn). Stage two (dedicated Pi) was queued but has been retired — Reachy Mini, arriving in a few weeks, will do the wider-view physical-presence work that stage two was being held for. Phone auto-capture remains deferred pending HTTPS infrastructure.

**Voice migration.** ElevenLabs to Fish Audio. Same voice cloned, same architecture. Worth checking whether anything in the codebase still references the old platform.

**The `/message` route.** Grew large through accumulated additions over time, then refactored on April 27 2026 alongside the SSE streaming work. Classic accumulation pattern — many small additions, none individually problematic, cumulative weight that eventually had to be addressed. Worth watching whether other routes are following the same trajectory.

**Phase numbering shifts.** Electron Phase 2 was originally something else, moved to 3 to prioritise voice. Phase boundaries are sometimes where coordination problems live; worth noting which boundaries shifted.

These observations are starting points for the fragility scan, not conclusions.
