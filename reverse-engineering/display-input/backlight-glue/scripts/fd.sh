#!/bin/bash
# usage: fd.sh MODULE func [func...]
L=/home/armol/kernel-work/gki-12901745-workspace/lieppos/glue
S='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts'
m=$1; shift; M=$(grep "/$m.ko$" $L/stock-kos.txt)
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
norm(){ sed -E 's/^ *[0-9a-f]+: //; s/0x[0-9a-f]+ <[^>]*>/<T>/; s/\t/ /g' ; }
for f in "$@"; do
python3 "$S/symdis.py" "$M" $f | norm > /tmp/gfdA
python3 "$S/symdis.py" $L/$m/src/$m.stripped.ko $f | norm > /tmp/gfdB
echo "=== $f A=$(grep -vc ';' /tmp/gfdA) B=$(grep -vc ';' /tmp/gfdB)"
diff /tmp/gfdA /tmp/gfdB | head -${N:-80}
done
