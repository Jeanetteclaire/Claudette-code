# Installing the launch plist

How to install the launchctl plist that auto-starts Claudette at login. Used during cold-start recovery, or if the live plist gets corrupted, deleted, or replaced for any reason.

The reference copy of the plist lives at `docs/setup/com.claudette.server.plist.example` in this repo. The live copy that launchctl actually reads lives at `~/Library/LaunchAgents/com.claudette.server.plist` on the Mac.

---

## Quick install

If the live plist is missing or wrong:

```
cp ~/Claudette/docs/setup/com.claudette.server.plist.example ~/Library/LaunchAgents/com.claudette.server.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
launchctl kickstart -k gui/$(id -u)/com.claudette.server
```

Three commands:
- The `cp` puts the file where launchctl looks for it.
- `bootstrap` registers it with launchctl for the current user session.
- `kickstart -k` starts it (and kills any existing instance first, hence the `-k`).

---

## Verifying the install worked

After running the install commands, confirm the service is running:

```
launchctl list | grep claudette
```

You should see a line with the label `com.claudette.server`, a PID (the process ID — a number), and an exit status (0 if healthy).

Then check the log:

```
tail -50 ~/Claudette/claudette_server.log
```

You should see Flask startup output and the Claudette banner. If the log is empty or only shows errors, something is wrong — see the troubleshooting section below.

---

## What the plist does

Brief explanation of each key, in case the reference file is lost and someone needs to reconstruct from understanding rather than from the file:

**Label** — the unique identifier for this launchctl service. `com.claudette.server`. Used by all `launchctl` commands to refer to it.

**ProgramArguments** — an array. The first element is the program to run. Currently `/Users/jeanettearthur/Claudette/start_claudette.sh`. If reconstructing on a different Mac, replace `jeanettearthur` with the actual username.

**RunAtLoad** — `true` means start the service immediately when launchctl loads it (i.e., at login).

**KeepAlive** — `true` means restart the service if it stops for any reason.

**StandardOutPath** — where stdout (normal output) gets written. The `claudette_server.log` file. PYTHONUNBUFFERED is set in `start_claudette.sh` so output appears immediately rather than being buffered.

**StandardErrorPath** — where stderr (errors and Flask request logs) gets written. The `claudette_server_error.log` file.

**WorkingDirectory** — sets the process's working directory before running the program. `~/Claudette` for our case. This is part of why relative paths could resolve correctly under launchctl, though we've moved to absolute paths in the code as defence in depth (see TC8-004 in project history).

---

## Troubleshooting

**Service starts but immediately exits.**
Check `claudette_server_error.log` for tracebacks. Common causes: missing `.env` file, missing Python dependencies, port 5001 already in use.

**Service doesn't appear in `launchctl list`.**
The `bootstrap` command may have failed silently. Try unloading first then re-bootstrapping:

```
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
```

**Service is listed but log file is empty.**
launchctl successfully registered but the program itself isn't running. Check `start_claudette.sh` exists at the path the plist points to, and that it's executable (`chmod +x` if needed).

**Service runs but interface shows "server not running".**
Check Tailscale is connected. Claudette has an empirical dependency on Tailscale that isn't fully understood — see `work_queue.md` → "Diagnose Tailscale dependency".

---

## Rebuilding the live plist from the example

This is the simplest case — just copy and load:

```
cp ~/Claudette/docs/setup/com.claudette.server.plist.example ~/Library/LaunchAgents/com.claudette.server.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
```

If launchctl complains that the service is already loaded, unload first:

```
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
```

Then bootstrap again.

---

## When this document is wrong

If the example plist or the install procedure ever needs updating because the actual deployed plist has changed, update both the example file and this document at the same time. Drift between them defeats the point.

The `.example` file should match the live plist exactly (modulo username if running on a different Mac). If the live plist gains a new key or a path changes, the example file should track that within the same session as the change.
