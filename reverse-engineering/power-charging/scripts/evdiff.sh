#!/bin/bash
# evdiff <module> <func> : diff of string/call/global event sequence
. /tmp/ispenv.sh
m=$1; f=$2
kdp $m $f --stock-only | grep -oE "S:'[^']*'|S:\"[^\"]*\"|CALL26 [A-Za-z_:0-9.]+|LDST[0-9]+_ABS_LO12_NC [a-z_]+|#0x[0-9a-f]{3,4}\b" | grep -v "ADR_PREL" > /tmp/ev_s.txt
kdp $m $f --rebuilt-only | grep -oE "S:'[^']*'|S:\"[^\"]*\"|CALL26 [A-Za-z_:0-9.]+|LDST[0-9]+_ABS_LO12_NC [a-z_]+|#0x[0-9a-f]{3,4}\b" | grep -v "ADR_PREL" > /tmp/ev_r.txt
diff /tmp/ev_s.txt /tmp/ev_r.txt
