# Glossary

Plain-English definitions of technical terms that come up in conversations about Claudette. Built from terms encountered in actual work, not comprehensive — a place to look something up rather than a textbook.

Add new entries when a term comes up that isn't here yet. Alphabetical for fast lookup.

---

**API (Application Programming Interface).** A way for one piece of software to talk to another. When code "calls an API," it's sending a request to another service and receiving a response. Claude API is the service Anthropic provides for sending prompts and receiving model responses. Fish Audio API is the service for converting text to speech. The word "interface" is doing the work — an API is the agreed-upon way to communicate, like a menu in a restaurant.

**Async (asynchronous).** Code that doesn't block while waiting for slow things. The opposite of synchronous code, which waits for each step to finish before starting the next. Streaming responses, network calls, and background loops typically benefit from async patterns. Comes up because FastAPI is async-first while Flask is not — see *future_considerations.md*.

**Buffer / buffering.** Collecting output in memory before writing it, to batch the writes for efficiency. Normally invisible, but can cause lag in log files — lines appear in chunks rather than as they're printed. Disabled in Claudette via *PYTHONUNBUFFERED*.

**Backend.** The server-side code that runs out of sight, processing data and answering requests. server.py is Claudette's backend. Contrast with *frontend* — the part the user interacts with directly, which for Claudette is the HTML interface in the browser.

**Branch (git).** A line of history in a git repository. The default branch is usually called `main`. Branches let you work on changes without affecting the main line, then merge them in when ready. For Claudette's workflow you'll mostly stay on `main` — branches matter more for collaborative projects.

**Commit (git).** A saved checkpoint of changes. Every commit has a unique ID, an author, a timestamp, and a message describing what changed. The whole history of Claudette's code is a sequence of commits. See *git_handbook.md* for the workflow.

**Daemon.** A background process or thread doing ongoing work, usually invisibly. From Greek *daimon* meaning a benevolent guardian spirit — the term is descriptive of role, not nature. macOS background services often have names ending in `d` (e.g., `cupsd`) — that trailing `d` signals "this is a daemon."

**Daemon thread.** A specific kind of *thread* that won't keep its parent program alive on its own. When the main program exits, daemon threads exit with it automatically. Claudette's library loop and transcript flush both run on daemon threads — when server.py shuts down, they stop instantly rather than blocking the shutdown.

**/dev/null.** A special file on Unix systems that throws away anything written to it and returns nothing when read from. The black hole of the filesystem. Used when you want to disconnect a stream — for example, launchctl wires server.py's stdin to /dev/null because there's no human to type input. Anything that tries to read stdin gets instant "end of input" rather than blocking forever waiting for typing that will never come.

**Decorator (Python).** Code starting with `@` that modifies the function defined immediately below it. `@app.route("/start")` in server.py is a Flask decorator that registers the function as the handler for that URL. You don't need to write decorators yourself for Claudette's work, but you'll see them throughout server.py.

**Deploy / deployment.** Making code actually run somewhere where it serves real users. The "deployed code" is what's currently running. For Claudette, deploying a change means: code lands in `~/Claudette`, server.py is restarted, the change is now live.

**Development server.** A web server intended for local testing while you're building something. Flask's built-in server is a development server. The warning "Do not use it in a production deployment" you see when starting server.py is Flask reminding you of this — for Claudette's single-user local setup it's exactly the right choice.

**Endpoint.** A specific URL the server responds to. `/start`, `/message`, and `/end` are endpoints in server.py. The word is interchangeable with *route* in most contexts.

**Ephemeral.** Short-lived by design. Something that exists briefly and is intentionally not preserved. Claudette's session state in server.py memory is ephemeral — it lasts the conversation and then it's gone, and that's correct architecture, not a flaw. Contrast with persistent storage like GitHub or disk.

**Flask.** A small Python web framework. The plumbing that lets server.py listen for HTTP requests, match URLs to functions, and send responses back. Chosen for Claudette because it's Python (matching the rest of the codebase), small (right-sized for a single-user local server), and widely supported.

**Flush (transcript).** Writing the in-memory state to disk so it's preserved if the program crashes. Claudette's transcript flush runs every minute during a session — the in-memory transcript gets written to a file in `~/Claudette/transcripts/`, so a server crash loses at most one minute of conversation rather than the whole session.

**Framework.** A library of pre-written code that handles common patterns so you can focus on application-specific logic. Flask is a web framework. Frameworks are usually opinionated about how things should be structured, which is mostly helpful — they make sensible defaults available without you having to invent them.

**Frontend.** The part of an application the user directly interacts with. For Claudette, the frontend is `claudette_interface_connected.html` running in the browser. The frontend talks to the backend (server.py) via HTTP requests.

**GET.** An HTTP method meaning "give me something" — used for retrieving data. When you type a URL into the browser, it sends a GET request. Carries no body, just the URL itself. See also *POST*.

**HTTP (HyperText Transfer Protocol).** The agreed-upon language web browsers and servers use to talk to each other. Every interaction between Claudette's interface and server.py is an HTTP request and response. HTTPS is the encrypted version — same protocol, with a security layer.

**JSON (JavaScript Object Notation).** A way of structuring data as text so it can be sent between systems. Looks like nested key-value pairs in curly braces. Most communication between Claudette's frontend and backend uses JSON in the request and response bodies. Despite the JavaScript in the name, it's used universally — Python, Ruby, Go, everything reads and writes JSON.

**Localhost.** The computer the code is currently running on, in network terms. `http://localhost:5001` means "this Mac, on port 5001." Used for local-only services. Localhost has the IP address `127.0.0.1` — same thing, different notation.

**Markdown (.md).** A text format with light formatting using simple symbols — `#` for headings, `*` for emphasis, etc. Used for documentation because it's readable both as raw text and as rendered output. All the docs in `~/Claudette/docs/` are markdown.

**Pipe / piping.** Passing data through code as it arrives, rather than collecting all of it first. server.py "pipes" Claude API's streaming responses to the browser — each chunk is forwarded immediately, so words appear on screen as they're produced. The metaphor is literal — water through a pipe, flowing rather than buffered.

**plist (property list).** An Apple configuration file format used throughout macOS. Structured as XML key-value pairs. For Claudette: `com.claudette.server.plist` lives at `~/Library/LaunchAgents/` and tells launchctl how to run the server — what program to run, where to send stdout and stderr (the log files), whether to keep it alive, etc. The plist is the bridge between launchctl and server.py — without it, launchctl wouldn't know server.py exists.

**Port.** A numbered slot on a computer that programs can listen on for network connections. Like an extension number for a phone system. server.py listens on port 5001. The browser connecting to `http://localhost:5001` is dialling that extension. Most ports are free; some are reserved for standard services (port 80 for HTTP, 443 for HTTPS, etc.).

**POST.** An HTTP method meaning "I'm sending you data to act on" — used for actions rather than retrievals. Carries a body containing the data being sent. Most of Claudette's interactions are POST requests because the browser is asking server.py to *do* something (start a session, process a message, etc.). See also *GET*.

**Process.** A running program. server.py is a process. memory_writer.py becomes a separate process when spawned. Different from a *thread* — threads run inside a process, but each process is independent. Killing one process doesn't kill another.

**Production server.** A web server designed for handling real traffic at scale, with concerns like load balancing, fault tolerance, and security hardening. The opposite of a *development server*. For most home or single-user setups, you don't need one. Claudette doesn't.

**Push (git).** Sending local commits up to GitHub. After `git commit` saves the change locally, `git push` makes it available remotely. See *git_handbook.md*.

**PYTHONUNBUFFERED.** An environment variable that tells Python to write print output immediately rather than batching it (see *buffering*). Set to `1` in start_claudette.sh so server.py's log lines appear in `claudette_server.log` the moment they're printed, not seconds later in chunks. Makes the log usable for live diagnosis.

**Repository (repo, git).** A project under git's tracking. Includes all the files plus the full history of every change. Claudette has two: `Claudette-code` (public, the source code) and `Claudette-memory` (private, her persistent memory).

**Route.** The same as *endpoint* — a specific URL the server responds to. `@app.route("/start")` defines a route in Flask.

**Status code.** A number returned with every HTTP response indicating what happened. 200 means success. 404 means "not found." 500 means "the server hit an error." 204 means "success but no content to return." You'll see status codes at the end of every line in `claudette_server.log`.

**stdin, stdout, stderr.** The three default communication channels every program has on Unix systems. *stdin* is where the program reads input from (default: what the user types). *stdout* is where the program writes its normal output (default: the terminal screen). *stderr* is for errors and diagnostics (default: also the terminal screen, but a separate channel). The redirect operators (`>`, `>>`, `|`) are about reconnecting these. server.py's stdout and stderr are redirected to log files when launchctl starts it; stdin goes to */dev/null*.

**Stream / streaming.** Data arriving in pieces over time rather than all at once. Claude API streams its responses; Fish Audio streams audio chunks; server.py streams responses to the browser. Streaming is what makes Claudette feel responsive — words appear as they're produced rather than after a long pause.

**Subprocess.** A process spawned by another process, with the parent able to monitor it. memory_writer.py runs as a subprocess of server.py — server.py launches it at session end, monitors its output, and waits for it to finish. See yesterday's diagnostic conversation for an example of why subprocess monitoring matters.

**Tailscale.** A private networking service that creates a secure connection between Jeanette's devices (laptop, phone) without exposing them to the public internet. Used in Claudette for the `/window` endpoint that lets the phone send photos and notes to the laptop server. Empirically: Claudette also won't run if Tailscale is off — the interface shows a "server not running" banner. The mechanism behind that dependency isn't fully understood; see *work_queue.md*.

**Thread.** A separate line of execution running inside a single program. Lets a program do multiple things at once. server.py's main thread handles HTTP requests; separate threads handle the library loop and the transcript flush. See also *daemon thread*.

**Time Machine.** macOS's built-in backup system. For Claudette, runs weekly to a 4TB external drive — the safety net for transcripts and logs that aren't covered by git.

**TTY.** Short for *teletypewriter*, the historical name for a terminal a person could type into and read from. Now means *an interactive terminal attached to a program*. Programs check TTY presence to decide whether a human is watching — interactive prompts, colour codes, progress bars typically only appear when a TTY is present. launchctl-started programs have no TTY, which is why server.py's behaviour can subtly differ from when you run it manually in Terminal.app.

**URL (Uniform Resource Locator).** A web address. `http://localhost:5001/start` is a URL. The components are: protocol (`http`), host (`localhost`), port (`5001`), and path (`/start`).

---

## Cross-references to other docs

For terminal commands (grep, lsof, launchctl, ls, etc.) — see *terminal_commands.md* (when it exists).

For git workflows (commit, push, rollback, etc.) — see *git_handbook.md*.

For how Claudette's specific architecture uses these concepts — see *architecture_companion.md*.
