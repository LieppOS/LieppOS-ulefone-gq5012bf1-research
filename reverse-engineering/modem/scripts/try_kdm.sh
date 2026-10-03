#!/bin/bash
# try_kdm.sh <nt6878 commit> "<paths>" "<build dirs>" "<mods>" : overlay paths from commit into KDM, build ($KOM), parity; restore unless KEEPTREE
. /tmp/modemenv.sh
c=$1; P=$2; BD=$3; MODS=$4
rm -rf /tmp/tkm && mkdir -p /tmp/tkm && git --git-dir=$NT archive $c $P | tar -m -x -C /tmp/tkm || exit 1
for p in $P; do if [ -d /tmp/tkm/$p ]; then rsync -rlpgoD --checksum --delete /tmp/tkm/$p/ $DM/$p/; else cp /tmp/tkm/$p $DM/$p; fi; done
"$MR/scripts/build_kdm.sh" "$BD" -k > /tmp/tkm_build.log 2>&1
grep -E ' error' /tmp/tkm_build.log | head -3
for m in $MODS; do "$MR/scripts/parity_modem.sh" $m 2>&1 | grep -v "^ " | sed "s/^/$c /"; done
if [ -z "$KEEPTREE" ]; then (cd $DM && git checkout -q -- $P && git clean -qfd $P); fi
