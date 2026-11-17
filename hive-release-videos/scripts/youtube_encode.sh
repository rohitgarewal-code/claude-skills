#!/usr/bin/env bash
# Make the file that goes to YouTube: the best quality that fits the Chrome upload tool's 10 MB limit.
#
#   youtube_encode.sh renders/<slug>-sound.mp4 renders/<slug>-youtube.mp4
#
# Two-pass x264 (veryslow, tuned for flat animation) aimed just under the limit, TV-range BT.709,
# AAC 192k, faststart. Refuses anything under 1920x1080 and anything that doesn't fit, so a bad file never
# reaches the upload step. Render at --scale 4/3 (2560x1440) first: YouTube then offers 1440p, and its
# encodes of a 1440p upload keep UI text sharper at 1080p too.
set -euo pipefail
in=${1:?usage: youtube_encode.sh in.mp4 out.mp4}
out=${2:?usage: youtube_encode.sh in.mp4 out.mp4}
LIMIT=10000000          # file_upload: combined size must stay under 10 MB
TARGET=${TARGET:-9500000}
AUDIO_K=192

IFS=x read -r w h < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$in")
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
if (( w < 1920 || h < 1080 )); then echo "REFUSED: source is ${w}x${h}; render at 1920x1080 or more (use --scale 4/3)" >&2; exit 2; fi

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for attempt in 1 2 3; do
  # video kbit/s = (target bits / duration) - audio - ~2% container overhead
  vk=$(python3 -c "print(int(($TARGET*8/$dur/1000 - $AUDIO_K) * 0.98))")
  common=(-c:v libx264 -preset veryslow -tune animation -b:v "${vk}k" -bf 2 -g 60
          -vf "scale=out_range=tv,format=yuv420p" -color_range tv
          -color_primaries bt709 -color_trc bt709 -colorspace bt709 -passlogfile "$tmp/x264")
  ffmpeg -y -v error -i "$in" "${common[@]}" -pass 1 -an -f null /dev/null
  ffmpeg -y -v error -i "$in" "${common[@]}" -pass 2 -c:a aac -b:a "${AUDIO_K}k" -movflags +faststart "$tmp/out.mp4"
  size=$(stat -f%z "$tmp/out.mp4" 2>/dev/null || stat -c%s "$tmp/out.mp4")
  if (( size < LIMIT - 200000 )); then break; fi
  echo "attempt $attempt: $size bytes, too close to the limit; retrying smaller" >&2
  TARGET=$(( TARGET * 94 / 100 ))
done
(( size < LIMIT - 200000 )) || { echo "REFUSED: could not fit under 10 MB ($size bytes)" >&2; exit 3; }

mv "$tmp/out.mp4" "$out.tmp.mp4" && mv "$out.tmp.mp4" "$out"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,pix_fmt,color_range,bit_rate -show_entries format=duration,size -of compact=p=0 "$out"
echo "OK $out ${w}x${h} video ${vk}k, $size bytes"
