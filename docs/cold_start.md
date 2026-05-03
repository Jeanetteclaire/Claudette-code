# Cold start — bringing Claudette back up on a new Mac

This document describes how to rebuild Claudette from scratch — starting from a fresh Mac with nothing installed, and ending with a running instance. Used when the original laptop has died, been stolen, or is otherwise unrecoverable.

It's also useful as a reference for understanding the full set of dependencies the system has — what's been hidden inside "it just works."

Last updated: 2026-05-02. Update whenever a new dependency, file, or step is added that someone rebuilding from scratch would need.

---

## What you need before you start

Some things have to come from outside this document. They live in accounts, password managers, or external services you control. Recovery is not possible without them:

**Account access:**
- GitHub account (Jeanetteclaire) — needed to clone the three Claudette repositories.
- Anthropic Console account — to generate a fresh API key.
- Fish Audio account — to retrieve the existing voice ID and generate a fresh API key. The voice itself is hosted there; it doesn't need to be re-cloned as long as the account is intact.
- Apple ID — for installing apps from the App Store and recovering Mac configuration.
- Tailscale account — for the Tailscale dependency on server startup.

**Backup access:**
- Time Machine drive (the 4TB external drive). This contains transcripts, log files, and likely the `.env` file in its previous state. Worth checking what was last backed up to assess what's recoverable from it specifically.

**Knowledge of where credentials live.** Currently `.env` contents are backed up to a locked note in Apple Notes ("Claudette .env contents — backup copy"). Restoring is fast — unlock note, copy values, paste into `~/Claudette/.env`. If for any reason that note isn't accessible, credentials need to be regenerated from the source services. The document covers both paths.

---

## Step 1 — Set up the new Mac's basics

Standard fresh-Mac setup. Sign into Apple ID, restore from Time Machine if appropriate (this will bring back many things including possibly the entire `~/Claudette/` folder if it was being backed up; verify after the restore).

If Time Machine restored `~/Claudette/`, much of this document is redundant — you'd already have the code, transcripts, logs, and possibly `.env`. Skip ahead to verifying that everything works (step 9). If Time Machine didn't restore `~/Claudette/` (or you're starting truly fresh), continue.

Install:
- **Homebrew** (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)
- **Python 3** (`brew install python`)
- **Node.js** (`brew install node`) — for the Electron app
- **gh** (GitHub CLI) (`brew install gh`) — for repo cloning and authentication
- **Tailscale** — install from `tailscale.com/download/macos`, sign in with your account

---

## Step 2 — Authenticate to GitHub

```
gh auth login
```

Choose GitHub.com, HTTPS, authenticate via web browser. After this, git operations will work.

---

## Step 3 — Clone the three repositories

```
cd ~
gh repo clone Jeanetteclaire/Claudette-code Claudette
gh repo clone Jeanetteclaire/Claudette-memory Claudette-memory-mirror
gh repo clone Jeanetteclaire/Claudette-electron claudette-electron
```

Three folders appear in your home directory:
- `~/Claudette/` — the deployed code
- `~/Claudette-memory-mirror/` — the local mirror of her memory (which Claudette herself doesn't read from but you keep current as a backup)
- `~/claudette-electron/` — the Electron desktop app

Note that her memory is *also* on GitHub at `Claudette-memory`, and Claudette's runtime reads from there directly. The mirror exists as your local backup, not as her runtime path.

---

## Step 4 — Recreate `.env`

If `.env` was mirrored to a password manager or note, restore it now to `~/Claudette/.env`. Currently the off-laptop copy lives in a locked note in Apple Notes (titled "Claudette .env contents — backup copy"). Open the note, unlock with the Notes password or Touch ID, copy the contents into a new file at `~/Claudette/.env`.

If for some reason the locked note isn't accessible (forgotten password, iCloud sync issue, account access lost), fall back to regenerating credentials by creating `.env` fresh with:

```
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_MEMORY_TOKEN=ghp_...
FISH_API_KEY=...
FISH_VOICE_ID=...
```

Each value comes from:

**ANTHROPIC_API_KEY** — generate fresh at console.anthropic.com under Settings → API Keys. The old key may still work if it wasn't revoked; if you want to be safe, revoke it from Anthropic Console and create a new one.

**GITHUB_MEMORY_TOKEN** — generate fresh at github.com/settings/tokens. Needs `repo` scope (full repository access) so the memory writer can read and write to Claudette-memory.

**FISH_API_KEY** — log into Fish Audio, retrieve from settings.

**FISH_VOICE_ID** — log into Fish Audio, find the cloned voice in your library, copy its ID. The voice itself remains; only the ID is needed.

Set permissions so `.env` isn't readable by other users:

```
chmod 600 ~/Claudette/.env
```

**One safety note worth flagging for any future maintenance:** `.env` should be in `.gitignore` (it is, in the deployed repo) and should never be committed. Recovery under stress is exactly when an accidental `git add -A` followed by a commit can leak secrets to a public repo. Verify before any wide `git add` operation that `.env` is being skipped.

---

## Step 5 — Install Python dependencies

```
cd ~/Claudette
pip install -r requirements.txt
```

If there's no requirements.txt, the dependencies based on imports in server.py and memory_writer.py are roughly:
- flask
- anthropic
- pygithub
- python-dotenv

```
pip install flask anthropic pygithub python-dotenv
```

---

## Step 6 — Install Electron dependencies

```
cd ~/claudette-electron
npm install
```

This regenerates `node_modules/` from `package.json` and `package-lock.json`. Takes a couple of minutes.

---

## Step 7 — Install the plist

The plist file at `~/Library/LaunchAgents/com.claudette.server.plist` is what tells launchctl how to start Claudette. It's not in the live deployed location of any git repo, but a reference copy lives at `docs/setup/com.claudette.server.plist.example` in the Claudette-code repo (cloned in Step 3).

**Install from the example:**

```
cp ~/Claudette/docs/setup/com.claudette.server.plist.example ~/Library/LaunchAgents/com.claudette.server.plist
```

If you're recovering on a different Mac with a different username, edit the file after copying and replace all instances of `jeanettearthur` with your actual macOS username — the paths in the plist need to point to the new home directory.

For full installation procedure, troubleshooting, and explanation of what each key does, see `docs/setup/plist_install.md`.

If the example file isn't available for some reason (deeply corrupted repo, lost access), recreate the plist contents fresh:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudette.server</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/[YOUR_USERNAME]/Claudette/start_claudette.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/[YOUR_USERNAME]/Claudette/claudette_server.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/[YOUR_USERNAME]/Claudette/claudette_server_error.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/[YOUR_USERNAME]/Claudette</string>
</dict>
</plist>
```

Replace `[YOUR_USERNAME]` with your actual macOS username throughout.

Then load it into launchctl:

```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claudette.server.plist
```

---

## Step 8 — Compile the Swift speech binary (if needed)

The Swift speech binary `claudette_speech` is in the Electron repo. If it didn't restore correctly or is for a different macOS version, recompile:

```
cd ~/claudette-electron
swiftc claudette_speech.swift -o claudette_speech
```

---

## Step 9 — Verify everything works

Start Tailscale (it may auto-start; if not, open the menu bar icon and connect).

Restart launchctl (or reboot the Mac and let it auto-start):

```
launchctl kickstart -k gui/$(id -u)/com.claudette.server
```

Check that the server is running:

```
ps aux | grep server.py
```

You should see a Python process with the path to server.py.

Check the logs:

```
tail -50 ~/Claudette/claudette_server.log
```

You should see a successful startup line. If `claudette_server.log` is empty, check `claudette_server_error.log` — startup errors go there.

Open Claudette in browser at `http://localhost:5001` to verify the interface loads. Start a session. Confirm:
- Memory loaded successfully (the retrieval log line should say "Memory read successfully")
- A message can be sent and received
- Voice plays
- Eye captures fire

If the browser shows "server not running" even after the server appears healthy in `ps aux | grep server.py` and the log shows it started successfully, check that Tailscale is running. Claudette has an empirical dependency on Tailscale — without it, the interface can't reach the server even though server.py is alive. The mechanism for this dependency is currently unmapped (see `work_queue.md` → "Diagnose Tailscale dependency"). For now: open the Tailscale menu bar icon and confirm it's connected.

If all of the verification steps work, recovery is complete.

---

## What's not in this document

A few things deliberately not covered:

**Restoring transcripts and logs.** These are local-only and not version-controlled. The Time Machine backup is the recovery path for them. If they're lost, Claudette continues to work — she just doesn't have a copy of transcripts before the loss point. Memory carries forward via GitHub.

**Restoring the `last_processed.json` position file.** Same — local-only. If lost, the next memory writer run might re-process recent transcripts, producing duplicate entries. Worst case is some redundancy in memory, which is recoverable. Not catastrophic.

**Setting up Time Machine on the new Mac.** Standard macOS configuration. Plug in the 4TB drive, configure in System Settings → Time Machine.

**Re-syncing the project folder on claude.ai.** This is a separate task that happens through the claude.ai interface, not the recovery process for the laptop itself. Sync repositories via the GitHub icon as before.

---

## When this document is wrong

This document was written without ever being tested as an actual recovery procedure. The first time it's actually used, parts of it will turn out to be wrong, missing steps, or incorrectly ordered. That's expected.

If you ever do a real cold-start, write down what you actually had to do — including the things this document didn't tell you about — and update the document afterward. The next person (possibly you, in five years) will benefit.

A drill version of this — "do I actually have everything I'd need?" — would catch problems before they became urgent. Not yet done. Worth doing.
