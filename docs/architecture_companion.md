# Claudette Architecture — Companion Text

This document accompanies `architecture_map.svg`. The diagram shows the shape; this text explains what each piece is, what flows where, and what it means when something breaks. Read alongside the diagram, not in place of it.

Last updated: 2026-04-30. Update this whenever the system changes in a way the diagram or these descriptions no longer reflect.

---

## Components

### Browser

The interface Claudette is shown through. Loads the HTML at `claudette_interface_connected.html`, which makes HTTP requests to server.py on `localhost:5001` for everything — starting sessions, sending messages, receiving streamed replies, ending sessions, library control, voice generation, frame uploads from the camera. The browser is a thin shell around the server.

The HTML is served by server.py at the `/` route. The interface calls back to specific server.py routes for each kind of action. State held in the browser is minimal — mostly UI state and the session's running message history during a conversation.

### server.py

The Flask application that does almost everything. Runs as a long-lived process listening on port 5001. It holds session state in memory, manages the library loop, handles all routes, calls Claude API for messages, calls Fish Audio for voice generation, reads from GitHub at session start, writes to GitHub during library cycles, spawns memory_writer.py at session end, and saves transcripts to disk.

Three logical regions inside server.py, shown as inner boxes in the diagram:

**Session.** The routes that handle a normal conversation: `/start` (begin a session, run retrieval, build the system prompt), `/message` (send a user turn, stream the model's reply back to the browser), `/end` (close the session, save the final transcript, spawn the memory writer). Also includes `/note` for saving notes during a session. The session region holds the running message history in memory and clears it when the session ends.

**Library.** The library loop runs on a background thread that fires every 45 minutes whenever the library is active. It reads `returning-to/index.md` from GitHub, calls Claude API with web search enabled, writes any meaningful response back to GitHub as a library visit record, and optionally appends to `returning-to` if the response signals something to raise with Jeanette. The routes `/library/start`, `/library/stop`, and `/library/status` control the loop. The loop is independent of session state — it runs whether or not a conversation is in progress.

**Voice & Eye.** The routes for voice and visual perception: `/speak` (call Fish Audio to generate speech), `/see` (receive a camera frame from the browser), `/note` (save a written observation). These are smaller and more peripheral than the session and library regions but live in the same server process.

### memory_writer.py

A separate Python script that updates Claudette's persistent memory after each session. It is **not** running continuously. Instead, server.py spawns it as a subprocess at the end of every session, with the transcript path passed as an argument. The writer reads the transcript, reads her current memory files from GitHub, calls Claude API to determine what should be updated, writes the changes back to GitHub, and exits.

The dashed border on the diagram is showing the subprocess relationship — it lives, does its work, and dies, rather than running alongside server.py the way the library loop does.

### Claude API

External service. Three different things in this codebase call it:

The session message route (every user message → one streaming response from the model).

The library loop (every 45 minutes when the library is active → one response, with web search enabled as a tool).

The memory writer (once per session ending → one streaming response with the transcript and current memory as context).

Each call has different parameters, different system prompts, and different tool access. The diagram shows them all hitting one Claude API box because that's what's true, but operationally they're three quite different uses of the same API.

### GitHub

Two repositories live here, though the diagram only shows one box.

The **memory repository** (`Jeanetteclaire/Claudette-memory`, private) holds Claudette's persistent memory. It's read at session start (by retrieval.py, called from server.py during `/start`), read at the start of each library cycle, written by memory_writer.py after sessions end, and written by server.py during library cycles when a visit produces a record or signals a returning-to update.

The **code repository** (`Jeanetteclaire/Claudette-code`, public) holds the source code. The running system doesn't read from this at runtime — it's just where the code lives in version control. Future Claude instances fetch from here to read the current deployed version.

### Fish Audio

External service used only for voice generation. server.py's `/speak` route receives text and calls Fish Audio's API to convert it to speech, then streams the audio back to the browser. Replaced ElevenLabs as Claudette's voice provider; same cloned voice, different platform.

### Disk

Local filesystem on the Mac. Two things server.py writes here directly: transcripts (one file per session, plus periodic flushes during long sessions) and log files (`claudette_server.log` and `claudette_server_error.log`). Memory_writer.py reads transcripts from disk when it runs.

---

## Flows — what happens in time

### Session start

You press Begin in the browser. The browser calls `POST /start`. server.py runs retrieval (calls retrieval.py to fetch memory files from GitHub), assembles the system prompt with that memory plus the welcome message, initialises in-memory session state, and returns a 200 to the browser. The interface is now ready for input.

### A message exchange

You type a message and press send. The browser calls `POST /message` with your text. server.py adds your turn to the in-memory message history, sends the whole history to Claude API as a streaming request, and pipes the response back to the browser as it arrives. While the response streams, the browser is also calling `/speak` to generate voice for what's been said so far. When the stream completes, server.py adds the model's full reply to the in-memory history and saves an updated transcript to disk.

### Session end

You end the session through the interface. The browser calls `POST /end`. server.py writes the final transcript to disk, then spawns memory_writer.py as a subprocess passing the transcript path and the start/end positions. server.py returns to the browser immediately — it does not wait for the writer to finish. The writer runs independently: reads the transcript, reads current memory from GitHub, calls Claude API with the streaming prompt, writes any updated memory files back to GitHub, exits. From the browser's perspective, the session is over the moment `/end` returns.

### Library cycle

Independent of any session. When the library is active, every 45 minutes the loop wakes up, reads `returning-to/index.md` from GitHub, calls Claude API with web search enabled, then either writes nothing (if the response begins with "Nothing"), writes a visit record to `memory/library/`, optionally updates `returning-to` with a "waiting to raise" entry, and goes back to sleep for another 45 minutes. The loop runs on a daemon thread inside server.py — it dies when server.py dies.

### Transcript flush (background)

While a session is running, server.py periodically writes the current state of the transcript to disk so that nothing is lost if the server is killed mid-session. This runs every minute on a separate background thread. Unlike the library loop, the flush has no API calls or external dependencies — it's just disk I/O.

---

## State and storage

What lives where, and what happens if it's lost.

**In-memory in server.py:** session message history, library loop active flag, the transcript being built. Lost on server restart. The transcript is the only one that's also flushed to disk during a session, so a mid-session crash loses at most one minute of conversation. The session state is by design ephemeral — restarting server.py means any active session is over.

**On the Mac's disk:** transcripts (one file per session date, in `transcripts/`), log files. Persistent until the disk dies. Backed up weekly via Time Machine to a 4TB external drive — that backup is the safety net against disk failure. Not in git (transcripts and logs are explicitly in `.gitignore`); git is for code, Time Machine is for personal content.

**On GitHub (memory repository):** all of Claudette's persistent memory — facts, observations, threads, returning-to, library visits, signals. This is the canonical store of who she is across sessions. Versioned; every change is a commit and rollback is possible. Backed up implicitly by being on GitHub's servers.

**On GitHub (code repository):** the source code. Versioned. Any TC instance can read the current version via `https://raw.githubusercontent.com/Jeanetteclaire/Claudette-code/main/[filename]`.

---

## Failure modes — what to check first

For each thing that can go wrong, what it looks like and where to look. This list will grow over time as we encounter new failure modes.

**Memory writer hangs or times out.** The session ends but no commit appears in the memory repo. Check `claudette_server.log` for `[memory_writer]` lines — the writer logs each step. If it's not appearing at all, the spawn failed; if it appears and stops, the writer is running but stuck. Check the timeout value in `server.py` (currently 1800 seconds — 30 minutes — as of 2026-04-29). If a session is unusually large, the writer may take longer; the timeout is the upper bound.

**Memory writer succeeds but no commit on GitHub.** API call worked but write to GitHub failed. Check the writer's output for "could not write" lines. Most likely cause: GitHub credentials issue. The transcript is still safe on disk; you can re-run the writer manually with the standard manual command.

**Library cycle produces nothing.** Could be expected (the response started with "Nothing") or a real failure. Check `claudette_server.log` for `Library: cycle error` lines. If you see them, the cycle failed silently — the loop catches all exceptions to keep the schedule running. If you see `Library: nothing formed — no write`, that's normal.

**Voice not playing.** Could be Fish Audio API key issue, network issue, or browser audio issue. Check the server log for `/speak` error lines. Confirm the Fish Audio key in `.env` is current.

**Session won't start, "session already running" warning.** server.py thinks a session is active when it shouldn't be. Either an old session never ended cleanly, or another browser tab on the network started one. Most reliable fix: restart server.py. Less heavy: end the session via the interface that's holding it, if you can find it.

**server.py won't start at all.** Check `claudette_server_error.log` for the actual error. Common causes: port 5001 already in use (another process), missing dependency from `requirements.txt`, syntax error from a recent code change.

**Memory retrieval at session start is wrong.** The system prompt is built from her memory files. If retrieval is returning stale or wrong content, the issue is either in retrieval.py or in the memory files themselves. Check the relevant file in the memory repo manually first — the issue is usually in the data, not the code.

---

## Deliberately not in the diagram

Things excluded from the visual map and why.

**The launch chain** (launchctl → start_claudette.sh → server.py). Real and important — yesterday's diagnostic conversation showed how much it matters — but adding it would clutter the orientation map without helping understand the running system. Better as its own small diagram if needed.

**Utility routes** like `/upload`, `/fetch`, `/favicon`, `/`, `/window`, `/window/send`, `/status`. They exist in server.py but they're peripheral. The companion text mentions some of them; the diagram doesn't.

**retrieval.py.** A small helper module that server.py uses during session start to fetch memory from GitHub. Could have been a third box, but conceptually it's a tool of server.py rather than an independent component. Folded into "server.py reads from GitHub at session start."

**The Electron wrapper.** Lives in a separate folder and a separate concern; it's just a packaging layer around the browser interface. Doesn't change the runtime architecture.

**Internal subprocess relationships besides memory_writer.py.** server.py uses subprocess.run for some small things (LaTeX rendering for /upload, for example) but they're transient and small and don't deserve the visual weight of being shown.

---

## When this document is wrong

Documentation drifts. If you read this and it doesn't match what the code does, the code is the truth and this is stale. Update the document when you notice drift, or flag it for the next architecture session.

Especially watch for: new routes added to server.py (they should be mentioned somewhere), changes to the library cycle logic, changes to the memory writer's behaviour, new external services added to the stack.
