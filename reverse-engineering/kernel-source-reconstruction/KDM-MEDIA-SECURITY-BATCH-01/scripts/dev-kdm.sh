#!/bin/bash
# Development-only KDM stage (no native): assemble, objects, witnesses, module link, strip.
# Mirrors bulk-build.sh KDM path exactly; native targets are built separately while the BTF base builds.
set -euo pipefail
N='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_kdm_media_security_ulefone_gq5012bf1'
cd /tmp; source "$N/scripts/lib.sh"; need_ws "$1"; TAG=$2; OUT=$WS/out/$TAG; mkdir -p "$OUT"
export KBUILD_BUILD_USER=lieppos KBUILD_BUILD_HOST=kdm-media-build KBUILD_BUILD_VERSION=1 KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026'
MARK='# LieppOS kdm-media-security-batch-01:'
bash "$N/scripts/assemble.sh" "$WS"
T=$SRC/kdm
GOALS=$(python3 - "$T" "$MARK" <<'PY'
import re,sys
from pathlib import Path
T=Path(sys.argv[1])
for f in sorted(T.rglob('Makefile')):
 if sys.argv[2] not in f.read_text(errors='replace'):continue
 for m in re.findall(r'^obj-m \+= (\S+\.o)$',f.read_text(),re.M):print(f.parent.relative_to(T)/m)
PY
)
COMMON=$COMMON KO=$KOUT KDM_DIR=$T bash "$N/scripts/kb.sh" -k -j"${JOBS:-4}" $GOALS > "$OUT/objects.log" 2>&1 && echo 0 > "$OUT/object-exit" || echo $? > "$OUT/object-exit"
python3 "$N/scripts/provider-witness.py" "$T" "$OUT/provider" > "$OUT/provider.log" 2>&1 || true
python3 - "$T" "$N/reference/BATCH-MANIFEST.tsv" "$MARK" <<'PY'
import csv,re,sys
from pathlib import Path
T=Path(sys.argv[1]);want={r['candidate_directory']+'/'+r['filename'].removesuffix('.ko')+'.o' for r in csv.DictReader(open(sys.argv[2]),delimiter='\t') if r['build_domain']=='KDM'}
for f in T.rglob('Makefile'):
 text=f.read_text(errors='replace')
 if sys.argv[3] not in text:continue
 f.write_text(''.join(l for l in text.splitlines(keepends=True) if not (re.match(r'^obj-m \+= (\S+\.o)$',l) and str(f.parent.relative_to(T)/re.match(r'^obj-m \+= (\S+\.o)$',l)[1]) not in want)))
PY
cp "$OUT/provider/natural-external-provider.symvers" "$OUT/joint-extra.symvers"
COMMON=$COMMON KO=$KOUT KDM_DIR=$T bash "$N/scripts/kb.sh" -k -j"${JOBS:-4}" KBUILD_EXTRA_SYMBOLS="$OUT/joint-extra.symvers" modules > "$OUT/modules.log" 2>&1 && echo 0 > "$OUT/module-exit" || echo $? > "$OUT/module-exit"
while IFS=$'\t' read -r d m; do [ -f "$T/$d/$m.ko" ] && { cp "$T/$d/$m.ko" "$OUT/"; llvm-strip --strip-debug -o "$OUT/$m.stripped" "$OUT/$m.ko"; } || true; done <<< "$MODULES"
log "dev KDM object=$(cat $OUT/object-exit) module=$(cat $OUT/module-exit)"
