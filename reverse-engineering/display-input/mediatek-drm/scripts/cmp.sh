#!/bin/bash
# cmp.sh BASE CAND : functions that become exact (+) or stop being exact (-)
export LC_ALL=C
join -t$'\t' <(awk -F'\t' 'NR>1{print $1"\t"$4}' par-$1/function-parity.tsv | sort) <(awk -F'\t' 'NR>1{print $1"\t"$4}' par-$2/function-parity.tsv | sort) | awk -F'\t' '$2!="BYTE-IDENTICAL" && $3=="BYTE-IDENTICAL"{print "+ "$1} $2=="BYTE-IDENTICAL" && $3!="BYTE-IDENTICAL"{print "- "$1}'
