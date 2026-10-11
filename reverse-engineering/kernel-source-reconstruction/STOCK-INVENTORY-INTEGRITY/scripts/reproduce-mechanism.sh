#!/usr/bin/env bash
# Reproduce the in-place llvm-objcopy signature strip on PRIVATE copies only.
# usage: reproduce-mechanism.sh EXTRACTED_SYSTEM_DLKM_DIR VENDOR_STOCK_MODULE_DIR SCRATCH
set -euo pipefail
X=$1; V=$2; S=$3
[ ! -e "$S" ] || { echo "scratch $S must not exist" >&2; exit 2; }
mkdir -p "$S"; cd "$S"
OC=$(command -v llvm-objcopy)
echo "llvm-objcopy: $(readlink -f "$OC") sha256=$(sha256sum "$(readlink -f "$OC")" | cut -c1-64)"
"$OC" --version | sed -n 2p
h() { sha256sum "$1" | cut -c1-64; }
row() { printf '%-28s size %6s -> %6s  inode %s -> %s  sha256 %s -> %s\n' "$1" "$2" "$(stat -c%s "$3")" "$4" "$(stat -c%i "$3")" "${5:0:16}" "$(h "$3" | cut -c1-16)"; }
for m in 6lowpan bluetooth can; do
  for form in btf modinfo; do
    f=$form-$m.ko; cp "$X/lib/modules/$m.ko" "$f"; s=$(stat -c%s "$f"); i=$(stat -c%i "$f"); b=$(h "$f")
    if [ $form = btf ]; then "$OC" --dump-section .BTF=/dev/stdout "$f" >/dev/null; else "$OC" --dump-section=.modinfo=/dev/stdout "$f" >/dev/null; fi
    row "system_dlkm $m ($form)" "$s" "$f" "$i" "$b"
    tail -c 28 "$f" | grep -q 'Module signature appended' && echo "   trailer still present" || echo "   trailer GONE"
  done
done
cp "$X/lib/modules/6lowpan.ko" safe.ko; "$OC" --dump-section .BTF=sec.bin safe.ko /dev/null
echo "safe form (explicit output operand /dev/null): input unchanged = $([ "$(h safe.ko)" = "$(h "$X/lib/modules/6lowpan.ko")" ] && echo yes || echo NO)"
cp "$V/bluetooth.ko" vendor-bluetooth.ko; b=$(h vendor-bluetooth.ko); "$OC" --dump-section .BTF=/dev/stdout vendor-bluetooth.ko >/dev/null
echo "unsigned vendor_dlkm bluetooth.ko rewritten in place: bytes unchanged = $([ "$(h vendor-bluetooth.ko)" = "$b" ] && echo yes || echo NO)"
NB=$(cd "$V" && for f in *.ko; do llvm-readelf -S "$f" | grep -q ' .BTF ' || { echo "$f"; break; }; done)
cp "$V/$NB" nobtf.ko; i=$(stat -c%i nobtf.ko); set +e; "$OC" --dump-section .BTF=/dev/stdout nobtf.ko >/dev/null 2>err.txt; rc=$?; set -e
echo "module without .BTF ($NB): exit $rc, inode unchanged = $([ "$(stat -c%i nobtf.ko)" = "$i" ] && echo yes || echo NO): $(cat err.txt)"
