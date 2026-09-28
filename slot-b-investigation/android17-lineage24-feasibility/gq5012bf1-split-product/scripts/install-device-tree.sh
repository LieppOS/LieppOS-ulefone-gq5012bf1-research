#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
SRC=$(realpath "$SCRIPT_DIR/../device-tree/gq5012bf1")
TREE=${1:-/mnt/SamsungSSD/android/lineage-24.0}
DST="$TREE/device/ulefone/gq5012bf1"
if [ -e "$DST" ]; then
  echo "Refusing to overwrite existing $DST" >&2
  echo "Review with: diff -ruN '$DST' '$SRC'" >&2
  exit 2
fi
mkdir -p "$(dirname "$DST")"
cp -a "$SRC" "$DST"
printf 'Installed review snapshot at %s\n' "$DST"
printf 'No build, flash, or phone operation was performed.\n'
