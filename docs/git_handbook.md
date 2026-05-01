# Git Handbook for Claudette

A practical reference for the workflows you actually use. Not a comprehensive git tutorial — just the things you need to do, when, and what command does it.

---

## The mental model

Three places exist:
- **GitHub** — the canonical, backed-up version of every file. The "last known good" copy lives here.
- **Your Claudette folder on the Mac** (`~/Claudette`) — your working copy. This is what's actually running.
- **Git's internal history** — every previous version of every file, available instantly with one command.

The deployed code lives in `~/Claudette` and runs from there. GitHub is the backup and the version history. Git inside `~/Claudette` is the bridge between the two.

---

## Workflow 1 — A TC changed a file, you need to test and ship it

This is the most common workflow.

### Step 1. Make sure your folder is clean before you start

Before bringing a new file in, check what state things are in:

```
cd ~/Claudette
git status
```

You want to see `nothing to commit, working tree clean`. That means the folder matches the last commit — there are no half-finished changes hanging around. If you see files listed as "modified" that you don't recognise, stop and figure out why before continuing. Don't pile new changes on top of mystery changes.

### Step 2. Drop the new file in

The TC has produced (say) a new `server.py`. Download it from the Claude conversation. Move it into `~/Claudette`, replacing the existing file:

```
mv ~/Downloads/server.py ~/Claudette/
```

(That's if your downloads land in `~/Downloads`. Adjust if yours is elsewhere.)

### Step 3. Test it

However you test things — restart Claudette, have a session, watch the logs. Do whatever check confirms the new version works. Take your time.

### Step 4a. If it works — commit and push

Three commands, with the message changed to describe what actually changed:

```
git add server.py
git commit -m "TC9-001: fix memory writer timeout"
git push
```

Reading what each line does:
- `git add server.py` — stage *just this file* for the next commit. (If the TC changed multiple files, list them all: `git add server.py memory_writer.py`.)
- `git commit -m "..."` — capture the staged changes as a new commit. The message should describe what changed and ideally include a TC reference.
- `git push` — send the commit to GitHub.

That's it. The new version is now on GitHub, and `~/Claudette` and GitHub agree.

### Step 4b. If it doesn't work — roll back

This is the moment git earns its keep. One command:

```
git checkout server.py
```

That tells git: "discard my current changes to server.py and restore the last committed version." The broken file vanishes. The previous working version is back. Takes one second.

If you want to confirm, run `git status` afterwards — you should see `nothing to commit, working tree clean` again. The folder is back to where it was before you tried the new file.

The broken file doesn't haunt the history because you never committed it. As far as git is concerned, it never existed.

---

## Workflow 2 — You're adding a new file (like the architecture map)

Same shape, but with a slightly different first command because there's no existing file to track.

```
cd ~/Claudette
git add docs/architecture_map.svg
git commit -m "Add architecture map orientation diagram"
git push
```

The `git add` works the same way — you tell git to start tracking the new file. Everything else is identical.

If you're adding a whole folder at once (like when you first created `docs/`):

```
git add docs/
```

That stages everything inside the folder.

---

## Workflow 3 — Multiple files in one TC session

If the TC produced new versions of three files — say `server.py`, `memory_writer.py`, and the HTML — and you've tested all three together as a set, commit them together:

```
git add server.py memory_writer.py claudette_interface_connected.html
git commit -m "TC9-001: fix memory writer timeout, update banner styling"
git push
```

All three files become one commit. If you ever need to roll back this change, you roll back all three together — which is what you want, because they're a coordinated set.

---

## Workflow 4 — You committed something and now want to undo it

You committed a change that seemed fine in testing but turns out to break something an hour later. The bad change is already on GitHub. What now?

Two options.

**Option A — go back to the previous version of just one file.**

If only one file is causing the problem and you want to restore the version before this commit:

```
git log --oneline server.py
```

This shows the commit history for that one file. You'll see something like:

```
05832f3 TC9-001: fix memory writer timeout
e7de8a1 Initial commit
```

The newest commit is on top. The one you want is the second one (the version before the broken commit). Copy its short ID — `e7de8a1` in this example.

```
git checkout e7de8a1 -- server.py
```

Reading it: `checkout` is the command, `e7de8a1` is which commit to take from, `--` is git's way of saying "what follows is a filename," and `server.py` is the file. Result: server.py is now the version from the older commit.

Then commit and push the rollback:

```
git add server.py
git commit -m "Roll back server.py to pre-TC9-001 (timeout broke X)"
git push
```

Now GitHub has three commits: the original, the broken change, and the rollback. The history is intact — you can see exactly what happened and when.

**Option B — undo the entire last commit.**

If multiple files were changed and you want to undo the whole last commit:

```
git reset --hard HEAD~1
```

This is a heavier tool. `HEAD~1` means "the commit before the current one" and `--hard` means "actually change my files to match." After this, your folder looks exactly like it did before the broken commit, and the broken commit is *gone* from your local history.

But — and this is important — **don't do this if you've already pushed**. If the broken commit is already on GitHub, this command makes your local history disagree with GitHub, and the next push will fail with a confusing error. For that situation, use Option A above.

---

## Daily check command

If you ever lose track of where things are, this command is your friend:

```
git status
```

Run it whenever you're not sure what state the folder is in. It tells you:
- Whether you have uncommitted changes
- Whether you have unpushed commits
- Whether there are untracked files

A clean working tree, fully synced with GitHub, looks like:

```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

This is the calm state. Aim to leave the folder this way at the end of each session.

---

## Looking at history

When you want to see what's changed and when:

```
git log --oneline
```

Shows every commit, one per line, with its short ID and message. Good for "when did we add the architecture map?" type questions.

```
git log --oneline server.py
```

Same, but only commits that touched `server.py`. Good for "when did the timeout change?" type questions.

Press `q` to exit if it opens a pager.

---

## What you should never do

A small list of things that cause real damage:

**Don't commit the .env file.** It's in `.gitignore` so it shouldn't happen automatically, but never use `git add .env` to force it. API keys on GitHub is a bad day, even on a public repo.

**Don't run `git push --force`.** This rewrites GitHub's history. There's almost never a reason to do this in your workflow. If a Claude instance ever suggests it, stop and check — it's the kind of command that can lose work.

**Don't edit files inside the `.git` folder.** You won't see this folder in Finder by default (it's hidden), but if you ever do — leave it alone. That's git's internal storage.

---

## When things look weird

If you run a command and the output confuses you, before doing anything else:

```
git status
```

Read what it says carefully. Most weird situations resolve when you can see clearly what state you're in. Then ask Claude what to do — paste back the full output of `git status` plus what you were trying to do.

Don't run additional commands hoping they'll fix it. Some git commands compound problems if used in the wrong state. Pause, observe, ask.
