#!/bin/bash
# Eight fresh compilations:each of four independently cloned engines builds joint27 B1/B2.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd);R=$(cd "$P/../../.." && pwd);BASE=$(dirname "$R")
C=${LIEPPOS_BATCH02_CLEANCHECK:-/home/armol/kernel-work/platform-batch-02-cleancheck};D=/home/armol/kernel-work/platform-batch-02-dev
mkdir -p "$C/recipes"
mapfile -t NAMES < <(python3 - "$P/SOURCE-REPOSITORIES.tsv" <<'PY'
import csv,sys
from pathlib import Path
for r in csv.DictReader(open(sys.argv[1]),delimiter='\t'):print(Path(r['repository']).name)
PY
)
for n in "${NAMES[@]}";do
 test -z "$(git -C "$BASE/$n" status --porcelain)"
 git clone -q --no-hardlinks "$BASE/$n" "$C/recipes/$n"
 test "$(git -C "$C/recipes/$n" rev-parse HEAD)" = "$(git -C "$BASE/$n" rev-parse HEAD)"
done
restore() {
 for n in "${NAMES[@]}";do [ ! -d "$BASE/$n.unavailable" ] || mv "$BASE/$n.unavailable" "$BASE/$n";done
 [ ! -d "$D.unavailable" ] || mv "$D.unavailable" "$D"
}
trap restore EXIT
for n in "${NAMES[@]}";do mv "$BASE/$n" "$BASE/$n.unavailable";done
mv "$D" "$D.unavailable"
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror JOBS=8
bash "$C/recipes/${NAMES[0]}/scripts/bootstrap.sh" "$C/ws"
for i in "${!NAMES[@]}";do
 N=$C/recipes/${NAMES[$i]}
 for B in B1 B2;do
  TAG=F$i-$B
  bash "$N/scripts/bulk-build.sh" "$C/ws" "$TAG"
  LIEPPOS_BATCH_RECIPE="$N" python3 "$P/scripts/compare-batch.py" "$C/ws/out/$TAG" "$C/comparison-$TAG"
 done
 # Real fresh-family proof before proceeding to next engine; target cache never survives assemble.
 python3 "$P/scripts/check-determinism.py" "$C" "$i"
done
python3 "$P/scripts/check-determinism.py" "$C" all
restore
trap - EXIT
