#!/usr/bin/env python3
"""Make captions from word timings: an .ass file to burn in, plus an .srt sidecar for platforms.

  captions.py work/words_edited.json --out work/captions [--style clean|pop] [--width 1920 --height 1080]
              [--font "Inter"] [--size 54] [--color FFFFFF] [--accent D9481F] [--upper] [--position bottom|middle]

clean  two short lines, white with a soft outline, bottom of frame (talking-head 16:9)
pop    3-5 words at a time, the spoken word lit in the accent colour (vertical / social cuts)

Burn in:  ffmpeg -i edit.mp4 -vf "ass=work/captions.ass:fontsdir=fonts" -c:a copy captioned.mp4
(compose.py does this for you when given --captions.)
"""
import argparse, json, re
from pathlib import Path


def ass_color(hexrgb, alpha=0):
    h = hexrgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def t_ass(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def t_srt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = int(t % 60); ms = int(round((t % 1) * 1000)) % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chunk(words, max_chars, max_words, max_gap=0.45):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur:
            text_len = len(" ".join(x["w"] for x in cur + [w]))
            gap = w["s"] - cur[-1]["e"]
            if text_len > max_chars or len(cur) >= max_words or gap > max_gap or re.search(r"[.?!]$", cur[-1]["w"]):
                out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def split_lines(ws, max_line):
    text = " ".join(w["w"] for w in ws)
    if len(text) <= max_line:
        return [ws]
    best, bi = 1e9, 1
    for i in range(1, len(ws)):
        a = len(" ".join(w["w"] for w in ws[:i])); b = len(" ".join(w["w"] for w in ws[i:]))
        if max(a, b) < best:
            best, bi = max(a, b), i
    return [ws[:bi], ws[bi:]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("--out")
    ap.add_argument("--style", choices=["clean", "pop"], default="clean")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--font", default="Inter")
    ap.add_argument("--size", type=int)
    ap.add_argument("--color", default="FFFFFF")
    ap.add_argument("--accent", default="FFD23F")
    ap.add_argument("--upper", action="store_true")
    ap.add_argument("--position", choices=["bottom", "middle"], default=None)
    a = ap.parse_args()

    words = [dict(w) for w in json.loads(Path(a.words).read_text())["words"]]
    for w in words:
        w["w"] = w["w"].upper() if a.upper else w["w"]
    vertical = a.height > a.width
    pop = a.style == "pop"
    size = a.size or (int(a.height * (0.045 if vertical else 0.05)) if not pop else int(a.height * (0.05 if vertical else 0.065)))
    max_line = 18 if vertical else 38
    groups = chunk(words, max_chars=max_line if pop else max_line * 2, max_words=4 if pop else 14)
    pos = a.position or ("middle" if (pop and vertical) else "bottom")
    align = 5 if pos == "middle" else 2
    margin_v = int(a.height * (0.08 if not vertical else 0.22)) if pos == "bottom" else 0

    out = Path(a.out or Path(a.words).parent / "captions")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {a.width}
PlayResY: {a.height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{a.font},{size},{ass_color(a.color)},{ass_color(a.accent)},{ass_color('000000', 0x40)},{ass_color('000000', 0x80)},{-1 if pop else 0},0,0,0,100,100,0,0,1,{max(2, size // 14) if pop else max(2, size // 18)},{0 if pop else 1},{align},{int(a.width * 0.08)},{int(a.width * 0.08)},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events, srt = [], []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        nxt = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else g[-1]["e"] + 1.5
        end = min(max(g[-1]["e"] + 0.15, start + 0.8), nxt)
        lines = split_lines(g, max_line)
        srt.append(f"{gi + 1}\n{t_srt(start)} --> {t_srt(end)}\n" + "\n".join(" ".join(w["w"] for w in l) for l in lines) + "\n")
        if not pop:
            events.append(f"Dialogue: 0,{t_ass(start)},{t_ass(end)},Cap,,0,0,0,,"
                          + r"\N".join(" ".join(w["w"] for w in l) for l in lines))
            continue
        flat = [w for l in lines for w in l]
        for wi, w in enumerate(flat):
            ws = w["s"] if wi else start
            we = flat[wi + 1]["s"] if wi + 1 < len(flat) else end
            parts = []
            for li, l in enumerate(lines):
                parts.append(" ".join(
                    (f"{{\\c{ass_color(a.accent)}}}{x['w']}{{\\c{ass_color(a.color)}}}" if x is w else x["w"]) for x in l))
            pop_in = r"{\fscx104\fscy104\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
            events.append(f"Dialogue: 0,{t_ass(ws)},{t_ass(we)},Cap,,0,0,0,,{pop_in}" + r"\N".join(parts))
    out.with_suffix(".ass").write_text(head + "\n".join(events) + "\n")
    out.with_suffix(".srt").write_text("\n".join(srt))
    print(f"{len(groups)} captions -> {out}.ass, {out}.srt")


if __name__ == "__main__":
    main()
