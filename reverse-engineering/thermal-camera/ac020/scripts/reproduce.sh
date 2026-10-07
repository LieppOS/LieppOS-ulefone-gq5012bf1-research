#!/bin/bash
# Regenerate the AC020-UVC static results from the stock partitions (offline; no device access).
# usage: scripts/reproduce.sh [workdir]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; AC="$HERE/.."
R="$(cd "$AC/../../.." && pwd)"
APP="$R/workspace/gq5012bf1/stock/partitions/system/app"
W="${1:-/tmp/ac020-repro}"; mkdir -p "$W"; cd "$W"
unzip -o -q "$APP/M170infisens/M170infisens.apk" 'lib/arm64-v8a/*' -d inf
unzip -o -q "$APP/M170infDlp/M170infDlp.apk" 'assets/RS300_TC2C_*' -d dlp
unzip -o -q dlp/assets/RS300_TC2C_*.zip -d pkg
L=inf/lib/arm64-v8a
sha256sum $L/libAC020sdk.so $L/libircmd020.so $L/libusbuvccamera020.so pkg/firmware_EXT.bin
for f in libircmd020 libusbuvccamera020 libAC020sdk; do llvm-objdump -d --no-show-raw-insn $L/$f.so > $f.dis; done
python3 "$HERE/parse_fw_usb_desc.py" pkg/firmware_EXT.bin > firmware-descriptor-dump.txt
python3 "$HERE/extract_vdcmd_headers_v2.py" libircmd020.dis > ops.tsv
python3 "$HERE/ctl_sites.py" libusbuvccamera020.dis libusb_control_transfer > uvc-ctl-sites.txt
python3 "$HERE/ctl_sites.py" libAC020sdk.dis libusb_control_transfer > sdk-ctl-sites.txt
diff <(grep -v '^#' "$AC/firmware-descriptor-dump.txt") firmware-descriptor-dump.txt && echo "descriptor dump: identical"
echo "ops: $(wc -l < ops.tsv) call sites; vendor-type sites in libusbuvccamera020: $(grep -c 'w1=0x41\|w1=0xc1' uvc-ctl-sites.txt || true)"
grep -E '0x2041|0x22c1|0x21c1' libAC020sdk.dis | wc -l | sed 's/^/vdcmd request constants in libAC020sdk: /'
