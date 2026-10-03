#!/bin/bash
# try_conn.sh <commit> <subdir under connectivity> <buildsubdir> <mods...>: overlay from nkm commit, build, parity (tree restored unless KEEPTREE)
. /tmp/connenv.sh
c=$1; d=$2; b=$3; shift 3
rm -rf /tmp/tc && mkdir -p /tmp/tc && git --git-dir=/home/armol/kernel-work/public-mtk/nkm.git archive $c connectivity/$d | tar -m -x -C /tmp/tc || exit 1
rsync -rlpgoD --checksum --delete --exclude='*.o' --exclude='*.ko' --exclude='.*.cmd' /tmp/tc/connectivity/$d/ $CS/$d/
"$CR/scripts/build_ext.sh" $b $BARGS > /tmp/tc_build.log 2>&1
grep -E ' error' /tmp/tc_build.log | head -3
for m in "$@"; do REBUILT=$(find $CO/$b -name $m.ko | head -1) "$CR/scripts/parity_conn.sh" $m 2>&1 | grep -v "^ " | sed "s/^/$c /"; done
if [ -z "$KEEPTREE" ]; then (cd $CS && git checkout -q -- $d && git clean -qfdx $d); fi
