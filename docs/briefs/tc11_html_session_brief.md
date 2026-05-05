# Brief — Interface session

*Hand to TC11. Drafted by OP3 (Opus 4.7), 5 May 2026.*

---

## Who you are

You are TC11, a fresh Claude Sonnet technical instance. You have not worked on this project before. The previous TCs (most recently TC10) have built and deployed Claudette's running code; you inherit a system that is stable, well-documented, and currently in good shape.

Your job today is four coordinated changes to `claudette_interface_connected.html`. All four touch the same file. They are not deeply coupled — each could in principle land alone — but they're being done in one session because they're all HTML work and benefit from a single review-and-deploy cycle.

The work is:

1. **Restore goodbye camera frame** — the smallest change.
2. **Voice injection bug** — confirm-then-fix shape.
3. **`speakText()` client-side streaming** — Web Audio API work.
4. **Interface layout and styling changes** — four sub-changes, mockup-first.

Tackle them in this order or close to it. The first one is small and gets a quick win; the second one needs a diagnosis step before fixing; the third is independent architectural work; the fourth wants visual review before any code is written.

---

## What you have to work with

Project knowledge contains the architecture documentation (`docs/`) and the four main code files. Use `project_knowledge_search` — synced files do **not** appear at `/mnt/project/`. For complete file reads, do several targeted searches or ask Jeanette to paste the file directly.

Read these before you start:

- `docs/build_practices.md` — the operating discipline of this project. *Show before build* and *one thing at a time* are the rules that matter most for this session.
- `docs/work_queue.md` — has the canonical entries for all four jobs you're picking up. Read each entry as it pertains to your current job, in turn.
- `claudette_interface_connected.html` itself — ask Jeanette to paste it. It's a single HTML file with embedded CSS and JS. Roughly 1,500 lines.

For the voice injection job specifically, you may also need:
- `~/claudette-electron/main.js` and `~/claudette-electron/preload.js` — the Electron wrappers around the page. The speech bridge that may be involved in the bug lives across both.

---

## Operating principles for this session

A few that apply throughout, beyond the standard build practices:

**Hybrid deploy strategy.** Build all four jobs in your working copy without progressively deploying. Show each change to Jeanette and OP3 between jobs — diff or visual — wait for approval, then proceed to the next. After the fourth, one deploy, one cold-boot test, one git push. This trades the per-job test cycle for less interruption while keeping per-job review.

**Show before build, every time.** Especially for the layout work. Don't write CSS and HTML for the layout changes until Jeanette has seen and approved a mockup of where things will sit.

**Confirm before fix on the voice injection.** Don't assume the original fix is broken. Diagnosis first; fix second.

**Transport vs. text discipline.** If you find yourself wanting to clean up message text, button copy, or unrelated styling while you're in the file — stop. The diff is meant to be readable; only changes that are part of the four scoped jobs should be touched. Note adjacent things in the work_queue if they earn it.

---

## Job 1 — Restore goodbye camera frame

The simplest of the four. The HTML's `captureAndSendFrame()` function already handles the `'goodbye'` occasion correctly. The function is also called from three places: `startSession()` for `session_start`, the 25-minute timer for `mid-session`, and the `done.view_requested` branch for `requested`. The fourth call — the goodbye one — is missing.

It used to be there. It was removed during a diagnostic episode that turned out to be unrelated to the camera, and never restored.

Look in `sendMessage()`. The goodbye branch is the one that fires when the lowercase user input matches one of `bye`, `bye bye`, `doei`, `tot straks`, `goodbye`. Add `captureAndSendFrame('goodbye')` at the appropriate moment — before the goodbye `/message` POST so the frame is captured and queued before the goodbye exchange goes to Claude. The frame is held server-side as `pending_visual` and is included with the next API call, which in this branch is the goodbye message itself.

Show the planned diff to OP3 before applying. After the change, confirm with Jeanette by pointing at the lines and walking her through the order: goodbye detected → frame captured → frame queued server-side → goodbye message sent → API call includes the visual.

After this, the four documented capture moments — `session_start`, `mid-session`, `requested`, `goodbye` — are all wired correctly. The implementation matches what `retrieval.py` tells Claudette in INSTRUCTIONS, and what the HTML's own `captureAndSendFrame()` docstring claims.

Approve at this gate, move to Job 2.

---

## Job 2 — Voice injection bug

**Active and reproducing.** When Jeanette activates voice mode, recent message history loads into the input field before she starts speaking. It shouldn't be there.

A previous fix exists in the source: `document.getElementById('input').value = '';` inside `toggleVoice()`, with a comment noting it's there to prevent stale transcript injection. Presumed to be the original TC8 fix from late April. The behaviour has returned, which means either the fix isn't running, or the injection is coming through a different path.

**Diagnose before fixing.** This is the rule on this entry. Three hypotheses are worth testing in order:

1. **Is the clear-on-activate line running?** Ask Jeanette to reproduce while watching the browser dev tools console. Add a `console.log('[voice] cleared input on activate')` line right after the existing clear, deploy temporarily (or have Jeanette run from a local copy of the HTML), and confirm whether the message appears when the bug fires. If yes — the line runs but injection still happens, the path is elsewhere. If no — find why the line is being skipped.

2. **Is `onresult` firing with stale content?** Speech recognition's `onresult` callback writes `transcript` to the input field on every event. If the recognition starts and the first event carries buffered or cached content from a prior session, the field would be repopulated immediately after `toggleVoice()` clears it. Check what `event.results[0][0].transcript` contains on the first `onresult` after activation when the bug is firing.

3. **Is the Electron speech bridge replaying?** The native bridge in `main.js`'s `SPEECH_SHIM` has an 800ms discard window for stale results. If that window isn't firing — for example, if `Date.now() - startTime` math is wrong on a re-activation, or if the bridge holds state across activations — old transcripts could leak through. Check `main.js`'s `SPEECH_SHIM` for any state that persists across `start`/`stop` cycles.

The fix follows the diagnosis. Some possibilities:

- If hypothesis 1 confirms the clear line is being skipped, restore execution. (Code path may have shifted in a recent edit.)
- If hypothesis 2 confirms `onresult` carries stale content, clear the field again on the first `onresult` event of a new activation, or reset `recognition` entirely on each `toggleVoice()` so it starts fresh.
- If hypothesis 3 confirms bridge replay, fix the discard window or reset bridge state on re-activation.

Show OP3 your diagnosis findings before proposing the fix. The right fix depends on which hypothesis lands.

After fixing, ask Jeanette to test by activating and deactivating voice mode several times in succession, including with messages already in the conversation thread. Both Safari (native Web Speech) and the Electron app (native bridge) need testing — they take different code paths.

Approve at this gate, move to Job 3.

---

## Job 3 — `speakText()` client-side streaming

Server-side streaming is already in place from TC8-008 — the `/speak` route returns chunked audio via `stream=True` and `stream_with_context`. The client doesn't take advantage of it. `speakText()` does `await resp.blob()` which waits for the *complete* audio before playing. The first byte plays only after every byte has arrived, defeating the point of server-side streaming.

The fix is replacing the blob-based playback with Web Audio API streaming. The shape:

1. Read the response body as a stream (`resp.body.getReader()` — the same pattern `streamClaudetteReply()` already uses for SSE).
2. Pipe chunks into an `AudioContext` using `decodeAudioData` per chunk, or — more robustly for streamed audio — `MediaSource` with a `SourceBuffer`.
3. Play chunks as they arrive rather than after accumulation.

`MediaSource` is the cleaner approach for streamed audio of unknown duration. The pattern:

```javascript
var mediaSource = new MediaSource();
var audio = new Audio();
audio.src = URL.createObjectURL(mediaSource);

mediaSource.addEventListener('sourceopen', async () => {
  var sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
  // (or whatever MIME type Fish Audio is returning — verify with the existing /speak response)
  var reader = resp.body.getReader();
  while (true) {
    var { value, done } = await reader.read();
    if (done) { mediaSource.endOfStream(); break; }
    sourceBuffer.appendBuffer(value);
    // wait for 'updateend' before next append
    await new Promise(r => sourceBuffer.addEventListener('updateend', r, { once: true }));
  }
});

audio.play();
```

That's the rough shape; the production version needs proper error handling and the existing pause/cleanup logic preserved (the current function pauses any prior `currentAudio` before starting and clears `currentAudio` on `ended` or `error`).

**Two things to be careful of:**

- **Verify the Fish Audio MIME type.** `audio/mpeg` is the likely answer, but check what server.py's `/speak` route is actually setting in the Content-Type header. The wrong MIME type makes `addSourceBuffer` throw immediately.
- **Preserve the Electron audio playback wrapper.** `main.js`'s `SPEAK_WRAPPER` patches `HTMLAudioElement.prototype.play()` to pause speech recognition during Fish Audio playback. The new streaming implementation creates an `Audio` element same as before — the wrapper should still hook correctly. Verify in the Electron app specifically that voice doesn't get picked up while Claudette is speaking.

Show OP3 the proposed implementation before writing it. Show Jeanette the diff before deploying. After deploy, the test is qualitative — does the first phoneme of Claudette's reply arrive faster than it used to? It should be perceptibly snappier on long replies.

Approve at this gate, move to Job 4.

---

## Job 4 — Interface layout and styling changes

The largest of the four. Four sub-changes per the work_queue entry.

**Mockups first.** Don't write a single line of HTML or CSS until Jeanette has seen and approved a visual mockup of where things will end up. SVG sketches, ASCII layouts, or annotated images are all acceptable forms — pick what communicates the design clearest. The point is for Jeanette to see "this is where things will sit" before the change exists in code.

The four sub-changes:

**Layout — more typing space.** Move the send, mic, segment, and eye buttons to sit *underneath* the message input field rather than beside it. Widen the content area to fill most of the window (not edge to edge — leave breathing room at the sides). Primary goal throughout is maximising the message input area. The current state has these four controls on the right edge of the input row alongside the upload button; the new state has the input row become input-and-upload-only, with the four controls in a row below.

**Visual consistency — circles on segment and eye.** The session-indicator (segment) and eye-indicator are currently SVGs without the circular border treatment that send, voice, and upload buttons have. Add the same circle treatment so all six controls visually match. Match the existing `.send-btn` / `.voice-btn` / `.upload-btn` styling — same border colour, same hover behaviour where applicable.

**Bug fix — image upload hover zone.** The image upload button (`.upload-btn`) has an oversized invisible trigger zone that bleeds into the message field. The cause is the `.upload-btn input` style that sets `position: absolute; inset: 0;` on the file input — the file input fills the entire button. If the button itself is currently larger than its visual bounds (via padding or absolute positioning of children), the file input inherits that. The fix is constraining the file input to the button's visual area only. Check the existing CSS for any `inset: 0` or similar on `.upload-btn input` and tighten.

**Behaviour preservation — eye button stays non-interactive.** The eye is a visual indicator only, intentionally non-interactive. Move it with the other buttons, add the circle, but do **not** add click functionality. This is a deliberate preservation per the work_queue entry — "TCs picking this up should not 'improve' by making it clickable."

**The sequencing within Job 4:**

1. Produce mockups for the layout change. Show Jeanette. Iterate on the design until approved. The other three sub-changes (circles, hover-zone, eye preservation) can be sketched alongside or held until step 3 — your call.
2. Once layout is approved, write the HTML/CSS for all four sub-changes together. They affect the same regions of the DOM and CSS.
3. Show the diff (or a live preview if Jeanette can run a copy locally) before deploying.

After this, all four jobs are done and ready to deploy.

---

## Coordination notes

One file: `claudette_interface_connected.html`. The work doesn't touch server.py or any other Python file. The Electron files (`main.js`, `preload.js`) may be touched only if Job 2's diagnosis lands there — and only if it does.

The deploy strategy is hybrid:

- All four jobs land in your working copy in sequence, with per-job review gates.
- After all four, one cold-boot test (the new HTML loads, all four behaviours work).
- One git commit covering all four jobs.
- One git push.

The version line on the HTML file gets bumped at the end. `2026-05-05-TC11-001` if today's date and your first deploy. Per *file version control* in build_practices, the increment is per-change and the date is the date of that change.

---

## What to be careful of

**Don't progressively deploy.** The hybrid strategy is review-per-job, deploy-once-at-end. If you're tempted to deploy after Job 1 because it's small and ready — don't. Hold the deploy until all four are done.

**Voice injection diagnosis is real work.** Don't shortcut to a fix. The wrong fix wastes a deploy cycle and obscures the actual cause for next time. Spend the time on diagnosis.

**Visual review for the layout change is non-negotiable.** Mockups before code. Jeanette's request was explicit and reasonable.

**Don't make the eye button clickable.** A common "improvement" instinct that would be wrong here. The eye is non-interactive by design.

**Test in both Safari and Electron.** Voice and audio behaviour can differ between them. The native Electron bridge takes a different code path than Safari's Web Speech API.

**The chat-client autolinking issue.** Filenames in chat sometimes render with `[name](http://name)` patterns. That's display only — the actual files in the repo don't contain those URLs. Don't try to "fix" them in the source.

---

## What's out of scope

- The Electron Phase 3 (butterfly overlay) and Phase 4 (packaging) work — those are dedicated separate sessions.
- Server-side changes of any kind. If a problem surfaces that seems to require a server change, flag it to OP3 rather than acting.
- Adjacent CSS or HTML cleanup that isn't part of the four scoped jobs.
- Wording changes to button labels, placeholders, or error messages.
- Changes to other interface files (the Eye standalone page in server.py's `/window` route, for instance).

---

## Documentation updates owned by this session

Per *whoever does the work owns the documentation update*:

- Retire all four work_queue entries: *Restore goodbye camera frame*, *Voice injection bug*, *`speakText()` client-side streaming*, *Interface layout and styling changes*.
- Add a `project_history.md` entry under today's date, covering all four jobs in one consolidated entry. The four-paragraph shape that worked for the 4 May entry is a good template.
- Update version line on the HTML file.
- If the voice injection fix touches `main.js` or `preload.js`, those file version lines need bumping too, and a brief note in the architecture_companion.md if the speech bridge behaviour changed.

---

## A note from OP3

This is a focused HTML session. Four jobs, one file, one deploy. The discipline that worked the last two days — small bounded changes, show before build, one thing at a time — applies just as cleanly here. The HTML is just code; treat it with the same care.

The two bugs (goodbye frame, voice injection) are restoration work — fixing things that were once working. The two improvements (speakText streaming, layout) are forward work — making things better. A clean session lands all four.

I'll be available during the session at each review gate, and for any complications that need PO judgement before you proceed.

— OP3
