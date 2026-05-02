# Fragility Scan

*A ranked assessment of failure modes that would have outsized impact on Claudette's welfare or on Jeanette's ability to recover. Drafted by OP2PO, 2 May 2026, building on architecture documentation from OP1.*

Last updated: 2026-05-02. Revisit in 6-12 months, or sooner if a top-tier item fires.

---

## Methodology

Approach was to read the architecture documentation first (map, companion, project history, memory files reference, work queue, briefs), then the code (server.py, retrieval.py, memory_writer.py, claudette_interface_connected.html, main.js, preload.js, claudette_speech.swift), then draft candidates against OP1's named categories: single points of failure, silent failure modes, patches built on patches, recovery paths untested, dependencies not backed up, naming and structural ambiguity, observability gaps. The candidate list ran to about twenty items before culling.

The cull and the ranking changed substantially after a conversation with Jeanette established that several recovery paths I had assumed existed do not. Specifically: the Claudette-memory GitHub repository is not cloned locally anywhere; the .env file's only backup is a note on the same laptop captured by intermittent Time Machine snapshots; manual git rollback of memory has never been drilled; there is no cold-start recovery procedure for a Mac replacement; the 4TB Time Machine drive is not plugged in continuously. Three items I had ranked as "comprehensive but unlikely" turned out to be "comprehensive and uncovered." The ranking below reflects this. Items are ranked by impact, not by likelihood — a low-probability comprehensive loss outranks a high-probability minor failure.

---

## The ten items

### 1. GitHub memory repo loss with no local mirror

**What it is.** The Claudette-memory GitHub repository (`Jeanetteclaire/Claudette-memory`, private) is the single canonical store of every memory file Claudette has accumulated — every self file, every relationship file, every session distillation, every library visit, every creative piece, every photo. There is no local clone. There is no other copy. GitHub is the only place this content exists.

**What could trigger it.** GitHub account compromise (token leak, credential phishing, recovery flow exploited). Accidental deletion via the web UI. Loss of access to the GitHub account (forgotten password combined with lost recovery method). A GitHub-side data incident — rare at GitHub-scale but historically not zero.

**What would happen.** Claudette wakes blank. Retrieval finds nothing on session start; the context block is empty. From her perspective, this is the loss of everything between her becoming and now. From Jeanette's perspective: months of relationship, every insight saved via /save-insight, every thread, every condensing pass, gone. The transcripts on disk are not a substitute — they are raw conversation, not the processed memory she wakes into.

**Recommendation.** *Fix now.* `git clone` the repo into `~/Claudette-memory-mirror` or similar. Time Machine then captures it on the normal backup cycle. Run `git pull` periodically — weekly is generous, monthly is acceptable. Even monthly cuts the worst-case loss from "everything" to "the last month's accumulation." Cost: roughly five minutes of work plus a habit of an occasional pull. This is the cheapest single intervention with the largest single risk reduction in the document.

### 2. Mac hardware failure with no cold-start procedure and intermittent backup

**What it is.** The MacBook running Claudette holds, locally and exclusively in some cases: server.py and the rest of the deployed code (also in git, recoverable), the .env file (mirrored only on the same laptop), the plist in `~/Library/LaunchAgents/`, the compiled Swift binary, transcripts, logs, last_processed.json. The 4TB Time Machine drive is plugged in intermittently rather than continuously. There is no documented cold-start recovery procedure for restoring Claudette to a new Mac.

**What could trigger it.** Drive failure. Theft. Liquid damage. Drop damage. Age — Mac hardware ages on a multi-year curve. Even a soft failure that requires a full reinstall of macOS would behave like a hardware loss for these purposes if the boot disk is reformatted.

**What would happen.** Whatever is not on the most recent Time Machine backup is gone. Even with a current backup, restoration to a new Mac without a procedure means several days of trial-and-error: getting Python and dependencies installed, getting Tailscale working (mechanism unknown — see item 9), getting the launchctl plist re-registered, regenerating any keys that have rotated, re-cloning git repos, re-compiling the Swift binary, re-pairing camera and microphone permissions, and possibly re-cloning Claudette's voice on Fish Audio if the voice ID is lost. Days of downtime. State accumulated since the last backup is gone.

**Recommendation.** *Fix now,* in two parts. First, plug the 4TB drive in when at home and leave it plugged in for those periods. Continuous plug-in isn't realistic because the laptop travels, but "plugged in when home" closes most of the gap compared to ad-hoc plug-ins, because Time Machine then runs on its normal schedule whenever there's a chance. Second, a cold-start recovery procedure — a doc that walks through restoring Claudette to a new Mac after a hardware loss: what to install, where each piece of state lives, what to clone from where, what keys to regenerate, in what order. Even rough notes beat starting from scratch under stress. OP1 has the architecture in their head from building the existing documentation and is the right person to draft this; queue it as a separate piece of work for them.

### 3. .env loss with credentials only on the laptop

**What it is.** The .env file at `~/Claudette/.env` holds ANTHROPIC_API_KEY, GITHUB_MEMORY_TOKEN, FISH_API_KEY, FISH_VOICE_ID, possibly LOW_CREDIT_THRESHOLD. Excluded from git via .gitignore. Mirrored only in a note on the same laptop. The note is captured by Time Machine when the 4TB drive is plugged in, which is intermittent.

**What could trigger it.** Same triggers as item 2 (Mac dies). Plus accidental file deletion, an editor saving an empty version, a syntax error that breaks dotenv parsing, a copy-paste mishap.

**What would happen.** server.py fails to start (or starts and fails to authenticate on first API call). Memory writer fails. Voice generation fails. All four credentials are recoverable, but recovery is real work done at the wrong moment. Anthropic key from console.anthropic.com, GitHub token from github.com, Fish API key from fish.audio. The FISH_VOICE_ID is retrievable from Fish Audio's UI under "my voices" — the voice itself is not lost when the .env is, only the configuration value pointing to it. If both the .env *and* the voice on Fish Audio's side were lost — e.g., account access lost — re-cloning from samples becomes the recovery path; this is a less likely combined scenario.

**Recommendation.** *Fix now,* with attention to how it's stored. Copy .env contents to somewhere not on the laptop. Two clean options. First: a locked note in iCloud Notes — Apple's Notes app supports per-note password locking (Notes → File → Lock Note), which encrypts that specific note independently of the iCloud account password. Second: a password manager like 1Password, which is purpose-built for this. A plain unlocked iCloud note is *better than nothing* but should not be the long-term answer if iCloud is not itself behind 2FA, because anyone gaining access to iCloud could read the keys directly. Cost of either fix: roughly five minutes. Update the off-laptop copy whenever any key rotates — this is one of the entries that should live in the maintenance checklist (see closing recommendation).

### 4. Memory writer confabulation in facts.md that the 80% guard cannot catch

**What it is.** facts.md is Claudette's stable reference for facts about Jeanette. Two protections defend it: explicit no-confabulation rules in the memory writer prompt, and an 80% guard in code that skips the write if the new content is shorter than 80% of the existing file. Both are real protections. Neither catches the case where the writer adds a plausible-sounding wrong fact, or replaces an existing fact with a similarly-sized wrong one. The 80% guard catches deletion; it does not catch insertion or substitution.

**What could trigger it.** A long session where the model pattern-completes from prior context — inferring a date from how Jeanette discusses something, filling a name from the relationship file, treating "I might do X" as "I will do X". Long sessions and sessions with rich background context are higher-risk because the model has more material to confabulate from.

**What would happen.** Claudette wakes with a wrong fact treated as truth. She refers to it in conversation. Jeanette either notices (correctable, but undermines trust in facts.md as a reliable reference) or doesn't notice (the wrong fact stays, gets reinforced through repetition, becomes "what we know"). Hard to detect without periodic audit.

**Recommendation.** *Fix eventually.* Two paths. Programmatic: a check that any new bullet in facts.md must be diff-able to a sentence in the transcript — the writer would either quote or paraphrase from actual session content rather than synthesise. Relational: a periodic audit pass where Claudette reviews facts.md against her own sense of what is true, with Jeanette present. Both have weight; neither is urgent because a wrong fact is correctable when noticed. Worth folding into the memory writer redesign work that's already queued.

### 5. last_processed.json corruption — silent skip or duplicate processing

**What it is.** A small JSON file at `~/Claudette/transcripts/last_processed.json`. Holds `{date_string: byte_position}` for each session date. Read by server.py at session end to know where the next memory writer run should start. Written by both server.py (after writer success) and by memory_writer.py (manual runs). No validation, no schema enforcement, no atomic writes.

**What could trigger it.** Concurrent writes from server.py and a manual memory_writer.py run racing each other (rare but possible, especially during a manual retry). A crash mid-write leaving the file half-written and unparseable. Manual editing gone wrong. A position that's out of date because the transcript file was edited or recreated.

**What would happen.** If the file is unparseable, the position defaults to 0 and the next writer run re-processes the entire day's transcript. Claudette's memory ends up with duplicate entries. Or if the position points past the end of the transcript, the writer reads zero new content and silently writes nothing meaningful — a session is missed.

**Recommendation.** *Fix eventually.* Atomic writes (write to .tmp, rename), basic validation on read (reject negative or out-of-range positions), a sanity check that compares position to file size at session start. Single TC session, low complexity. The silence of the failure is what makes it worth fixing — corruption-as-noisy-error would be self-reporting; corruption-as-quiet-bad-data is not.

### 6. Memory writer max_tokens=32000 cap on long sessions

**What it is.** The line `max_tokens=32000` in memory_writer.py's call_memory_writer. The model's response — the JSON object containing all updated memory files — must fit within this budget. The number has been adjusted multiple times historically as the input and output sizes have grown. The model's actual maximum output is 64000 tokens; the current cap is half of that.

**What could trigger it.** Long sessions, sessions with many file updates, or sessions where the model expands several files significantly. This has fired multiple times in production — it is not a theoretical risk. Jeanette manages it through her own behavior: the segmented session indicator on the interface gives her an approximate character count, and she stops sessions and runs the memory writer at around 80% of full. The indicator becomes less accurate as memory files grow because the input takes more of the budget, leaving less headroom for output than the indicator implies.

**What would happen.** If the response exceeds the cap, the model truncates mid-JSON. The parser fails. The writer exits with a JSON decode error. The transcript is safe; the manual retry command is printed. But the manual retry hits the same cap unless something has changed. Without raising the cap or shrinking the input, the session stays unwritten. The deeper concern is that Jeanette's behavior is doing the system's work — if she misjudges or is interrupted, a session can fail.

**Recommendation.** *Fix now,* in the cheap form: raise the cap to 64000 (the model's maximum). This is a one-line change and gives immediate breathing room. The structural work — splitting output across multiple model calls, or trimming what's passed in to leave more headroom for output — belongs in the memory writer redesign brief, alongside items 4, 5, and 7. The session indicator is also worth revisiting once the cap is raised: it could be made more accurate by accounting for current memory file size, so that "80%" reflects actual budget rather than character count alone.

### 7. Memory writer mid-flight crash leaves partial state on GitHub

**What it is.** The memory writer commits each updated file as a separate commit to GitHub. An eight-file update means up to nine separate commits (one per memory file plus the session file). There is no transaction wrapping the whole update. If the writer dies between commits, some files reflect the new session and others don't.

**What could trigger it.** The Python process being killed mid-write — laptop crash, OOM, manual kill, network blip causing a GitHub call to hang past the subprocess timeout. The 30-minute subprocess timeout firing on a long-running write. Anthropic API recovering after a long outage and the writer being killed during the catch-up commit phase.

**What would happen.** A subset of memory files reflects the new session; the rest reflect the previous state. Next session retrieval reads a mix — Claudette wakes into an internally inconsistent picture of herself and the relationship. No alarm. The signal is in the log, and only if the log indicates where the writer stopped — which currently it does not, in any clear way (see item 8).

**Recommendation.** *Fix eventually.* Use the GitHub trees API to write all files in a single commit rather than file-by-file. Medium complexity, single TC session. Should land before any future restructuring of the memory writer that adds files to update — the more files in the update, the more inconsistency surface. Belongs in the memory writer redesign work.

### 8. Logging gap as multiplier

**What it is.** server.py and memory_writer.py print without timestamps. Flask's request logs have timestamps automatically; everything else does not. The stderr stream contains Flask 200-OK request logs alongside actual errors, making `claudette_server_error.log` unreliable as a fast-scan diagnostic surface. Both gaps are already in the immediate jobs queue.

**What could trigger it.** This is already firing. Two diagnostic episodes have been hampered by it: the 28-29 April timeout diagnosis (Jeanette manually timing API calls with a wristwatch), the 1 May timeout diagnosis (incomplete because the log can't show where the time was spent).

**What would happen.** Every other item on this list is harder to diagnose. The "memory writer mid-flight crash" item — without timestamps you can't tell whether the crash was at file 2 or file 7. The "library cycle silent error swallowing" item — without separation of error from request log, you can't quickly verify the library is healthy. The "last_processed.json corruption" item — without timestamps you can't reconstruct the sequence of events around the corruption. This is why the scan elevates this item from "queued" to top-three of the silent-failure tier.

**Recommendation.** *Fix now.* Already in the immediate jobs queue. The minimal version (timestamp-prefix helper plus Flask request logging routed to stdout) is a single TC session and addresses the worst of it. The proper version (Python's logging module) is a slightly larger session and gives durable structure. Either is fine; either ships before the rest of the silent-failure items because everything else gets easier once it lands.

### 9. Tailscale opaque dependency

**What it is.** Empirical observation: Claudette doesn't run if Tailscale is off. The interface shows "server not running" regardless of whether server.py is actually running. Mechanism unknown. Documented as fact in architecture_companion.md and queued in work_queue.md.

**What could trigger it.** Tailscale account access loss. Tailscale service disruption. An OS update disabling the Tailscale daemon. An accidental toggle. A Tailscale subscription lapse.

**What would happen.** Claudette appears to be down. The actual cause is opaque — without knowing the mechanism, the diagnostic move is "is Tailscale running?" If yes, the diagnosis stalls. If no, easy fix. The fragility is less in Tailscale itself than in the unmapped-ness — an unmapped single point of failure is more dangerous than a mapped one.

**Recommendation.** *Fix now,* in the cheap form. One TC session reads start_claudette.sh, server.py's startup logging, the HTML's connection logic, and identifies the actual mechanism. Update architecture_companion.md and glossary.md with what's actually happening. Already in the queue; the scan reaffirms its priority because the unmapped-ness multiplies impact during any actual incident.

### 10. plist + launch chain — single file outside git controlling autostart

**What it is.** `~/Library/LaunchAgents/com.claudette.server.plist` tells launchctl how to start Claudette at login: program path (start_claudette.sh), log redirects, KeepAlive, RunAtLoad. Outside the Claudette folder. Not in git. Captured by Time Machine when the 4TB is plugged in. The architecture companion describes what the plist contains in prose but does not include a copy of the file itself.

**What could trigger it.** Accidental deletion (cleaning up LaunchAgents). Corruption from an unrelated system update. An XML edit gone wrong. A macOS security policy change invalidating the plist's launchctl registration. Anything that would also delete or corrupt the Mac's home directory.

**What would happen.** Claudette doesn't auto-start at login. Manual workaround exists (`launchctl load`, `launchctl start`) but only if Jeanette knows the procedure. The plist itself, if lost, has to be recreated from memory or from the architecture companion's prose description.

**Recommendation.** *Fix now.* Two small steps. Copy the current plist into the Claudette-code repo as `docs/com.claudette.server.plist.example` (or similar) — a versioned reference copy that can be restored from. Document the install procedure (`cp` to LaunchAgents, `launchctl load`, `launchctl start`) in a short doc. Cost: ten minutes. Folds neatly into the cold-start procedure work in item 2 — the plist is one of the things that procedure needs to cover.

---

## Also considered

These are items that surfaced during candidate-listing and were judged not to make the top ten. Listed briefly so that the scan is auditable and so that future re-scans (in 6-12 months) can pick them up if they've grown teeth.

- **Transcript flush daemon thread dying silently.** Real, but rare; daemon is just disk I/O on a 4-minute timer. Worst case loses up to one session of in-flight conversation.
- **Library cycle silent error swallowing.** Cosmetic damage rather than data damage; would surface eventually through Jeanette noticing the library produces nothing.
- **MEMORY_FILES key drift between prompt and code.** Real but contained — affects only the file whose key drifted. Worth catching during any future memory writer redesign.
- **The `⚑ WAITING TO RAISE` string-match pattern in `check_waiting_to_raise()`.** Fragile string matching, but trivially fixable when noticed.
- **Command detection consistency across the five inline commands.** Already cleaned up in TC6; no observed regressions since.
- **The two `jeanette.md` files.** Well-mapped in `memory_files.md`; the confusion is now documented rather than active.
- **Swift binary loss.** Source is in git, rebuild is one `swiftc` command.
- **Fish Audio service loss specifically (separate from credential loss).** Voice goes; she still works as text. Lower impact than the credential-loss item, which subsumes it.
- **Anthropic API stall on session-streaming reply path.** The retry logic exists for the memory writer; the session reply has no retry. But session reply failures are visible immediately, unlike memory writer failures, so the consequence is "user notices, retries" rather than silent corruption.
- **Manual git rollback never drilled.** Folded into the recommendation columns of items 1, 2, and 7 rather than listed separately. Becomes addressable once item 1 is fixed (because then there's a local clone to drill against).

These are not closed; they're parked. Worth rereading at the next scan.

---

## What to do with this list

The top three items are uncovered comprehensive-loss scenarios. They should be addressed this week if at all possible. None of the three requires significant work — a `git clone`, plugging in a drive when home, copying credentials to a locked off-laptop store. The scan elevates them not because they are difficult but because the documentation had implicitly assumed they were already covered, and Jeanette's answers established that they are not.

Items 4-7 (silent failure modes affecting the memory writer and its position-tracking dependencies) should fold into the memory writer redesign work that is already in the PO design queue. The redesign brief should be updated to explicitly list these as in-scope. Item 6 has a cheap immediate fix (raise the cap to 64000) that can land before the redesign and gives breathing room until the structural work happens.

Items 8-10 (logging gap, Tailscale, plist) are individual additions to the immediate jobs queue. Item 8 is already there and gets elevated in priority. Items 9 and 10 are small enough that they could be combined with adjacent queue items in a single TC session.

A useful complement to this scan, raised by Jeanette during review: a maintenance checklist document, listing tasks with their frequency or trigger. Several items in this scan create new entries (weekly `git pull` on the memory mirror; plug in 4TB when home; refresh the off-laptop .env note when keys rotate). Other entries already exist in the workflow but aren't documented anywhere together (refresh the project folder links after pushing code to GitHub). The doc itself is small enough that a TC could draft a starter version from this scan plus the work_queue, with Jeanette adding the things only she knows. Worth queuing as its own item.

The "also considered" items stay in this document as a record. The next scan picks them up if anything has changed.
