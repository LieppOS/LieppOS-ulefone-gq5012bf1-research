#!/bin/sh
# st21-fw-loader-reproduce.sh — regenerate every committed Phase 4b firmware-loader
# artifact from the committed runtime blobs, using only host binutils/LLVM.
#
# Everything under analysis/st21-gemini-audit/audit/ is derived data: if a
# reviewer disputes a claim in firmware-loader-rev2.md, re-run this and diff.
# The raw disassembly corpus (audit/disasm/*.asm, ~15 MB) is deliberately not in
# git; it is regenerated here as an intermediate.
#
# Usage: hardware/nfc/tools/st21-fw-loader-reproduce.sh [--keep-asm]
set -eu

here=$(cd "$(dirname "$0")" && pwd)
nfc=$(dirname "$here")
audit=$nfc/analysis/st21-gemini-audit
blob=$audit/runtime-blobs/nfc_nci.st21nfc.st.so
out=$audit/audit
disasm=$out/disasm

for t in nm readelf llvm-objdump llvm-readelf c++filt python3; do
  command -v "$t" >/dev/null || { echo "missing tool: $t" >&2; exit 1; }
done

mkdir -p "$disasm"
echo "== raw disassembly corpus -> $disasm"
llvm-objdump -d --no-show-raw-insn "$blob" > "$disasm/nfc_nci.st21nfc.st.so.text.asm"
llvm-objdump -d --no-show-raw-insn "$audit/runtime-blobs/libstnfc-nci.so" > "$disasm/libstnfc-nci.so.text.asm"

echo "== loader/patch descriptors"
python3 "$here/st21-loader-tables.py" "$blob" > "$out/loader-tables.txt"

echo "== are the patch tables payloads or pointer arrays?"
python3 "$here/st21-data-graph.py" "$blob" '^(loader|s_|DW)' > "$out/fw-loader-data-graph.txt"

echo "== firmware/config literals + dynamic-symbol evidence per blob"
python3 "$here/st21-fw-path-literals.py" > "$out/fw-path-literals.txt"

echo "== call-site trace of the firmware-download region"
python3 "$here/st21-fw-loader-recovery.py" "$blob" > "$out/fw-loader-recovery.tsv"

echo "== string xrefs inside the firmware-download region"
python3 "$here/st21-annotate.py" "$blob" xref \
  'FW|fw_|loader|Loader|patch|Patch|AUTH|Auth|configuration|conf|\.bin|\.txt|APDU|NCI_PROP|erase|flash' \
  > "$out/fw-loader-xref.txt"

echo "== per-function listings referenced by the write-up"
for a in 0x176d0 0x17b00 0x218a8 0x237f0 0x23900; do
  python3 "$here/st21-annotate.py" "$blob" dump "$a" > "$disasm/dump-$a.txt"
done

if [ "${1:-}" != "--keep-asm" ]; then
  rm -f "$disasm"/*.asm
fi
echo "== done: $(ls "$out" | tr '\n' ' ')"
