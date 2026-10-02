#!/bin/bash
# vtest.sh <relpath.c in $B> <tu-key> <func> [occ]  -- compile one TU from its .cmd to /tmp/v.o and compare func vs stock
. /tmp/camenv.sh
src=$1; tu=$2; fn=$3; occ=${4:-0}
d=$(dirname $B/$src); b=$(basename $src .c)
cmd=$(sed -n '1s/^cmd_[^ ]* := //p' $d/.$b.o.cmd | sed "s# -o [^ ]*\.o # -o /tmp/v.o #; s# -Wp,-MMD,[^ ]* # #")
(cd $W/kout && eval "$cmd") 2>&1 | grep -E "error" | head -5
python3 - "$tu" "$fn" "$occ" <<'PY'
import sys,os
sys.path.insert(0, os.environ['RS']+'/scripts')
import imgsensor_parity as P, fdiff as F
from elfmini import Elf
se=Elf(os.environ['SKO']); re_=Elf(os.environ['B']+'/imgsensor.ko')
rb=P.attribute_rebuilt(re_, os.environ['B']); owner={}
for t,s in rb: owner.setdefault(s.name,t)
st=P.attribute_stock(se, owner)
sf=F.find(se,st,sys.argv[1],sys.argv[2],int(sys.argv[3]))
v=Elf('/tmp/v.o'); cand=[s for s in v.symbols if s.name==sys.argv[2] and s.type==2]
cf=cand[int(sys.argv[3])] if len(cand)>int(sys.argv[3]) else cand[0]
import difflib
a=F.listing(os.environ['SKO'],se,sf,P.Normaliser(se)); 
# variant .o: text section may be .text (no -ffunction-sections)
b=F.listing('/tmp/v.o',v,cf,P.Normaliser(v))
import re
n=lambda L:[re.sub(r'adrp (x\d+), <[^>]*>',r'adrp \1',l) for l in L]
same = P.fbytes(se,sf)==P.fbytes(v,cf)
print("BYTES", "EQUAL" if same else "DIFF", sf.size, cf.size, "kcfi", hex(P.kcfi(se,sf)), hex(P.kcfi(v,cf) or 0))
if not same:
    for l in difflib.unified_diff(n(a),n(b),'stock','variant',n=2,lineterm=''): print(l)
PY
