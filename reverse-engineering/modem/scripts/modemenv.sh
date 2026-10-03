# source me: modem parity environment
. /tmp/ispenv.sh
export MR="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/modem"
export CR="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/connectivity"
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KOM=$G/lieppos/modem/kout
export KDO=$G/lieppos/modem/kernel_device_modules-6.1
export NT=/home/armol/kernel-work/public-mtk/nt6878.git
export DTS="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts"
mpa(){ "$MR/scripts/parity_modem.sh" "$@"; }
mpc(){ awk -F'\t' '$6!="EXACT"' "$MR/binary-analysis/per-module/$1.function-parity.tsv"; awk -F'\t' '$6!="EXACT"' "$MR/binary-analysis/per-module/$1.data-parity.tsv"; }
mdc(){ m=$1; shift; s=$(find "$VD" "$VR" -name "$m.ko" | head -1); python3 "$KI/scripts/ko_fdiff.py" "$s" /tmp/mstripped/$m.ko "$@"; }
