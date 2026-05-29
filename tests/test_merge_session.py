"""
test_merge_session.py
---------------------
Standalone test for the wrap_session and merge_session_content helpers
from the memory_writer.py overwrite bug fix (TC13-001, 15 May 2026).

Pure functions — no API, no GitHub. Exercises the merge logic in isolation
so we can iterate on the shape before touching the live writer.

Run:
    python3 test_merge_session.py

Exits 0 on all-pass, 1 on any failure.
"""

# ── The helpers under test (mirrored from the proposed patch) ─────────────────

def wrap_session(content: str, session_number: int, timestamp: str) -> str:
    """
    Wrap session content with HTML-comment markers.
    Format mirrors the recovery script's shape, minus the commit hash —
    the writer has no commit hash at write time (the commit hasn't happened yet).
    """
    return (
        f"<!-- Session {session_number} — {timestamp} -->\n\n"
        f"{content.strip()}\n\n"
        f"<!-- end session {session_number} -->"
    )


def merge_session_content(existing: str, new_content: str, timestamp: str):
    """
    Returns (merged_text, session_number).

    Three cases:
      1. existing empty                → wrap new as Session 1.
      2. existing has '<!-- Session '  → append new as Session N+1
                                         (N = count of opening markers).
      3. existing non-empty, no marker → wrap legacy as Session 1 with
                                         a 'pre-fix legacy content' timestamp,
                                         append new as Session 2.

    Counting substring '<!-- Session ' (capital S, trailing space) matches
    both native writes and recovery-format markers
    ('<!-- Session N — commit [hash] — [ts] -->'), and does not match
    the lowercase '<!-- end session ' closers.
    """
    existing = existing.strip()
    new_content = new_content.strip()

    if not existing:
        return wrap_session(new_content, 1, timestamp), 1

    marker_count = existing.count("<!-- Session ")

    if marker_count == 0:
        wrapped_legacy = wrap_session(existing, 1, "pre-fix legacy content")
        new_section = wrap_session(new_content, 2, timestamp)
        return wrapped_legacy + "\n\n" + new_section, 2

    next_number = marker_count + 1
    new_section = wrap_session(new_content, next_number, timestamp)
    return existing + "\n\n" + new_section, next_number


# ── Tests ─────────────────────────────────────────────────────────────────────

TS = "2026-05-15 14:32 UTC"

failures = []

def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        if detail:
            print(f"        {detail}")
        failures.append(label)


# Case 1 — empty file (single-session day, first run)
print("\n── Case 1: empty existing file ──")
merged, n = merge_session_content("", "Morning session content.", TS)
print(merged)
check("session number == 1", n == 1)
check("opening marker present", "<!-- Session 1 — 2026-05-15 14:32 UTC -->" in merged)
check("closing marker present", "<!-- end session 1 -->" in merged)
check("content body present", "Morning session content." in merged)
check("exactly one opening marker", merged.count("<!-- Session ") == 1)


# Case 2 — one native-marked session present (multi-session day, second run)
print("\n── Case 2: one native-marked session existing ──")
existing = wrap_session("Morning session content.", 1, "2026-05-15 09:00 UTC")
merged, n = merge_session_content(existing, "Afternoon session content.", TS)
print(merged)
check("session number == 2", n == 2)
check("morning preserved", "Morning session content." in merged)
check("afternoon appended", "Afternoon session content." in merged)
check("Session 1 opener intact", "<!-- Session 1 — 2026-05-15 09:00 UTC -->" in merged)
check("Session 2 opener present", "<!-- Session 2 — 2026-05-15 14:32 UTC -->" in merged)
check("exactly two opening markers", merged.count("<!-- Session ") == 2)


# Case 3 — recovery-format markers present (commit hash in marker)
# This is what existed in the 20 recovered files. The fix must count these correctly.
print("\n── Case 3: recovery-format markers existing ──")
existing = (
    "<!-- Session 1 — commit a1b2c3d — 2026-04-16 08:30 UTC -->\n\n"
    "First recovered session.\n\n"
    "<!-- end session 1 -->\n\n"
    "<!-- Session 2 — commit e7f8901 — 2026-04-16 14:15 UTC -->\n\n"
    "Second recovered session.\n\n"
    "<!-- end session 2 -->"
)
merged, n = merge_session_content(existing, "Native afternoon session.", TS)
check("session number == 3", n == 3)
check("both recovered sessions preserved",
      "First recovered session." in merged and "Second recovered session." in merged)
check("new section is Session 3 with native (no commit) format",
      "<!-- Session 3 — 2026-05-15 14:32 UTC -->" in merged)
check("three opening markers", merged.count("<!-- Session ") == 3)


# Case 4 — legacy unmarked content (pre-fix file that survived without recovery)
print("\n── Case 4: pre-fix legacy content (no markers) ──")
existing = "# Session — 2026-04-30\n\nLegacy content with no markers."
merged, n = merge_session_content(existing, "New session content.", TS)
print(merged)
check("session number == 2 (legacy becomes Session 1)", n == 2)
check("legacy wrapped as Session 1 with placeholder timestamp",
      "<!-- Session 1 — pre-fix legacy content -->" in merged)
check("legacy body preserved", "Legacy content with no markers." in merged)
check("new appended as Session 2",
      "<!-- Session 2 — 2026-05-15 14:32 UTC -->" in merged and "New session content." in merged)
check("exactly two opening markers after merge", merged.count("<!-- Session ") == 2)


# Case 5 — whitespace-only existing treated as empty
print("\n── Case 5: whitespace-only existing ──")
merged, n = merge_session_content("   \n\n   \n", "Fresh session.", TS)
check("session number == 1", n == 1)
check("treated as first session", "<!-- Session 1 — 2026-05-15 14:32 UTC -->" in merged)


# Case 6 — closing markers without openers must not be counted as openers
# Synthetic edge to verify the substring choice is correct.
print("\n── Case 6: end-session closer without opener is not counted ──")
existing = "Some content\n<!-- end session 99 -->"
merged, n = merge_session_content(existing, "New.", TS)
check("treated as legacy (count of '<!-- Session ' is 0)", n == 2)
check("legacy block produced", "<!-- Session 1 — pre-fix legacy content -->" in merged)


# Case 7 — three existing native sessions, append a fourth
print("\n── Case 7: three existing native sessions ──")
existing = "\n\n".join([
    wrap_session("Session one body.",   1, "2026-05-15 08:00 UTC"),
    wrap_session("Session two body.",   2, "2026-05-15 12:00 UTC"),
    wrap_session("Session three body.", 3, "2026-05-15 16:00 UTC"),
])
merged, n = merge_session_content(existing, "Evening fourth.", TS)
check("session number == 4", n == 4)
check("four opening markers after merge", merged.count("<!-- Session ") == 4)
check("all three bodies preserved",
      "Session one body." in merged
      and "Session two body." in merged
      and "Session three body." in merged
      and "Evening fourth." in merged)


# ── Summary ───────────────────────────────────────────────────────────────────

print("\n──────────────────────────────────────────")
if failures:
    print(f"FAIL — {len(failures)} failure(s): {failures}")
    raise SystemExit(1)
print("All tests passed.")
