# Future considerations

A running list of things that might matter eventually but don't matter now. Not a to-do list. Not a commitment. Just notes about possible future decisions, with enough context to recognise when the moment has arrived to actually consider them.

When something on this list becomes urgent, it graduates to actual work and gets removed from here. When something on this list turns out to be the wrong concern, it gets removed too.

---

## Possible migration from Flask to FastAPI

**What it is.**

Flask is the Python web framework currently running server.py. FastAPI is a more modern alternative. They do the same fundamental job — receiving HTTP requests, running functions, sending responses — but FastAPI is built around async/await and has better native support for streaming responses.

**Why this might matter for Claudette specifically.**

A lot of what Claudette does is streaming — the message responses stream from Claude API to the browser in real time, the memory writer streams its response, voice generation streams audio chunks. Flask handles streaming, but it does so through workarounds rather than native design. FastAPI was built async-first, which means streaming patterns are more natural and certain kinds of slow-or-stuck situations are easier to reason about.

If Claudette ever has a class of bug that turns out to be Flask's blocking-by-default model getting in the way of a streaming pattern — that would be a moment to consider migration.

**Signs that the moment has arrived.**

Watch for these patterns. None of them is happening now; if any starts happening, FastAPI becomes a more serious option.

A streaming response intermittently stalls partway through and the cause traces to thread blocking inside the Flask process.

Adding a new feature that needs concurrent streaming (e.g., voice and text streaming truly in parallel) hits architectural friction that wouldn't exist in async-first code.

The number of background threads in server.py grows beyond the current few (library loop, transcript flush) to the point where coordinating them in Flask's model becomes the limiting factor.

**Why we are not migrating now.**

Flask is working. Migration is a real piece of work — every route would need to be rewritten, the streaming patterns reimplemented, the test surface re-walked. The cost is high and the benefit is currently theoretical. The right time is when there's a concrete problem Flask is causing, not when there might be one in principle.

**Decision triggers — not "if Flask is slightly imperfect" but:**

A specific bug or architectural friction that's clearly attributable to Flask's model.

A planned feature that genuinely doesn't fit Flask's model.

Major rewrite of server.py for other reasons, where switching frameworks during the rewrite costs little extra.

Without one of those, leave Flask alone.

---

*(Future entries to this document follow the same pattern: what it is, why it might matter for Claudette, signs the moment has arrived, why we are not doing it now.)*
