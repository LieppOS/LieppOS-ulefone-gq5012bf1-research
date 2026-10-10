#!/bin/bash
# Offline independent source clones and fresh target compilation with originals unavailable.
set -euo pipefail
P=$(cd "$(dirname "$0")/.." && pwd);R=$(cd "$P/../../.." && pwd);BASE=$(dirname "$R")
C=/home/armol/kernel-work/platform-batch-01-cleancheck;D=/home/armol/kernel-work/platform-batch-01-dev
mkdir -p "$C/recipes"
NAMES=(android_kernel_modules_cmdq_ulefone_gq5012bf1 android_kernel_modules_iommu_aux_ulefone_gq5012bf1 android_kernel_modules_smi_platform_ulefone_gq5012bf1 android_kernel_modules_power_platform_ulefone_gq5012bf1)
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
N=$C/recipes/android_kernel_modules_power_platform_ulefone_gq5012bf1
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror JOBS=8
bash "$N/scripts/bootstrap.sh" "$C/ws"
for B in B1 B2;do
 # Headers may be safely reused: complete base config and official ABI are verified each run.
 # assemble always deletes ALL target/provider source outputs: no target cache reuse.
 bash "$N/scripts/bulk-build.sh" "$C/ws" "$B"
 LIEPPOS_BATCH_RECIPE="$N" python3 "$P/scripts/compare-batch.py" "$C/ws/out/$B" "$C/comparison-$B"
done
python3 - "$C" <<'PY'
import sys,json,hashlib
from pathlib import Path
C=Path(sys.argv[1]);A=C/'ws/out/B1';B=C/'ws/out/B2'
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','batch-stock-provider.Module.symvers','provider/natural-external-provider.symvers','provider/scpsys-dummy.symvers','provider/provider-witnesses.json','provider/scpsys-link-name-witnesses.json']:
 assert (A/f).read_bytes()==(B/f).read_bytes(),f
assert len(list(A.glob('*.ko')))==len(list(B.glob('*.ko')))==35
for f in A.glob('*.ko'):assert f.read_bytes()==(B/f.name).read_bytes(),f
for f in A.glob('*.stripped'):assert f.read_bytes()==(B/f.name).read_bytes(),f
j=json.loads((C/'comparison-B1/comparison.json').read_text());k=json.loads((C/'comparison-B2/comparison.json').read_text());assert j==k
accepted=[x['module'] for x in j if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];failed=[x['module'] for x in j if x['status']=='SOURCE_BUILD_UNVERIFIED'];assert len(accepted)==31 and len(failed)==4
(C/'cleancheck-result.json').write_text(json.dumps({'result':'PASS_31_ACCEPTED_4_REPRODUCED_ABI_RESIDUALS','original_development_and_all_four_recipes_unavailable_during_build':True,'fresh_source_recipe_clones':4,'fresh_target_and_provider_recompilation_each_build':True,'base_headers_reused_with_hash_verification':True,'raw_modules_deterministic':35,'stripped_modules_deterministic':35,'intermediate_object_count':len((A/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'independently_stock_accepted':accepted,'unaccepted_residuals':failed,'unexpected_failures':[]},indent=2)+'\n')
print('PASS:31 accepted,4 accurately unaccepted;35 raw/stripped modules and intermediates deterministic')
PY
restore
trap - EXIT
