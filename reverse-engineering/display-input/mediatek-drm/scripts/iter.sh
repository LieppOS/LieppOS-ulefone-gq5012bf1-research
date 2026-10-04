#!/bin/bash
# iter.sh TAG : build recon, parity -> par-TAG, summary + delta vs par-5e415e059253
cd /home/armol/kernel-work/gki-12901745-workspace/lieppos/drm
S='/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts'
export PATH=/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
./build.sh recon >/dev/null || exit 1
rm -rf par-$1; python3 "$S/ko-parity-tsv.py" stock-mediatek-drm.ko recon/drivers/gpu/drm/mediatek/mediatek_v2/mediatek-drm.stripped.ko par-$1 > par-$1.log 2>&1
grep -h '^functions\|^data\|^exports\|^imports' par-$1/SUMMARY.txt | cut -c1-140
./cmp.sh ${BASE:-5e415e059253} $1 | sort | awk '{c[$1]++; l[$1]=l[$1]" "$2} END{for(k in c) print k, c[k]":", substr(l[k],1,600)}'
