#!/usr/bin/env python3
"""Propose a tight edit from words.json: trim long pauses, drop filler words and false starts.

Writes:
  edl.json        {"source", "keep": [[start, end], ...], "removed": [{"s","e","reason","text"}]}
  paper_edit.md   the kept script with every cut marked, for the person to approve before rendering

The EDL is a proposal. Edit edl.json by hand (or regenerate with different flags) before apply_edl.py.
You can also force cuts with --drop "12.4-18.9,61-64.5" (source seconds) or keep only --range 30-210.

Usage: cutlist.py work/words.json [--max-pause 0.7] [--keep-pause 0.3] [--no-fillers] [--no-restarts] [--punch 1.12]
"""
import argparse, json, re
from pathlib import Path

FILLERS = {"um", "uh", "erm", "er", "uhm", "umm", "hmm", "mm", "ah"}


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def parse_ranges(s):
    out = []
    for part in (s or "").split(","):
        if part.strip():
            a, b = part.split("-")
            out.append((float(a), float(b)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("--max-pause", type=float, default=0.7, help="pauses longer than this are shortened")
    ap.add_argument("--keep-pause", type=float, default=0.3, help="what a shortened pause becomes")
    ap.add_argument("--pad", type=float, default=0.08, help="audio kept before the first / after the last word of a run")
    ap.add_argument("--no-fillers", action="store_true", help="keep um/uh")
    ap.add_argument("--no-restarts", action="store_true", help="keep repeated phrases (false starts)")
    ap.add_argument("--drop", help="extra source ranges to remove, e.g. 12.4-18.9,61-64.5")
    ap.add_argument("--range", help="only use this source range, e.g. 30-210")
    ap.add_argument("--punch", type=float, default=0, help="zoom (e.g. 1.12) on every other segment to hide jump cuts")
    ap.add_argument("--out")
    a = ap.parse_args()

    data = json.loads(Path(a.words).read_text())
    words = data["words"]
    out = Path(a.out or Path(a.words).parent)
    n = len(words)
    cut = [None] * n  # reason or None

    if not a.no_fillers:
        for i, w in enumerate(words):
            if norm(w["w"]) in FILLERS:
                cut[i] = "filler"

    # False starts: a 2-5 word phrase that is said again within the next few words -> drop the first attempt.
    if not a.no_restarts:
        toks = [norm(w["w"]) for w in words]
        i = 0
        while i < n:
            hit = False
            for L in (5, 4, 3, 2):
                if i + L > n:
                    continue
                phrase = toks[i:i + L]
                if any(not t for t in phrase):
                    continue
                for j in range(i + 1, min(n - L + 1, i + L + 8)):
                    # a finished sentence is never a false start
                    if re.search(r"[.?!]$", words[j - 1]["w"]):
                        break
                    if toks[j:j + L] == phrase and words[j]["s"] - words[i]["s"] < 10:
                        for k in range(i, j):
                            cut[k] = cut[k] or "restart"
                        i = j
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                i += 1

    drops = parse_ranges(a.drop)
    rng = parse_ranges(a.range)
    for i, w in enumerate(words):
        mid = (w["s"] + w["e"]) / 2
        if any(x <= mid <= y for x, y in drops):
            cut[i] = "manual"
        if rng and not any(x <= mid <= y for x, y in rng):
            cut[i] = "outside range"

    # Build keep ranges from runs of kept words, shortening long pauses.
    keep = []
    kept = [w for i, w in enumerate(words) if not cut[i]]
    half = a.keep_pause / 2
    for idx, w in enumerate(kept):
        s, e = w["s"], w["e"]
        if not keep:
            keep.append([max(0.0, s - a.pad), e + a.pad])
            continue
        prev_e = kept[idx - 1]["e"]
        gap = s - prev_e
        # removed words between prev and this one: never keep any part of them
        between = [words[k] for k in range(n) if cut[k] and prev_e - 0.01 <= words[k]["s"] < s]
        if gap <= a.max_pause and not between:
            keep[-1][1] = e + a.pad
        else:
            stop = min(prev_e + half, between[0]["s"] if between else s)
            start = max(s - half, between[-1]["e"] if between else prev_e)
            keep[-1][1] = stop
            keep.append([max(start, stop), e + a.pad])
    if keep:
        keep[-1][1] = min(keep[-1][1], data.get("duration", keep[-1][1]))
    keep = [[round(x, 3), round(y, 3)] for x, y in keep if y - x > 0.05]
    if a.punch and a.punch > 1:
        keep = [k + [{"zoom": a.punch}] if i % 2 else k for i, k in enumerate(keep)]

    removed = []
    for i, w in enumerate(words):
        if cut[i]:
            if removed and removed[-1]["reason"] == cut[i] and removed[-1]["_i"] == i - 1:
                removed[-1]["e"] = w["e"]; removed[-1]["text"] += " " + w["w"]; removed[-1]["_i"] = i
            else:
                removed.append({"s": w["s"], "e": w["e"], "reason": cut[i], "text": w["w"], "_i": i})
    for r in removed:
        r.pop("_i")

    src_len = data.get("duration") or (words[-1]["e"] if words else 0)
    new_len = sum(k[1] - k[0] for k in keep)
    edl = {"source": data["source"], "source_duration": src_len, "edited_duration": round(new_len, 2),
           "keep": keep, "removed": removed}
    (out / "edl.json").write_text(json.dumps(edl, indent=1))

    # Paper edit: kept text, with cuts struck through and pauses shown.
    lines, cur = [], []
    for i, w in enumerate(words):
        if i and words[i]["s"] - words[i - 1]["e"] > a.max_pause:
            cur.append(f"⟨{words[i]['s'] - words[i - 1]['e']:.1f}s pause⟩")
        cur.append(f"~~{w['w']}~~" if cut[i] else w["w"])
        if w["w"].endswith((".", "?", "!")):
            lines.append(f"`{int(w['e'] // 60):02d}:{w['e'] % 60:05.2f}` " + " ".join(cur)); cur = []
    if cur:
        lines.append(" ".join(cur))
    md = [f"# Paper edit: {Path(data['source']).name}",
          f"Source {src_len:.1f}s → edited {new_len:.1f}s ({len(keep)} segments, {len(removed)} cuts). "
          f"Struck-through words are removed; pauses over {a.max_pause}s become {a.keep_pause}s.", ""]
    md += lines
    md += ["", "## Cuts", "| Source time | Reason | Text |", "|---|---|---|"]
    md += [f"| {r['s']:.2f}–{r['e']:.2f} | {r['reason']} | {r['text']} |" for r in removed]
    (out / "paper_edit.md").write_text("\n".join(md) + "\n")
    print(f"{src_len:.1f}s -> {new_len:.1f}s, {len(keep)} segments, {len(removed)} cuts -> {out}/edl.json, paper_edit.md")


if __name__ == "__main__":
    main()
