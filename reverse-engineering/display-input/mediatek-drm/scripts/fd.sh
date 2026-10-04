#!/bin/bash
# fd.sh BUILD_KO func... : normalized disasm diff stock vs build
S='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts'
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
B=$1; shift
norm(){ sed -E 's/^ *[0-9a-f]+: //; s/0x[0-9a-f]+ <[^>]*>/<T>/; s/\t/ /g' ; }
for f in "$@"; do
python3 "$S/symdis.py" /home/armol/kernel-work/gki-12901745-workspace/lieppos/drm/stock-mediatek-drm.ko $f | norm > /tmp/dfdA
python3 "$S/symdis.py" $B $f | norm > /tmp/dfdB
echo "=== $f A=$(grep -vc ';' /tmp/dfdA) B=$(grep -vc ';' /tmp/dfdB)"
diff /tmp/dfdA /tmp/dfdB | head -${N:-60}
done
