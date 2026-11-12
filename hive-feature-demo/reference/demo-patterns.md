# Demo motion patterns (and where they live in `templates/hive-demo.html`)

Every beat has to *show* the change, not label it. Pick the pattern that acts out the release note's verb.

| The note says… | Pattern | In the template |
|---|---|---|
| "…instead of failing", "works again", "now" | **Before → after**: the old result appears faded with a mono BEFORE tag, gets struck through (`clip` 0→1), and collapses. The new result lands in the same slot | `#m-before`, `#strike`, then `#m-reply` (timeline beat 2) |
| "prepares it for approval", "sends it to Review", "lands in…" | **Fly to where it lands**: copies of the new items travel on a bezier into the nav badge or list that receives them. The badge counts up (`Motion.steps`) and pulses (`scale` 1.45→1, `outBack`) | `#f1`/`#f2` and the flights hook; `#badge` steps |
| "you approve / confirm / send" | **Cursor click → state change**: the cursor eases to a layout-measured target, presses (scale 0.86) with a blue ring and a `click` cue. The button fades out, the row gets the green done tint, a status ("✓ SENT") slides in, and a `ding` sounds | cursor keyframes hook (`P` targets via `pos()`), `#r1b`/`#r1f`/`#r1s` |
| navigating to a page | **Nav highlight slides** from the old item to the new one. The top-bar title and footer label step. The old page fades out, the new one fades up, and new rows arrive at the top with the blue `newglow` edge | `hl` element, `#ptitle`/`#fpage` steps, `#pg-today` → `#pg-review` |
| the detail that matters is small | **Camera zoom** to scale 1.4–1.6 on the action region (ease camera, ~0.9 s), held while the cursor works, pulled back before overlays | camera keyframes hook (`keys` as [t, scale, focusX, focusY]) |
| a count changes | **Count steps** on every place the count shows (nav badge, card pill), changing at the same moment as the action | `Motion.steps('#badge', …)`, `Motion.steps('#rvcount', …)` |
| a background job is fixed | **Spinner settles**: a sync icon spins (ease camera, ~0.75 s), turns green, then each fixed behaviour ticks in with a drawn check and a chime | `#sync` hook, `#c1`/`#c2`, `.ck` draw |
| "X can be submitted / moved to Y" | **Item travels**: a small copy of the item rides an arrow into a status pill, which pops in (`outBack`) with a chime | `#docfly`, `#darrow`, `#inreview` |

## Timing budget (19.5 s template)

| Beat | Template times | Notes |
|---|---|---|
| Title | 0–2.3 | Kicker at 0.15, headline words from 0.35 (0.08 s per word), out at 2.0 |
| Trigger | 2.3–7.3 | Window in 2.3; typing 2.95–4.15 (about 0.02 s per character); send 4.25; before/after 4.6–5.6; result rows 5.9 / 6.25 |
| Effect | 7.2–13.6 | Flights 7.2–8.0; cursor appears 8.35; click 9.05; zoom 9.45–10.35; approve clicks 11.05 / 12.45; pull back 13.35–14.1 |
| Also | 13.95–17.75 | Cards 14.2 / 15.5; checks 14.95–15.4; travel 16.0–16.5 |
| End | 17.6–19.5 | Mark 17.7, wordmark 17.95, date 18.2 |

Keep these rhythms when you swap content: a beat change every 2–5 s, at least 0.6 s between cursor moves, and every achievement followed by about 0.4 s of hold before the next action.

## Gotchas found building the template

- A **to-only tween starts from the element's natural state** (opacity 1). Anything that must start hidden needs `from: { opacity: 0 }`; otherwise it shows early.
- Measure cursor targets with `pos(el, cam)` (layout coordinates, which ignore transforms). Never measure them with `getBoundingClientRect` while the camera is zoomed.
- Captions sit outside the camera, so they don't zoom. Keep the action in the upper two-thirds while a caption shows.
- For text that wraps badly, put a `<br>` in the headline. `Motion.words` keeps line breaks.
- Don't leave an arrow pointing from nothing: move a copy of the item and keep the source in place.
