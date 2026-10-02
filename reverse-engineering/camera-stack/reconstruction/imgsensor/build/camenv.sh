export G=/home/armol/kernel-work/gki-12901745-workspace
export W=$G/lieppos/camera-imgsensor
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export RS="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/camera-stack"
export SKO="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/imgsensor.ko"
export B=$G/vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2
fd(){ python3 "$RS/scripts/fdiff.py" "$SKO" $B/imgsensor.ko $B "$@"; }
fdr(){ python3 "$RS/scripts/fdiff.py" "$SKO" $B/imgsensor.ko $B "$1" "$2" ${3:-0} --stock-only | grep ";" | sed 's/^ *[0-9a-f]*: //' > /tmp/fdr.s; python3 - "$1" "$2" ${3:-0} <<'PY'
import sys,os,subprocess,difflib
sys.path.insert(0, os.environ['RS']+'/scripts')
import imgsensor_parity as P, fdiff as F
from elfmini import Elf
re_=Elf(os.environ['B']+'/imgsensor.ko'); rb=P.attribute_rebuilt(re_, os.environ['B'])
f=F.find(re_, rb, sys.argv[1], sys.argv[2], int(sys.argv[3]))
import re
rl=[re.sub(r'^ *[0-9a-f]*: ','',l) for l in F.listing(os.environ['B']+'/imgsensor.ko', re_, f, P.Normaliser(re_)) if ';' in l]
sl=open('/tmp/fdr.s').read().splitlines()
norm=lambda l: re.sub(r'<[^>]*>','',l)
for l in difflib.unified_diff([norm(x) for x in sl],[norm(x) for x in rl],'stock','rebuilt',n=1,lineterm=''): print(l)
PY
}
