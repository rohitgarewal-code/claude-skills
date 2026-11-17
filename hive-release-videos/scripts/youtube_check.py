#!/usr/bin/env python3
"""Check a published video from YouTube's public watch page, the way a viewer sees it.

    python3 youtube_check.py <video id> [--title "<expected title>"] [--min-tags 10] [--min-desc 400]

Exits 0 only when the video is public (not private, not unlisted), plays, has a description of at least
--min-desc characters, at least --min-tags tags, and (if given) the expected title. Prints the qualities
YouTube has finished encoding: 1080p and 1440p appear a few minutes after publishing, so a missing one
right after upload is "still processing", not a failure (pass --need-hd to make it one).
Reads a public page only; it never signs in or changes anything.
"""
import argparse
import json
import re
import sys
import urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("video_id")
ap.add_argument("--title")
ap.add_argument("--min-tags", type=int, default=10)
ap.add_argument("--min-desc", type=int, default=400)
ap.add_argument("--need-hd", action="store_true", help="fail unless 1080p or higher is listed")
a = ap.parse_args()

req = urllib.request.Request(
    f"https://www.youtube.com/watch?v={a.video_id}&hl=en",
    headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"},
)
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});(?:var|</script>)", html, re.S)
if not m:
    print(f"FAIL {a.video_id}: no player data on the watch page (private, deleted or still uploading)")
    sys.exit(1)
p = json.loads(m.group(1))
status = p.get("playabilityStatus", {}).get("status")
vd = p.get("videoDetails", {})
mf = p.get("microformat", {}).get("playerMicroformatRenderer", {})
formats = p.get("streamingData", {}).get("adaptiveFormats", [])
heights = sorted({int(re.match(r"\d+", f["qualityLabel"]).group()) for f in formats if f.get("qualityLabel")})
desc, tags, title = vd.get("shortDescription", ""), vd.get("keywords", []), vd.get("title", "")

problems = []
if status != "OK":
    problems.append(f"not playable ({status}: {p.get('playabilityStatus', {}).get('reason', '')})")
if vd.get("isPrivate") is not False:
    problems.append("private")
if mf.get("isUnlisted") is not False:
    problems.append("unlisted")
if len(desc) < a.min_desc:
    problems.append(f"description {len(desc)} chars (< {a.min_desc})")
if len(tags) < a.min_tags:
    problems.append(f"{len(tags)} tags (< {a.min_tags})")
if a.title and title.strip() != a.title.strip():
    problems.append(f"title is {title!r}")
hd = heights and max(heights) >= 1080
if a.need_hd and not hd:
    problems.append(f"no HD encode yet (have {heights})")

print(json.dumps({
    "id": a.video_id, "title": title, "public": vd.get("isPrivate") is False and mf.get("isUnlisted") is False,
    "description_chars": len(desc), "tags": tags, "qualities": [f"{h}p" for h in heights],
    "hd_ready": bool(hd),
}, indent=1))
if problems:
    print("FAIL " + "; ".join(problems))
    sys.exit(1)
print("OK" + ("" if hd else " (HD still processing)"))
