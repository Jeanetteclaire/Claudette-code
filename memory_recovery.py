"""
memory_recovery.py
------------------
One-shot recovery script for the experience file overwrite bug in memory_writer.py.

Background:
    write_memory_updates() writes experience files (memory/experiences/sessions/YYYY-MM-DD.md)
    with no read-merge-append step. On multi-session days, each writer run overwrites the file
    entirely, so only the last session's content survives in the current file. Earlier sessions
    are preserved in git commit history but not in the file itself.

What this script does:
    For each affected experience file, fetches every commit that touched it in chronological
    order, retrieves the file content at each commit, concatenates them with session markers,
    and writes the result back as a single new commit.

Scope:
    22 affected files: 2026-04-16 through 2026-05-11 (see AFFECTED_FILES below).
    2026-05-12 is explicitly excluded — manually recovered by Jeanette on 12 May 2026.

Usage:
    Dry run on single test file (run this first, verify output before proceeding):
        python3 ~/Claudette/memory_recovery.py --file 2026-05-06.md

    Full run across all 22 affected files (only after dry-run verified):
        python3 ~/Claudette/memory_recovery.py --all

    The script is idempotent: if a file already contains session markers from a prior
    recovery run, it will be skipped.

Auth:
    Reads GITHUB_MEMORY_TOKEN from environment (same as memory_writer.py).
    Writes to Jeanetteclaire/Claudette-memory.

This script does not:
    - Fix the underlying bug in memory_writer.py (separate session)
    - Delete or rewrite any existing commits
    - Touch any files outside the 22 listed
    - Require any new dependencies beyond what memory_writer.py already uses
"""

import os
import sys
import base64
import argparse
from datetime import timezone
from github import Github, GithubException

# ── Configuration ─────────────────────────────────────────────────────────────

REPO_NAME    = "Jeanetteclaire/Claudette-memory"
SESSIONS_DIR = "memory/experiences/sessions"

# The 22 affected files. 2026-05-12 is intentionally excluded — manually recovered.
AFFECTED_FILES = [
    "2026-04-16.md",
    "2026-04-17.md",
    "2026-04-18.md",
    "2026-04-19.md",
    "2026-04-20.md",
    "2026-04-21.md",
    "2026-04-22.md",
    "2026-04-23.md",
    "2026-04-24.md",
    "2026-04-26.md",
    "2026-04-27.md",
    "2026-04-28.md",
    "2026-04-29.md",
    "2026-04-30.md",
    "2026-05-01.md",
    "2026-05-03.md",
    "2026-05-04.md",
    "2026-05-05.md",
    "2026-05-06.md",
    "2026-05-07.md",
    "2026-05-08.md",
    "2026-05-11.md",
]

# Idempotency sentinel — if a file's current content contains this string,
# recovery has already run and the file will be skipped.
RECOVERY_MARKER = "<!-- Session 1 —"

# ── GitHub setup ──────────────────────────────────────────────────────────────

def get_repo():
    token = os.environ.get("GITHUB_MEMORY_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_MEMORY_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)
    g = Github(token)
    try:
        repo = g.get_repo(REPO_NAME)
        return repo
    except GithubException as e:
        print(f"ERROR: Could not access repo {REPO_NAME}: {e}", file=sys.stderr)
        sys.exit(1)

# ── Core recovery logic ───────────────────────────────────────────────────────

def recover_file(repo, filename):
    """
    Recover a single experience file by concatenating all historical versions.
    Returns True on success, False if skipped, raises on error.
    """
    filepath = f"{SESSIONS_DIR}/{filename}"
    date_str = filename.replace(".md", "")

    print(f"\n── {filename} ──────────────────────────────────────")

    # Step 1: Fetch current file to check idempotency and get current SHA.
    try:
        current = repo.get_contents(filepath)
        current_content = current.decoded_content.decode("utf-8")
        current_sha = current.sha
    except GithubException as e:
        print(f"  ERROR: Could not fetch current file: {e}")
        raise

    # Idempotency check: skip if already recovered.
    if RECOVERY_MARKER in current_content:
        print(f"  SKIP: Already contains recovery markers — skipping.")
        return False

    # Step 2: Fetch all commits that touched this file, oldest first.
    print(f"  Fetching commit history...")
    try:
        commits = list(repo.get_commits(path=filepath))
    except GithubException as e:
        print(f"  ERROR: Could not fetch commits: {e}")
        raise

    commits.reverse()  # GitHub returns newest-first; we want oldest-first.
    print(f"  Found {len(commits)} commits.")

    if len(commits) < 2:
        print(f"  SKIP: Only {len(commits)} commit(s) — nothing to recover.")
        return False

    # Step 3: Fetch file content at each commit.
    versions = []
    for i, commit in enumerate(commits, start=1):
        sha   = commit.sha
        # Commit timestamp — use author date, fall back to committer date.
        dt    = commit.commit.author.date
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ts    = dt.strftime("%Y-%m-%d %H:%M UTC")
        short = sha[:7]

        print(f"  Fetching content at commit {short} ({ts})...")
        try:
            file_at_commit = repo.get_contents(filepath, ref=sha)
            content = file_at_commit.decoded_content.decode("utf-8").strip()
        except GithubException as e:
            if e.status == 404:
                # File didn't exist at this commit — likely a deletion commit.
                # Skip it; it contributes no content to recover.
                print(f"  SKIP commit {short} ({ts}): file not present at this point (404 — deletion or pre-creation commit).")
                continue
            print(f"  ERROR: Could not fetch content at {short}: {e}")
            raise

        versions.append({
            "sha":     sha,
            "short":   short,
            "ts":      ts,
            "content": content,
        })

    # Step 4: Concatenate with session markers.
    # Session numbers are sequential over surviving versions only —
    # 404-skipped commits do not appear as sessions.
    if not versions:
        print(f"  SKIP: No recoverable content found across all commits.")
        return False

    sections = []
    for idx, v in enumerate(versions, start=1):
        section = (
            f"<!-- Session {idx} — commit {v['short']} — {v['ts']} -->\n\n"
            f"{v['content']}\n\n"
            f"<!-- end session {idx} -->"
        )
        sections.append(section)

    recovered = "\n\n".join(sections)

    # Step 5: Write back as a single new commit.
    # n reflects actual content sessions, not raw commit count.
    n = len(versions)
    commit_message = (
        f"Recover {date_str} — restore overwritten session content "
        f"({n} sessions concatenated)"
    )

    print(f"  Writing recovered content ({n} sessions concatenated)...")
    try:
        repo.update_file(
            path    = filepath,
            message = commit_message,
            content = recovered,
            sha     = current_sha,
        )
    except GithubException as e:
        print(f"  ERROR: Could not write recovered content: {e}")
        raise

    print(f"  OK: {filename} recovered — {n} sessions, committed.")
    return True

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Recover overwritten experience files in Claudette-memory."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file",
        metavar="FILENAME",
        help="Recover a single file by name (e.g. 2026-05-06.md). Use for dry-run verification.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Recover all 22 affected files. Only run after --file dry-run is verified.",
    )
    args = parser.parse_args()

    # Safety check: explicit exclusion of the manually-recovered file.
    if args.file and args.file == "2026-05-12.md":
        print("ERROR: 2026-05-12.md was manually recovered and is excluded from this script.")
        sys.exit(1)

    # Validate --file is in scope.
    if args.file and args.file not in AFFECTED_FILES:
        print(f"ERROR: {args.file} is not in the affected files list.")
        print(f"Affected files: {', '.join(AFFECTED_FILES)}")
        sys.exit(1)

    repo = get_repo()
    print(f"Connected to {REPO_NAME}.")

    files_to_process = [args.file] if args.file else AFFECTED_FILES

    recovered = 0
    skipped   = 0
    failed    = 0

    for filename in files_to_process:
        try:
            result = recover_file(repo, filename)
            if result:
                recovered += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"\nFATAL ERROR processing {filename}: {e}")
            print("Stopping. Fix the issue above and re-run.")
            print(f"\nSummary so far: {recovered} recovered, {skipped} skipped, 1 failed.")
            sys.exit(1)

    print(f"\n{'─' * 50}")
    print(f"Done. {recovered} recovered, {skipped} skipped, {failed} failed.")

if __name__ == "__main__":
    main()
