#!/usr/bin/env bash
# Scaffold a Hive feature demo:  bash new_demo.sh <slug> [parent-dir]
# Creates <parent-dir>/<slug>/ (default ~/hive-demos/<slug>) with fonts, Playwright, the working
# template (demo.html) and the example storyboard. Works outside any git repo on purpose.
set -euo pipefail
slug="${1:?usage: new_demo.sh <slug> [parent-dir]}"
parent="${2:-$HOME/hive-demos}"
here="$(cd "$(dirname "$0")/.." && pwd)"
vs="${VIDEO_STUDIO:-$HOME/.claude/skills/video-studio}"
if [ ! -f "$vs/scripts/render_html.mjs" ] || [ ! -f "$vs/scripts/soundtrack.py" ]; then
  echo "video-studio skill not found at $vs (install it, or set VIDEO_STUDIO=/path/to/video-studio)"; exit 1
fi
command -v ffmpeg >/dev/null || { echo "ffmpeg not found: brew install ffmpeg"; exit 1; }
"$vs/.venv/bin/python" -c "import numpy, scipy" 2>/dev/null || echo "note: soundtrack needs numpy and scipy: pip install numpy scipy"

dir="$parent/$slug"
mkdir -p "$dir/fonts" "$dir/renders" "$dir/work" "$dir/ref"
cd "$dir"
[ -f package.json ] || npm init -y >/dev/null
npm i -D --silent --ignore-scripts playwright@1.64.1 @fontsource/ibm-plex-sans @fontsource/ibm-plex-sans-condensed @fontsource/ibm-plex-mono
for f in ibm-plex-sans/files/ibm-plex-sans-latin-{400,500,600}-normal \
         ibm-plex-sans-condensed/files/ibm-plex-sans-condensed-latin-{600,700}-normal \
         ibm-plex-mono/files/ibm-plex-mono-latin-{400,600}-normal; do
  cp "node_modules/@fontsource/$f.woff2" fonts/
done
[ -f demo.html ] || cp "$here/templates/hive-demo.html" demo.html
[ -f storyboard.example.md ] || cp "$here/templates/storyboard-example.md" storyboard.example.md
npx playwright install chromium >/dev/null 2>&1 || echo "note: couldn't install Playwright's Chromium; pass --chrome \"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome\" to render_html.mjs"

cat <<EOF
Ready: $dir
  demo.html              working template to edit (shell, pages, chat window, cursor, camera, captions, end card)
  storyboard.example.md  the shape to follow; write yours to storyboard.md
  ref/                   put screenshots and repo notes here
Next:
  node $vs/scripts/render_html.mjs demo.html --stills 1.6,4,6.9,9.3,11.4,15.6,18.9 --out work/stills
  node $vs/scripts/render_html.mjs demo.html --out renders/$slug.mp4 --workers 4
  $vs/.venv/bin/python $vs/scripts/soundtrack.py renders/$slug.mp4 --music afrohouse --drop 2.3 --outro 1.9 --loudness -15.2 --out renders/$slug-sound.mp4
EOF
