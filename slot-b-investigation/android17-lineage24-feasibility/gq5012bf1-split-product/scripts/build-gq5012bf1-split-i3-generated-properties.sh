#!/bin/bash
set -o pipefail
TREE=/mnt/SamsungSSD/android/lineage-24.0
OUT=out-android17-gsi-erofs
ART=/mnt/SamsungSSD/TIER3/phase5/android17
LOG="$ART/logs/build-lineage_gq5012bf1-cp2a-userdebug-split-i3-generated-properties.log"
RC="$ART/logs/build-lineage_gq5012bf1-cp2a-userdebug-split-i3-generated-properties.rc"
REF="$ART/out-lineage_gsi_arm64-erofs/target/product/generic_arm64/system.img"
export OUT_DIR="$OUT"
export PATH="$ART/tools/git-lfs-3.8.0:$HOME/bin:$PATH"
cd "$TREE" || exit 125
: > "$LOG"; rm -f "$RC"
{
  echo "START=$(date -Is)"
  echo "GSI_SHA_BEFORE=$(sha256sum "$REF" | awk '{print $1}')"
  source build/envsetup.sh
  lunch lineage_gq5012bf1 cp2a userdebug || exit $?
  echo 'COMMAND=m -j32 systemimage systemextimage productimage vbmetasystemimage vbmetaimage'
  m -j32 systemimage systemextimage productimage vbmetasystemimage vbmetaimage
  rc=$?
  echo "BUILD_EXIT=$rc"
  echo "GSI_SHA_AFTER=$(sha256sum "$REF" | awk '{print $1}')"
  echo "END=$(date -Is)"
  printf '%s\n' "$rc" > "$RC"
  exit "$rc"
} 2>&1 | tee "$LOG"
exit ${PIPESTATUS[0]}
