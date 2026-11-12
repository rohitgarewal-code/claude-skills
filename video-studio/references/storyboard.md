# Storyboard

The storyboard is the spec the build follows. A good one means the render is a formality. Write it as `storyboard.md` in the project folder and get approval before building.

## 1. Brief (a table)

| Item | Direction |
|---|---|
| Viewer | Who exactly, and what they already know. Treat experts as peers: show the mechanism, skip the marketing. |
| What it must land | 1–3 points, in order. If it can't be said in three, it's two videos. |
| Where it plays | Laptop across a table, LinkedIn feed (muted autoplay), all-hands screen, website hero, sent afterwards. |
| Sound | Sound-off by design (on-screen text carries the argument; VO lines become speaker notes) or sound-on (VO carries it; text reinforces). |
| Format | 16:9 1920×1080 / 9:16 1080×1920 / 1:1 1080×1080, 30 fps, target length. Name any short cut (e.g. scenes tagged CUT make a 30 s version). |
| Tone | e.g. "technical and calm, never markety". Diagrams and type; no stock imagery unless supplied. |
| Sources | The documents, numbers and screenshots everything on screen comes from. |

Ask only what you can't infer from the request and the material. Default to sound-off for social posts and sound-on for walkthroughs.

## 2. Narrative arc and scene list

One sentence for the arc (e.g. "respect → friction → mechanism → payoff"), then a table:

| # | In | Len | Scene | Viewer leaves with | Out | Cut |
|---|---|---|---|---|---|---|
| 1 | 0:00 | 6s | Hook | The one-line problem | cut | CUT |
| 2 | 0:06 | 10s | ... | ... | dissolve | |

- "Viewer leaves with" is one plain sentence. If you can't write it, the scene has no job, so cut it.
- 5–12 s per scene for explainers. Hooks are 3–6 s. Nothing over 20 s without a change on screen.
- Transitions: cut, dissolve (crossfade), dip (through background), wipe (direction), push (direction), zoom in/out (into or out of an element), match cut (the same shape carries over). Most transitions should be plain cuts and dissolves. Save the rest for moments that mean something.

## 3. Scene direction (one block per scene)

```
### Scene 3 · The waterline · 0:22–0:38
Purpose: An applet is the tip; production is the rest.
Frame: Layout in thirds (TL/TC/TR/ML/MC/MR/BL/BC/BR). What is where, what is accent-coloured.
On screen: "Headline text, verbatim." / Mono label: "verbatim"
Motion that explains: Requirements pile up below the waterline faster than the tip grows (the verb is "hides").
Animation:
- Headline: word by word, 0.09s per word. Trigger: scene start + 0.3s
- Iceberg body: wipe up, 0.8s inOutCubic. Trigger: after headline
- Six requirement labels: fade-in, stagger 0.12s. Trigger: after 1.6s
VO: "The line the narrator says." (or speaker note when sound-off)
Transition: dissolve 0.5s into Scene 4.
Assets: iceberg outline (create), labels (type).
```

**Motion that explains** is required for every content scene. Name the sentence's verb, then the movement that acts it out (see motion-craft.md). If you can't name one, the scene is a slide: change the visual, merge the scene into another, or cut it.

Write on-screen text exactly as it should appear, because the build copies it verbatim. Keep headlines at 8 words or fewer and supporting lines at 14 or fewer.

## 4. Frame and continuity

Describe the persistent frame (top bar, section counter values per scene, rule, grid texture) and how scenes hand over (content clears fast inside the frame; which elements carry over). Name the closing beat: what happens next, with its time.

## 5. Visual system

- Palette tokens (bg, ink, muted, line, accent, accent-2) with hex values. One accent used sparingly: it marks the thing the scene is about.
- Type: one sans and one mono; sizes from the scale in motion-craft.md.
- Shapes and icons: line weight, corner radius, and whether they're filled or outlined. Draw everything as SVG or CSS.
- Motion personality: e.g. "calm: outQuint entrances, no bounce, 0.5–0.8 s" or "punchy: outBack, 0.3–0.5 s, hard cuts".
- Recurring elements: e.g. one diagram that stays and grows across Act 2.

## 6. Guardrails

- Banned words and claims (from the person, battle cards or brand rules).
- Names and figures that must not appear (confidential customers, internal metrics).
- No logos or images except supplied files. No people photos unless supplied.
- Reduced motion: if it's also published as a page, cut between end states.

## 7. Open decisions

A short table of calls the person should make (title wording, which number to show, length of the short cut), each with your recommended default. When the build has to proceed without answers, use the defaults and list them in the handoff.

## The build check (after rendering)

Go through the scene list row by row: start and length within 0.1 s, the transition as written, on-screen text exact, guardrails respected. Then run the functional test on every content scene: pull a frame mid-motion and the last frame. If the motion taught nothing the last frame doesn't show, it isn't done. List any direction you couldn't follow and why.
