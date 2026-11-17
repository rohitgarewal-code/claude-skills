---
name: video-studio
description: Make and edit videos. Builds motion-graphics explainers, animated charts and product walkthroughs as code and renders them to MP4. Also edits raw vlog and talking-head footage: transcribe, tighten the cut, add captions, add animated overlays tied to what is being said, add music, and make vertical or short versions. Use when asked to make, animate, storyboard, render, edit, caption or cut down a video.
---

# Video Studio

Two kinds of job, one toolkit:

- **Explainer**: an animation built from nothing (titles, diagrams, numbers, product UI). It is written as a seekable HTML page and rendered frame by frame to MP4.
- **Vlog edit**: the person's own footage. Transcribe it, propose a paper edit, cut it, then layer captions, animated overlays and music on top.

Both are motion graphics written as code, like Claude Motion. Neither generates footage. Never invent realistic people, places or B-roll. If a shot needs real footage, ask for it or say it's missing.

The quality comes from the **storyboard**, not the renderer. Two habits separate a good explainer from animated slides, and both are mandatory: **functional motion** (each scene's movement acts out its sentence: things pile up at a blocker, lanes merge, one bar splits into many) and **continuity** (one persistent frame with a section counter, where scenes clear and rebuild inside it instead of crossfading). Read the first two sections of `references/motion-craft.md` before storyboarding. Never start building before the storyboard (or the paper edit) is agreed, unless the person explicitly says to skip it.

## Toolkit

All paths are relative to this skill's folder (`~/.claude/skills/video-studio/`).

| Script | Does |
|---|---|
| `templates/scene.html` | Starter page with a tiny deterministic timeline engine (`Motion.scene`, `Motion.tween`), brand tokens and a preview player. Copy it into the project. |
| `scripts/render_html.mjs` | Renders the page to MP4 (parallel workers), to transparent ProRes 4444 (`--alpha`, for overlays), or to PNG stills (`--stills`). Can mux audio. `--scale 4/3` draws the 1920×1080 layout at 2560×1440, the default for anything bound for YouTube. Output is always TV-range BT.709. |
| `scripts/soundtrack.py` | Scores a rendered video: an original generated Afro house bed (`--music afrohouse`) or a supplied track, plus effects on the page's cues (chimes for achievements that step up the scale, ticks, swooshes). Mixes to -14 LUFS and muxes without re-encoding the video. |
| `scripts/tts.py` | Voiceover per scene (ElevenLabs if `ELEVENLABS_API_KEY` is set, macOS `say` as scratch), durations, and a placed VO track. |
| `scripts/transcribe.py` | Word-timed transcript (`mlx-whisper` on Apple Silicon, else `faster-whisper`, else the OpenAI API). |
| `scripts/cutlist.py` | Proposed edit: long pauses shortened, um/uh dropped, false starts dropped. Writes `edl.json` and `paper_edit.md`; `--punch` adds jump-cut zooms. |
| `scripts/apply_edl.py` | Renders the edit with click-free cuts, optional voice cleanup and loudness, and remaps word timings. `--proxy` gives a fast 540p check. |
| `scripts/captions.py` | `.ass` (burn-in) and `.srt` (sidecar) captions: `clean` or `pop` (spoken word highlighted). |
| `scripts/compose.py` | One encode that lays overlays at timestamps, burns captions, and ducks a music bed under the voice. |

References, read when you reach that step:
- `references/storyboard.md`: the storyboard format and the brief questions. Read before any explainer.
- `references/motion-craft.md`: type scale, timing, easing, transitions, diagram patterns, the `Motion` API. Read before writing scene.html.
- `references/vlog-editing.md`: the vlog pipeline in detail, overlay patterns, vertical cuts, ffmpeg recipes. Read before any footage edit.

## One-time setup (check, don't assume)

```bash
which ffmpeg ffprobe node python3                 # brew install ffmpeg node   (Homebrew ffmpeg includes libass)
ffmpeg -hide_banner -filters | grep -E " ass |sidechaincompress"   # captions + ducking need these
```

Per project folder:
```bash
npm init -y >/dev/null && npm i -D playwright @fontsource-variable/inter @fontsource/jetbrains-mono
npx playwright install chromium                   # or pass --chrome "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p fonts && cp node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2 \
  node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2 fonts/
```
For transcription: `pip install mlx-whisper` (Apple Silicon) or `pip install faster-whisper`. The first run downloads the model.
On Rohit's Mac mini, mlx-whisper, numpy and scipy are installed in this skill's own venv: run `~/.claude/skills/video-studio/.venv/bin/python scripts/transcribe.py ...` (and `soundtrack.py`), not `python3`. ffmpeg there is Homebrew's `ffmpeg-full` (has libass), linked in place of `ffmpeg`.

Fonts load from `./fonts`, so renders look the same on every machine. Use other brand fonts the same way: woff2 files in `fonts/` and an `@font-face` in the page.

## Brands

`brands/<name>/` holds ready-made brand packs: a README (tokens, rules, when to use it), CSS and components as code, and a demo page. When the person names a brand, read its README first, copy its files into the project, and build with its components instead of drawing your own. Available: **launch-control** (Hive's dark program-map look, also called the program-tracker style).

Watch the render output for `[page]` warnings. Brand components warn when text doesn't fit its card. Fix every warning before the full render.

## Project layout

Make one folder per video, e.g. `videos/<slug>/`:
```
brief.md          storyboard.md     scene.html      fonts/      assets/    (logos, screenshots the person gave you)
vo/               work/             renders/        brand.json (optional: colors, fonts, logo path)
```
If `brand.json` exists, or the person names a brand or design system, set the `:root` tokens from it. Otherwise use the template's neutral palette and say so. Never draw a third-party logo from memory. Only use logo files you were given.

## Workflow A: explainer

1. **Brief.** Settle viewer, the 1–3 things it must land, where it plays (sound on or off), length, format (16:9 1920×1080, 9:16 1080×1920, 1:1 1080×1080) and tone. Ask only what you can't infer. Read `references/storyboard.md`.
2. **Storyboard → approval gate.** Write `storyboard.md`. It has the scene list table (in, length, scene, "viewer leaves with", transition), then per-scene frame, verbatim on-screen text, **the motion that explains** (the sentence's verb and how it's acted out), animation notes with durations and easing, the VO line, plus the persistent frame, a visual system and guardrails. Keep the people and sources the material names. Show it and wait for a yes or for edits. Unless told otherwise, at 30 fps a 60 s video is 6–9 scenes.
3. **Voiceover (if sound-on).** Put the VO lines in `vo.json` and run `tts.py`. Each scene must be at least `VO length + 0.8 s`, so fix the scene timings from `durations.json` before building. If the person will record the VO, build to the storyboard timings and leave audio for later.
4. **Build.** Copy `templates/scene.html` and set the tokens. Write one `<section class="scene">` per scene and declare the timeline. Rules: everything is a pure function of time, so no CSS transitions, `setTimeout` or `Date.now()`. Keep text exactly as storyboarded. Use one accent color per scene. Respect the 96 px safe margin. Nothing smaller than 28 px at 1080p. Read `references/motion-craft.md`.
5. **Look before rendering.** Render stills at the busiest moment of each scene and at every transition midpoint (`--stills 2.4,7.9,...`), combine them into one contact sheet, and *look at it*. Fix overflow, collisions, wrong wraps and empty frames now. Also open `scene.html` in a browser and scrub through it.
6. **Sound.** Unless the brief says sound-off, declare cues in the timeline as you build: `Motion.cue(t, 'ding')` on every achievement (something lands Done, a target is hit, a figure lands), `'tick'` for rows or counts landing, and `'whoosh'` (gain 0.5–0.7) on scene changes. Never put a chime on bad news; a blocker gets silence or `'hit'`. Launch Control's Done nodes cue their own chime.
7. **Render once.** `node render_html.mjs scene.html --out renders/v1.mp4` (add `--workers N` on big machines). It also writes `renders/v1.cues.json`.
8. **Score.** `python3 soundtrack.py renders/v1.mp4 --music afrohouse --drop <first content scene start> --outro <close length>` → `renders/v1-sound.mp4`. If the person has a house track (licensed), use `--music track.mp3` instead. Re-scoring never re-renders the video. With voiceover, mix the VO in with compose.py afterwards, or lower `--music-db` to about -26.
9. **Check** (below), then deliver: the MP4 path, its length, and anything you couldn't follow.

## Workflow B: vlog / footage edit

1. **Probe** with `ffprobe` (length, resolution, fps, rotation, audio). For phone footage, check whether it's vertical.
2. **Transcribe**: `python3 transcribe.py raw.mov --out work/`. Read `work/transcript.txt` to understand the piece.
3. **Paper edit → approval gate**: run `cutlist.py work/words.json` (add `--punch 1.1` for jump-cut zooms). Then go further than the script does. Read the transcript as an editor would: find the story, the hook in the first 5 s, tangents to drop and the best ending. Add those as `--drop` ranges or by editing `edl.json`. Show `paper_edit.md` with a short summary (source length → new length, what you cut and why). Wait for a yes.
4. **Proxy check**: `apply_edl.py work/edl.json --proxy` and watch the cut points. Then do the full render with `--clean` if the audio is noisy.
5. **Animation plan → approval gate** (skip if the person only wants a cut). Map overlays to timestamps on the *edited* timeline using `work/words_edited.json`. Typical overlays: a title card in the first 3 s, a lower third with name and role, keyword pops on key phrases, a diagram or number when a concept or figure is mentioned, a chapter card between sections, and an end card. Present the overlays as a table (time, words they're tied to, overlay, length).
6. **Build overlays** as one transparent page per overlay (or one page with several timed sections) and render with `--alpha`. Keep them out of the speaker's face. Lower thirds sit in the bottom-left safe area; keyword pops go in the empty side of the frame.
7. **Captions**: `captions.py work/words_edited.json --style clean` (16:9) or `--style pop` (vertical/social). Match `--width/--height` to the video.
8. **Compose**: `compose.py work/edit.mp4 --out renders/final.mp4 --overlay ov1.mov@0 ... --captions work/captions.ass --fontsdir fonts [--music bed.mp3]`.
9. **Versions** on request: 9:16 reframe, 30–60 s cut-downs (a new EDL from the same words), a thumbnail still. See `references/vlog-editing.md`.

## Checks before you say it's done

- **Frames:** pull 6–10 frames from the final file (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.png`) at scene midpoints, transitions and overlay moments, and view them. Look for clipped text, overlaps, empty frames, and overlays covering faces.
- **Spec:** every scene against its storyboard row (start, length, transition). On-screen text matches word for word, and no banned word from the guardrails appears.
- **Numbers:** every figure on screen traces to a source the person gave. Never round up or invent one.
- **Sound:** you can't listen, so measure it. Integrated loudness near -14 LUFS with true peak under -1 dBTP. Chime-band (2.2–6 kHz) energy should jump at each ding cue, and low-band energy should jump at `--drop`. Look at a spectrogram (`showspectrumpic`) of the busiest stretch.
- **File:** `ffprobe` duration is as planned; size, fps and audio stream are as expected. For sound-on video, `ffmpeg -i out.mp4 -af loudnorm=print_format=summary -f null -` reads near -14 LUFS.
- **Functional motion:** for each content scene, compare a mid-motion frame with the last frame. If the motion added nothing, rework the scene before delivering.
- **Reading time:** every text block is held at least 1 s plus about 0.3 s per word after it finishes animating in.
- Say plainly what you could not do (missing footage, a voice you couldn't generate, a font you substituted).

## Changing a finished video

- One scene changed: re-render only that range (`--from 12.5 --to 21`) to a part file, then splice with the concat demuxer. If a crossfade crosses the boundary, re-render from the previous scene's start.
- New sound or a shorter end: `ffmpeg -i v.mp4 -i new.wav -map 0:v -map 1:a -c:v copy ...` (no re-render).
- New captions or a smaller copy: re-encode the finished file. Nothing needs redrawing.
- Many small text or number changes: edit `scene.html` and render once more. That's what code-as-video is for.

## Rendering rules

- Draw at the output size, at 30 fps unless asked for more. A 60 s 1080p render takes a few minutes. Use `--workers` up to about half your cores.
- Every script writes to a temporary name and renames on success. A file under its final name is always complete.
- Mixing parts: same size, fps and encoder settings, then join with `-f concat -c copy`. Put crossfades inside one render, never between finished files.
- Keep `work/` and `renders/` between sessions. Re-rendering one scene is cheap, a full rebuild isn't.

## Notes

- Remotion is an alternative renderer (React). Companies over 3 people need a paid Remotion company license, so this skill uses plain HTML + Playwright, which needs no license.
- `soundtrack.py --music afrohouse` composes an original groove in code (122 BPM, minor 9th chords, kick-sidechained). It is a genre bed, not a copy of any track. Seeds (`--seed`) give different grooves, and `--key` and `--bpm` change the feel.
- `tts.py` with `say` is scratch audio for timing only. A final cut needs the person's own VO or a real voice (ElevenLabs).
- The renderer also seeks plain CSS animations (`document.getAnimations()`) and calls `window.seek(t)` if a page defines it, so GSAP or canvas pages work too: `window.seek = t => tl.seek(t)`.
