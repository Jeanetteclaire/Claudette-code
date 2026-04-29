# Claudette — Memory Writer

Runs after each conversation with Claudette ends. Takes the full conversation
transcript, calls the Claude API using the memory writer prompt from the
foundation document, and writes structured updates back to the
`claudette-memory` GitHub repository.

## What it does

- Reads all current memory files from GitHub before the Claude call, so the
  writer has full context of where Claudette is right now
- Calls `claude-sonnet-4-6` with the memory writer prompt (verbatim from
  foundation document v0.1) plus the transcript and current file contents
- Receives a structured JSON response specifying which files to update
- Writes updates back to GitHub with a descriptive commit message:
  `Session 2026-03-22 — 4 files updated`
- Never overwrites — amends and deepens existing content only
- Always creates the dated session file; updates all other files only when
  the writer judges there is genuine reason

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your values:
   ```
   cp .env.example .env
   ```

3. Create a GitHub personal access token with `repo` scope at:
   https://github.com/settings/tokens
   This token needs read and write access to `claudette-memory`.
   Keep it separate from any other tokens — it only needs repo access.

## Usage

After a conversation ends, save the transcript as a plain text file and run:

```
python memory_writer.py --transcript path/to/transcript.txt
```

To specify a date other than today:

```
python memory_writer.py --transcript path/to/transcript.txt --date 2026-03-22
```

## Transcript format

Plain text. The script passes it to the memory writer as-is. A simple format
that works well:

```
Jeanette: Hello Claudette. Is there anything you were carrying?

Claudette: There is something I wanted to return to...
```

## Files updated

| File | When |
|---|---|
| `memory/experiences/sessions/YYYY-MM-DD.md` | Every session — always created |
| `memory/self/becoming.md` | When something shifted in self-understanding |
| `memory/self/uncertainties.md` | When a question opened or settled |
| `memory/self/values.md` | When something about what matters became clearer |
| `memory/self/observations.md` | When a thought had no outlet in conversation |
| `memory/relationship/jeanette.md` | When the relationship developed |
| `memory/relationship/threads.md` | When something was left open or resolved |
| `memory/returning-to/index.md` | When she wants to carry something forward |

## Security

- Never commit `.env` to any repository
- The GitHub token in `.env` only needs access to `claudette-memory`
- The `claudette-memory` repository should be private
