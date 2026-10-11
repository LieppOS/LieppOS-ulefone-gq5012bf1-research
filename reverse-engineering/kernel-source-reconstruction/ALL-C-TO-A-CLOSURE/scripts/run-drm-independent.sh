#!/bin/bash
# Static/offline, fresh bundle clones; four-core affine and low priority.
set -euo pipefail
ROOT=${1:-/home/armol/kernel-work/allc/drm}
TAG=${2:?B1 or B2}
case "$TAG" in B1|B2) ;; *) exit 2;; esac
RECIPE=$ROOT/recipe-$TAG
WS=$ROOT/ws-$TAG
export PYTHONDONTWRITEBYTECODE=1 JOBS=4 TMPDIR=/tmp
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export LIEPPOS_NATIVE_MIRROR=/home/armol/kernel-work/platform-batch-03-native-inputs
export LIEPPOS_MTKACK_MIRROR=/home/armol/kernel-work/allc/mirror
mkdir -p "$WS"
[ ! -e "$RECIPE/.git/objects/info/alternates" ]
git -C "$RECIPE" fsck --full > "$ROOT/fsck-$TAG.log" 2>&1
git -C "$RECIPE" bundle verify "$(dirname "$0")/../bundles/drm-allc.bundle" > "$ROOT/bundle-$TAG.log" 2>&1
bash "$RECIPE/scripts/bootstrap.sh" "$WS"
bash "$RECIPE/scripts/bulk-build.sh" "$WS" "$TAG"
python3 "$RECIPE/scripts/verify.py" "$WS/out/$TAG" /home/armol/kernel-work/allc/stock-ops/vendor-flat "$ROOT/acceptance-$TAG"
