# Vlog and footage editing

## Getting the footage

The raw file lives on the person's machine or in their Drive. Work on a copy in `videos/<slug>/`. Never edit the original. Phone footage is often variable frame rate and HEVC; `apply_edl.py` normalises to a constant `--fps` and H.264.

## The paper edit is the edit

`cutlist.py` handles the mechanical part: pauses, um/uh and repeated-phrase false starts. The editorial part is yours. Read `transcript.txt` and decide:

- **Hook**: the first 3–5 s must state why to keep watching. If the best line is at 2:40, open with it (cold open) and then return.
- **Spine**: the 3–5 points the piece actually makes. Cut tangents that don't serve them, even good ones (offer them as separate shorts).
- **Retakes**: when the person says a line twice, keep the better (usually the last) take. Check `removed` in `edl.json` to make sure the detector picked the abandoned one.
- **Ending**: end on the strongest line, not on "so yeah, that's it".
- Target about 60–70% of raw length for a typical talking-head vlog.

Edit `edl.json` directly to reorder, which is how you do a cold open. `keep` is played in list order, so move a segment to the front. `apply_edl.py` remaps words correctly for any order because it maps each word to the segment that contains it.

Show `paper_edit.md` plus a 3-line summary, then wait for approval before the full render.

## Audio

- `--clean` = 80 Hz high-pass + gentle FFT denoise. Don't stack heavier denoise; it makes voices sound underwater.
- Loudness: -14 LUFS integrated for YouTube, LinkedIn and Instagram; -16 for podcasts. True peak -1.5 dB.
- Music: 18–22 dB under the voice, ducked (compose.py does this). Only use music the person supplied or licensed.

## Overlays tied to speech

Build the overlay map from `words_edited.json`. Find the phrase, take its first word's `s` as the anchor, and land the overlay 0.1–0.2 s before it.

| Overlay | When | Placement | Length |
|---|---|---|---|
| Title card | 0–3 s | full frame, or top third over footage | 2.5–3.5 s |
| Lower third (name, role) | first time the speaker appears | bottom-left safe area | 4–5 s |
| Keyword pop | the 3–6 phrases that matter most | the empty side of frame, opposite the face | 1.5–2.5 s |
| Concept diagram / number | when a mechanism or figure is said | half-frame panel on the empty side, or full-frame cutaway | 4–8 s |
| Chapter card | between sections | full-frame cutaway or corner tag | 1.5–2 s |
| End card | last 4–6 s | full frame | 4–6 s |

Build each as a transparent page from `templates/scene.html`, then render with `node render_html.mjs ov_x.html --alpha --out work/ov_x.mov`. Find the face position by pulling a few frames and viewing them, and keep overlays clear of it. For a full-frame cutaway, give the page an opaque background (no `--alpha` needed) and overlay it the same way.

## Captions

- 16:9 talking head: `--style clean`, bottom, two lines at most.
- 9:16 social: `--style pop --upper` optional, middle or lower-middle, 3–4 words at a time.
- Check the brand font is installed or in `fonts/` (pass `--fontsdir fonts` to compose.py), or libass silently falls back.
- Always also deliver the `.srt` so platforms can show native captions.

## Versions

- **9:16 from 16:9**: centre crop `crop=ih*9/16:ih,scale=1080:1920`. If the speaker isn't centred, offset x: `crop=ih*9/16:ih:X:0`. Pull frames to find X. Re-run captions at `--width 1080 --height 1920`, and re-render overlays at 1080×1920. Don't reuse the 16:9 ones.
- **Cut-downs (30/60 s)**: make a new EDL from the same `words.json` (copy `edl.json`, keep only the best segments) and render it. Hook first, one point, end card.
- **Thumbnail**: a still frame with a big 3–5 word headline, made as a one-scene page rendered with `--stills`.

## Useful ffmpeg one-liners

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact in.mov
ffmpeg -ss 00:01:23.4 -i edit.mp4 -frames:v 1 frame.png                           # look at a moment
ffmpeg -i in.mp4 -af loudnorm=print_format=summary -f null - 2>&1 | tail -12      # measure loudness
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy vertical.mp4     # reframe
ffmpeg -i in.mp4 -vf scale=-2:540 -c:v libx264 -crf 28 -preset ultrafast small.mp4  # share-size proxy
```
