# Motion craft

## First: motion that explains (read this before anything else)

Entrances are not animation. A scene where things fade up and then sit still is a slide. The bar is **functional motion**: the movement itself carries part of the meaning.

**The test:** pause on the last frame of the scene. If watching the motion taught nothing that the last frame doesn't show, the scene is a slide. Rework it.

**How to find it:** take the scene's sentence, find its verb or relationship, and animate *that*:

| The sentence says… | Animate it as… |
|---|---|
| X is blocked / stuck | things flow and **pile up against a barrier** before X; the queue keeps growing while the scene holds |
| X and Y combined / merged | two separate lanes or links **converge** into one node or bracket |
| X splits into / becomes many | one bar or node **branches** into several (lines draw out, copies slide apart) |
| staged / first A then B | a **timeline arrow** with A landing first; B waits (dashes marching) until A lands |
| X processed N items in T | items **travel through** the pipeline while the counter climbs, and the count is the result of the flow |
| N is the biggest / the risk | it gets a **highlight fill** (a row band or card tint), not just a colour |
| X moved to time T | the item **slides** along a time axis to its new slot |
| from many to one / one source of truth | scattered items **gather** into one container |
| a decision is open | the row stays **unresolved**: an open marker, a different fill, sitting at the end of the ledger |

Keep looping motion meaningful (particles only on links that are actually flowing, dashes only on links that are waiting), and let it keep running while the scene holds, so the hold still says something.

## Sound that explains

Sound follows the same rule as motion: it marks meaning, not decoration.
- **Chime = achievement.** Something lands Done, a target is hit, a figure lands. Consecutive chimes rise through the scale, so a run of wins plays as a rising run. Put the cue about 0.1 s after the visual lands.
- **Tick** = a row or item arriving in a list. Soft and quiet.
- **Swoosh** = a scene change, kept quiet (gain 0.5–0.7).
- **Silence for bad news.** Blockers, risks and misses get no chime.
- **Music follows the structure.** The groove drops on the first content scene (`--drop`), and the drums leave for the close (`--outro`) so the ending can breathe.

## Continuity: one page, not a slideshow

- **A persistent frame**: a top bar with the piece's name and date on the left, a section counter on the right ("MOVE 2 OF 3", "DECISIONS", "ON THE RADAR", "END"), and a hairline rule. It never animates out. Update the counter with `Motion.steps`.
- **Clear and rebuild inside the frame.** Between scenes the content clears fast (0.25–0.35 s), the frame stays, and the next kicker appears straight away. No full-frame crossfades, at most one hard cut per minute.
- **Headlines type on word by word** with `Motion.words` (about 0.09 s per word): kicker first, then the headline, then the diagram, then the number.
- **Keep the people in.** "Dan Downs' lead-generation automation" and "Sivaram and Adrian agreed…" beat an anonymous claim. A short source caption under a figure ("Per Sophia Clifton at Radian Compliance") makes it trustworthy.
- **Lists of 4+ items go in a ledger** (name column + one line each, rows landing ~0.5 s apart), not a cut-down list. Structure makes density readable.
- **End on what happens next** (the next meeting, decision or deadline, with its time), not on a title card.

## Type at 1080p (scale ×1 for 1920×1080; for 1080×1920 vertical use the same pixel sizes)

| Role | Size | Weight | Notes |
|---|---|---|---|
| Hero headline | 96–120 px | 700 | ≤ 8 words, tight tracking (-0.035em) |
| Headline | 64–80 px | 650 | |
| Body / supporting | 36–44 px | 450 | ≤ 14 words, muted colour |
| Label / kicker | 26–30 px | 500 mono | uppercase, +0.08em tracking |
| Big number | 140–220 px | 700 mono | tabular, count up from 0 or from the "before" value |

Minimum is 28 px anywhere. Social video is watched on phones, so go larger, not smaller. Keep line length under 30 characters for vertical and 45 for 16:9.

## Layout

- Safe margin is 96 px (16:9) or 120 px top and bottom plus 64 px sides (9:16; platform UI covers the bottom 20%).
- Think in a 3×3 grid (TL…BR). One focal point per scene, and most scenes are left-aligned.
- Leave whitespace: if a frame looks full, split the scene.
- Recurring diagrams stay in one place and grow. Don't rebuild them from scratch in each scene.

## Timing

- Entrances take 0.4–0.8 s and exits 0.3–0.5 s. Exits are faster than entrances.
- Stagger related items by 0.06–0.15 s, never all at once and never more than 0.2 s apart.
- Hold text for at least 1 s + 0.3 s per word *after* it lands, before anything replaces it.
- Leave 0.3–0.5 s of stillness at the end of each scene before the transition: viewers need a settled frame.
- Number count-ups take 1.2–2 s with `outExpo`, so they slow down onto the true value.
- Sound-on: on-screen text lands just *before* the VO says it (about 0.2 s), never after.

## Easing (Motion.EASE names)

| Use | Ease |
|---|---|
| Things arriving | `outQuint` (calm) / `outCubic` (neutral) / `outBack` (pop, small elements only) |
| Things leaving | `inCubic` |
| Things moving from A to B on screen, lines drawing | `inOutCubic` |
| Gentle loops, breathing, drifting | `inOutSine` |
| Count-ups | `outExpo` |
| Progress bars tied to time | `linear` |

When the project has a design system, use its curves instead: `Motion.EASE.settle = Motion.bezier(0.22, 0.9, 0.24, 1)`, then `ease: 'settle'`. Use its durations too, scaled up about 1.3× for video, because UI timings feel rushed on a full screen.

## Moves that read well

| Move | How with Motion |
|---|---|
| Fade-up | `from: { opacity: 0, y: 24 }` |
| Line or arrow draws on | SVG path, `from: { draw: 0 }, to: { draw: 1 }` |
| Wipe-reveal text or a bar | `from: { clip: 0 }, to: { clip: 1 }` (left → right) |
| Typewriter | `from: { text: 0 }, to: { text: 1 }`, linear, about 0.04 s per character |
| Pop-in node | `from: { opacity: 0, scale: 0.8 }`, `outBack` 0.5 s |
| Count up | `from: { count: 0 }, to: { count: 377 }`, `format: n => ...` |
| Focus pull | others `to: { opacity: 0.25 }` and the focused one keeps its colour, or `blur` on the background |
| Push/zoom transition | tween a wrapper `scale` 1 → 1.15 plus opacity out while the next scene fades in |
| Bar chart | bars `from: { scale: 0 }` with `transform-origin: bottom` on the bar element, stagger 0.08 |

Avoid spins, bounces on text, rainbow gradients, and more than one thing moving in different directions at once.

**Render cost:** a CSS `filter: blur()` on a large element (aurora blobs, glows) is redrawn every frame and can make a render 5× slower. Use radial-gradient ellipses for soft light instead, and keep SVG blur filters to small elements.

## Motion API (templates/scene.html)

```js
Motion.scene('#s2', start, end, { in: 0.5, out: 0.5, title: 'Name' });   // fades the section; 0 = hard cut
Motion.tween('#el' | ['#a', '#b'] | element, {
  at: 5.2, dur: 0.6, ease: 'outQuint', stagger: 0.1,     // stagger applies across matched elements
  from: { opacity: 0, y: 30 }, to: { ... },             // from-only animates to the natural state
  format: n => n.toFixed(1) + '%'                        // for count
});
Motion.words('#headline', { at: 3.4, stagger: 0.09 });                  // word-by-word reveal; cls: 'grad' for gradient text
Motion.steps('#section', [[0, 'INTRO'], [3.2, 'MOVE 1 OF 3'], ...]);   // swap text at times
Motion.hook(t => { /* anything else: queues, particles, canvas, a chart lib's setTime */ });
Motion.duration = 60;
```
Props: `opacity x y scale rotate blur draw text count clip`. Motion owns `transform` on any element it animates. If you need a static CSS transform as well, put it on a wrapper. Crossfade = the next scene starts at the previous scene's `end - out`.

## Diagram patterns

**Queue piling up at a blocker** (the pattern for "blocked"):
```js
// items spawn every `gap` s, travel along `path` at `speed` px/s, and stop in a queue in front of the end
const len = path.getTotalLength();
Motion.hook(t => dots.forEach((d, i) => {
  const born = t0 + i * gap; if (t < born) { d.style.opacity = 0; return; }
  const slot = len - 18 - i * 22;                       // queue position: first arrival sits nearest the barrier
  const p = path.getPointAtLength(Math.min(slot, (t - born) * speed));
  d.setAttribute('transform', `translate(${p.x} ${p.y})`); d.style.opacity = 1;
}));
```

- **Sources → brain → front ends**: three columns, particles (small squares) travelling along connectors (use `Motion.hook` to place particles by `t`), nodes popping in where they land.
- **Before / after**: a split screen, or the same layout with the mess on the left resolving into order. Use a match cut between them.
- **Ladder or rungs**: one rung per beat that tilts up. Earlier rungs drop to muted when the next one lands.
- **Iceberg / waterline**: a small visible tip, then wipe the rest up.

## Product screenshots

Put supplied screenshots in `assets/` and show them inside a simple device or browser frame drawn in CSS. Animate a highlight box, a zoom on the region that matters (scale a wrapper, `inOutCubic`) and an annotation label. Never fake UI the person didn't supply. If a screen is needed but missing, draw a clearly schematic version and say so.
