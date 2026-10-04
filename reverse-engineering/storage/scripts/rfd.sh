#!/bin/bash
# rfd.sh FUNC : normalized stock-vs-rebuild disasm diff for rpmb-mtk
S='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts'
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
W=/home/armol/kernel-work/gki-12901745-workspace/lieppos/storage
M=${M:-rpmb-mtk}; D=${D:-drivers/char/rpmb}
norm(){ sed -E 's/^ *[0-9a-f]+: //; s/0x[0-9a-f]+ <[^>]*>/<T>/; s/\t/ /g' ; }
for f in "$@"; do
python3 "$S/symdis.py" $W/stock/$M.ko $f | norm > /tmp/rfdA
python3 "$S/symdis.py" $W/trees/5e41/$D/$M.stripped.ko $f | norm > /tmp/rfdB
echo "=== $f A=$(grep -vc ';' /tmp/rfdA) B=$(grep -vc ';' /tmp/rfdB)"
diff /tmp/rfdA /tmp/rfdB | head -${N:-60}
done
