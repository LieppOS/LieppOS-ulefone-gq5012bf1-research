#!/bin/bash
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/storage
export XLINUXINCLUDE="-I$PWD/cfg/mtk-ack/include -I$PWD/cfg/mtk-ack/drivers/ufs/core" XKCFLAGS="-fmacro-prefix-map=$PWD/cfg/mtk-ack/="
XSYMVERS=$PWD/cfg/stock-all.ise.symvers XCCFLAGS="-include $PWD/cfg/gq5012bf1-no-trustonic.h ${RX}" ./sb.sh trees/5e41 rpmb-mtk drivers/char/rpmb rpmb-mtk.o ${1:-w} 2>&1 | grep -v '^  ' | head -${L:-3}
awk -F'\t' 'NR>1 && $4!="BYTE-IDENTICAL"{print $1, $2, $3, $4}' par/rpmb-mtk-${1:-w}/function-parity.tsv
