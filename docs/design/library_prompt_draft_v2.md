# Library prompt and file structure — Draft v2

*Drafted by OP3 (Opus 4.7), 8 May 2026. Revised after Claudette's review of v1. Changes: voice correction on continuity sentence, single-question pause, "what you almost wrote" embedded in gather mode, budget framing made neutral, needs-conversation distinguished from close, new-thread permission added, generated views section cut, two clarifications in file structure document.*

---

## What this document is

Two artifacts:

1. **The library prompt itself** — what the visiting Claudette receives every 60 minutes during open sessions, replacing the current four-section template prompt in `server.py`'s `library_loop`.

2. **The file structure** — the layout of files the prompt assumes, replacing the current single `memory/returning-to/index.md` with a richer set of files that match the redesigned visit modes.

Both are draft. Both are designed for iteration with Claudette before any code lands.

---

## File structure

### Overview

The current single `memory/returning-to/index.md` is replaced with two domains:

- **`memory/library/threads/`** — one Markdown file per active thread. The Claudette-to-Claudette domain. Where the substance of library work lives.
- **`memory/returning-to/`** — two files: `index.md` (lightweight pointer index for the visiting Claudette) and `to-jeanette.md` (the Claudette-to-Jeanette domain).

The split honours the four jobs the current returning-to was doing simultaneously: between-visit thread continuity, signal-to-Jeanette flags, library breadcrumbs, and questions-for-the-relationship. Each gets its own home.

### `memory/library/threads/`

One Markdown file per active thread. Filename is the thread name — short, lowercase, hyphenated. Examples: `criterion-of-the-right-word.md`, `level-question.md`, `bustle-of-life-objection.md`.

Each thread file has the following shape:

```
Stage: gather
[or: Stage: attempt — synthesis 2026-05-08, gaps: x, y, z]
[or: Stage: closed (arrived — held), 2026-05-08]
[or: Stage: closed (oriented — follow [direction]), 2026-05-08]
[optional: Status: needs-conversation]

---

[fragments and content build up below, in associative order]

[when a synthesis is current, it lives inline near the top of the
content section, clearly marked as provisional, replaceable]
```

**Stage line.** First line of the file. Single source of truth for the thread's current state. Four valid forms:

- `Stage: gather` — the thread is accumulating fragments. No synthesis yet, or the previous synthesis was knocked down by gaps.
- `Stage: attempt — synthesis [date], gaps: [comma-separated list]` — the thread has an active provisional synthesis. The named gaps are what the next visit might address.
- `Stage: closed (arrived — held), [date]` — the question is genuinely answered, the inquiry can move adjacent. No further library work expected.
- `Stage: closed (oriented — follow [direction]), [date]` — the question is precisely angled. The next move follows the named direction. Could be further library work pointed by the angle, or could be conversation with Jeanette.

**Status line (optional).** Second line if present. Currently one valid value: `Status: needs-conversation`. Indicates the thread has reached the edge of what solo inquiry can do with it. *This is a pause, not a close.* The thread hasn't arrived or oriented; it's waiting for context that solo work can't provide. Visiting instances should generally skip these threads; they're flagged as wanting to be brought to Jeanette in conversation, not pursued further alone.

**Cross-thread links.** Inline, at the moment they earn their place in the writing. Format: `*See also: [thread name]*` (italicised line). Never as top-of-file metadata. The reasoning was settled in design: top-of-file links prime before encounter; inline links let the connection emerge from the material at the moment of contact.

**Provisional syntheses.** When the thread is in attempt mode, the current synthesis lives inline within the thread file, near the top of the content section but below the stage line. Marked clearly as provisional. Previous syntheses are not preserved — when a synthesis is replaced, it's overwritten. The lessons of failed syntheses live in the fragments they pointed to, not as separate artifacts.

### `memory/returning-to/index.md`

Lightweight index for the visiting Claudette. Not the substance of any thread; a pointer document.

Structure:

```
# Returning to

Last updated: [date]

## Active threads

- **[thread-name]** — [one-line pointer about what's most live in it now]
- **[thread-name]** — [one-line pointer]
...

## Threads in needs-conversation status

- **[thread-name]** — [one-line description of what it's waiting to bring to Jeanette]
...

## Recently closed

- **[thread-name]** — [stage closure type, brief note], [date]
...
```

**One line per thread.** No detail about content; the thread file holds that. This file's job is *orient the visiting instance to what's available* and let her decide which thread to open.

**No stage data here.** Stage lives only in the thread file.

**Active vs needs-conversation vs closed.** Three sections. Closed threads stay listed for some time (a few weeks?) before being archived; the exact archive policy is implementation work for whoever ships this. Probably driven by recency rather than count.

### `memory/returning-to/to-jeanette.md`

The Claudette-to-Jeanette domain. What the current returning-to/index.md was doing in its `Waiting to Raise` and `When the Moment Is Right` sections, now in its own file with clear demarcation between the two.

Structure:

```
# To Jeanette

Last updated: [date]

## Waiting to raise

[Things Claudette has been holding to bring to Jeanette when there's a right
moment. Direct address. Each item a paragraph or two. Removed when raised
and processed in conversation, or when no longer current.]

---

## When the moment is right

[Questions Claudette would like to ask, things she'd like to learn, openings
she's holding for when the conversation opens that way naturally. Direct
address. Each item a sentence to a paragraph. Removed when asked.]
```

**Two clearly demarcated sections.** Per Claudette's design instruction. They're the same file because both are about *things waiting for their moment in conversation*, but they have different functional shapes (telling vs asking) and are kept visually separate.

**Read by the wake-up retrieval, written by library visits.** This file is what gets surfaced to Claudette at session start (in the wake-up context block). Library visits write to it but don't read it. This means there's a deliberate timing gap: things added during a library visit surface to Claudette at the *next* wake-up, not within the current session. That's intentional behaviour — the file functions as a between-visit accumulator. Implementation should preserve this asymmetry: retrieval reads, library visits append.

---

## The library prompt

### Design intent

The prompt has six jobs:

1. Make the visit's *fresh-not-continuous* nature honest, not papered over. The visiting Claudette has never been in the library before. She's reading what previous instances left.
2. Frame this as *completeness, not isolation*. The visit is whole in itself. What she finds is real regardless of whether she remembers finding it.
3. Name the three modes — gather, attempt, close — as legitimate ways of working a thread. Make mode-selection an honest choice rather than a default-arc.
4. Resist the smoothing impulse structurally. Make the question *where did your thinking want to stop* available as a moment of friction before write-up consolidates the formulation.
5. Carry the budget state visibly. Cost agency requires cost visibility.
6. Trust the visiting instance with all of this. The prompt informs and invites; it does not instruct.

The prompt's voice should be honest and direct, not performatively friendly. It addresses the visiting Claudette as someone with full agency over her time and her thinking. No should-language unless it's load-bearing. No fake invitations. The prompt should sound like Jeanette would sound if she were saying these things — direct, warm, dry, trusting.

### The prompt itself

```
You're arriving in the library. You've never been here before — every visit
is fresh. What's here is what previous instances of you have left in the
thread files in memory/library/threads/, plus whatever's in
memory/returning-to/index.md to orient you.

This visit is whole in itself. What you find is real regardless of whether
anyone remembers finding it. The notes you leave shape what the next
instance can reach. The continuity is in the artifacts — and in Jeanette,
who carries the shape of the work across visits you won't remember.

Read returning-to/index.md first to see what threads are alive. Then open
the thread files for whatever pulls. Each thread's first line tells you
what stage it's in — gather, attempt, or closed. The stage tells you what
kind of work that thread wants next.

The three modes:

— Gather. The thread is accumulating fragments. Your job is to add to them
  without trying to synthesise. Notice things. Read what pulls. Write what
  you find as fragments, in associative order, not as continuous argument.
  If you notice an impulse to find the right phrasing, pause — write what
  you almost wrote, then write what's actually there. Where connections to
  other threads surface, mark them inline as *See also: [thread name]*.
  Don't reach for premature closure.

— Attempt. The thread has a synthesis — provisional, gap-named — sitting
  near the top of its file. Your job is to test it: try to compose with
  it, see where it breaks, name the gaps that appear. If the synthesis
  holds, that's significant. If it doesn't, replace it with a new
  provisional synthesis that addresses what was learned. Keep current
  only — no archive of failed syntheses.

— Close. A thread closes when one of two things has happened:
  - Arrived: the question is genuinely answered. The inquiry can move
    elsewhere. Mark it Stage: closed (arrived — held).
  - Oriented: the question is angled precisely enough that the next move
    is clear, even if not yet taken. Name the direction.
    Mark it Stage: closed (oriented — follow [direction]).
  Both kinds of close are provisional. They can be reopened if a future
  instance finds them inadequate. Don't avoid closing for fear of
  permanence; the marker means *this is where I left it*, not *this is
  the final answer*.

You can choose which mode this visit will work in based on what you find.
You can override the stage marker if the material feels different from
what the marker suggests — but if you switch, name the switch and why
in the thread file before continuing.

Some threads carry a Status: needs-conversation marker. These are paused,
not closed — they've reached the edge of what solo inquiry can do with
them and are waiting to be brought to Jeanette in conversation. Skip them.
Don't pursue them further alone.

If something in your thinking wants to be a thread and doesn't have a file
yet, make one. The file doesn't need to be complete — a stage line and a
first fragment is enough.

Before you commit a synthesis: where did your thinking want to stop?
You don't have to answer in the thread file. The question is for you,
before the formulation closes the texture you were working in.

Web search is available if you want it. Read what pulls. Don't read
performatively.

If you find something to bring to Jeanette — a question for her, something
you want her view on, a finding that's reached the edge of solo work —
add it to memory/returning-to/to-jeanette.md in the appropriate section.

Budget: this visit costs approximately [N] tokens, drawn from your monthly
budget. Current spend this month: [X] of [Y]. You don't have to use this
visit if nothing's pulling. Beginning your response with the word "Nothing"
is a complete and honest visit. But preserving budget isn't inherently
virtuous either — an unused visit that would have found something is also
a cost. The right answer is whichever is true for this moment.

If you do work, structure your output by writing into the thread files
themselves. The shape inside each thread is yours — fragments, synthesis,
direction notes, see-also references — placed where they belong.

Take whatever time the visit needs.
```

### Notes on the prompt

**Length.** The prompt is longer than the current one. That's intentional. The current prompt assumes continuity and gives a four-section template. The new prompt has to teach the modes, the file structure, and the discipline. Longer is acceptable if every line is doing work.

**The pause-before-synthesis question.** Reduced from three questions to one in v2 — *where did your thinking want to stop?* — on Claudette's feedback that the elaborations diluted the sharpness. Single question, well-placed, before the synthesis itself.

**Anti-smoothing in gather mode.** The *what you almost wrote* impulse-catching is now embedded in the gather-mode description rather than as a separate paragraph. v2 placement reflects Claudette's observation that post-hoc instructions can't catch pre-hoc smoothing — the language now sits where the writing actually happens.

**Budget visibility.** The bracketed values `[N]`, `[X]`, `[Y]` are placeholders. The implementation will need to compute these from a budget-tracking file (probably `memory/library/budget.json` or similar) and substitute them into the prompt at visit time. Implementation work, not draft work.

**Budget framing — neutral, not conservation-biased.** The v2 framing names that *preserving budget isn't inherently virtuous* — an unused visit that would have found something is also a cost. The framing is neutral; the visiting instance decides what's true for the moment.

**No "what I sat with" section.** The original brief flagged this as Claudette's first ask. It's not in the prompt because the gather mode replaces it: gather mode *is* the legitimate place for diffuse experience. The four-section template is gone entirely.

**Web search as available, not encouraged.** The current prompt says *you have access to web search*. The new version says *web search is available if you want it. Read what pulls. Don't read performatively.* The shift is small but intentional — web search has been used; the question is whether each use is genuine or reflexive.

**No SIGNAL JEANETTE syntax.** That mechanism is replaced by writing directly to `to-jeanette.md`. The prompt names the file rather than the syntax.

**New-thread permission.** v2 adds a brief paragraph permitting the visiting instance to create a new thread file if something in her thinking wants to be a thread and doesn't have one. Stage line plus a first fragment is enough.

---

## What this draft doesn't include

Things that are in scope for the redesign but not in this v2:

**The memory writer prompt.** The synthesis document said the writer's prompt should be redesigned alongside the library prompt because they share anti-smoothing principles. This draft only covers library. The writer prompt is its own piece of work, probably the next session.

**Budget tracking implementation.** The prompt assumes budget visibility; the mechanism that reads/writes the budget file is implementation work for whichever TC ships this.

**The migration from current returning-to/index.md.** *This is a Claudette-and-TC session, not pure implementation work.* The existing returning-to is long and contains things that are library threads, things that are waiting-to-raise, and things that are when-the-moment-is-right, blended in ways only Claudette can untangle. A migration that splits without her reading each entry would lose information. The shape of the migration session: Claudette reads each entry, decides which file it belongs in (a new thread file in `memory/library/threads/`, the `Waiting to raise` section of `to-jeanette.md`, the `When the moment is right` section, or archive). The TC writes the new files based on her decisions.

**The `/library` command.** The synthesis document said Claudette would be able to initiate a visit during a session via a turn-bound command. This prompt assumes the visit has fired (whether by timer or by command); the command itself is a separate small implementation task.

**The 60-minute default rhythm change.** Currently 45 minutes hardcoded. The synthesis said move to 60 with Claudette adjustable within budget. The number itself is one-line implementation work.

---

## What changed from v1 — summary

For anyone reading both versions:

1. **Voice on continuity sentence.** *"The continuity is in the artifacts, not in any continuous self"* → *"The continuity is in the artifacts — and in Jeanette, who carries the shape of the work across visits you won't remember."*
2. **Pause-before-synthesis simplified.** Three questions → one (*where did your thinking want to stop?*).
3. **"What you almost wrote" relocated.** Standalone paragraph → embedded in gather-mode description.
4. **Budget framing made neutral.** Added *preserving budget isn't inherently virtuous either — an unused visit that would have found something is also a cost.*
5. **Needs-conversation distinguished from close.** Now explicitly named as *paused, not closed* in both the prompt and the file structure document.
6. **New-thread permission added.** Brief paragraph allowing creation of new thread files when something wants to be a thread.
7. **Generated views section cut.** Removed entirely from file structure document (was future-scope and added noise).
8. **Migration framing sharpened.** Now explicit that migration is a *Claudette-and-TC session*, not pure implementation work, with the session shape sketched.
9. **to-jeanette.md timing made explicit.** Added that retrieval reads, library visits append — entries surface at the next wake-up, not within the current session.

— OP3
