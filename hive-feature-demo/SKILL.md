---
name: hive-feature-demo
description: Make a 15–20 second demo video of a Hive feature from a feature description or release note. Rebuilds the real Hive UI, shows the feature working with a cursor, camera zooms and captions, and scores it with the Afro house bed and achievement chimes. Use when asked for a Hive feature demo, a release or what's-new video, or a short product clip of something shipped in Hive.
---

# Hive feature demo

Turn one shipped change into a 15–20 s video that shows it **working in the Hive UI**: the user does the thing, Hive visibly responds, and the result lands. There's no voiceover; a music bed and sound effects carry it.

Rendering and sound come from the **video-studio** skill (`~/.claude/skills/video-studio`): `render_html.mjs` and `soundtrack.py`. Check it's installed first. This skill adds the Hive kit, the demo structure and the patterns.

| File | What it is |
|---|---|
| `templates/hive-demo.html` | A complete, working demo (the "Google Chat can prepare emails and meetings" release). It has the Hive shell (sidebar, top bar, footer), Today and Review pages, a generic chat window, flying items, a cursor, a camera, captions, "also in this release" cards and an end card. **Copy it and edit it**; don't start from a blank page. |
| `templates/storyboard-example.md` | The storyboard that demo was built from. Match its shape. |
| `reference/hive-look.md` | Hive's tokens, type, shell measurements and component classes, sampled from production screenshots. Verify them against the repo. |
| `reference/demo-patterns.md` | The motion patterns (before → after, fly-to-where-it-lands, cursor click → state change, camera zoom, count steps), with where each lives in the template. |
| `scripts/new_demo.sh` | Scaffolds `~/hive-demos/<slug>/` with fonts, Playwright and the template. |

## Workflow

1. **Read the feature.** The input is a description, or a release entry (in the Hive repo, `frontend/src/data/releaseNotes.ts` feeds `/whats-new`). Split it into:
   - **The hero change:** the one with a user-facing part. Name the surface (a Hive page, the Sayya panel, Google Chat, Slack, Telegram or email), the trigger (what the user does) and the visible result.
   - **Secondary changes:** backend fixes and small things. They go into one "also in this release" beat, one line each, in the release note's own words.
   - **No user-facing part at all?** Say so, and propose an "also in this release"-style card instead of inventing UI.

2. **Ground it in the real product** (read; don't change the repo):
   - Find the screens involved: grep `frontend/src` for the route, page and component names and for strings from the feature. Read the page component and its children for layout, labels, button text, empty and done states, and the order of things.
   - Read the new-look theme: `frontend/packages/ui-kit/tokens.css` under `html[data-look="new"][data-theme="dark"]` on local `qa` (`git show qa:...`), and check it against `reference/hive-look.md`. Where the repo differs, the repo wins: update the template's `:root`. Build demos in the new look, not the old default theme.
   - If the person gave screenshots, they're the ground truth for the look. If the dev server runs without a login wall (`npm run dev`, usually `localhost:5173`), screenshot the real pages with Playwright for reference. If it doesn't, rebuild from the code.
   - Use only behaviour the code or the release note supports. When a screen you need doesn't exist yet, build it from Hive's existing components and say so in the handoff.

3. **Storyboard** (`storyboard.md`, same shape as the example). The default structure for 15–20 s:

   | Beat | Length | What happens |
   |---|---|---|
   | Title | ~2.3 s | Kicker "WHAT'S NEW IN HIVE · <date>"; the release title types on over the dimmed shell |
   | Trigger | 4–5 s | Where the user acts. Type the ask, click the button. Show **before → after** when the note says "instead of", "again" or "now" |
   | Effect in Hive | 5–6 s | The result lands where it lives (items fly into a nav badge or list; counts step). The cursor acts, the camera zooms in, and states change to done with a chime |
   | Also in this release | ≤ 3.5 s | Secondary changes as one or two cards, each acted out (a spinner settling green, an item sliding into "In review") |
   | End | ~2 s | Hive mark · "What's new · <date>" |

   Rules:
   - At most three numbered captions, seven words or fewer each.
   - Every beat has motion that explains (see `reference/demo-patterns.md` and the video-studio skill's motion-craft guide).
   - **Use invented sample data by default**: fictional people and companies. Never use real customer, prospect, employee or personal data unless the person asks for an internal-only cut.
   - Third-party products (Google Chat, Slack, HubSpot) appear as a generic window or chip labelled with the product's name: **no third-party logos or lookalike branding**.
   - Show the storyboard, then build without waiting, unless the person asked to approve it first.

4. **Scaffold and build.** Run `bash ~/.claude/skills/hive-feature-demo/scripts/new_demo.sh <slug>`. It works in `~/hive-demos/<slug>/`, **never inside the Hive repo**. Edit `demo.html`:
   - Keep the shell. Swap the page sections for the screens you need, rebuilt from the repo's components.
   - Rewrite `timeline.js`, which is inlined at the bottom of the template as the "Timeline" block, beat by beat.
   - Cursor and camera targets are measured from the layout with `pos(el, cam)`, so they survive layout changes. Don't hard-code pixel targets for buttons.

5. **Look before rendering.** Render stills at the busiest moment of each beat (`node ~/.claude/skills/video-studio/scripts/render_html.mjs demo.html --stills 1.6,4,6.9,9.3,11.4,15.6,18.9 --out work/stills`), put them on one contact sheet, and look at it. Fix overflow, collisions, captions covering the action, anything appearing early (a to-only tween starts from the natural state), and empty frames.

6. **Render at 1440p.** `node ~/.claude/skills/video-studio/scripts/render_html.mjs demo.html --out renders/<slug>.mp4 --scale 4/3 --crf 14 --preset slow --workers 4`. The page keeps its 1920×1080 layout and is drawn at 2560×1440. This also writes `renders/<slug>.cues.json`. Never deliver below 1920×1080 (Rohit's call, 17 Nov 2026). For YouTube, finish with `hive-release-videos`' `scripts/youtube_encode.sh`, which fits the best quality into the 10 MB browser upload.

7. **Score.** `python3 ~/.claude/skills/video-studio/scripts/soundtrack.py renders/<slug>.mp4 --music afrohouse --drop <trigger start> --outro <end-card length> --loudness -15.2 --out renders/<slug>-sound.mp4`. Use `--music <track>` for the house track. Cue conventions, declared in the timeline:
   - `click` on every cursor press;
   - `tick` when prepared items or rows land;
   - `ding` on each achievement (sent, booked, approved, fixed, submitted);
   - `hit` at gain 0.45 on the "before" failure;
   - `whoosh` at gain 0.4–0.6 on beat changes.

8. **Check, then deliver.**
   - **Frames:** a frame grid across the beats.
   - **Sound:** loudness -14 ±1 LUFS with true peak under -1 dBTP, and a jump in chime-band energy at each ding (method in the video-studio skill).
   - **Safety:** no real names, no third-party logos.
   - **Length:** 15–20 s.
   - **Deliver:** the MP4 plus one line per beat, and anything you had to invent because the repo didn't have it.

## Defaults

Laid out at 1920×1080 and rendered at 2560×1440 (`--scale 4/3`), 30 fps, about 19.5 s. 1920×1080 is the minimum output. Hive dark theme. IBM Plex Sans, Sans Condensed and Mono. Afro house bed, drop at the trigger beat, drums out for the end card.
