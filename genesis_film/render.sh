#!/usr/bin/env bash
# Render the Genesis film in parallel act groups, join them without re-encoding the
# picture, and add the ambient soundtrack synthesized from the real act timings.
#
# Every group runs the whole scene and renders only its own acts, skipping the
# others. Skipped acts still compute their state, so each group starts exactly
# where the previous one ends and the joined film has no seams.
#
#   MANIM=/path/to/manim PYTHON=/path/to/python QUALITY=qm ./render.sh   # 1280x720, 30 fps
set -euo pipefail
cd "$(dirname "$0")"
MANIM=${MANIM:-manim}
PYTHON=${PYTHON:-python3}
QUALITY=${QUALITY:-qm}
ACT_GROUPS=${ACT_GROUPS:-"1-2 3 4-5 6-9 10-14"}
WORK=${WORK:-$(mktemp -d)}
mkdir -p output

pids=()
for group in $ACT_GROUPS; do
  GENESIS_ACTS=$group "$MANIM" "-$QUALITY" --disable_caching --save_sections \
    --media_dir "$WORK/$group" -o "part_$group" genesis.py Genesis \
    > "$WORK/log_$group.txt" 2>&1 &
  pids+=($!)
done
status=0
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
if [ "$status" -ne 0 ]; then
  echo "a group failed; logs are in $WORK" >&2
  exit 1
fi

list="$WORK/parts.txt"
: > "$list"
for group in $ACT_GROUPS; do
  part=$(find "$WORK/$group" -name "part_$group.mp4" -not -path "*/sections/*" | head -n 1)
  echo "file '$part'" >> "$list"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy "$WORK/picture.mp4"

# Act timeline from the section indexes, in film order.
"$PYTHON" - "$WORK" $ACT_GROUPS > "$WORK/timeline.json" <<'EOF'
import json, pathlib, sys
work, groups = pathlib.Path(sys.argv[1]), sys.argv[2:]
timeline, clock = [], 0.0
for group in groups:
    index = next((work / group).rglob("sections/*.json"))
    for section in json.loads(index.read_text()):
        name, duration = section["name"], float(section.get("duration", 0) or 0)
        if name.startswith("act") and duration > 0:
            timeline.append([int(name[3:]), clock, clock + duration])
            clock += duration
print(json.dumps(timeline))
EOF
"$PYTHON" soundtrack.py "$WORK/timeline.json" "$WORK/soundtrack.wav"
ffmpeg -y -loglevel error -i "$WORK/picture.mp4" -i "$WORK/soundtrack.wav" -c:v copy \
  -c:a aac -b:a 128k -shortest -movflags +faststart output/genesis.mp4
echo "wrote output/genesis.mp4 (work files in $WORK)"
