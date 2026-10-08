#!/bin/bash
# Natural CRCs for the 30 external-provider exports Mali/GED/gpufreq import.
# Full -k build of public MT6878 ALPS 5e415e059253 (local pristine archive 2ae742fda9cd; top Kbuild taken
# from NothingOSS 957dac: it only lists directories) against the same vendor kout; genksyms CRCs
# are read from the '#SYMVER <sym> <crc>' records kbuild (>=5.19) writes into each object's .cmd file.
set -euo pipefail
W=${W:-/home/armol/kernel-work/accelerator-mali-gpu-kernel}; T=$W/provtree
rm -rf $T; mkdir -p $T
git -C /home/armol/kernel-work/gki-12901745-workspace/lieppos/tinysys/trees/5e41 archive 2ae742fda9cd461bfe8cf8a5c04f95e212f8e699 | tar -x -C $T
cp $W/donor/kdm-957dac/Kbuild $T/Kbuild
KDM_DIR=$T $W/scripts/kb.sh kdm -k -j16 modules KBUILD_MODPOST_WARN=1 > $W/provtree.log 2>&1 || true
grep -rh '^#SYMVER ' --include='*.cmd' $T | awk '{print $2, $3}' | sort -u > $W/provtree-symver.txt
python3 - "$W" <<'PY'
import sys; W=sys.argv[1]; nat={}
for l in open(W+'/provtree-symver.txt'):
    s,c=l.split(); nat.setdefault(s,set()).add(int(c,16)&0xffffffff)
with open(W+'/symvers/natural-external-provider.symvers','w') as o:
    for l in open(W+'/symvers/stock-external-provider.symvers'):
        crc,s,m,e,ns=l.rstrip('\n').split('\t'); n=nat[s]; assert len(n)==1, s
        o.write(f"0x{next(iter(n)):08x}\t{s}\t{m}\t{e}\t{ns}\n")
PY
cmp $W/symvers/natural-external-provider.symvers $W/symvers/stock-external-provider.symvers && echo "all natural provider CRCs == stock-published CRCs"
