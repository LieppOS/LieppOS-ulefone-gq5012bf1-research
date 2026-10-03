#!/bin/bash
# try_aud.sh <commit> "<dirs>" "<mods>" : overlay dirs from MTK commit into DM (KEEPF files kept from current tree), build, parity; restore unless KEEPTREE
. /tmp/audenv.sh
c=$1; DIRS=$2; MODS=$3
rm -rf /tmp/ta && mkdir -p /tmp/ta && git --git-dir=/home/armol/kernel-work/public-mtk/nt6878.git archive $c $DIRS | tar -m -x -C /tmp/ta
for f in $KEEPF; do mkdir -p /tmp/ta/$(dirname $f); cp $DM/$f /tmp/ta/$f; done
for d in $DIRS; do rsync -rlpgoD --checksum --delete /tmp/ta/$d/ $DM/$d/; done
/tmp/build_aud.sh "$BDIRS" -k > /tmp/ta_build.log 2>&1
grep -E ' error' /tmp/ta_build.log | head -5
"$AR/scripts/parity_aud.sh" $MODS 2>&1 | grep -v "^ " | sed "s/^/$c /"
if [ -z "$KEEPTREE" ]; then (cd $DM && git checkout -q -- $DIRS && git clean -qfd $DIRS); fi
