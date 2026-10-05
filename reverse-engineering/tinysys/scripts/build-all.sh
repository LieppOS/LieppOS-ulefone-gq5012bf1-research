#!/bin/bash
# build-all.sh TAG : isolated M= rebuild of the two TinySys messaging modules from the pinned
# KDM tree (MTK ALPS mt6878 5e415e059253, pristine) + parity vs stock into par/<mod>-TAG.
# Workspace: /home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys (trees/5e41 branch tinysys = base 2ae742f).
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys
TAG=${1:-B1}
./sb.sh trees/5e41 mtk_rpmsg_mbox  drivers/rpmsg          mtk_rpmsg_mbox.o  $TAG
./sb.sh trees/5e41 mtk_tinysys_ipi drivers/soc/mediatek   mtk_tinysys_ipi.o $TAG
