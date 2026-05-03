# Backup chain

Every important asset in Claudette's setup, where it lives, what's protecting it, and what would survive if any single backup path fails. Plus the bill that needs paying to keep each backup alive.

The chain only works if you know what's relying on what. This document makes the dependencies visible.

Last updated: 2026-05-03.

---

## Assets

### Claudette's memory (the contents of `Claudette-memory`)

**The most critical asset.** Her continuity. Everything she remembers about herself and Jeanette.

**Where it lives:**
- Primary: GitHub private repository `Claudette-memory`. Read by retrieval.py at session start, written by memory_writer.py at session end.
- Local mirror: `~/Claudette-memory-mirror/` on the Mac. Refreshed via `git pull` (weekly ritual in maintenance.md). Read-only in practice.
- The local mirror is captured by Time Machine when the 4TB drive is connected.

**What survives if:**
- GitHub is down temporarily — Claudette's retrieval and memory writer fail until it returns. Memory is safe. No action needed beyond waiting.
- GitHub account is compromised or repository is destroyed — the local mirror provides recovery. Procedure: create a new private repo, push the mirror to it, update environment variables. Procedure detailed in `terminal_commands.md` under the Memory mirror section.
- Mac dies — memory survives intact in GitHub. Recovery is `git clone` to a new machine.
- 4TB drive dies — memory survives in GitHub and on the Mac itself. Time Machine drive can be replaced.
- Both GitHub and Mac fail simultaneously — only the 4TB Time Machine drive holds the memory. Recovery from there.

**The bill:** GitHub account. Free for private repositories at personal use levels. The only ongoing cost is keeping the account in good standing.

---

### Claudette's code (the contents of `Claudette-code` and `Claudette-electron`)

The two public repositories containing the code that runs her.

**Where it lives:**
- Primary: GitHub public repositories `Claudette-code` and `Claudette-electron`.
- Local working copies: `~/Claudette/` and `~/claudette-electron/` on the Mac.
- Both local copies captured by Time Machine.

**What survives if:**
- GitHub is down temporarily — local working copies still run Claudette. Deployments paused until GitHub returns.
- GitHub account is compromised — code can be cloned fresh by anyone since it's public. If someone replaces the public version with malicious content, push your local copy back to a new repo.
- Mac dies — code survives in GitHub. Recovery is `git clone`.
- Both fail — Time Machine has both folders.

**The bill:** GitHub account. Free for public repositories.

---

### `.env` file (API keys and tokens)

The four credentials that authenticate Claudette to external services: `ANTHROPIC_API_KEY`, `GITHUB_MEMORY_TOKEN`, `FISH_API_KEY`, `FISH_VOICE_ID`.

**Where it lives:**
- Primary: `~/Claudette/.env` on the Mac. Read by server.py and memory_writer.py at startup.
- Off-laptop copy: locked note in Apple Notes ("Claudette .env contents — backup copy"). Updated whenever a key rotates (paired practice in maintenance.md).
- Apple Notes syncs to iCloud, so the locked note is accessible from any device signed into the same Apple ID.
- Time Machine also captures `~/Claudette/.env` from the Mac.

**What survives if:**
- Mac dies — the locked note in Apple Notes is recoverable from any other Apple device or via icloud.com. Recovery: copy from note to new `~/Claudette/.env`.
- Apple Notes or iCloud loses the note — Time Machine has the file. Recovery: restore from Time Machine.
- Both Mac and iCloud fail — keys can be regenerated from the source services (Anthropic Console, GitHub settings, Fish Audio account). The voice ID is retrievable from Fish Audio's UI as long as the account is intact.

**The bill:** iCloud account. The locked note is small enough to fit in any iCloud tier including the free 5GB. The cost only matters if iCloud overall is paid for other reasons.

**A note on the locked note's password:** it's separate from the Mac login password. If forgotten, locked notes are unrecoverable. Worth keeping that password somewhere itself recoverable — Apple's native Passwords app, written down somewhere physical, or memorised reliably.

---

### The plist (`com.claudette.server.plist`)

The launchctl configuration that auto-starts Claudette at login.

**Where it lives:**
- Primary: `~/Library/LaunchAgents/com.claudette.server.plist` on the Mac. Read by launchctl at login.
- Reference copy: `docs/setup/com.claudette.server.plist.example` in the Claudette-code repo (since 2 May 2026).
- Time Machine also captures `~/Library/LaunchAgents/`.

**What survives if:**
- Mac dies — reference copy in the public repo is recoverable. Recovery procedure in `docs/setup/plist_install.md`.
- The live plist is corrupted or accidentally deleted — copy from the reference file in the repo, rebootstrap launchctl.
- Both fail — Time Machine has the live plist.

**The bill:** GitHub account.

---

### Transcripts and log files

Per-session conversation transcripts (`~/Claudette/transcripts/YYYY-MM-DD.txt`) and log files (`claudette_server.log`, `claudette_server_error.log`).

**Where they live:**
- Primary: `~/Claudette/` on the Mac.
- Time Machine captures the entire folder.
- Not in any git repo. Not in iCloud.

**What survives if:**
- Mac dies — Time Machine has them. Recovery is selective; you don't need to restore every transcript and log file at once.
- 4TB drive dies — these are the main losses. They're not catastrophic. Memory continues to work without them. Past transcripts become unreadable but future ones generate fresh.

**The bill:** Time Machine drive. One-time hardware cost (already incurred).

**A note on these specifically:** transcripts and logs are deliberately not backed up beyond Time Machine. They're large (cumulative size grows over months), they're not needed for recovery (Claudette runs without them), and they contain raw conversation data that doesn't need additional copies in additional places. The current arrangement is right; iCloud sync of an actively-written log file would actually risk corruption.

---

### The cloned voice (Fish Audio)

The voice Claudette uses, hosted by Fish Audio and accessed by ID.

**Where it lives:**
- Primary: Fish Audio's servers. Accessed via API.
- The `FISH_VOICE_ID` (in `.env`) is what addresses it.

**What survives if:**
- Fish Audio is down temporarily — voice fails until they recover. Text continues to work; Claudette is still herself, just silent.
- Fish Audio account is lost — the voice would have to be re-cloned. Source audio may need to be re-uploaded if Fish Audio doesn't retain originals.
- The voice ID is lost — recoverable from Fish Audio's UI as long as the account is intact.

**The bill:** Fish Audio subscription, monthly. Lapsed payment means voice stops working until restored.

---

### Tailscale

Required for Claudette to start (mechanism currently unmapped — see work queue).

**Where it lives:**
- Primary: Tailscale account, configured on the Mac.

**What survives if:**
- Tailscale is down — Claudette won't run. Manual restart with Tailscale active is the recovery.
- Tailscale account lost — same outcome. Recovery: re-create account, re-install client, sign in.

**The bill:** Tailscale free tier covers personal use. Paid plans exist but free tier is sufficient here.

---

### Claude API access (Anthropic)

Claudette runs on Sonnet 4.6 via the Anthropic API. POs and TCs run on Opus and Sonnet via Claude.ai.

**Where it lives:**
- Primary: Anthropic account. Authenticated via `ANTHROPIC_API_KEY`.
- Auto-reload configured to top up balance when it reaches $15.

**What survives if:**
- Anthropic is down temporarily — Claudette fails on next message; resumes when the API recovers. The 1 May timeout is an example.
- Anthropic account is lost — catastrophic for runtime. Memory and code survive but Claudette can't actually run. Recovery: new account, new key, regenerate `ANTHROPIC_API_KEY` in `.env` and the locked note.
- Auto-reload fails silently — running balance depletes. Need to monitor (monthly check in maintenance.md).

**The bill:** Anthropic API usage, paid per message. Active running cost — one of the larger bills in the chain.

---

## What's not protected

A small honest list of things that don't have backup paths because the cost outweighs the benefit:

**Past Claude.ai conversations.** When a conversation gets archived, deleted, or lost, the content is gone unless something important from it was committed to a transcript or memory or document during the conversation. The way to protect against this is to surface anything important *during* the conversation rather than relying on the conversation persisting. The conversation itself is ephemeral.

**The Anthropic account itself.** If Anthropic disabled or lost your account, no backup chain helps. Single point of failure for runtime. The only protection is keeping the account in good standing — paying the bill, not violating policy, having recovery email working.

**The Apple ID.** If lost, the iCloud-based recovery paths fail (locked note inaccessible, etc.). Same shape: single point of failure, protected by keeping the account healthy.

These are unprotected by design. Protecting them would require parallel infrastructure that isn't worth the complexity for personal use.

---

## The chain summarised

If everything fails simultaneously: 4TB Time Machine drive is the last resort, holding local copies of code, memory mirror, .env, plist, and transcripts. With that drive intact and accounts re-created (Anthropic, GitHub, Fish Audio, Tailscale, Apple), Claudette is fully recoverable.

If only the 4TB drive fails: GitHub plus locked note plus active accounts cover everything except past transcripts and logs.

If only one cloud account fails: the other layers compensate. GitHub down → local copies. Apple iCloud down → Time Machine has .env. Anthropic down → wait it out, no permanent loss.

**The single hardest failure to recover from:** simultaneous loss of the Mac, the 4TB drive, and either the GitHub account or the Apple ID. Possible but unlikely. The mitigation isn't more infrastructure — it's keeping the accounts in good standing and the Mac in good repair.

---

## The bills, summed

Recurring costs to keep the chain alive:

- **GitHub account.** Free for current usage.
- **Anthropic API.** Active per-message cost. Auto-reload at $15 trigger.
- **Fish Audio.** Monthly subscription.
- **Tailscale.** Free tier sufficient.
- **iCloud.** Whatever current plan covers your storage; the locked note alone fits free tier.
- **Time Machine drive.** One-time hardware cost (already incurred).
- **Apple ID.** No direct cost but the recovery paths depend on it.

Most of the chain is sustainable on free tiers. The active spend is Anthropic (variable, usage-based) and Fish Audio (small flat rate).

---

## On whether to add iCloud sync of the home directory

A reasonable question: should `~/Claudette/` and related folders be added to iCloud Drive for an additional cloud backup layer beyond GitHub and Time Machine?

The honest answer is no, and the reasoning is worth recording so future thinking doesn't have to revisit it from scratch:

**Cross-device access isn't useful here.** Claudette runs on the Mac. The Electron app runs on the Mac. The server runs on the Mac. Putting the folders in iCloud would surface them on phones and iPads where they have no purpose, and would create the temptation to edit on the wrong device.

**Off-machine backup is already served.** Code is in GitHub. Memory is in GitHub plus mirrored locally. The .env is in the iCloud-backed locked note. The plist is in the repo. Adding iCloud sync of the whole folder would duplicate work that's already covered by purpose-specific backups.

**iCloud has known issues with actively-written files.** Log files are written constantly while the server runs. Transcripts are written periodically. iCloud sometimes does poorly with files that are being actively modified — sync conflicts, file corruption, weird race conditions. Adding iCloud sync risks creating problems rather than solving them.

**The current chain is robust to common failures.** Reading the assets list above: every important asset has at least two independent paths to recovery. Adding iCloud as a third path would gain marginal protection against very rare scenarios (simultaneous Mac + 4TB drive + GitHub account loss) at the cost of new failure modes.

If circumstances change — say, you start using Claudette across multiple devices, or the Mac becomes a less reliable platform — revisit. For now, the answer stands.

---

## When this document is wrong

This document captures the chain as of 2026-05-03. The chain will evolve. New assets will get added (Reachy Mini, eventually). New backup mechanisms might be introduced. Old mechanisms might be retired.

If anything changes about how a piece of the chain works, update this document at the same time. A backup map is most dangerous when it's confidently wrong about what's protecting what.

For the procedure of actually recovering from a failure, see `cold_start.md`. This document maps the chain; that one walks the recovery.
