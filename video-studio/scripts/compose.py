#!/usr/bin/env python3
"""Lay animated overlays, captions and music onto an edited video in one encode.

  compose.py work/edit.mp4 --out final.mp4 \
      --overlay work/ov_title.mov@0 --overlay work/ov_stat.mov@42.5 --overlay work/logo.mov@0@1600,60 \
      --captions work/captions.ass --fontsdir fonts \
      --music bed.mp3 --music-db -20 [--no-duck] [--loudness -14]

--overlay FILE@START[@X,Y]  a transparent .mov from render_html.mjs --alpha (full-frame unless X,Y given),
                            placed at START seconds on the edited timeline. Repeat for each overlay.
--captions FILE.ass         burned in last, above the overlays.
--music FILE                looped/trimmed to the video, set to --music-db, and ducked under the voice.
"""
import argparse, os, subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--overlay", action="append", default=[])
    ap.add_argument("--captions")
    ap.add_argument("--fontsdir")
    ap.add_argument("--music")
    ap.add_argument("--music-db", type=float, default=-20)
    ap.add_argument("--no-duck", action="store_true")
    ap.add_argument("--loudness", type=float, default=-14)
    ap.add_argument("--crf", default="18")
    ap.add_argument("--preset", default="veryfast")
    a = ap.parse_args()

    inputs = ["-i", a.video]
    f, v = [], "[0:v]"
    for i, spec in enumerate(a.overlay, start=1):
        bits = spec.split("@")
        path, start = bits[0], float(bits[1]) if len(bits) > 1 else 0.0
        x, y = (bits[2].split(",") if len(bits) > 2 else ("0", "0"))
        inputs += ["-i", path]
        f.append(f"[{i}:v]setpts=PTS-STARTPTS+{start}/TB[o{i}]")
        f.append(f"{v}[o{i}]overlay=x={x}:y={y}:eof_action=pass:format=auto[v{i}]")
        v = f"[v{i}]"
    if a.captions:
        cap = a.captions.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        fd = f":fontsdir={a.fontsdir}" if a.fontsdir else ""
        f.append(f"{v}ass='{cap}'{fd}[vcap]")
        v = "[vcap]"
    f.append(f"{v}format=yuv420p[vout]")

    has_audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout.strip() != ""
    amap = []
    if a.music:
        mi = len(a.overlay) + 1
        inputs += ["-stream_loop", "-1", "-i", a.music]
        if has_audio:
            f.append("[0:a]asplit=2[voice][key]")
            f.append(f"[{mi}:a]volume={a.music_db}dB[bed]")
            if a.no_duck:
                f.append("[bed]anull[ducked]")
            else:
                f.append("[bed][key]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[ducked]")
            f.append("[voice][ducked]amix=inputs=2:duration=first:normalize=0[mix]")
        else:
            f.append(f"[{mi}:a]volume={a.music_db}dB[mix]")
        f.append(f"[mix]loudnorm=I={a.loudness}:TP=-1.5:LRA=11,aresample=48000[aout]")
        amap = ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    elif has_audio:
        amap = ["-map", "0:a", "-c:a", "copy"]

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                         capture_output=True, text=True, check=True).stdout.strip()
    out = Path(a.out)
    tmp = str(out.with_name(out.stem + ".tmp" + out.suffix))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats", *inputs, "-filter_complex", ";".join(f),
           "-map", "[vout]", *amap, "-c:v", "libx264", "-preset", a.preset, "-crf", a.crf,
           "-t", dur, "-movflags", "+faststart", tmp]
    subprocess.run(cmd, check=True)
    os.replace(tmp, out)
    print(out)


if __name__ == "__main__":
    main()
