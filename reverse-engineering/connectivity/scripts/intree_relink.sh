#!/bin/bash
# intree_relink.sh <rel dir under kout> <module> [scmversion]
# GKI-tree modules (cfg80211, mac80211) built via M= lack the modpost in-tree markers; stock vendor build
# was in-tree. Re-emit MODULE_INFO(intree)/(scmversion) exactly where modpost puts them and re-run the
# recorded mod.o compile + final link commands. Code/data are untouched.
. /tmp/connenv.sh
d=$1; m=$2; scm=${3:-g945dff7bc1bf}
cd $KOA
python3 - "$d/$m.mod.c" "$scm" <<'PY'
import sys
p,scm=sys.argv[1:]; s=open(p).read()
if 'MODULE_INFO(intree' not in s:
    k='\t.arch = MODULE_ARCH_INIT,\n};\n'
    s=s.replace(k,k+'\nMODULE_INFO(intree, "Y");\n\nMODULE_INFO(scmversion, "%s");\n'%scm,1)
    open(p,'w').write(s)
PY
for c in $d/.$m.mod.o.cmd $d/.$m.ko.cmd; do eval "$(sed -n '1s/^cmd_[^ ]* := //p' $c | sed 's/;  *make -f .*Makefile.postlink.*//')"; done
