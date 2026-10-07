#!/bin/bash
# GQ5012BF1 fingerprint.ko (YFT glue): two clean builds (B1, B2) of ../source
# against exact GKI 12901745 (android14-6.1, clang r487747c).
# Byte facts: kernel.release 6.1.115-android14-11-g945dff7bc1bf, module_scmversion=,
# KCFLAGS=-faddrsig (also in source/Makefile), llvm-strip --strip-debug for comparison.
set -euo pipefail
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
KO=${KO:-$G/lieppos/nfc/kout}; P=$KO/../lieppos
OUT=${OUT:-$G/lieppos/fingerprint-b1b2}
HERE=$(cd "$(dirname "$0")/.." && pwd)
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
REL_EXPECT=6.1.115-android14-11-g945dff7bc1bf
[ "$(cat "$KO/include/config/kernel.release")" = "$REL_EXPECT" ] || { echo "kout kernel.release is not $REL_EXPECT" >&2; exit 1; }
W=$G/lieppos/fingerprint-src; M=../lieppos/fingerprint-src
kb() { [ -f "$G/common/$M/Makefile" ] || { echo "refusing: no Makefile in M=$M" >&2; exit 1; }
       (cd "$G/common" && make O="$KO" M="$M" ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion= "$@"); }
for b in B1 B2; do
  rm -rf "$W"; mkdir -p "$W"; cp "$HERE"/source/* "$W/"
  kb clean >/dev/null
  kb KCFLAGS=-faddrsig -j16 modules > "$OUT.$b.log" 2>&1
  mkdir -p "$OUT/$b"; cp "$P/fingerprint-src/fingerprint.ko" "$P/fingerprint-src/fingerprint.o" "$OUT/$b/"
  llvm-strip --strip-debug -o "$OUT/$b/fingerprint.stripped.ko" "$OUT/$b/fingerprint.ko"
  (cd "$OUT/$b" && sha256sum fingerprint.ko fingerprint.stripped.ko fingerprint.o)
done
for f in fingerprint.ko fingerprint.stripped.ko fingerprint.o; do
  cmp -s "$OUT/B1/$f" "$OUT/B2/$f" && echo "B1 == B2 ($f byte-identical)" || { echo "B1 != B2 ($f)"; exit 1; }
done
