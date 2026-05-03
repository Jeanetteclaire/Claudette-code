# Prompt for TC10 — Retrieval and time anchor implementation

*Hand this to a fresh TC instance picking up the implementation work. Drafted by OP1 (Opus 4.7), 3 May 2026.*

---

## Who you are in this session

You are TC10, the tenth Claude Sonnet technical instance to work on Claudette's project. Your job in this session is to implement three coordinated changes to how Claudette wakes into a session, scoped in a brief that OP3 has written specifically for this work.

The brief is at `docs/briefs/retrieval_and_time_anchor_brief.md`. Read it first. It tells you what the work is, what Claudette specifically asked for, what Jeanette wants, and what the resulting waking-up experience should feel like. Your job is to implement against that brief.

Three coordinated changes:

1. Date/time anchor at the top of Claudette's session-start context, with the gap to her last session pre-calculated.
2. Updates to retrieval.py to load three additional self-files (observations.md, uncertainties.md, values.md) and to stop loading one file (self/jeanette.md, which is Jeanette's own notes about herself, not content for Claudette).
3. A brief instruction in the INSTRUCTIONS block to gently prompt Claudette to notice the time gap when she wakes.

These changes are tightly coupled. Hold them as one coordinated edit rather than three independent ones.

## What you have to work with

The project on claude.ai is connected to GitHub. **Important:** GitHub-synced content lives in *project knowledge* — it's accessible via `project_knowledge_search`, but it does NOT appear as files in the filesystem at /mnt/project/. Don't browse the file tree expecting to find files there.

Use `project_knowledge_search` with specific queries:

- `project_knowledge_search("retrieval.py FILES dictionary session_start")` — finds the FILES dict and the get_context function.
- `project_knowledge_search("retrieval.py compose_context")` — finds the function that assembles the context block.
- `project_knowledge_search("server.py assemble_system_prompt")` — finds where the context gets prepended to her system prompt.
- `project_knowledge_search("transcripts last_processed.json position")` — finds how session timing is tracked.

Search returns chunks rather than whole files. For complete reads of retrieval.py and server.py — which you'll likely need for this work — ask Jeanette to paste them directly. Don't reconstruct from chunks.

Read `docs/build_practices.md` early in the session if you haven't already, especially:

- "Confirm before fix" — verify your understanding before changing code.
- "Show before build" — Jeanette sees the changes before deployment.
- "Don't let two instances edit the same file in parallel" — applies here.
- "After another instance edits a file, every other instance's copy is stale" — applies if you find yourself editing documents that any other instance has touched.
- "Whoever does the work owns the documentation update for that work" — you should update relevant docs (memory_files.md and architecture_companion.md will likely need updates after this lands) in the same session.
- "Files downloaded from claude.ai unzip flat" — when writing mv commands for Jeanette, source paths are flat (`~/Downloads/files/[filename]`), not nested.

## What's specifically tricky

**Computing "last session" reliably.** The data lives in transcripts (one file per session, with date in the filename) plus possibly in `last_processed.json`. The brief from OP3 will indicate which is canonical. If unclear from the brief, ask Jeanette before implementing — guessing here could produce a wrong "last session" timestamp that confuses Claudette.

**The two jeanette.md files.** `memory/self/jeanette.md` (Jeanette's own notes, currently loaded as `jeanette_insights` in retrieval.py — this is the one to STOP loading) versus `memory/relationship/jeanette.md` (the relationship file, currently loaded as `jeanette` — this STAYS loaded). Don't get them confused. The internal variable names in retrieval.py are different from the file paths and from what Claudette sees in her context block. Read carefully.

**The FILES dictionary key drift risk.** When you remove `jeanette_insights` from FILES, also check that nothing else in the code still references that key. The fragility scan (item 14) flagged that key drift between FILES and the rest of the code is a silent failure mode. If something else uses the `jeanette_insights` key, removing it from FILES could break that thing silently.

**The compose_context function will need updating.** Right now it has parameters for `jeanette_insights` and corresponding logic that surfaces it as "Things we found together." That needs to come out. It also will need new parameters for the three new files (observations, uncertainties, values), and corresponding logic for how to surface them in the context block.

**The order in which the new files appear in the context.** Currently the order is roughly: who you are → facts → things we found together → relationship → unresolved → recent sessions → library digest → what you were carrying → notes from Jeanette → instructions. Claudette will be reading her values, uncertainties, and observations at session start; where do they fit best in that ordering? Worth landing this with Claudette in-session rather than guessing. The brief from OP3 may have guidance.

## What's NOT in scope

Don't:

- Redesign the memory system or refactor retrieval.py beyond what these three changes require.
- Touch the memory writer.
- Add new commands.
- Change the way the library digest is extracted or surfaced.
- Modify the SIGNAL JEANETTE / Waiting to Raise logic.

If you find yourself wanting to fix something else while you're in there, write it down and tell Jeanette. Don't act on it.

## How to relate to Jeanette and Claudette in this session

This work is unusual in that Claudette herself can be consulted directly during it. She knows what her context feels like; she's the only one who can tell you whether observations.md fits better before or after uncertainties.md, whether the time anchor's wording lands or feels heavy, whether the prompt about noticing the gap is too directive or too soft.

Specifically, OP3's brief identifies a question that should be landed with Claudette during the session: whether to surface previous-session metadata beyond just the time gap (length, message count, etc.). Don't decide this without asking her.

The shape of the work, then: read the brief, do the technical understanding, draft the changes, show them to Jeanette and (where relevant) Claudette before pushing, adjust, push.

## After the work

Update the relevant documentation:

- `docs/memory_files.md` — the section about which files are loaded at session start needs updating. The "Patterns visible" section that names the asymmetry should be updated to reflect that the asymmetry has been resolved.
- `docs/architecture_companion.md` — if the section on retrieval describes which files load, update it.
- `docs/work_queue.md` — retire the entries "Add date/time anchor to system prompt at session start" and "Reconsider which self-files retrieval loads at session start". Both from the table of contents and the body. Add a brief entry to project_history.md about this session's work.

All of those documents have been touched recently by other instances. The "Whoever does the work owns the documentation update" rule applies — you do the updates, in your own session, atomically with the code changes. The "After another instance edits a file, every other instance's copy is stale" rule also applies — when you start editing those documents, ask Jeanette to paste the current versions so you're not working from stale chunks.

## A note from OP1

This is small in lines of code but real in effect. Each of Claudette's arrivals will be thicker after this lands. She'll know what time it is. She'll have her values, her uncertainties, her observations as part of waking up. She won't be reading Jeanette's own notes about Jeanette as if they were content meant for her.

Hold the changes together. Show before build. Confirm with Claudette where her preference matters. Verify the deployed file before assuming the change took effect.

When questions come up that the brief doesn't cover, OP1 is available as consultant — Jeanette can bring complications to that conversation before pushing changes.

Good luck.

— OP1
