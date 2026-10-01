#!/bin/bash
# usage: run.sh NAME args...
. /tmp/a17env.sh
N=$1; shift
{ echo "===== RUN $N ====="; echo "\$ $CV $*"; } >> "$T"
"$CV" "$@" > $WK/run$N.stdout 2> $WK/run$N.stderr.raw
rc=$?
sed 's/\x1b\[[0-9;]*m//g' $WK/run$N.stderr.raw > $WK/run$N.stderr
echo "$rc" > $WK/run$N.exit
{ echo "--- stdout ---"; cat $WK/run$N.stdout; echo "--- stderr ---"; cat $WK/run$N.stderr; echo "--- exit status: $rc ---"; } >> "$T"
echo "RUN $N exit=$rc stdout_lines=$(wc -l <$WK/run$N.stdout) stderr_lines=$(wc -l <$WK/run$N.stderr) last_stdout=$(tail -n1 $WK/run$N.stdout)"
