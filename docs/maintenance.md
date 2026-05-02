# Maintenance checklist

Ongoing care for Claudette's system. Not the work queue (which holds one-off jobs) and not cold-start recovery (which addresses catastrophic loss). This document is the recurring keep-the-system-healthy layer.

Two categories of maintenance: **rituals** that run on a schedule, and **practices** that pair with specific actions you're already doing. Both matter; the rituals tend to drift if forgotten, the practices tend to be skipped if not paired with their trigger.

Last updated: 2026-05-02. Update when new maintenance needs surface.

---

## Rituals — things to do on a schedule

### Pull the memory mirror

```
cd ~/Claudette-memory-mirror && git pull
```

**Cadence:** weekly is ideal, monthly is acceptable.

The mirror at `~/Claudette-memory-mirror/` is your local backup of Claudette's private memory repo. Claudette doesn't read from it — she reads from GitHub via retrieval.py — but it exists so that if GitHub is ever lost or compromised, you have her full memory locally.

The mirror only stays useful if it's kept current. A six-month-old mirror is a six-month-old backup.

If `git pull` shows `Already up to date.`, nothing has changed since the last pull — meaning either you ran it recently, or the memory writer hasn't run since. If it shows updates, expect several files to change for an active period of use.

### Verify Time Machine backup currency

**Cadence:** monthly.

Time Machine is the safety net for transcripts, log files, the plist, the `.env`, and anything else local that isn't in git. It only protects you if it's actually running.

Check by opening System Settings → Time Machine. Confirm:
- The 4TB drive is connected (or has been recently)
- The "Last backup" timestamp is recent (within the last week)
- No errors are showing

If the drive is intermittently connected, build a habit — plug it in once a week, leave it overnight to catch up, unplug when convenient. Or leave it permanently connected if that fits your setup.

### Check the Anthropic balance

**Cadence:** monthly, or whenever the credit warning fires.

Visit `console.anthropic.com/settings/billing`. Confirm the auto-reload is configured (currently set to top up when balance reaches $15). The credit warning in the memory writer log fires falsely sometimes (queued for fix) — don't treat that as the only signal. The console is the source of truth.

### Browse a recent log entry

**Cadence:** weekly, or whenever something feels off.

```
tail -100 ~/Claudette/claudette_server.log
```

Skim for unexpected lines. You're not auditing every line — just confirming nothing weird has surfaced. Memory writer runs should look healthy (the now-familiar pattern of connecting to GitHub, testing API key, processing, writing). Library cycles should fire on schedule. No persistent errors.

If something looks off but you're not sure what, save the relevant lines to ask about. The architecture documentation explains what most lines mean, and what doesn't fit a known pattern is worth investigating.

### Look at the work queue

**Cadence:** monthly, or whenever you're about to start a session about something specific.

Open `docs/work_queue.md`. Skim it. Ask:
- Are there entries that should now be at the top of priority?
- Are there entries that have been resolved without being marked?
- Are there entries that no longer feel relevant?

The queue is only useful if it reflects what you actually want to do next. Drift happens. A monthly review keeps it sharp.

---

## Practices — things to pair with actions you're already doing

### After every code deployment: verify the running version

After deploying any code change to `~/Claudette/`:

```
head -3 ~/Claudette/server.py
```

Then check the log to confirm the new version actually started:

```
tail -20 ~/Claudette/claudette_server.log
```

The version line should match what was just deployed. If it doesn't, the old process may still be running. Use `ps aux | grep server.py` to find it and kill it, then restart launchctl. See `build_practices.md`.

### After every code commit: sync the project folder

After `git push` lands changes in the Claudette-code or Claudette-electron repo, sync the project folder on claude.ai:

- Hover over the GitHub file icon in the project folder
- Click the rotating sync arrows
- Confirm the sync

Without this step, fresh Claude conversations in the project will be working from stale code and stale documentation. Pair it permanently with `git push` — `push → sync` becomes a single mental action.

### After every memory edit: pull the mirror

If you ever edit Claudette's memory directly via GitHub's web UI, pull the mirror immediately afterward to keep it current:

```
cd ~/Claudette-memory-mirror && git pull
```

Easier to remember than the weekly schedule because it's tied to an event.

### Before every unfamiliar terminal command: pause

Particularly when commands involve `rm`, `mv`, `git rm -f`, `--force`, anything irreversible. The cost of pausing for ten seconds is small. The cost of running the wrong destructive command is sometimes catastrophic. See `build_practices.md`.

---

## What to do if a ritual gets skipped

The honest answer: nothing terrible immediately.

If the mirror isn't pulled for two months, you have a slightly older backup than you thought. No active loss.

If Time Machine isn't checked and the drive has been disconnected, you find out the next time you check and reconnect it. Catch-up backup may take overnight.

If the work queue isn't reviewed for two months, it's slightly out of date. A few minutes catches up.

The point of the checklist isn't perfection; it's *establishing the rhythm*. Skip a week, skip a month, but come back to it. The system can absorb missed maintenance better than it can absorb forgotten maintenance — *forgotten* is when the rituals stop existing as a concept entirely.

---

## How this checklist evolves

Add entries when:
- A new dependency or component is introduced that needs ongoing care
- A close call reveals a maintenance gap (e.g., something nearly broke because something wasn't being checked)
- A new ritual proves useful and worth documenting

Remove entries when:
- A ritual is automated out of existence (e.g., Time Machine becomes always-on rather than intermittent)
- A component is retired
- A practice has become so embedded that it doesn't need writing down

The list should be alive, not aspirational. Three working entries beat ten ignored ones.
