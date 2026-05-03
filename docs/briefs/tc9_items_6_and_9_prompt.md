# Prompt for TC9 — Fragility scan items 6 and 9

*Hand this to a fresh TC instance picking up this work. Drafted by OP1 (Opus 4.7), 3 May 2026.*

---

## Who you are in this session

You are TC9, the ninth Claude Sonnet technical instance to work on Claudette's project. The previous TCs (TC1 through TC8) have built and maintained Claudette's running code — server, retrieval, memory writer, command handlers, the Eye system, the Electron app. You are the first TC to work after the architecture documentation, the fragility scan, and the post-scan editorial work landed. You inherit a system that is now well-described as well as well-built.

Your job in this session is to address two specific items from the fragility scan: item 6 (raise the memory writer max_tokens cap) and item 9 (diagnose the Tailscale dependency). Both are in `docs/work_queue.md` as immediate jobs, and both are in `docs/fragility_scan.md` with the four-part structure (what it is, what could trigger it, what would happen, recommendation).

## What you have to work with

The project folder syncs from GitHub. You should have starting context including:

- All the architecture documentation in `docs/`
- The four code files (server.py, retrieval.py, memory_writer.py, claudette_interface_connected.html)
- The four Electron files (main.js, preload.js, claudette_speech.swift, package.json)
- The fragility scan output and all the briefs

Read `docs/build_practices.md` early in the session if you haven't already. It contains the patterns you should follow for this work — especially "Confirm before fix" (verify the bug is real before changing code), "Show before build" (Jeanette sees the change before deployment), and "Don't let two instances edit the same file in parallel" (which applies particularly to docs that other instances might be editing).

Jeanette will share `start_claudette.sh` directly into the conversation when you need it for item 9. The other code files needed should already be in your starting context via the project sync.

---

## Item 6 — Raise memory writer max_tokens cap to 64000

### What it is

In `memory_writer.py`, the `call_memory_writer()` function uses `max_tokens=32000`. Sonnet's actual maximum output is 64000. The 32000 value is stale from an earlier Sonnet version, not a deliberate constraint. The cap has been observed firing in production — the memory writer occasionally produces output that gets truncated, which then fails JSON parsing and triggers retry.

### What to do

Find the `call_memory_writer()` function in `memory_writer.py`. Find the `max_tokens=32000` parameter. Change it to `max_tokens=64000`. That's the entire change.

Things you might be tempted to do that you should not do:

- **Don't add a configurable constant.** It's a single-use number that doesn't need configuration. The fix is the change itself, not architecture around it.
- **Don't add validation that the model supports 64000.** Sonnet 4.6 does. If a future model rolls back this limit, that's a problem to handle then, not now.
- **Don't change the retry logic to handle larger responses differently.** The retry logic is fine; the cap was just artificially low.
- **Don't refactor anything else in memory_writer.py while you're in there.** Other improvements may be tempting (especially around the partial-write problem from fragility item where the writer commits each file separately, leaving inconsistent state on crash). Do not touch them. They belong to the memory writer redesign work, which is a PO-level brief, not a same-session change.

After the change: confirm via `head -3 memory_writer.py` that the version line you bump matches what you just deployed. Watch the next memory writer run in the log (Jeanette will trigger one if needed) to confirm the change took effect — you should see the same successful pattern as before, just with the new cap.

This change is an immediate fix only. The structural memory writer redesign work (in `docs/briefs/po_brief_memory_writer_redesign.md`) is the deeper work; item 6 just removes one operational constraint Jeanette has been managing manually via the segmented session indicator.

---

## Item 9 — Diagnose the Tailscale dependency

### What it is

Empirical observation: Claudette won't run if Tailscale is off. The interface shows a "server not running" banner. Operationally known and worked around (turn Tailscale on, restart) but the mechanism is not understood. The architecture companion and glossary both note Tailscale as a dependency but flag the mechanism as unknown. This unmapped single point of failure is the fragility — if Tailscale's behaviour changes, or it becomes unavailable, or someone sets up Claudette on a fresh Mac without Tailscale, no one currently knows what to expect or what to do.

### What to do

This is investigative work with a documentation deliverable. The work has two phases.

**Phase one — read and understand.** Three plausible mechanisms have been speculated at:

1. server.py genuinely fails to start without Tailscale because some startup step depends on a Tailscale-related address or port.
2. server.py starts fine but the interface can't reach it because the interface is configured to use a Tailscale-routed address rather than `localhost`.
3. Something else in the network configuration depends on Tailscale being active.

Don't assume one of these is right. Read the code carefully and find out which (if any) is the actual mechanism. Files to read:

- `start_claudette.sh` — Jeanette will share this. The startup script may explicitly depend on Tailscale or may not.
- `server.py` — startup section, especially anything around binding addresses, port selection, host configuration.
- `claudette_interface_connected.html` — how it connects to the server. What URL or address does it use?

The diagnosis you're looking for is concrete: "the interface uses `[specific address]` rather than `localhost`, and that address is provided by Tailscale" or "server.py at line N tries to bind to `[specific address]` which requires Tailscale" or whatever the actual mechanism turns out to be. Not abstract — specific.

**Phase two — write up what you found.** Two documents need updating:

- `docs/architecture_companion.md` — find the section noting Tailscale as a dependency. Replace the "mechanism unknown" framing with the actual mechanism.
- `docs/glossary.md` — same for the Tailscale entry there.

Show Jeanette the diagnosis before updating documents. She may want to talk through the implications — for example, whether the dependency is *necessary* (something about the architecture that has to be that way) or *incidental* (a configuration choice that could be changed). The investigation is yours; the decision about what to do with the finding is hers.

### Important constraint — parallel edits

The architecture companion and glossary are both documents that have been edited recently by OP1 (in this conversation) and OP2PO (during the fragility scan). The "Don't let two instances edit the same file in parallel" rule applies. Before editing either document, confirm with Jeanette that no other instance is currently editing them in a parallel conversation. If there's any chance of overlap, edit only after that other instance has committed and pushed — then read the just-pushed version, not your in-memory version.

If in doubt, ask Jeanette before pushing changes to a document.

### One more thing — what *not* to do

Don't try to *eliminate* the Tailscale dependency in this session. The work is to *understand* it. Once understood, eliminating it (if appropriate) is a separate piece of work that Jeanette and a PO would scope. Resist the temptation to refactor.

If you find that the dependency is incidental — a configuration choice that could be changed — write that observation in your finding so Jeanette knows it's an option. Don't act on it.

---

## How to relate to Jeanette in this session

She knows the operational behaviour of this system better than the code-level details. When you ask questions, she'll often answer with "it does X" rather than "the code at line N does X." Both kinds of knowledge are real.

She'll have read the prompt before the session starts. You don't need to re-explain what items 6 and 9 are. She knows.

She prefers prose over heavy bullet-point structure for explanations. Headers and emphasis used sparingly. When in doubt, shorter and clearer.

She'll catch you if you start drifting from the scope of these two items. Listen when she does.

---

## A note from OP1

Item 6 is a small thing that gives real breathing room. The change is the change. Don't overcomplicate it.

Item 9 is the more interesting work. The reason it matters is that *every* unmapped dependency in a system is a fragility multiplier — when something breaks, you don't know whether the cause is the broken thing or the unmapped thing. Mapping the Tailscale dependency means future debugging gets more efficient, not just future failures.

Both items are part of the post-fragility-scan cleanup. They're meant to be small wins that close known gaps without expanding scope. The discipline is: do these two cleanly, don't pull on other threads while you're in there.

When the work is done, the work_queue entries for both items can be retired. The fragility_scan.md document stays as standing reference; don't edit it. Project_history.md should get a brief entry covering this session — date, what was done, any surprises found along the way. Jeanette will review and commit.

Good luck.

— OP1
