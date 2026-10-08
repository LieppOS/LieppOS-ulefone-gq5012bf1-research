#!/bin/bash
# try_gpu_commit.sh <nkm-commit>  : build mali r44p1 (mgm, prot_alloc, kbase) from a NothingOSS kernel_modules commit
set -uo pipefail
W=/home/armol/kernel-work/accelerator-mali-gpu-kernel; C=$1; D=$W/cand/$C
rm -rf $D; mkdir -p $D
git -C /home/armol/kernel-work/public-mtk/nkm.git archive $C gpu/Kbuild gpu/Makefile gpu/mt6878 gpu/gpu_mali/Makefile gpu/gpu_mali/mali_avalon/mali-r44p1 | tar -x -C $D
mv $D/gpu $D/tree
GPU_DIR=$D/tree $W/scripts/kb.sh gpu -j16 modules KBUILD_EXTRA_SYMBOLS="$W/build/kdm/Module.symvers $W/symvers/stock-external-provider.symvers" > $D/build.log 2>&1
echo "rc=$?"
