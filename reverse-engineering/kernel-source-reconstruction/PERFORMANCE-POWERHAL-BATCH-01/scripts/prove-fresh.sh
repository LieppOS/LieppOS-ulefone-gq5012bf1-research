#!/bin/bash
# Independent committed-source proof for one tag (B1|B2). Static/offline, four CPUs, low priority.
# Fresh --no-hardlinks clone of the authenticated bundle, new workspace, full offline bootstrap (KDM only; no BTF base for this batch).
set -euo pipefail
TAG=${1:?B1|B2}; CPUS=${2:?cpu list}; case "$TAG" in B1|B2) ;; *) exit 2;; esac
HERE=$(cd "$(dirname "$0")/.." && pwd)
K=/home/armol/kernel-work/performance-powerhal-batch-01; ROOT=$K/proof; R=$ROOT/recipe-$TAG; WS=$ROOT/ws-$TAG; OUT=$ROOT/result-$TAG
EXPECT=${EXPECT_COMMIT:?expected recipe commit}
[ ! -e "$K/dev" ] || { echo "development directory still reachable: $K/dev" >&2; exit 3; }
[ ! -e "$R" ] && [ ! -e "$WS" ] || { echo "stale $TAG proof paths; use a new root" >&2; exit 3; }
mkdir -p "$OUT"
export GIT_NO_LAZY_FETCH=1 GIT_ALLOW_PROTOCOL=file GIT_TERMINAL_PROMPT=0 PYTHONDONTWRITEBYTECODE=1 JOBS=4 TMPDIR=$ROOT/tmp-$TAG
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
mkdir -p "$TMPDIR"
git clone -q --no-hardlinks "$HERE/bundles/performance.bundle" "$R"
# bundle verify needs a repository context (failed-proof-01 ran it from /tmp)
git -C "$R" bundle verify "$HERE/bundles/performance.bundle" > "$OUT/bundle-verify.log" 2>&1
[ "$(git -C "$R" rev-parse HEAD)" = "$EXPECT" ]
[ ! -e "$R/.git/objects/info/alternates" ]
git -C "$R" fsck --full > "$OUT/fsck.log" 2>&1
RUN="nice -n 10 taskset -c $CPUS"
$RUN bash "$R/scripts/bootstrap.sh" "$WS" > "$OUT/bootstrap.log" 2>&1
$RUN bash "$R/scripts/bulk-build.sh" "$WS" "$TAG" > "$OUT/bulk-build.log" 2>&1
python3 "$R/scripts/verify.py" "$WS/out/$TAG" "$K/stock-flat" "$OUT/acceptance" > "$OUT/verify.log" 2>&1
(cd "$R/scripts" && $RUN python3 mutation-test.py "$WS/out/$TAG" "$K/stock-flat") > "$OUT/mutations.json" 2>&1
for f in SHA256SUMS INTERMEDIATE-SHA256SUMS CONFIG-SHA256SUMS TARGET-SOURCE-TREE joint-extra.symvers batch-full.Module.symvers object-exit native-exit module-exit provider.log; do cp "$WS/out/$TAG/$f" "$OUT/"; done
cp -r "$WS/out/$TAG/provider" "$OUT/provider"; cp "$WS/assembled-source-tree" "$WS/source-scope.patch" "$OUT/"
[ ! -e "$WS/btfbase" ] || { echo "unexpected BTF base build" >&2; exit 4; }
echo "$TAG PASS $(git -C "$R" rev-parse HEAD)" > "$OUT/DONE"
