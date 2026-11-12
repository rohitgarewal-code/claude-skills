# Brand: Launch Control

Use when the person asks for Launch Control, the program-tracker style, or Hive's dark program-map look.

## Files
- `lc.css`: tokens, base type and the persistent frame, kicker/headline/caption, KPI tile, ledger row, card and NEXT bar styles. Link it in the page's `<head>`.
- `lc.js`: map nodes, state icons, links (charged with particles, moving/pending/blocked dashes, into-gate), lane pills, the queue-at-a-barrier pattern, and the opening sequence. Load it after the Motion engine and before the timeline.
- `demo.html`: every state and link type on one map, as a working reference. Render it with `--stills` to see the look. Don't reuse its layout for content.

Setup: copy `lc.css`, `lc.js` (and `demo.html` if useful) into the project, plus fonts: `npm i -D @fontsource-variable/inter @fontsource/jetbrains-mono @fontsource/gelasio`, then copy `inter-latin-wght-normal.woff2`, `jetbrains-mono-latin-400-normal.woff2` and `gelasio-latin-400-normal.woff2` into `fonts/`.

The page skeleton: `<div id="stage">` holding three `.aurora` divs (#au1–3), a `.grid`, your `<section class="scene">`s, then `#frame` (left: `.live` dot plus the title, right: `#section` counter) and `#rule` with `.bar#pbar`. Give each map scene an `<svg id="mN" width=1920 height=1080>` and call `map('mN')`. Animate the aurora drift and the progress bar with a `Motion.hook`, and step the counter with `Motion.steps`.

## Rules that matter most on video
- Map the content's real states onto the fixed state words. If the source doesn't say what state something is in, use `state: 'none'` (ink), never a guessed colour.
- Blocked → the `queue()` pile-up. Combined or merged → lane pills converging into a gate. Done chains → charged links with particles. Waiting → pending dashes.
- A Done node entering through `enter()` cues a chime automatically (`{ n, ding: false }` to skip it). Add `Motion.cue` yourself for counts landing and checks drawing.
- Gradient text only on the title (class `grad`, passed through `Motion.words(..., { cls: 'grad' })`).

# Design system reference

Source: the "Launch Control" design system artifact (tokens.json and README). A dark, living map of a program: tasks, outside inputs and gates. One theme, `night`.

## Principles
1. **State is the colour, and nothing else is coloured.** Each hue means one state. Surfaces stay near-black and text uses the ink scale. If something is coloured, it is telling you a state.
2. **Motion means flow.** Particles travel only along links whose source is Done. Dashes march only along links that are still waiting, faster when the step before is underway.
3. Fixed state words: **Done, In progress, To verify, Blocked, Ready to start, Waiting** (tasks); **Awaiting, Received** (outside inputs); **Cleared, In progress, Not started, Blocked** (gates).
4. IDs are short, uppercase and monospaced, shown before the title. Times are 24-hour with the zone. Durations are compact ("2h 14m", "in 22h 40m"). No emoji.

## Colour tokens
| Token | Value | Use |
|---|---|---|
| ground | #05070d | page ground, under two radial glows |
| glow-blue / glow-violet | #13203d / #261143 | top-left / top-right radial glows |
| aurora-blue / -violet / -green | #2563eb / #a21caf / #059669 | slow blobs, blur 90px, 20% / 20% / 12% opacity |
| surface-card | #0c111e | node and card fill |
| surface-glass | rgba(255,255,255,.04) | chips, rows, KPI tiles, countdown |
| surface-avatar | #1a2133 | owner initial discs (18% white ring) |
| line / line-strong | rgba(255,255,255,.08) / .16 | hairline borders |
| ink / ink-2 / ink-3 | #eef2f8 / #a7b0c3 / #737c95 | primary / secondary / captions |
| ink-waiting / ink-pending | #b7bfd0 / #8b95ad | titles and IDs of waiting work |
| state-done | #34d399 | Done; charged links and their particles (core #ecfdf5) |
| state-progress | #60a5fa | In progress, and anything moving |
| state-verify | #fbbf24 | To verify |
| state-blocked | #f87171 | Blocked or overdue only, never decoration |
| state-ready | #e2e8f0 | Ready to start |
| state-waiting | #64748b | Waiting (marks only, never text) |
| state-input | #e879f9 | outside inputs (customer asks): diamond, magenta links |
| state-gate | #22d3ee | gates and milestones: hexagon |
| fill-done / fill-input / fill-gate | #0b1712 / #170c1c / #071a1f | card fills by kind |
| on-done / on-blocked | #05110c / #1a0505 | check / cross drawn on state discs |

Gradients appear only on the program title (`#ffffff → #c7d2fe → #f5d0fe`, 100°), the ring's big number (`#ffffff → #a7f3d0`) and the tab indicator.

## Type
- `serif` (Anthropic Serif, falling back to Georgia): numbers people look at, and the program's name. Weight 400.
- `mono` (ui-monospace / SF Mono): IDs and uppercase micro-labels: eyebrow 0.18em tracking, kicker 0.16em, section label 0.14em, IDs 0.08em.
- `sans` (Anthropic Sans, falling back to system UI): everything else. Tabular numerals everywhere.
- Outside claude.ai use stand-ins: Inter (sans), Gelasio (serif, metric-compatible with Georgia), JetBrains Mono.

## Components
- **Node:** surface-card, radius 12 (scale up for video), a 3px state bar on the left, an 18px state icon, a mono ID line in the state colour ("D2-04 · Blocked"), the title, and up to three owner initials. Done and active nodes get a soft blurred halo in their colour; in-progress halos breathe on a 2.8s cycle.
- **Icons:** Done = filled disc with a check · In progress = spinning quarter arc (1.1s) · To verify = ring with a blinking dot · Blocked = filled disc with a cross · Ready = ring with a ping · Waiting = dashed circle · Input = diamond · Gate = hexagon.
- **Links:** cubic curves with horizontal tangents, right edge to left edge. Charged: state-done, solid, 55%, with particles at 80px/s. Moving: state-progress, dash 5 7, 75%, a 0.8s march. Pending: ink-pending, dash 3 9, 40%, a 1.4s march. Awaiting: state-input, dash 4 8. Blocked: state-blocked, dash 4 8.
- **KPI tile:** a glass tile with a glowing state dot, a label, and a serif count. **Row:** a glass row with a state icon, the title, and meta on the right. **Cover:** state-coloured blocks bleeding off the right edge, joined by the four link styles, with the serif name at bottom left.
- **Background:** ground plus the two glows plus the aurora. Map areas get a 24px dot grid.

## Motion
- ease-settle `cubic-bezier(0.22, 0.9, 0.24, 1)`: the house curve, for entries. ease-camera `cubic-bezier(0.645, 0.045, 0.355, 1)`: for moves. Linear: for loops.
- Opening sequence: nodes rise in left to right, staggered by up to 38ms (0.45s each). Each link draws on over 1s, 160ms after its target lands. Particles start once everything has landed.
- Panes fade in from 12px below with a 6px blur.
