#!/usr/bin/env python3
"""Render the edit described by edl.json and remap word timings to the new timeline.

  apply_edl.py work/edl.json --out work/edit.mp4 [--words work/words.json] [--clean] [--loudness -14]
               [--fps 30] [--height 1080] [--crf 18] [--preset veryfast] [--proxy]

--clean     light voice cleanup: 80 Hz high-pass + gentle FFT denoise
--loudness  integrated loudness target in LUFS (-14 social / YouTube, -16 podcasts); 0 to skip
--proxy     fast 540p preview render (use it to check the cut before the full render)

A keep entry may carry options: [start, end, {"zoom": 1.12}] punches in (centre crop) for that segment,
the usual way to hide a jump cut. cutlist.py --punch 1.12 sets this on alternate segments.

Every segment gets 12 ms audio fades so cuts don't click. Writes edit.mp4 and words_edited.json
(the kept words on the edited timeline, for captions and for timing overlays).
"""
import argparse, json, os, subprocess, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--out")
    ap.add_argument("--words")
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--loudness", type=float, default=-14)
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--height", type=int, default=0, help="output height (keeps aspect); 0 = source")
    ap.add_argument("--crf", default="18")
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--proxy", action="store_true")
    a = ap.parse_args()

    edl = json.loads(Path(a.edl).read_text())
    work = Path(a.edl).parent
    out = Path(a.out or work / ("edit_proxy.mp4" if a.proxy else "edit.mp4"))
    keep = [k[:2] for k in edl["keep"]]
    zooms = [(k[2].get("zoom", 1.0) if len(k) > 2 and isinstance(k[2], dict) else 1.0) for k in edl["keep"]]
    if not keep:
        sys.exit("EDL has no segments")
    fade = 0.012
    W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0:s=x", edl["source"]],
                                   capture_output=True, text=True, check=True).stdout.strip().split("x")[:2])

    parts, vlabels = [], []
    n = len(keep)
    parts.append(f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n)))
    parts.append(f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n)))
    for i, (s, e) in enumerate(keep):
        d = e - s
        z = zooms[i]
        punch = f",crop=iw/{z}:ih/{z},scale={W}:{H}:flags=lanczos,setsar=1" if z and abs(z - 1) > 1e-3 else ",setsar=1"
        parts.append(f"[vs{i}]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS{punch}[v{i}]")
        parts.append(f"[as{i}]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={fade}:st=0,afade=t=out:d={fade}:st={max(0, d - fade):.3f}[a{i}]")
        vlabels.append(f"[v{i}][a{i}]")
    parts.append("".join(vlabels) + f"concat=n={n}:v=1:a=1[vc][ac]")

    vchain = [f"fps={a.fps}"]
    h = 540 if a.proxy else a.height
    if h:
        vchain.append(f"scale=-2:{h}:flags=lanczos")
    vchain.append("format=yuv420p")
    parts.append(f"[vc]{','.join(vchain)}[vout]")

    achain = []
    if a.clean:
        achain += ["highpass=f=80", "afftdn=nr=10:nf=-30:tn=1"]
    if a.loudness and not a.proxy:
        achain.append(f"loudnorm=I={a.loudness}:TP=-1.5:LRA=11")
    achain.append("aresample=48000")
    parts.append(f"[ac]{','.join(achain)}[aout]")

    tmp = str(out.with_name(out.stem + ".tmp" + out.suffix))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats", "-i", edl["source"],
           "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "ultrafast" if a.proxy else a.preset, "-crf", "28" if a.proxy else a.crf,
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp]
    subprocess.run(cmd, check=True)
    os.replace(tmp, out)

    # remap words to the edited timeline
    wpath = Path(a.words) if a.words else work / "words.json"
    if wpath.exists():
        words = json.loads(wpath.read_text())["words"]
        offs, acc = [], 0.0
        for s, e in keep:
            offs.append(acc); acc += e - s
        new = []
        for w in words:
            mid = (w["s"] + w["e"]) / 2
            for (s, e), off in zip(keep, offs):
                if s <= mid <= e:
                    new.append({**w, "s": round(max(w["s"], s) - s + off, 3), "e": round(min(w["e"], e) - s + off, 3)})
                    break
        new.sort(key=lambda w: w["s"])  # keep may be reordered (cold open)
        (work / "words_edited.json").write_text(json.dumps({"duration": round(acc, 3), "words": new}, indent=1))
        print(f"{out}  ({acc:.1f}s, {len(new)} words remapped -> {work}/words_edited.json)")
    else:
        print(out)


if __name__ == "__main__":
    main()
