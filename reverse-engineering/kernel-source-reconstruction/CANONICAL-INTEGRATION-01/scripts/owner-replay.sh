#!/bin/bash
# Independent owner replay of CANONICAL-INTEGRATION-01 from canonical f61ebf03.
#   owner-replay.sh <new-worktree-path> <integration-commit> <authentic-operand-root> <report-dir>
# <authentic-operand-root> must contain workspace/gq5012bf1 and kernel/nothing-module-index.csv
# that pass STOCK-INVENTORY-INTEGRITY verify-inventory.py (458/471, 60/60 signed). Never point
# it at the damaged canonical shared copies. Creates a detached worktree; never touches master.
set -euo pipefail
W=$1; I=$2; SRC=$3; OUT=$4
ROOT='/home/armol/androido_dalykai/LieppOS custom ROM'; C="$ROOT/ulefone-gq5012bf1-research"
PKG=reverse-engineering/kernel-source-reconstruction/CANONICAL-INTEGRATION-01
AUD=reverse-engineering/kernel-source-parity-audit
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"; [ ! -e "$W" ]
git -C "$C" worktree add -q --detach "$W" f61ebf03275ba2d3f6aa4f9d5aebe18e12922263
cp -a --reflink=auto "$SRC/workspace/gq5012bf1" "$W/workspace/gq5012bf1"
cp --reflink=auto "$SRC/kernel/nothing-module-index.csv" "$W/kernel/"
git -C "$C" show 143a6db2:reverse-engineering/kernel-source-reconstruction/STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py > "$OUT/verify-inventory.py"
python3 "$OUT/verify-inventory.py" "$W" --json "$OUT/inventory.json" > /dev/null
python3 -c "import json,sys;d=json.load(open('$OUT/inventory.json'));assert d['result']=='PASS' and not d['errors'],d['errors'][:5]"
G() { git -C "$W" -c user.name='LieppOS Canonical Integration' -c user.email='integration@lieppos.local' "$@"; }
G merge -q --ff-only 437ebd5762afa2512fe1ba10102e6b4f4d6beba9
for x in "f00bd8af7e6bd4fde4355ae67e8392feab596a80 AUDIO-BATCH-01" "40bfedda097cc33d05eba145fa0c51d6ceb0a07e SCP-CONNECTIVITY-BATCH-01" \
         "fb558640b3227eb57b4172e129c6048b46d07ed6 AUDIO-DEPENDENCIES-BATCH-02" "143a6db22434216e815e4a16c5da41a255efed2b STOCK-INVENTORY-INTEGRITY"; do
  set -- $x; t=$(git -C "$W" rev-parse HEAD^{tree})
  G merge -q --no-ff -m "replay: record original $2 history ($1)" "$1"; [ "$(git -C "$W" rev-parse HEAD^{tree})" = "$t" ]
done
G merge -q --no-ff -m 'replay: merge USB-TYPEC-CLOSURE' 7e196c3242ecb7bc0d203ddb3669c97e86e24655
G merge -q --no-ff -m 'replay: merge ALL-C-TO-A-CLOSURE' 652e41958056816fe70c8e9064ad5c56f8818f2b
# committed integration inputs only (scripts + reverify evidence); generated outputs are recomputed
mkdir -p "$W/$PKG"; git -C "$C" archive "$I" "$PKG/scripts" "$PKG/evidence/reverify" | tar -x -C "$W"
H=$(git -C "$W" rev-parse HEAD)
python3 "$W/$PKG/scripts/plan-canonical.py" > "$OUT/plan.log"
python3 "$W/$PKG/scripts/apply-canonical.py" --expected-head "$H" --apply > "$OUT/apply.log" 2>&1
python3 "$W/$PKG/scripts/finalize-summary.py" > "$OUT/finalize.log"
(cd "$W/$AUD/scripts" && python3 validate.py > "$OUT/validate.json" && python3 test_validate.py -v > "$OUT/mutations.log" 2>&1)
# byte-identity of every audit file and of the regenerated CAS plan / application log
for f in $(git -C "$C" ls-tree -r --name-only "$I" "$AUD"); do
  cmp -s "$W/$f" <(git -C "$C" show "$I:$f") || echo "DIFF $f"
done > "$OUT/audit-diff.txt"
for f in CAS-PLAN.tsv DELTA-APPLICATION-LOG.tsv CLASSIFICATIONS-BEFORE-AFTER.tsv; do
  cmp -s "$W/$PKG/$f" <(git -C "$C" show "$I:$PKG/$f") || echo "DIFF $PKG/$f"
done >> "$OUT/audit-diff.txt"
( cd "$W" && git ls-files "$AUD" | sort | xargs sha256sum ) > "$OUT/audit-sha256.txt"
python3 - "$OUT" <<'EOF'
import json,sys
o=sys.argv[1];v=json.load(open(o+'/validate.json'));d=open(o+'/audit-diff.txt').read().split('\n')
r=dict(validator=v['result'],errors=len(v['errors']),counts=v['source_status_counts'],identities=v['distinct_stock_identities'],
       occurrences=v['stock_occurrences'],mutations='OK' in open(o+'/mutations.log').read().splitlines()[-1],
       differing_files=[x for x in d if x])
json.dump(r,open(o+'/replay-result.json','w'),indent=2);print(json.dumps(r))
assert not r['differing_files'] and r['errors']==0 and r['mutations']
EOF
