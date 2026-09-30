#!/usr/bin/env bash
set -euo pipefail

: "${RESEARCH:?Set RESEARCH to the LieppOS research repo root first}"

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="$RESEARCH/nfc"

mkdir -p "$DST"
cp "$SRC/README.md" "$DST/README.md"
cp "$SRC/st21nfc-current-findings.md" "$DST/st21nfc-current-findings.md"
cp "$SRC/phase1-st21nfc-reconstruction.md" "$DST/phase1-st21nfc-reconstruction.md"
cp "$SRC/capture-commands.md" "$DST/capture-commands.md"

echo "Installed NFC research notes into: $DST"
