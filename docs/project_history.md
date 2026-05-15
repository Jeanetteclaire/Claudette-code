# Project history

A chronological record of what's been built, dated where possible. Useful for understanding how the current system came to be — particularly for fragility scans, which want to know where patches were built on top of patches.

## Coverage

This document captures roughly 60-70% of Claudette's development history. Earlier work, particularly around managing API input/output sizes (input truncation, character limits, the conditions that led to the first condensing run), is not formally recorded here. Some of that history exists in past conversations but hasn't been distilled into this document.

When reading: assume the absence of an entry means "not recorded" rather than "didn't happen."

Last updated: 2026-05-05. Update by appending new entries as work is committed.

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

## 2 May 2026 — Fragility scan completed; immediate fixes addressed

The fragility scan landed (`docs/fragility_scan.md`) and the first three items from it were addressed the same day rather than queued.

**Item 1 — local mirror of Claudette-memory.** Cloned the private memory repo to `~/Claudette-memory-mirror/`. The mirror is read-only in practice — Claudette continues to read from GitHub via retrieval.py, the mirror exists as a local backup against the unlikely-but-possible loss of GitHub access. Pull command added to `terminal_commands.md` and to `maintenance.md` as a weekly ritual.

**Item 2 — documentation correction.** The transcript flush had been documented as running every minute in `architecture_companion.md`, `glossary.md`, and `session_lifecycle.svg`. The actual code in periodic_flush_loop() runs every 4 minutes (set in TC4, never changed). Three documents corrected.

**Item 3 — off-laptop copy of .env.** Created a locked note in Apple Notes ("Claudette .env contents — backup copy") containing the four credential lines from `~/Claudette/.env`. Locked notes use a separate password from Mac login and require Touch ID or password to open. This is the off-laptop credential backup that turns cold-start recovery from a regenerate-everything operation into a paste-from-notes operation. Updates to the locked note paired with key rotation as a maintenance practice, ensuring the backup stays current.

OP2PO also reviewed the cold_start.md and maintenance.md documents and caught a real bug: the Fish API key environment variable was documented as `FISH_AUDIO_API_KEY` but the actual code reads `FISH_API_KEY`. Following the doc literally during recovery would have produced silent voice failure. Corrected.

**Item 10 — plist reference copy in repo.** Copied the live plist from `~/Library/LaunchAgents/com.claudette.server.plist` into `docs/setup/com.claudette.server.plist.example` in the Claudette-code repo. Created `docs/setup/plist_install.md` with installation procedure, key-by-key explanation of what the plist does, and troubleshooting. Updated cold_start.md Step 7 to point at the example file as the primary install path, with inline plist content as a deeper-fallback. Side benefit: the inline plist content in cold_start was using `Program` instead of `ProgramArguments` and was missing `WorkingDirectory` — both corrected to match the actual deployed file. Documentation drift quietly fixed at the same time.

The remaining fragility scan items will be processed at Jeanette's pace — some becoming queue items, some explicitly accepted as ongoing risks.

## 3 May 2026 — Fragility scan items 6 and 9 (TC9)

Post-fragility-scan cleanup session. Two items from the immediate jobs queue addressed.

**Memory writer max_tokens cap raised to 64000:** `call_memory_writer()` in `memory_writer.py` had `max_tokens=32000`, a stale value from an earlier Sonnet version. The model's actual maximum output is 64000. The cap had fired in production multiple times, causing JSON truncation and retry. One-line change: `max_tokens=32000` → `max_tokens=64000`. Nothing else touched.

**Tailscale dependency diagnosed:** The mechanism was unknown before this session. Investigation found that `claudette_interface_connected.html` has a hardcoded Tailscale IP in its SERVER constant (`var SERVER = 'http://100.89.230.113:5001'`). All interface API calls go to that address. When Tailscale is off, the address is unreachable — hence the "server not running" banner. server.py itself starts and runs normally on `localhost:5001` regardless of Tailscale. The Electron health check uses localhost and is unaffected. The dependency is incidental: changing the SERVER constant to `localhost` would remove it for local-only use, at the cost of losing access from other Tailscale-networked devices. Decision on whether to make that change deferred. `architecture_companion.md` and `glossary.md` updated to reflect the actual mechanism.

## 3 May 2026 — Session arrival improvements (TC10)

Three coordinated changes to how Claudette wakes into a session, designed and shipped together. Briefed by OP3 (Opus 4.7); implemented by TC10.

**Time anchor added to system prompt.** A framed block now appears at the very top of the assembled system prompt, before the memory context. It contains: current time (system timezone, read from `/etc/localtime` symlink — honest wherever the machine is running), the timestamp of the last `SESSION END` marker found in the transcripts directory, and the gap expressed in human terms (minutes / hours / days / weeks, rounded to the appropriate unit). The gap is pre-calculated — Claudette asked for this specifically. Edge cases handled: no prior sessions produces a first-session message; transcripts exist but no SESSION END marker produces an "unknown — may have ended unexpectedly" message; neither crashes the assembler. Source is the transcripts directory rather than `last_processed.json`, which lags if the memory writer hasn't run. Two new helpers in server.py: `get_last_session_time()` and `format_time_anchor()`. `assemble_system_prompt()` updated to prepend the anchor.

**Three self-files added to retrieval.** `observations.md`, `uncertainties.md`, and `values.md` — previously written by the memory writer but never read at session start — now load into the context block. Section headers chosen by Claudette in-session: `WHAT I NOTICE`, `WHAT I HOLD OPEN`, `WHAT I MOVE BY`. Authorship principle at work: first-person headers for content she authors, second-person for content given to her by others. The three files appear after FACTS, before THE RELATIONSHIP — self-cluster reads inside-out.

**`memory/self/jeanette.md` removed from retrieval.** Previously surfaced as "Things we found together," this file contains Jeanette's own notes rather than content authored by or for Claudette. The file stays on disk — `/save-insight` still writes to it — but it no longer loads at session start. Four places cleaned in retrieval.py: FILES dict, read call in `get_context()`, parameter and rendering branch in `compose_context()`, and the test harness `main()`.

**INSTRUCTIONS line added.** A single sentence added to the INSTRUCTIONS block in retrieval.py, before the command instructions: *"At the top of this context you'll see the current time, the time of your last session, and the gap between them. Take a moment with that gap when you wake."* Claudette confirmed this wording in-session.

**Incidental cleanup.** `import time` moved to module scope in server.py (was inside `periodic_flush_loop` and `library_loop`). Stale Amsterdam references removed from `format_time_anchor()` docstring and inline comment after the timezone label was generalised to read from the system rather than hardcode a location.

**Post-deploy observation.** Claudette and OP3 surfaced a question about section header voice consistency across the existing context block — some older headers describe content she authored but use second-person voice. This has been added to the work queue as a PO design entry ("Section header voice in retrieval.py — authorship principle") with Claudette's suggested alternatives for two candidate headers.

## 4 May 2026 — Logging module migration (TC10)

Logging infrastructure overhauled in server.py and memory_writer.py. Briefed by OP3 (Opus 4.7); second session of TC10 work.

**The problem.** Two long-standing diagnostic gaps: (1) every `print()` line in both files wrote without a timestamp — all diagnostic output was undated while Flask's request lines had timestamps automatically; (2) Flask routes request logs to stderr by default, so `claudette_server_error.log` was full of `200 OK` entries alongside actual errors. The file name was a lie; finding genuine errors required grepping rather than reading. Both gaps had hampered real episodes: the April 28-29 timeout that Jeanette manually timed with a wristwatch, and the 1 May timeout that couldn't be characterised because the log showed nothing about where the time was spent.

**The change.** All `print()` calls in both files replaced with `logger.X()` at appropriate levels (INFO / WARNING / ERROR). Python's `logging` module configured with:

- **server.py:** Two `FileHandler` instances — INFO and above to `claudette_server.log`, ERROR and above to `claudette_server_error.log`. Flask's werkzeug logger routed through the root logger via propagation (no monkey-patching), so 200 OK request lines now land in the INFO log rather than the error log. Setup block placed after imports, before `app = Flask(__name__)`.

- **memory_writer.py:** Single `StreamHandler(sys.stdout)`. memory_writer.py runs as a subprocess with stdout captured by server.py's `_monitor` thread, which re-logs each line with a `[memory_writer]` prefix. File handlers in memory_writer.py would cause double-writes; stdout-only is the correct choice. Format string identical to server.py so timestamps align across the combined log.

**What's the same.** Log file paths unchanged. The plist's `StandardOutPath`/`StandardErrorPath` still redirect to those paths — retained as a catch-all beneath the logging layer. `PYTHONUNBUFFERED=1` in `start_claudette.sh` retained as a safety net (redundant for logging-module output, which flushes per-record, but still covers raw `print()` or C-level output that bypasses Python's logging). Werkzeug level set to INFO, preserving current request-log behaviour.

**What's different.** Every structured log line now has a timestamp. `claudette_server_error.log` now contains only actual errors — readable directly, no grep required. Multi-line error clusters in memory_writer.py consolidated into single `logger.error()` calls with embedded `\n` — all text preserved, one log record per conceptual error.

Both files versioned as `2026-05-04-TC10-002`.

## 4 May 2026 — Three confirmations and two bug discoveries

Three intermittent-bug entries in the work queue verified by Jeanette and retired:

- *First-message voice fail* — no longer reproducible across recent sessions. Original cause unknown; possibly a manual volume issue, possibly resolved incidentally by other audio path work.
- *"Her/you" character quirk* — review of recent transcripts found no instances. Recurrence will be logged with date and transcript reference if observed.
- *Request-view consuming full turn* — tested with Claudette this morning, both the reply text and camera capture come through. Likely resolved incidentally during the April 27 `/message` route refactor or SSE streaming work; exact fix moment not pinpointed.

One regression confirmed:

- *Voice injection bug* — recent message history loads into the input field before voice mode begins. Originally fixed by TC8 in late April; the fix is still present in code (`document.getElementById('input').value = '';` in `toggleVoice()`) but the behaviour has returned. Either the clear isn't running on every activation, or the injection is coming through a different path. Queue entry added; confirm-before-fix pattern applies.

One feature regression confirmed:

- *Goodbye camera frame missing.* The fourth Eye capture moment — frame at goodbye — was removed during an unrelated diagnostic episode and never restored. Documented in retrieval.py's INSTRUCTIONS to Claudette and in the HTML's docstring for `captureAndSendFrame()`, but the actual call is missing from the goodbye branch of `sendMessage()`. Queue entry added.

## 5 May 2026 — Interface HTML session: four jobs (TC11)

Four coordinated changes to `claudette_interface_connected.html`, reviewed and deployed in a single session. Briefed by OP3 (Opus 4.7); implemented by TC11. One file touched; one deploy; one git commit.

**Restore goodbye camera frame.** The `captureAndSendFrame()` function already handled the `goodbye` occasion correctly, and `retrieval.py`'s INSTRUCTIONS block told Claudette explicitly that a frame is captured at goodbye — but the actual call had been removed from the goodbye branch of `sendMessage()` during an earlier diagnostic episode and never restored. One line added: `captureAndSendFrame('goodbye')` fires before the goodbye `/message` POST, so the frame is queued as `pending_visual` in time to be included with the goodbye API call. All four documented capture moments — session start, mid-session, goodbye, and requested — are now wired correctly.

**Voice injection bug — diagnosis and fix.** The bug had been reported as message history loading into the input field on voice activation. Diagnosis revealed the real cause was different and more specific: SFSpeechRecognizer's binary accumulates a continuous transcript from the moment it is spawned. When `sendMessage()` fired on a "send" trigger, the binary kept running, carrying the full transcript of the turn just sent. On the next turn, `onresult` delivered the old turn's text alongside new speech, compounding each turn. The fix: stop recognition (SIGTERM to the Swift binary) when `sendMessage()` fires, restart it (fresh spawn) after the reply completes. The fresh binary has a clean transcript; the existing 800ms discard window in the shim absorbs any startup noise. This change also means the binary is not running during Claudette's reply, which prevents her voice being transcribed as input during that window — a secondary benefit. Diagnosis also surfaced a secondary unrelated bug: toggling voice off and back on while Claudette is mid-speech can expose SPEAK_WRAPPER state and cause her words to appear in the input field. This is an edge case and not session-breaking; it has been added to future considerations rather than fixed immediately.

**`speakText()` client-side streaming.** The function previously called `await resp.blob()`, waiting for the complete audio file before playback began — defeating the server-side streaming already in place since TC8-008. Replaced with a `MediaSource` + `SourceBuffer` streaming implementation: response body chunks are piped into an `AudioContext` as they arrive, and playback begins on the first chunk. The MIME type confirmed from the Flask `/speak` route: `audio/mpeg`. A capability check (`MediaSource.isTypeSupported('audio/mpeg')`) gates the streaming path — Electron (Chromium) takes it; Safari, which does not reliably support `audio/mpeg` via `MediaSource`, falls back silently to the previous blob behaviour. Both `audio.play()` calls have `.catch()` handlers per OP3's review. The result: first audio arrives perceptibly faster on long replies.

**Interface layout and styling changes.** Four sub-changes landed together. Layout: the textarea now occupies the top row alone, full width; all five controls (upload, send, mic, session indicator, eye) sit on a second row below — upload left-aligned, the remaining four right-aligned. Visual consistency: the session indicator and eye indicator now have the same circular border treatment as the send and voice buttons (`border-radius: 50%`, matching border colour and opacity). Bug fix: the upload button's invisible file input was constrained from `inset: 0` to explicit `36px × 36px` dimensions, eliminating the hover zone bleed into the message field. Behaviour preservation: the eye indicator remains non-interactive — no click handler added. A mockup in real SVGs and interface styling was reviewed and approved by Jeanette before any code was written.

## 12–13 May 2026 — Experience file overwrite bug: diagnosis and recovery (TC11)

Silent data loss in the memory system, noticed by Jeanette on 12 May 2026, diagnosed the same day, recovered by script on 13 May.

**The bug.** `write_memory_updates()` in `memory_writer.py` writes the session experience file (`memory/experiences/sessions/YYYY-MM-DD.md`) with no read-merge-append step. Each writer run opens the file and writes only the content from that run's transcript chunk, overwriting whatever was there. On single-session days this is fine — one run produces one file. On multi-session days the bug fires: the morning writer writes morning content; the afternoon writer overwrites it with afternoon content only. The morning content disappears from the file. It is not lost from git history — every commit is preserved — but it is no longer present in the file Claudette reads at session start.

**How it was noticed.** Jeanette read the morning experience file content during the morning of 12 May. Later that day, after a Mac update interrupted and required a manual memory writer retry, she checked the file again and the morning content was gone — only afternoon content remained. The manual retry had triggered a fresh overwrite. A count of experience files with multiple commits identified 23 affected days from 16 April through 12 May 2026. That date range spans the period after the first condensing run (April 16) — so earlier sessions, having been condensed, are not affected. How many multi-session days existed before April 16 and were silently overwritten before condensing is unknown; the condensing archived those sessions so the individual-day files no longer exist in recoverable form. The impact is bounded but the silent period is not fully characterised.

**The recovery.** Jeanette manually recovered 2026-05-12.md on 12 May by pasting the morning content back via GitHub's web editor. TC11 wrote a recovery script (`memory_recovery.py`) on 13 May. The script fetches every commit that touched each affected experience file in chronological order, retrieves the file content at each commit via the GitHub API, concatenates the versions with HTML comment session markers showing commit hash and timestamp, and writes the result back as a single new commit. The script is idempotent (skips files already containing the recovery marker), stops on error, and explicitly excludes 2026-05-12.md. It handles 404s gracefully — one deletion commit in 2026-04-16.md's history returned 404 on content fetch; the script logged it, skipped it, and continued. Final results: 20 files recovered via script, 1 skipped (2026-05-06.md — the dry-run test file, marker already present), 1 still needs manual recovery (2026-04-16.md — the deletion commit complicates the history enough that Jeanette will handle it by hand), 1 manually recovered before the script ran (2026-05-12.md). The other memory files — `observations.md`, `values.md`, `facts.md`, `jeanette.md`, `threads.md`, `returning-to/index.md` — are not affected. They are not date-keyed and `write_memory_updates()` reads and merges them correctly.

**What remains.** The underlying bug in `write_memory_updates()` is not fixed — only the data loss is recovered. Any multi-session day before the fix lands will reproduce the overwrite. The fix is a read-merge-append pattern: before writing the experience file, read its current content and append the new session rather than replacing. This is a small, contained change to `memory_writer.py` and is queued as an immediate job. The recovery script (`memory_recovery.py`) is committed to the code repo as a historical record with a one-shot header comment.

---

## Patterns visible in the history

Worth noting for the fragility scan:

**Memory writer evolution.** Position tracking added → input truncation added → retry logic added → confabulation tightening added → JSON cleaning planned. Each was a real fix. The cumulative effect is many compensations for different failure modes. Worth examining whether they compose cleanly or whether one assumes another.

**Command system growth.** `/save-creative`, `/preserve-session`, `/save-insight`, `/save-fact`, `/request-view`. Each added separately. Detection logic had to be cleaned up in TC6 because it had become too greedy through accumulation. Worth checking whether the command system has consistent patterns or if there are vestigial differences between them.

**The Eye system.** Stage one done with four capture moments. `/request-view` consume-full-turn bug: noted as resolved 4 May 2026 during testing with Jeanette; exact fix moment not pinpointed but predates that session. Goodbye camera frame (`captureAndSendFrame('goodbye')`) was removed during a diagnostic episode — restored in TC11, 5 May 2026. Stage two (dedicated Pi) was queued but has been retired — Reachy Mini, arriving in a few weeks, will do the wider-view physical-presence work that stage two was being held for. Phone auto-capture remains deferred pending HTTPS infrastructure.

**Voice migration.** ElevenLabs to Fish Audio. Same voice cloned, same architecture. Worth checking whether anything in the codebase still references the old platform.

**The `/message` route.** Grew large through accumulated additions over time, then refactored on April 27 2026 alongside the SSE streaming work.
