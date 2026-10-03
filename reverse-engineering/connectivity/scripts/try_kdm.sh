#!/bin/bash
# try_kdm.sh <nt6878 commit> "<paths>" "<build dirs>" "<mods>" : overlay paths from commit into KDM, build (connectivity kout), parity; restore unless KEEPTREE
. /tmp/connenv.sh
c=$1; P=$2; BD=$3; MODS=$4
rm -rf /tmp/tk && mkdir -p /tmp/tk && git --git-dir=/home/armol/kernel-work/public-mtk/nt6878.git archive $c $P | tar -m -x -C /tmp/tk || exit 1
for p in $P; do if [ -d /tmp/tk/$p ]; then rsync -rlpgoD --checksum --delete /tmp/tk/$p/ $DM/$p/; else cp /tmp/tk/$p $DM/$p; fi; done
"$CR/scripts/build_kdm.sh" "$BD" -k > /tmp/tk_build.log 2>&1
grep -E ' error' /tmp/tk_build.log | head -3
for m in $MODS; do REBUILT=$(find $G/lieppos/connectivity/kernel_device_modules-6.1 -name $m.ko | head -1) "$CR/scripts/parity_conn.sh" $m 2>&1 | grep -v "^ " | sed "s/^/$c /"; done
if [ -z "$KEEPTREE" ]; then (cd $DM && git checkout -q -- $P && git clean -qfd $P); fi
