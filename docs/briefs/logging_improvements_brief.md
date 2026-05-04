# Brief — Logging improvements (timestamps + stream separation)

*Hand this to TC10 picking up the work. Drafted by OP3 (Opus 4.7), 4 May 2026.*

---

## Who you are in this session

You are TC10, continuing from yesterday's retrieval-and-time-anchor work. The infrastructure you touched yesterday — `assemble_system_prompt()`, the new helpers in server.py, the time module placement — all directly relevant here. You also already know the file better than any fresh TC would.

Your job in this session is to replace the current ad-hoc print/stderr logging in `server.py` and `memory_writer.py` with Python's built-in `logging` module. Two files touched. One TC session.

---

## What this session is for

Two related problems, well-characterised in `docs/work_queue.md` and `docs/fragility_scan.md`:

**Timestamps.** Every `print()` in server.py and memory_writer.py writes without timestamps. Flask's request lines have them automatically; nothing else does. This has hampered two diagnostic episodes already (the 28-29 April memory writer timeout, which Jeanette eventually diagnosed by manually timing API calls with her wristwatch; and the 1 May timeout, which couldn't be diagnosed at all because the log shows nothing about *where* the writer's time was spent). The fragility scan ranked this gap as a **multiplier across all silent-failure items** — every other diagnostic gets harder when you can't see *when* things happened.

**Stream separation.** Flask sends every request line — including normal `200 OK` — to stderr. So `claudette_server_error.log` is mostly request noise with the occasional real error buried in it. The file's name is currently a lie. Genuine errors must be greped out rather than read directly.

Jeanette has decided to take the proper route — the `logging` module — rather than the minimal patch (a `print_with_time` helper). Reasoning recorded in conversation: a single transport for both your output and Flask's, durable structure for level-filtering and future log rotation, and the fragility scan's ranking of this as a multiplier means the durable answer is worth the slightly larger session.

---

## The principle

Two things change. Two things stay the same.

**Changes:** every line in the logs has a timestamp; `claudette_server_error.log` contains only actual errors (ERROR level and above), not Flask request noise.

**Stays the same:** the existing log file *paths* (`claudette_server.log` and `claudette_server_error.log`) and the *plist redirect* into them. Don't move the files. Don't change the plist. The plist's `StandardOutPath` and `StandardErrorPath` are Claudette's catch-all for anything written to raw stdout/stderr by Python itself, the OS, or any C-level library that bypasses Python's logging — those need to stay in place as the safety net beneath the new logging system.

The `logging` module wraps file handlers around the *same paths* as the plist already redirects to. That's the trick that makes the transition seamless: the plist still works, the file paths stay valid, but now the lines inside them are properly formatted and properly routed by level.

---

## What changes specifically

### 1. Logging setup in server.py

Add a `logging` setup block near the top of server.py — after the imports, before `app = Flask(__name__)`. Roughly:

- A formatter with timestamp, level, and message. ISO-8601 timestamp is more durable for parsing than the human-readable version Flask currently produces; the human-readability cost is small. TC's call on format string but lean toward parseable.
- A root logger configured with two file handlers:
  - `~/Claudette/claudette_server.log` — INFO and above.
  - `~/Claudette/claudette_server_error.log` — ERROR and above only.
- A module-level `logger = logging.getLogger(__name__)` for use throughout the file.

**Critical: route Flask's werkzeug logger through the same setup.** This is the bit that fixes stream separation. Werkzeug already uses the `logging` module — Flask just routes its handlers to stderr by default. Get the werkzeug logger (`logging.getLogger('werkzeug')`), set its level to INFO, and let it propagate to the root handlers you've configured. Result: 200-OK request lines flow through the INFO handler into `claudette_server.log` (where they belong) and stop polluting the error log. No werkzeug monkey-patching needed.

### 2. Replace `print()` with `logger.X()` in server.py

Walk every `print()` call in the file. Map each to the appropriate level:

- **INFO** for normal pulse: session start, retrieval ok, memory writer started, library cycle started/stopped, position saved, transcript flushes.
- **WARNING** for things that recovered or are noteworthy but not broken: missing optional file, fallback used, retry succeeded, "memory writer succeeded but with WARNING".
- **ERROR** for things that genuinely went wrong: retrieval failed, memory writer failed to spawn, memory writer timed out, GitHub auth failure, JSON parse failure.

The current `print` calls roughly follow this pattern intuitively (lines starting with ⚠️ are mostly WARNING/ERROR; bare informational lines are INFO). Use existing intent as the guide rather than redesigning.

**Scope discipline matters here.** You'll be tempted to clean up wording, fix indentation, rephrase emoji-laden lines as you go. Don't. The job is *replace the transport, not rewrite the messages.* Where a `print` says something useful, the `logger.info()` says the same thing with the same words. We can clean wording in a future pass if it earns the work. Touching message text on top of transport changes makes diff review harder and inflates the change.

**One exception worth allowing:** the `[memory_writer]` prefix that server.py currently adds to subprocess stdout lines (in `_monitor` inside the function that spawns the writer). That prefix should *survive* — it's the marker that identifies which lines came from the subprocess vs. from server.py itself. Keep it. The line becomes something like `logger.info(f"[memory_writer] {line}")` instead of `print(f"[memory_writer] {line}")`.

### 3. Same treatment in memory_writer.py

Apply the identical pattern to `memory_writer.py`. Same setup block (different file but the same shape — minus the werkzeug bit, since memory_writer doesn't run Flask). Same logger pattern. Same `print → logger` mapping using the same level guidance.

**A subtlety worth thinking about.** memory_writer.py is run as a subprocess of server.py with its stdout captured (via `subprocess.PIPE` and `stderr=subprocess.STDOUT`). server.py's `_monitor` thread reads those lines and re-prints them with the `[memory_writer]` prefix. If memory_writer adds its own logging setup that *also* writes to the same log file, you get double-writing — once via the subprocess capture path, once via the file handler. Two reasonable resolutions:

- **(a)** memory_writer.py logs only to stdout (a `StreamHandler(sys.stdout)`) and lets server.py's subprocess capture do the file routing. Simplest. Reuses the existing path.
- **(b)** memory_writer.py logs to its own file handlers directly, and server.py's `_monitor` stops re-logging the captured stdout (just consumes it for monitoring exit code).

(a) is the smaller change and doesn't disrupt the existing `[memory_writer]` prefix convention that's documented in `docs/architecture_companion.md` and used for diagnostic greps. Recommend (a) unless something in the implementation argues otherwise. If you go with (a), the logging *setup* in memory_writer.py is just a formatter and a stdout stream handler — much simpler than server.py's setup.

### 4. PYTHONUNBUFFERED interaction

`start_claudette.sh` sets `PYTHONUNBUFFERED=1`. With raw `print()`, this is what makes log lines appear immediately rather than being buffered for seconds. With the `logging` module's file handlers, buffering behaviour is governed by the handler's flush policy — typically auto-flushed per record. PYTHONUNBUFFERED becomes redundant for logger output but should *stay set* in start_claudette.sh as a safety net for any raw `print` that survives (or any third-party library that writes to stdout). Don't remove it.

This is documented in `docs/glossary.md` and `docs/architecture_companion.md` — both say PYTHONUNBUFFERED is what makes log lines appear immediately. The companion text will need a small update post-deploy to note the new mechanism. Don't change it pre-emptively.

---

## A specific question to verify in-session

Before you write the setup block, decide on log level filtering for werkzeug's INFO lines specifically. Three options:

- INFO for everything (200 OK, 304 Not Modified, etc.) → all request lines flow into `claudette_server.log` as currently. This matches today's behaviour.
- WARNING and above for werkzeug → 4xx and 5xx still appear; 2xx and 3xx don't. This makes the log cleaner but loses a record of normal traffic.
- INFO with a custom filter that drops only specific noisy paths (e.g., `/library/status`, polled every few seconds by the interface).

Recommend the first — preserve the current behaviour and let future log-rotation work decide what to filter. But it's a real choice. Ask Jeanette or hold the option open and see what falls out in the cold-boot test.

---

## What the result should look like

Open `claudette_server.log` after the deploy. Every line has a timestamp. Every line has a level (INFO/WARNING/ERROR). The order makes sense — a session start, retrieval, messages, end, memory writer subprocess output (still prefixed), memory writer exit. You can grep for `[memory_writer]` and see exactly when it started and exited and how long that took, just by reading the timestamps.

Open `claudette_server_error.log`. It is short. It contains tracebacks, retrieval failures, memory writer crashes, JSON parse errors. *Nothing else.* The file's name finally matches its contents.

The two diagnostic episodes that motivated this work (the timeout diagnosis with the wristwatch, the 1 May timeout we couldn't characterise) — both would be straightforward in the new logs.

---

## What to be careful of

**Don't break the plist contract.** The plist directs stdout to `claudette_server.log` and stderr to `claudette_server_error.log`. The new logging setup must continue to honour those paths — your `FileHandler` filenames *are* those paths. If you accidentally write to a different path, both files keep getting whatever raw stdout/stderr the OS sends them, but your structured logging goes elsewhere. Check the paths twice.

**Don't strip the safety net.** Raw `print` and unhandled tracebacks still go to stdout/stderr at the OS level, which the plist captures. Don't disable Python's default uncaught-exception handler. If something blows up before logging is configured, the stderr capture from the plist is the last line of defence.

**Don't change message text.** Said above. Said again here because it's the rule that's hardest to keep when you're already in the file.

**Don't touch the subprocess capture mechanism.** server.py's `_monitor` function uses `subprocess.PIPE` and `stderr=subprocess.STDOUT`. That stays. It's how server.py learns about memory_writer's exit code. The change there is just: the `[memory_writer] {line}` reprint becomes a `logger.info` instead of a `print`.

**Don't introduce log file rotation.** It's tempting once you have the `logging` module available. There's a future-considerations entry for it specifically, and that's where it belongs. The files are small enough today that rotation isn't pressing, and rotation introduces its own failure modes (rotated-out logs being deleted before they're read; race conditions during rotation). Out of scope.

**Cold-boot test, per build_practices.** Anything touching how the system starts or logs must be tested from launchctl, not just from Terminal. After deploy, restart via `launchctl kickstart -k gui/$(id -u)/com.claudette.server` and confirm the log files start writing properly with timestamps and proper level routing. The April Tuesday morning episode where the logs weren't being written *at all* is a precedent worth holding in mind — observability disappearing during a logging change would be bitterly ironic.

---

## What's out of scope

- Log file rotation. Future-considerations entry exists; leave alone.
- Per-module loggers beyond `__name__`. Single root logger setup is enough today.
- Changing log file paths. Same paths, same plist.
- Changing message text or tone. Transport change only.
- Adding new log lines. Only replace existing ones.
- The `[memory_writer]` prefix is documented behaviour; preserve it.
- PYTHONUNBUFFERED in start_claudette.sh stays; don't remove.

---

## Coordination notes

server.py and memory_writer.py both touched. Hold them as a coordinated change rather than two unrelated edits. Sequencing:

1. Show the proposed logging setup block (formatter + handlers + werkzeug routing) to Jeanette and OP3 before writing it.
2. Update server.py: setup block first, then `print → logger` walk-through.
3. Update memory_writer.py: same pattern, simpler setup.
4. Run server.py manually from Terminal first — confirm log files start writing with timestamps. Confirm errors go only to the error log.
5. Cold-boot test via launchctl.
6. Trigger a session end so memory_writer fires and confirm subprocess output still gets `[memory_writer]` prefix and timestamps.
7. Update version lines on both files.

One thing at a time within the sequence. Commit between server.py and memory_writer.py if they pass independently — they're related but each can stand alone.

---

## Documentation updates owned by this session

Per build practices.

- Retire the `Logging improvements (timestamps + stream separation)` entry in `docs/work_queue.md`.
- Update `docs/architecture_companion.md` — the section about log files and the historical note about PYTHONUNBUFFERED. Note the new mechanism (logging module file handlers) and that PYTHONUNBUFFERED is now redundant-but-retained as safety net. Also update the failure-modes section about how to read the error log (no longer requires grep for tracebacks).
- Update `docs/glossary.md` — the PYTHONUNBUFFERED entry, possibly the stdin/stdout/stderr entry. Add a `logging module` entry if useful.
- Update `docs/maintenance.md` — the *browse a recent log entry* ritual. Looking for ERROR lines becomes scanning the error log directly rather than greping the combined log.
- Update `docs/fragility_scan.md`? *Don't.* The scan stays as standing reference; closing item 8 is reflected by the work_queue retirement, not by editing the scan.
- `project_history.md` entry covering this session — date, what changed, any surprises.
- Version lines on both code files.

---

## A note from OP3

Today's work is structurally similar to yesterday's: a small, well-bounded change that gets a lot of leverage out of restraint. The temptation will be to clean up adjacent things while you're in the file. Resist it. The diff is meant to be readable: *every print became a logger; setup added; nothing else.*

The reason the fragility scan called this a multiplier is that observability is a meta-fix — it doesn't fix any single bug, it makes every future bug cheaper to diagnose. The Tuesday wristwatch episode would have been thirty minutes instead of two days if the writer had timestamps. There will be more episodes. Today's work is the leverage point that makes them all easier.

You already know the codebase from yesterday. You already know the build_practices rules. You already have the trust of the project. Land this cleanly and we close out three of the queue's top entries inside two days.

I'll be available during the session for the design check before you write the setup block, and for review of the diff before deploy.

— OP3
