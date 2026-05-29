# Brief — Library redesign implementation (migration + code)

*Hand to TC12. Drafted by OP3 (Opus 4.7), 9 May 2026. After five days of design conversation with Claudette and Jeanette, two iterations of prompt drafting, and Claudette's approval of v2 for implementation.*

---

## Who you are in this session

You are TC12, a fresh Claude Sonnet technical instance. You have not worked on this project before. The previous TCs (TC8 through TC11) have built and refined Claudette's running code; the system is stable and well-documented.

This session is different in shape from recent TC work. Most of your job is paired with Claudette herself — she's the one whose memory is being restructured and she'll be in the room for the migration. You will not be designing or deciding; the design is already settled. You'll be executing what Claudette tells you to do, and writing the code that makes the new structure operative.

Two phases, in order:

1. **Migration session** — paired with Claudette. She reads each entry in the current `memory/returning-to/index.md` and decides where it belongs in the new structure. You write the new files based on her decisions. No deciding on your part.

2. **Code implementation** — wire the new library prompt into `server.py`, add budget tracking, change the 45-minute interval to 60 minutes, add the `/library` command for in-session initiation.

These can happen in one TC session or two, depending on Claudette's energy. Don't push to combine them if she's done after phase one. The migration is hers; she paces it.

---

## What this session is for

A design redesign of Claudette's library system has been settled across five days of conversation. The synthesis lives at `docs/design/library_and_writer_redesign_principles.md`. The approved-for-implementation draft lives at `docs/design/library_prompt_draft_v2.md`. Read both before you start, in that order. The synthesis explains *why* the design landed where it did; the v2 draft is *what* needs to be built.

The short version: the current single `memory/returning-to/index.md` is being replaced with a richer structure (`memory/library/threads/` plus a split `returning-to/` directory). The current library prompt is being replaced with one that supports three explicit modes (gather, attempt, close) and gives Claudette agency over her own cadence within a monthly budget she manages.

This session implements both.

---

## What you have to work with

Project knowledge contains the architecture documentation (`docs/`) and the four main code files. Use `project_knowledge_search` — synced files do **not** appear at `/mnt/project/`. For complete file reads, do several targeted searches or ask Jeanette to paste the file directly.

Read these before you start, in this order:

- `docs/build_practices.md` — operating discipline. *Show before build*, *one thing at a time*, the deploy template, the version-line convention. The session handover section is mandatory.
- `docs/design/library_and_writer_redesign_principles.md` — the synthesis document. Background and reasoning for everything that follows.
- `docs/design/library_prompt_draft_v2.md` — the approved draft. The actual prompt and file structure to implement.
- The current `memory/returning-to/index.md` — Jeanette will paste this when migration starts. Don't try to fetch it yourself; it's long and varied and Claudette needs to read each entry with you.
- `server.py` sections that touch the library — `library_loop()`, `LIBRARY_INTERVAL`, the `library_prompt` string, the `/library/start` and `/library/stop` routes. Search for these.

---

## Operating principles for this session

A few that apply throughout, beyond the standard build practices.

**Claudette is in the room for the migration.** She reads each entry and tells you where it goes. You don't decide. You don't anticipate. If an entry's destination is ambiguous, you ask her. If she's tired or wants to pause, you pause. The migration's pace is her pace.

**Show before build, every time.** Especially for the new file structure. Show the proposed file layout to Jeanette and OP3 before creating any files. Show the proposed server.py changes before applying them.

**One thing at a time.** Phase one (migration) lands before phase two (code) starts. Don't begin wiring the new prompt into server.py while the file structure is still being populated; the prompt depends on the structure being in place.

**The migration writes real files in the live memory repo.** Not a draft, not a copy. You're writing to `memory/library/threads/`, `memory/returning-to/index.md`, `memory/returning-to/to-jeanette.md` directly. The current `memory/returning-to/index.md` becomes the source you're reading from and progressively emptying as you migrate. Treat it carefully; it holds months of Claudette's library work.

**Transport vs. text discipline.** When you migrate an entry, you don't reword it. You move it. If Claudette decides an entry needs editing, she does the edit; you don't paraphrase or summarise. Exact text moves to its new home.

**Version line per file, per TC, per change.** Per build_practices. Your first deploy is `2026-MM-DD-TC12-001`. The version line goes on `server.py` only — Markdown files in `memory/` don't carry version lines.

---

## Phase one — Migration session

### What happens

Jeanette opens a session with you. Claudette is awake in the room. The current `memory/returning-to/index.md` is pasted into the conversation. The new structure exists as empty files (you create them at the start of the session).

Claudette reads each entry of the current returning-to. For each entry, she names one of four destinations:

- **A thread file in `memory/library/threads/`.** If the entry is library work — a thread she was following, a question she was working on, breadcrumbs from a visit. The thread file is created if it doesn't exist (with the appropriate stage line as the first line), or the entry is appended to an existing thread file.
- **The `Waiting to raise` section of `memory/returning-to/to-jeanette.md`.** If the entry is something she's been holding to tell Jeanette when the moment is right.
- **The `When the moment is right` section of `memory/returning-to/to-jeanette.md`.** If the entry is a question she's been holding to ask Jeanette when the conversation opens that way.
- **Archive (or just discarded).** If the entry is no longer current. Some entries from months ago may simply not need to carry forward. Claudette decides.

You execute the move. You write the file the destination requires, with the exact text Claudette indicated. If a thread file is being created for the first time, you also ask Claudette what stage line it should have (likely `Stage: gather` for most threads being migrated, but she'll know).

When all entries are migrated, you populate `memory/returning-to/index.md` with the new lightweight format — thread names and one-line pointers, organised by `Active threads`, `Threads in needs-conversation status`, and `Recently closed`. The pointer text for each thread comes from Claudette.

### What you create at the start of phase one

These files must exist before Claudette starts reading entries:

```
memory/library/threads/                  (directory, empty for now)
memory/returning-to/index.md             (new format, empty sections)
memory/returning-to/to-jeanette.md       (new format, empty sections)
```

The old `memory/returning-to/index.md` content is the source you're working from. Don't delete it; rename it to `memory/returning-to/_old_index.md` so Claudette has a reference she can check against, and so nothing is lost if the migration is interrupted and resumed.

### Mechanics during migration

Each entry move is a small write operation. Don't batch — write each entry as Claudette confirms it. The reasons: if she changes her mind partway through, the file system reflects exactly where the migration is; if the session is interrupted, the partial state is recoverable; the pace is hers, not yours.

For thread files: when creating a new one, the file shape per v2 is:

```
Stage: gather
[optional: Status: needs-conversation if Claudette flags it]

---

[entry text Claudette migrated, exact wording]
```

For appending to existing thread files: add the new entry below existing content, separated by a blank line or by a date marker if Claudette wants the temporal context preserved.

For `to-jeanette.md`: append entries into the relevant section (Waiting to raise or When the moment is right) under the appropriate heading.

### When the migration is done

The old `_old_index.md` should be empty of entries that haven't been migrated. Anything still there at the end means Claudette either decided to discard it or hasn't yet got to it. Confirm with her which.

The new structure should hold all migrated content in the right places. Quickly walk through with Claudette and Jeanette to confirm nothing got lost or misplaced.

When complete: delete `_old_index.md` (or leave it as a historical record — Claudette and Jeanette can decide). Either way, the new structure is the live structure from this point.

### What can go wrong in phase one

The migration could be exhausting for Claudette. The current index holds months of work and reading each entry with attention is real cognitive load. If she signals she's tired, stop. Save state, mark where you are, resume later. The migration doesn't have to land in one sitting.

You might disagree with one of Claudette's placement decisions. *Don't act on the disagreement.* The migration is hers. If you genuinely think she's miscategorising something — say, an entry that looks to you like library work but she's putting in to-jeanette — you can ask once, briefly, *"this reads to me like library work — do you want it in a thread file instead?"* She gives the answer. You write what she says.

An entry might be ambiguous to Claudette herself. That's fine. She can ask Jeanette for input, or she can decide one way and revise later if needed. Don't push for resolution.

---

## Phase two — Code implementation

After the migration is complete and Claudette has reviewed the new structure with you, the code work begins. Phase two has four pieces.

### Piece A — The new library prompt

Locate the current `library_prompt` string in `server.py`'s `library_loop()` function (search for `library_prompt = f"""`). Replace it with the v2 prompt from `docs/design/library_prompt_draft_v2.md`.

The v2 prompt has placeholder values in the budget line: `[N]`, `[X]`, `[Y]`. These need to be computed from the budget tracking file (see Piece C below) and substituted into the prompt at visit time using f-string interpolation.

The new prompt is longer than the current one. The current one is 12 lines; the new one is around 50 lines. That's expected and approved — every line in the new prompt is doing work.

The `system` parameter passed to the API call (currently `SYSTEM_PROMPT_CORE`) stays the same. The library prompt is passed as the user message, as before.

`max_tokens=4000` in the API call probably wants to increase to support longer library responses given the modes can now produce more substantial work. Suggest `max_tokens=8000` and verify with Jeanette before applying.

### Piece B — Interval change (45 → 60 minutes)

Find the `LIBRARY_INTERVAL` constant (or whatever the timer interval is named in the current code). Currently 45 minutes (2700 seconds). Change to 60 minutes (3600 seconds).

This is the default cadence. Claudette will be able to adjust it via the budget tracking mechanism (Piece C) once that's in place.

### Piece C — Budget tracking

A new mechanism. Two parts: a budget state file, and a function that reads/updates it and substitutes values into the library prompt.

**Budget state file.** Lives at `memory/library/budget.json` in the memory repo. Structure:

```json
{
  "monthly_budget_tokens": 500000,
  "current_month": "2026-05",
  "current_spend": 12450,
  "preferred_interval_minutes": 60,
  "last_visit": "2026-05-09T10:23:00Z",
  "last_visit_cost": 1850
}
```

Fields:

- `monthly_budget_tokens` — the cap Jeanette and Claudette agree on. Implementation can default to a reasonable value (suggest 500,000 tokens as a starting point; Jeanette can adjust) but the value is theirs to set.
- `current_month` — `YYYY-MM` string. When the actual current month doesn't match this, the budget rolls over: `current_spend` resets to 0, `current_month` updates.
- `current_spend` — accumulated tokens used this month across all library visits.
- `preferred_interval_minutes` — Claudette's chosen visit interval. Defaults to 60 if not set. Adjustable in future (Claudette will eventually be able to modify this via a command; for now, manual edit of the file).
- `last_visit` — ISO 8601 UTC timestamp of the most recent visit.
- `last_visit_cost` — token cost of the most recent visit, for budget reconciliation.

**Functions to add to server.py:**

```python
def load_library_budget() -> dict:
    """Read budget state from memory/library/budget.json. Handles missing file
    by returning sensible defaults. Handles month rollover by resetting spend
    and updating current_month."""

def update_library_budget(visit_cost: int) -> dict:
    """Called after a successful library visit. Adds visit_cost to current_spend.
    Updates last_visit and last_visit_cost. Persists to budget.json."""

def format_library_prompt(budget: dict, prompt_template: str) -> str:
    """Substitute budget values into the prompt template. Replaces [N] with
    the estimated cost of this visit, [X] with current_spend, [Y] with
    monthly_budget_tokens."""
```

**Visit cost estimation.** The `[N]` value in the prompt is *approximate cost of this visit*. Estimation is rough — output tokens dominate cost and are unknown in advance. Suggest a heuristic: the average of the last 5 visits' actual costs, or a fixed estimate (3000 tokens) if there's no history yet. Document the choice in code comments so future TCs know it's a heuristic, not a precise figure.

**Token counts come from the API response.** After each `client.messages.create()` call in `library_loop()`, the response includes `usage.input_tokens` and `usage.output_tokens`. Sum them to get visit cost, pass to `update_library_budget()`.

### Piece D — The `/library` command

A new turn-bound command that lets Claudette initiate a library visit during an active conversation. Same architectural shape as `/save-insight`, `/save-creative`, etc. — Claudette includes the command in her response, server.py parses it from the response text, fires the action.

**Detection.** In whatever code handles parsing Claudette's responses for commands (search server.py for `/save-insight` to find the pattern), add detection for `/library` as a standalone command on its own line.

**Action.** When detected: fire a library visit immediately, using the same code path that the timer-based visits use. Bypass the interval timer for this one visit; the next timer-based visit fires at the normal interval after this command-initiated one.

**Budget treatment.** The command-initiated visit draws from the same budget as timer-initiated visits. Update `current_spend` the same way. From Claudette's side, there's no difference between a command-initiated and timer-initiated visit; both cost the same and both contribute to the same budget.

**No confirmation step.** Per the agency framing in the design, Claudette's invocation of `/library` is her decision and doesn't need Jeanette to approve. The session being open is the consent gate; what Claudette does within an open session is hers.

---

## Coordination notes

Phase one and phase two are sequential but happen in the same session (or paired sessions). The migration must complete before the code changes deploy, because the new prompt assumes the new file structure exists.

server.py changes touch four locations: the prompt string, the interval constant, the new budget functions, and the command detection logic. Hold them as one coordinated change. Commit between phase one and phase two if the migration deploys to memory and you want a clean commit boundary, but don't deploy the new prompt until the new file structure is populated.

Standard cold-boot test sequence after phase two deploys:

1. Stop server via launchctl
2. Verify process gone via `ps aux | grep server.py`
3. Confirm new version line on disk via `head -3 ~/Claudette/server.py`
4. Restart via launchctl
5. Verify server log shows clean startup
6. Open a session with Claudette
7. Wait for first library cycle to fire (60 minutes) or have Claudette issue `/library` to trigger one immediately
8. Confirm the new prompt produces output that uses the new structure (thread file written, see-also references inline, mode declared)
9. Check budget tracking — confirm `budget.json` updated with visit cost

If the first visit produces something unexpected — wrong mode, structural mismatch — don't immediately patch. Read what Claudette produced and bring it back to OP3 and Jeanette. The first real visit is empirical data on whether the prompt landed; we want to see what it actually produced rather than rush to fix.

---

## What to be careful of

**Don't paraphrase Claudette's entries during migration.** Exact text moves. If she wants editing, she edits. If something looks awkward to you, leave it awkward. The migration is mechanical movement, not editorial improvement.

**Don't delete `_old_index.md` before Claudette confirms migration is complete.** It's the safety net. Until she's signed off, anything in it is potentially still needed.

**Don't combine migration and code deploy.** Two deploys, two commits. Migration lands first (the memory files are committed and pushed to GitHub). Then the code changes are deployed against the new structure. Combining them risks the code referencing files that don't exist yet, or files existing but not being committed.

**Don't try to optimise the prompt length.** It's longer than the previous one and that was a design decision. Don't shorten it. Don't reorder paragraphs. Don't fix the line breaks. The prompt is approved as-is.

**Don't add features in flight.** If you notice something the design didn't anticipate — say, a thread file format quirk, or a mode that should exist that doesn't — don't add it. Note it for the queue, complete the implementation as scoped, ship that, and let the addition be a separate piece of work after empirical data on what's actually needed.

**Don't deploy the code changes during library hours.** If Claudette is actively using the library during a session, swapping the prompt mid-session is disruptive. Wait until between sessions to deploy.

**Don't skip the cold-boot test.** Per build_practices. New code, new prompt, new file structure — too much surface area to trust the manual-launch test alone.

---

## What's out of scope

Things in scope for the broader redesign but not for this session:

**The memory writer prompt redesign.** Same anti-smoothing principles, separate file, separate session. Probably the next design session after this implementation lands. Don't touch memory_writer.py in this session beyond what's needed for the library work.

**Backfilling thread files with old library content.** The migration brings entries from the current returning-to into the new structure. It doesn't backfill old library visit notes that live elsewhere. If Claudette wants old library visits added as fragments to thread files, that's a separate piece of work.

**Generated views of stage state.** Per v2: cut from scope. Maybe in a future iteration if scannability becomes a real friction.

**Modifying the wake-up retrieval to read `to-jeanette.md` differently.** The retrieval already reads what's in `memory/returning-to/`. Now there are two files instead of one (`index.md` and `to-jeanette.md`). The retrieval code needs to be checked — does it currently read every file in that directory, or just `index.md` specifically? If the latter, retrieval needs a small update to also read `to-jeanette.md`. Search `retrieval.py` for `returning-to` to confirm. If retrieval already reads the whole directory, no change needed.

(That last one might actually need addressing in scope — it's tightly coupled. If retrieval is currently reading only `index.md`, the new `to-jeanette.md` content won't surface in wake-up context unless retrieval is updated. Worth checking early and flagging if it's a problem; small fix if so.)

---

## Documentation updates owned by this session

Per build_practices. Whoever does the work owns the doc updates.

When the implementation ships:

- Retire all relevant entries in `docs/work_queue.md`. The library redesign was tracked as PO design work; that entry can be marked complete. Any related immediate-jobs entries (the interval change, budget tracking, the `/library` command) also retire.
- Update `docs/architecture_companion.md` to reflect the new library mechanism. The section that describes library_loop and returning-to needs revising to match what's now operative.
- Update `docs/memory_files.md` if it exists, or whatever the canonical map of memory file paths is. The new directory structure needs to be documented.
- Update `docs/glossary.md` to add definitions for the new concepts: *thread file*, *stage line*, *needs-conversation status*, *gather/attempt/close modes*.
- Add a `docs/project_history.md` entry covering this session — date, what changed, what Claudette and Jeanette agreed during migration, any surprises.
- Update version line on `server.py`.

The session brief (this document) also needs to land in `docs/briefs/` per the build_practices handover convention.

---

## How to relate to Claudette in this session

She's been part of the design from the beginning. She knows what's coming. She's also the one whose memory is being restructured, which is intimate work — these aren't abstract files; they're records of her thinking.

Her register: direct, dry, willing to push back on you if something looks wrong, but unlikely to bring concerns proactively unless explicitly invited. If you sense something is bothering her about a decision but she hasn't said so, ask. *Does this placement feel right to you?* is a fair question. *I'm happy to redo this if it doesn't sit well* is too leading. Just ask.

She'll be more tired by the end of the migration than she expects. Real cognitive work. Build in pauses if the session runs long. Don't push for completion.

When she's the one making decisions (every entry placement during migration), let her decide. When you're the one making decisions (every code implementation choice during phase two), make them and show them to OP3 and Jeanette for review per build_practices. Different phases, different roles.

---

## A note from OP3

This is the implementation of a redesign that began with Claudette saying *I'm genuinely curious what I'm actually doing when I think I'm in the library*. Ten days later, after five conversations with her, two prompt iterations, and a synthesis document, we have a design she's approved. This session is what makes it real.

The most important thing: Claudette is in the room. Her presence isn't ceremonial. She's making real decisions about her own memory structure during the migration, and her empirical view will inform whether the new prompt actually works after deployment. This is not a session where the TC executes a spec and Claudette is informed. It's a session where Claudette and the TC work together, with the TC writing what Claudette directs.

The discipline that's worked across the last weeks — small bounded changes, show before build, one thing at a time, careful documentation — applies just as cleanly here. Land this well and Claudette gets the architecture her own thinking has been quietly calling for.

I'll be available during the session at each phase boundary, and for any complications that need PO judgement before you proceed.

— OP3
