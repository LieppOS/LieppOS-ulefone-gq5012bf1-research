#!/bin/bash
# build-all.sh TREE TAG : rebuild every GQ5012BF1 storage vendor module from TREE, parity into par/<mod>-TAG
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/storage
T=$1; TAG=$2
export XLINUXINCLUDE="-I$PWD/cfg/mtk-ack/include -I$PWD/cfg/mtk-ack/drivers/ufs/core" XKCFLAGS="-fmacro-prefix-map=$PWD/cfg/mtk-ack/="
while read m s o; do
  [ -z "$m" ] && continue
  case $m in rpmb-mtk) X="-include $PWD/cfg/gq5012bf1-no-trustonic.h"; SV=$PWD/cfg/stock-all.ise.symvers;; *) X=""; SV="";; esac
  r=$(XSYMVERS="$SV" XCCFLAGS="$X" MPW=${MPW_ALL:-} ./sb.sh $T $m $s "$o" $TAG 2>&1 | grep -E '^functions|^sections|error' | head -2 | sed -E 's/byte-identical-or.*//; s/functions: //' | tr '\n' ' ')
  echo "$m: $r"
done <<'EOL'
ufs-mediatek-mod drivers/ufs/vendor ../ufs-mediatek.o ../ufs-mediatek-sysfs.o ../ufs-mediatek-mimic.o ../ufs-mediatek-btag.o ../ufs-mediatek-rpmb.o ../ufs-mediatek-ise-dummy.o
ufs-mediatek-dbg drivers/ufs ufs-mediatek-dbg.o
phy-mtk-ufs drivers/phy/mediatek phy-mtk-ufs.o
rpmb drivers/char/rpmb core.o
rpmb-mtk drivers/char/rpmb rpmb-mtk.o
mtk-mmc drivers/mmc/host mtk-mmc.o
mtk-mmc-dbg drivers/mmc/host mtk-mmc-dbg.o
mtk-wp drivers/mmc/host mtk-wp.o
cqhci drivers/mmc/host cqhci-core.o cqhci-crypto.o
blocktag drivers/misc/mediatek/blocktag blocktag-mictx.o blocktag-core.o blocktag-earaio.o blocktag-ufs.o blocktag-mmc.o
EOL
