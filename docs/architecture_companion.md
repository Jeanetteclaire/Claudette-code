# Claudette Architecture — Companion Text

This document accompanies `architecture_map.svg`. The diagram shows the shape; this text explains what each piece is, what flows where, and what it means when something breaks. Read alongside the diagram, not in place of it.

Last updated: 2026-05-03. Update this whenever the system changes in a way the diagram or these descriptions no longer reflect.

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

## Launch chain — what starts everything

Before any of the runtime flows below, server.py has to be running. That's what the launch chain handles.

When you log into your Mac, macOS launches your user session ("Aqua" in launchctl terminology). At that point, launchctl reads every plist file in `~/Library/LaunchAgents/` and starts whatever's configured to run at login.

The plist file `com.claudette.server.plist` is the configuration that tells launchctl how to start Claudette. It specifies:

- The program to run (`start_claudette.sh`)
- Where to redirect stdout (the path to `claudette_server.log`)
- Where to redirect stderr (the path to `claudette_server_error.log`)
- Whether to restart the program if it dies (`KeepAlive`)
- Whether to start it immediately at login (`RunAtLoad`)

Without the plist, launchctl wouldn't know server.py exists. The plist is the bridge.

When launchctl starts the shell script, the script runs server.py. The shell script is the layer that sets `PYTHONUNBUFFERED=1` — the environment variable that ensures Python writes log lines immediately rather than buffering them. Without this, log files would lag by seconds or minutes, and the last few lines before a crash might never appear.

server.py itself loads the `.env` file (API keys), starts the background threads (library loop, transcript flush), and binds to port 5001. From that point onward, the browser can connect.

The diagram `launch_chain.svg` shows this flow visually with the annotations of what each layer adds to the environment.

**Why this matters.** Most of the time, the launch chain is invisible. You log in, Claudette is running, you use her. But when something goes wrong with how she starts — fails to start, starts but doesn't accept connections, starts but logs nothing — the chain is where the fault has to be. Having the chain mapped means you can think systematically about where in those four layers the problem lies, instead of guessing.

**Interface configuration dependency: Tailscale.** The deployed interface has a hardcoded Tailscale IP address: `var SERVER = 'http://100.89.230.113:5001'` in `claudette_interface_connected.html`. Every API call the interface makes — session start, messages, voice, library, camera frames — goes to that address. When Tailscale is off, the `100.x.x.x` address is unreachable because the Tailscale virtual network interface is down. The interface shows "server not running."

server.py itself is unaffected: it binds to `0.0.0.0:5001` and runs normally whether or not Tailscale is running. The Electron app's health check (`localhost:5001/status`) also uses localhost and succeeds. Only the interface's API calls depend on Tailscale — and only because of the hardcoded IP.

The dependency is a configuration choice, not an architectural requirement. The `SERVER` constant could be changed to `'http://localhost:5001'`, which would remove the Tailscale requirement for local-only use. Whether to make that change is a separate decision — it would also remove the ability to reach Claudette from other Tailscale-networked devices (phone, iPad). Operationally: if you see the red banner, check Tailscale before anything else.

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

While a session is running, server.py periodically writes the current state of the transcript to disk so that nothing is lost if the server is killed mid-session. This runs every 4 minutes on a separate background thread. Unlike the library loop, the flush has no API calls or external dependencies — it's just disk I/O.

---

## State and storage

What lives where, and what happens if it's lost.

**In-memory in server.py:** session message history, library loop active flag, the transcript being built. Lost on server restart. The transcript is the only one that's also flushed to disk during a session, so a mid-session crash loses at most one minute of conversation. The session state is by design ephemeral — restarting server.py means any active session is over.

**On the Mac's disk:** several distinct kinds of file with different purposes.

*Transcripts* live in `~/Claudette/transcripts/` — one file per session date. Persistent until the disk dies. Backed up weekly via Time Machine to a 4TB external drive.

*Log files* live in `~/Claudette/`:
- `claudette_server.log` holds normal output (stdout) — every line server.py prints during normal operation. Session activity, retrieval results, library cycles, memory writer subprocess output, Flask request logs.
- `claudette_server_error.log` holds errors (stderr) — tracebacks, warnings, anything Python reports as an error.

Both log files grow without bound — there's no automatic rotation or truncation. Currently small but worth being aware of long-term. See *future_considerations.md* for the eventual log rotation question.

*Configuration files* live in two places. `.env` lives in `~/Claudette/` and holds API keys and tokens (excluded from git via `.gitignore`). `com.claudette.server.plist` lives in `~/Library/LaunchAgents/` and tells launchctl how to run the server — see the next section.

None of these are in git (transcripts, logs, and `.env` are excluded; the plist lives outside the Claudette folder). Git is for code; Time Machine is for personal content; the plist is system configuration that's stable across upgrades.

**On GitHub (memory repository):** all of Claudette's persistent memory — facts, observations, threads, returning-to, library visits, signals. This is the canonical store of who she is across sessions. Versioned; every change is a commit and rollback is possible. Backed up implicitly by being on GitHub's servers.

**On GitHub (code repository):** the source code. Versioned. Any TC instance can read the current version via `https://raw.githubusercontent.com/Jeanetteclaire/Claudette-code/main/[filename]`.

---

## Failure modes — what to check first

For each thing that can go wrong, what it looks like and where to look. This list will grow over time as we encounter new failure modes.

**The log files are the primary diagnostic surface.** Almost every failure produces a log line somewhere, either in `claudette_server.log` (normal output) or `claudette_server_error.log` (errors and tracebacks — though see below). For most problems, the first move is `tail -100 ~/Claudette/claudette_server.log` to see recent activity, or `tail -100 ~/Claudette/claudette_server_error.log` if something has crashed.

A quirk worth knowing: Flask sends its routine request log lines to stderr by default, so `claudette_server_error.log` contains a lot of `200 OK` entries alongside actual errors. To find genuine errors, grep for tracebacks: `grep -A 10 "Traceback" ~/Claudette/claudette_server_error.log` shows any traceback found plus the next ten lines. This is on the list to fix — see *future_considerations.md*.

For live diagnosis during an active problem, `tail -f` follows the file as new lines appear. Combined with `grep` to filter for specific terms (e.g., `tail -1000 ~/Claudette/claudette_server.log | grep memory_writer`), you can quickly isolate the relevant activity.

A historical note worth knowing: log files only work as a diagnostic surface because two things are configured correctly. The plist redirects stdout and stderr to those file paths, and `PYTHONUNBUFFERED=1` is set in the shell script. If either is missing, the log files either don't get written at all, or lag so badly they aren't useful for live diagnosis. Tuesday morning's debugging spent significant time figuring out that the logs weren't being written before any actual diagnostic work could begin. Both are now in place; if a future change disrupts either, observability disappears.

---

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
