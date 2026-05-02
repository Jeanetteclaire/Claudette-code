# Terminal commands

A reference for the commands that come up in working with Claudette. Organised by purpose, not alphabetically — when you need a command you usually know what kind of thing you're trying to do, not its name.

For git commands, see *git_handbook.md*. For concepts (process, daemon, port, etc.), see *glossary.md*.

---

## Navigation — moving around and seeing what's there

**`pwd`** — print working directory. Tells you the full path of where you currently are. Use whenever you're unsure. Costs nothing to run.

**`cd <path>`** — change directory. Moves Terminal into a folder. The most common ones for Claudette work:
- `cd ~/Claudette` — go to the Claudette folder
- `cd ~/Downloads` — go to your downloads
- `cd ..` — go up one level (the parent folder)
- `cd` (with nothing after) — go to your home folder

The `~` symbol means "my home folder" — equivalent to `/Users/jeanettearthur`.

**`ls`** — list files. Shows what's in the current folder.
- `ls` — basic listing
- `ls -la` — long format, including hidden files (those starting with `.`). Use this when you need to see hidden files like `.env` or `.gitignore`.
- `ls docs/` — list a specific folder without changing into it

---

## Looking inside files

**`cat <filename>`** — print the contents of a file to the terminal. Good for short files. Don't use on huge files; the entire content scrolls past.

**`wc -c <filename>`** — count characters in a file. Used during memory writer diagnostics to find positions in transcripts. The `-c` is for characters; `-l` would count lines, `-w` words.

**`tail -n <number> <filename>`** — show the last n lines of a file. Useful for log files because the recent entries are at the bottom. Example: `tail -100 ~/Claudette/claudette_server.log` shows the last 100 lines.

**`tail -f <filename>`** — follow a file as it grows. Shows lines as they're written. Press Ctrl+C to stop following. Useful for watching a log live during testing.

---

## Inspecting Claudette's logs (common patterns)

The two log files: `~/Claudette/claudette_server.log` for normal output, `~/Claudette/claudette_server_error.log` for errors.

**See recent activity:**
```
tail -100 ~/Claudette/claudette_server.log
```

**Check for crashes or errors:**
```
tail -100 ~/Claudette/claudette_server_error.log
```

**Watch live during a session or test:**
```
tail -f ~/Claudette/claudette_server.log
```

Open this in one Terminal window, then use Claudette in the browser. The log lines appear as activity happens. Press Ctrl+C to stop watching.

**Find specific activity (e.g., memory writer):**
```
grep "memory_writer" ~/Claudette/claudette_server.log
```

**Find recent specific activity:**
```
tail -1000 ~/Claudette/claudette_server.log | grep "memory_writer"
```

Last 1000 lines, filtered for memory writer mentions.

**Check log file size:**
```
ls -lh ~/Claudette/claudette_server.log
```

The `-h` makes the size human-readable (KB, MB, GB) rather than raw bytes.

**Find genuine errors in the error log:**
```
grep -A 10 "Traceback" ~/Claudette/claudette_server_error.log
```

The `-A 10` means "show 10 lines after each match" — useful because tracebacks are multi-line and you want to see the whole stack, not just the first line. Needed because Flask routinely writes normal request logs to stderr alongside actual errors, so you can't just `cat` the error log and expect to see only errors.

---

## Memory mirror — keeping a local backup of Claudette-memory

Claudette-memory is a private GitHub repository — her actual memory files. To protect against the unlikely-but-possible loss of GitHub access (account compromised, repository deletion accident, GitHub itself going down hard), a local mirror of the repo lives at `~/Claudette-memory-mirror/`.

The mirror is read-only in practice. Claudette doesn't read from it — she reads from GitHub via retrieval.py. Don't edit files in the mirror directly. If you need to edit memory directly, edit on GitHub via the web UI as usual, then refresh the mirror.

**Refresh the mirror:**

```
cd ~/Claudette-memory-mirror && git pull
```

Run this whenever you remember — weekly is fine, monthly is acceptable. Output will be `Already up to date.` if there's nothing new, or a list of `Updating X..Y` with files changed since last pull.

If you've been using Claudette daily, expect the pull to bring down several files each time. The first few weeks of running this you might want to do it more often just to confirm it does what you expect.

**If you ever need to restore from the mirror after a GitHub loss:** the path is roughly to create a new private repo on GitHub with the same name, then push the entire mirror history to it:

```
cd ~/Claudette-memory-mirror
git remote set-url origin [new repo URL]
git push -u origin main
```

That uploads the full history to the new repo. Claudette is back. Detail of this lives in `cold_start.md`.

## Searching

**`grep <pattern> <filename>`** — find lines matching a pattern. Most common use: finding specific entries in log files.
- `grep "memory_writer" claudette_server.log` — find lines mentioning the memory writer
- `grep -i "claudette"` — case-insensitive (matches "Claudette" and "claudette")
- `grep -n "pattern" file` — show line numbers
- `grep -v "pattern" file` — invert; show lines NOT matching the pattern

You can also pipe other commands' output into grep:
- `ps aux | grep server.py` — list all processes, then filter for ones mentioning server.py

The pipe (`|`) sends one command's output as input to the next. Common pattern.

**`which <command>`** — find where a program is installed. `which gh` tells you the path to the gh binary, or nothing if it's not installed. Used for confirming whether something is available before trying to use it.

---

## Files and folders — moving, creating, deleting

**`mkdir <name>`** — make a new folder. `mkdir docs` creates a folder called `docs` in the current directory. The `-p` flag means "don't error if it already exists, and create parent folders as needed if any are missing": `mkdir -p docs/briefs`.

**`mv <source> <destination>`** — move or rename. `mv old.txt new.txt` renames a file. `mv old.txt subfolder/` moves it into a folder. Used during the git setup to move downloaded files from `~/Downloads` into `~/Claudette`.

**`cp <source> <destination>`** — copy. Same shape as `mv` but the original stays put. Use when you want a duplicate rather than a relocation.

**`rm <filename>`** — remove a file. **Permanent** — there's no Trash equivalent. Be careful. `rm -r foldername` removes a folder and everything in it. `rm -rf` skips even the safety prompts. Power tool; treat carefully.

---

## Processes — what's running

**`ps aux`** — list every process running on the Mac. Almost always piped into grep to filter, e.g., `ps aux | grep server.py` to find Claudette's server.

The output columns: user, process ID, CPU%, memory%, then various state info, then the command that started the process. The PID (process ID) is the number you'd use to interact with that specific process.

**`lsof -i :<port>`** — list anything using a specific network port. `lsof -i :5001` shows what's on port 5001 (Claudette's server). Useful when checking whether a port is free before starting a server, or finding out what's holding a port.

**`kill <pid>`** — politely ask a process to stop. The process can clean up before exiting. If it ignores the request: `kill -9 <pid>` is the harder version that terminates immediately without a chance to clean up. Use the polite version first.

---

## launchctl — managing background services on macOS

**`launchctl list`** — list everything launchctl is managing. Almost always piped into grep: `launchctl list | grep -i claudette` to find Claudette specifically. The output shows PID, last exit status, and label.

**`launchctl list <label>`** — show details for one specific service. Example: `launchctl list com.claudette.server`. Returns a block of configuration including the program path and arguments.

**`launchctl kickstart -k gui/$(id -u)/<label>`** — restart a service. The `-k` flag means "kill it first if running." The `gui/$(id -u)/` part identifies your graphical user session. Used when you've changed a config or code file and want the service to pick up the change.

**`launchctl bootout gui/$(id -u) <plist-path>`** — fully unload a service. Stops it and prevents it from being restarted automatically. Used when you want to test something without launchctl interfering. Reverse with `bootstrap` (same shape) to load it back.

---

## Python — running scripts

**`python3 <script.py>`** — run a Python script. The `3` matters because some Macs have both Python 2 and Python 3; `python3` ensures you get the modern one. For Claudette work, always use `python3`.

**`python3 <script.py> --flag value`** — most Claudette scripts accept flags. Examples used in memory writer manual runs:
- `python3 memory_writer.py --transcript transcripts/2026-04-29.txt --date 2026-04-29 --retry`
- `python3 memory_writer.py --transcript ... --start-position 157683 --date ...`

The flags are read by the script itself; what flags exist depends on the script. The script's own documentation tells you which flags it accepts.

---

## Timing things

**`time <command>`** — measure how long a command takes. `time python3 memory_writer.py --transcript ...` runs the script normally, then prints three lines at the end:
- `real` — wall-clock time from start to finish (this is the one you usually care about)
- `user` — CPU time spent in the program itself
- `sys` — CPU time spent in system calls

Used during the memory writer diagnosis to measure how long manual runs actually take.

---

## Network and system info

**`whoami`** — print your username. Useful occasionally when commands need it.

**`id -u`** — print your numeric user ID. Used by launchctl commands as `$(id -u)`. The `$()` syntax means "run this command and substitute its output here," so launchctl gets your actual user ID number rather than the literal text.

**`hostname`** — print the computer's network name. Rarely needed but good to know.

---

## Redirection and pipes — combining commands

**`>`** — redirect output to a file, replacing it. `cat .gitignore > backup.txt` writes the contents of .gitignore into backup.txt (creates if missing, overwrites if existing).

**`>>`** — redirect output to a file, appending. Same as `>` but adds to the end rather than overwriting.

**`<<`** — heredoc. Used to include multi-line input directly in a command. We used this when creating .gitignore: `cat > .gitignore << 'EOF' [contents] EOF` reads everything between the EOF markers as the input.

**`|`** — pipe. Sends one command's output as input to the next. `ps aux | grep server.py` runs `ps aux` and pipes its output into `grep server.py`, which filters it.

---

## Stopping and restarting things in Terminal

**Ctrl+C** — cancel the currently-running command. Sends an interrupt signal. Most programs respond by stopping cleanly. Use when something is hanging or you started something by mistake.

**Ctrl+D** — end of input. Mostly useful in interactive prompts (Python's REPL, for example). Tells the program "I'm done sending input."

**Cmd+K (in Terminal.app)** — clear the visible window. Doesn't stop anything; just gives you a clean slate visually. The history is still there if you scroll up.

---

## Editing — quick edits inside Terminal

**`nano <filename>`** — opens a simple text editor inside Terminal. To save: Ctrl+O, then Enter to confirm. To exit: Ctrl+X. Useful for quick edits to small config files. Examples: `nano .env` to update an API key, `nano server.py` to change a single value.

For real code editing, use a proper editor outside Terminal. nano is for small edits in place.

---

## When something looks weird

**`pwd`** first. Confirm where you are.

**`ls -la`** second. See what's actually in the current folder, including hidden files.

**`echo $PATH`** if a command isn't found. `$PATH` is the list of folders the shell searches for commands. If something isn't in any of those folders, the shell can't find it.

Don't experiment by running new commands hoping they fix the situation. Pause, observe, ask.
