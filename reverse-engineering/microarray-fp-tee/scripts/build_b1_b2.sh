#!/bin/bash
# GQ5012BF1 microarray_fp_tee.ko: two clean builds (B1, B2) of ../source against
# exact GKI 12901745 (android14-6.1, clang r487747c), linked ONLY against
# natural, source-built providers:
#   fingerprint     <- $G/lieppos/fingerprint-recon      (YFT glue, source-built)
#   spi-mt65xx      <- $G/lieppos/spi-mt65xx             (direct-match source)
#   tkcore          <- pristine public TrustKernel core/ (anvil-kernel
#                      8e1a0f39478f, tree 6b94428f), scripts/build_tkcore_core_natural.sh
# No stock symvers witness is used.
#
# Environment facts that matter for byte parity:
#   kernel.release 6.1.115-android14-11-g945dff7bc1bf (stock vermagic),
#   module_scmversion= (no srcversion git suffix), KCFLAGS=-faddrsig,
#   two-object link order mtk-settings.o madev.o (source/Makefile).
set -euo pipefail
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
KO=${KO:-$G/lieppos/nfc/kout}; P=$KO/../lieppos
OUT=${OUT:-$G/lieppos/microarray-fp-tee-b1b2}
HERE=$(cd "$(dirname "$0")/.." && pwd)
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
REL_EXPECT=6.1.115-android14-11-g945dff7bc1bf
[ "$(cat "$KO/include/config/kernel.release")" = "$REL_EXPECT" ] || { echo "kout kernel.release is not $REL_EXPECT" >&2; exit 1; }

kb() { # kbuild in an M= dir (never without M=)
  local m=$1; shift
  [ -n "$m" ] && [ -f "$G/common/$m/Makefile" ] || { echo "refusing: bad M=$m" >&2; exit 1; }
  (cd "$G/common" && make O="$KO" M="$m" ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion= "$@")
}

# providers (natural)
kb ../lieppos/fingerprint-recon KCFLAGS=-faddrsig -j16 modules >/dev/null
kb ../lieppos/spi-mt65xx KCFLAGS=-faddrsig -j16 modules >/dev/null
bash "$HERE/scripts/build_tkcore_core_natural.sh" >/dev/null
SYM="$P/fingerprint-recon/Module.symvers $P/spi-mt65xx/Module.symvers $P/tkcore-core-natural/src/core/Module.symvers"
grep -P '\ttee_spi_transfer\t' "$P/tkcore-core-natural/src/core/Module.symvers"

W=$G/lieppos/microarray-fp-tee-src
for b in B1 B2; do
  rm -rf "$W"; mkdir -p "$W"; cp "$HERE"/source/* "$W/"
  kb ../lieppos/microarray-fp-tee-src clean >/dev/null
  kb ../lieppos/microarray-fp-tee-src KCFLAGS=-faddrsig KBUILD_EXTRA_SYMBOLS="$SYM" -j16 modules > "$OUT.$b.log" 2>&1
  mkdir -p "$OUT/$b"
  cp "$P/microarray-fp-tee-src/microarray_fp_tee.ko" "$P/microarray-fp-tee-src/mtk-settings.o" \
     "$P/microarray-fp-tee-src/madev.o" "$P/microarray-fp-tee-src/microarray_fp_tee.mod.c" "$OUT/$b/"
  llvm-strip --strip-debug -o "$OUT/$b/microarray_fp_tee.stripped.ko" "$OUT/$b/microarray_fp_tee.ko"
  (cd "$OUT/$b" && sha256sum microarray_fp_tee.ko microarray_fp_tee.stripped.ko mtk-settings.o madev.o)
done
for f in microarray_fp_tee.ko microarray_fp_tee.stripped.ko mtk-settings.o madev.o; do
  cmp -s "$OUT/B1/$f" "$OUT/B2/$f" && echo "B1 == B2 ($f byte-identical)" || { echo "B1 != B2 ($f)"; exit 1; }
done
