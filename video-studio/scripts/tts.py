#!/usr/bin/env python3
"""Voiceover for explainers: one audio clip per scene, their lengths, and (optionally) the placed VO track.

  tts.py vo.json --out vo/ [--engine elevenlabs|say] [--voice ID_OR_NAME]
  tts.py vo.json --out vo/ --layout starts.json      # also writes vo/vo_track.wav with each line at its start

vo.json:     {"lines": [{"id": "s1", "text": "Every team is building its own AI tools."}, ...]}
starts.json: {"s1": 0.4, "s2": 6.2, ...}  seconds on the video timeline (usually scene start + 0.3)
Writes vo/<id>.wav and vo/durations.json — set each scene's length to at least its line + 0.8 s.

Engines:
  elevenlabs  needs ELEVENLABS_API_KEY; --voice is a voice ID (or ELEVENLABS_VOICE_ID). Real, natural VO.
  say         macOS built-in, offline. Scratch VO for timing only, never for a final cut.
If the person records their own VO, skip this script: cut their recording per line and use durations from ffprobe.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "48000", str(dst)], check=True)


def eleven(text, voice, dst):
    key = os.environ.get("ELEVENLABS_API_KEY")
    voice = voice or os.environ.get("ELEVENLABS_VOICE_ID")
    if not key or not voice:
        sys.exit("Set ELEVENLABS_API_KEY and pass --voice <voice id> (or ELEVENLABS_VOICE_ID)")
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r, tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(r.read()); tmp = f.name
    to_wav(tmp, dst); os.unlink(tmp)


def say(text, voice, dst):
    if not shutil.which("say"):
        sys.exit("'say' is macOS only. Use --engine elevenlabs or record the VO.")
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
        tmp = f.name
    subprocess.run(["say", "-v", voice or "Samantha", "-o", tmp, text], check=True)
    to_wav(tmp, dst); os.unlink(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vo")
    ap.add_argument("--out", default="vo")
    ap.add_argument("--engine", choices=["elevenlabs", "say"], default=None)
    ap.add_argument("--voice")
    ap.add_argument("--layout")
    ap.add_argument("--total", type=float, help="length of the placed track (default: last line end + 1 s)")
    a = ap.parse_args()
    engine = a.engine or ("elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "say")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    lines = json.loads(Path(a.vo).read_text())["lines"]
    durations = {}
    for ln in lines:
        dst = out / f"{ln['id']}.wav"
        if not dst.exists():
            (eleven if engine == "elevenlabs" else say)(ln["text"], a.voice, dst)
        durations[ln["id"]] = round(dur(dst), 3)
        print(f"{ln['id']}: {durations[ln['id']]:.2f}s  {ln['text'][:60]}")
    (out / "durations.json").write_text(json.dumps(durations, indent=1))

    if a.layout:
        starts = json.loads(Path(a.layout).read_text())
        ids = [l["id"] for l in lines if l["id"] in starts]
        total = a.total or max(starts[i] + durations[i] for i in ids) + 1.0
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for i in ids:
            cmd += ["-i", str(out / f"{i}.wav")]
        f = [f"[{k}:a]adelay={int(starts[i] * 1000)}:all=1[d{k}]" for k, i in enumerate(ids)]
        f.append("".join(f"[d{k}]" for k in range(len(ids))) + f"amix=inputs={len(ids)}:normalize=0,apad,atrim=0:{total:.3f}[a]")
        cmd += ["-filter_complex", ";".join(f), "-map", "[a]", "-ar", "48000", str(out / "vo_track.wav")]
        subprocess.run(cmd, check=True)
        print(f"placed track -> {out / 'vo_track.wav'} ({total:.1f}s)")


if __name__ == "__main__":
    main()
