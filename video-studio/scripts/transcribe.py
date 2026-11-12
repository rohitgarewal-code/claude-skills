#!/usr/bin/env python3
"""Transcribe a video/audio file with word-level timestamps.

Writes to --out (default: <input stem>_work/):
  words.json      {"source", "duration", "language", "words":[{"w","s","e","p"}], "segments":[{"s","e","text"}]}
  transcript.srt  sentence-level subtitles of the raw recording
  transcript.txt  plain text with [mm:ss] markers every segment

Backends, tried in order unless --backend is given:
  mlx      mlx-whisper (fastest on Apple Silicon)   pip install mlx-whisper
  faster   faster-whisper (CPU/GPU, any OS)         pip install faster-whisper
  openai   OpenAI API whisper-1 (needs OPENAI_API_KEY, files < 25 MB of audio)

Usage: transcribe.py raw.mp4 [--model large-v3-turbo] [--language en] [--out work/]
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path


def sh(*a):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def extract_audio(src, dst):
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", dst)


def run_mlx(wav, model, lang):
    import mlx_whisper  # noqa
    repo = model if "/" in model else f"mlx-community/whisper-{model}"
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=repo, word_timestamps=True, language=lang)
    segs, words = [], []
    for s in r["segments"]:
        segs.append({"s": s["start"], "e": s["end"], "text": s["text"].strip()})
        for w in s.get("words", []):
            words.append({"w": w["word"].strip(), "s": w["start"], "e": w["end"], "p": w.get("probability", 1.0)})
    return words, segs, r.get("language", lang)


def run_faster(wav, model, lang):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="auto", compute_type="auto")
    it, info = m.transcribe(wav, word_timestamps=True, language=lang, vad_filter=False,
                            condition_on_previous_text=False)
    segs, words = [], []
    for s in it:
        segs.append({"s": s.start, "e": s.end, "text": s.text.strip()})
        for w in s.words or []:
            words.append({"w": w.word.strip(), "s": w.start, "e": w.end, "p": w.probability})
    return words, segs, info.language


def run_openai(wav, model, lang):
    from openai import OpenAI
    client = OpenAI()
    mp3 = wav.replace(".wav", ".mp3")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "64k", mp3)
    with open(mp3, "rb") as f:
        r = client.audio.transcriptions.create(model="whisper-1", file=f, response_format="verbose_json",
                                               timestamp_granularities=["word", "segment"], language=lang)
    words = [{"w": w.word.strip(), "s": w.start, "e": w.end, "p": 1.0} for w in r.words]
    segs = [{"s": s.start, "e": s.end, "text": s.text.strip()} for s in r.segments]
    return words, segs, r.language


def ts(t, sep=","):
    h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)) % 1000:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--language", default=None)
    ap.add_argument("--backend", choices=["mlx", "faster", "openai"])
    ap.add_argument("--out")
    a = ap.parse_args()
    out = Path(a.out or Path(a.input).with_suffix("").as_posix() + "_work")
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "audio.wav")
        extract_audio(a.input, wav)
        order = [a.backend] if a.backend else ["mlx", "faster", "openai"]
        last = None
        for b in order:
            try:
                fn = {"mlx": run_mlx, "faster": run_faster, "openai": run_openai}[b]
                print(f"transcribing with {b} ({a.model})...", file=sys.stderr)
                words, segs, lang = fn(wav, a.model, a.language)
                break
            except ImportError as e:
                last = e
                continue
        else:
            sys.exit(f"No transcription backend installed ({last}). Try: pip install mlx-whisper  (Apple Silicon) "
                     f"or pip install faster-whisper")

    words = [w for w in words if w["w"]]
    data = {"source": str(Path(a.input).resolve()), "duration": duration_of(a.input), "language": lang,
            "words": words, "segments": segs}
    (out / "words.json").write_text(json.dumps(data, indent=1))
    with open(out / "transcript.srt", "w") as f:
        for i, s in enumerate(segs, 1):
            f.write(f"{i}\n{ts(s['s'])} --> {ts(s['e'])}\n{s['text']}\n\n")
    with open(out / "transcript.txt", "w") as f:
        for s in segs:
            f.write(f"[{int(s['s'] // 60):02d}:{int(s['s'] % 60):02d}] {s['text']}\n")
    print(f"{len(words)} words, {len(segs)} segments -> {out}/words.json")


if __name__ == "__main__":
    main()
