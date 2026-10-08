#!/bin/bash
# parity.sh <report-dir> [module...]  — ko-pair-parity (stock A vs build B) for owned modules
set -uo pipefail
W=${W:-/home/armol/kernel-work/accelerator-mali-gpu-kernel}
R=$W/research
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
S=$R/workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules
OUT=$1; shift; mkdir -p $OUT
declare -A P=(
 [mtk_gpu_hal]=$W/build/kdm/drivers/gpu/mediatek/hal/mtk_gpu_hal.ko
 [mtk_gpu_qos]=$W/build/kdm/drivers/gpu/mediatek/gpu_bm/mtk_gpu_qos.ko
 [mtk_gpufreq_wrapper]=$W/build/kdm/drivers/gpu/mediatek/gpufreq/v2/mtk_gpufreq_wrapper.ko
 [mtk_gpufreq_mt6878]=$W/build/kdm/drivers/gpu/mediatek/gpufreq/v2/mtk_gpufreq_mt6878.ko
 [ged]=$W/build/kdm/drivers/gpu/mediatek/ged/ged.ko
 [mali_mgm_mt6878_r44]=$W/build/gpu/mt6878/mali_avalon/mali-r44p1/drivers/base/arm/memory_group_manager/mali_mgm_mt6878_r44.ko
 [mali_prot_alloc_mt6878_r44]=$W/build/gpu/mt6878/mali_avalon/mali-r44p1/drivers/base/arm/protected_memory_allocator/mali_prot_alloc_mt6878_r44.ko
 [mali_kbase_mt6878_r44]=$W/build/gpu/mt6878/mali_avalon/mali-r44p1/drivers/gpu/arm/midgard/mali_kbase_mt6878_r44.ko
)
MODS=${*:-mtk_gpu_hal mtk_gpu_qos mtk_gpufreq_wrapper mtk_gpufreq_mt6878 ged mali_mgm_mt6878_r44 mali_prot_alloc_mt6878_r44 mali_kbase_mt6878_r44}
for m in $MODS; do
  b=${P[$m]}; [ -f "$b" ] || { echo "== $m: NOT BUILT"; continue; }
  python3 $R/reverse-engineering/scripts/ko-pair-parity.py $S/$m.ko $b > $OUT/$m.txt 2>&1
  echo "== $m"; grep -E '^(FUNCTIONS|DATA OBJECTS|IMPORTS|EXPORTS|SECTIONS)' $OUT/$m.txt
done
