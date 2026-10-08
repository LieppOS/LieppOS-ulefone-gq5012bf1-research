#!/bin/bash
# MALI-GPU-KERNEL deterministic clean builds B1 and B2 of all 8 owned modules.
# Each build: wipe $CLEAN, git-archive the pinned reconstruction trees, fresh copy of the
# prepared vendor kout, build kdm (ged, hal, gpu_bm, gpufreq) then gpu (mali r44p1) against
# kdm's natural Module.symvers + the stock external-provider ABI record. Same absolute paths
# for B1 and B2 (DWARF paths feed the build-id).
set -euo pipefail
W=${W:-/home/armol/kernel-work/accelerator-mali-gpu-kernel}
CLEAN=$W/clean; OUT=${OUT:-$W/b1b2}
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
KDM_REV=$(git -C $W/build/kdm rev-parse HEAD); GPU_REV=$(git -C $W/build/gpu rev-parse HEAD)
mods="drivers/gpu/mediatek/hal/mtk_gpu_hal drivers/gpu/mediatek/gpu_bm/mtk_gpu_qos drivers/gpu/mediatek/gpufreq/v2/mtk_gpufreq_wrapper drivers/gpu/mediatek/gpufreq/v2/mtk_gpufreq_mt6878 drivers/gpu/mediatek/ged/ged"
gmods="gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/memory_group_manager/mali_mgm_mt6878_r44 gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/protected_memory_allocator/mali_prot_alloc_mt6878_r44 gpu_mali/mali_avalon/mali-r44p1/drivers/gpu/arm/midgard/mali_kbase_mt6878_r44"
rm -rf $OUT; mkdir -p $OUT
for b in B1 B2; do
  rm -rf $CLEAN; mkdir -p $CLEAN/kdm $CLEAN/gpu
  git -C $W/build/kdm archive $KDM_REV | tar -x -C $CLEAN/kdm
  git -C $W/build/gpu archive $GPU_REV | tar -x -C $CLEAN/gpu
  rm -rf $W/kout-clean; cp -a $W/kout-base $W/kout-clean   # same depth as common: kbuild resolves relative M= against O=
  export KO=$W/kout-clean KDM_DIR=$CLEAN/kdm GPU_DIR=$CLEAN/gpu
  $W/scripts/kb.sh kdm -j16 modules KBUILD_EXTRA_SYMBOLS=$W/symvers/stock-external-provider.symvers > $OUT/$b.kdm.log 2>&1
  $W/scripts/kb.sh gpu -j16 modules KBUILD_EXTRA_SYMBOLS="$CLEAN/kdm/Module.symvers $W/symvers/stock-external-provider.symvers" > $OUT/$b.gpu.log 2>&1
  mkdir -p $OUT/$b
  for m in $mods; do cp $CLEAN/kdm/$m.ko $OUT/$b/; done
  for m in $gmods; do cp $CLEAN/gpu/$m.ko $OUT/$b/; done
  cp $CLEAN/kdm/Module.symvers $OUT/$b/kdm.Module.symvers; cp $CLEAN/gpu/Module.symvers $OUT/$b/gpu.Module.symvers
  for k in $OUT/$b/*.ko; do llvm-strip --strip-debug -o ${k%.ko}.stripped $k; done
  (cd $OUT/$b && sha256sum *.ko *.stripped *.symvers > SHA256SUMS)
done
echo "kdm=$KDM_REV gpu=$GPU_REV"
if diff $OUT/B1/SHA256SUMS $OUT/B2/SHA256SUMS; then echo "B1 == B2 (all .ko, stripped .ko and Module.symvers byte-identical)"; else echo "B1 != B2"; exit 1; fi
