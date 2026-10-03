# source me: connectivity parity environment
. /tmp/ispenv.sh
export CR="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/connectivity"
export AR="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/audio"
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KOA=$G/lieppos/connectivity/kout
export CO=$G/lieppos/connectivity/vendor/mediatek/kernel_modules/connectivity
export CS=$G/vendor/mediatek/kernel_modules/connectivity
export DTS="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts"
cpa(){ "$CR/scripts/parity_conn.sh" "$@"; }
kpc(){ awk -F'\t' '$6!="EXACT"' "$CR/binary-analysis/per-module/$1.function-parity.tsv"; awk -F'\t' '$6!="EXACT"' "$CR/binary-analysis/per-module/$1.data-parity.tsv"; }
kdc(){ m=$1; shift; s=$(find "$VD" "$VR" -name "$m.ko" | head -1); python3 "$KI/scripts/ko_fdiff.py" "$s" /tmp/stripped/$m.ko "$@"; }
