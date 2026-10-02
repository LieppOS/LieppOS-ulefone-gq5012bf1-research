#!/usr/bin/env python3
"""Identifier-level source coverage of stock camera kernel modules against a
donor source tree (cheap pre-build triage, not a parity proof).

For every listed stock .ko: defined FUNC symbols (minus compiler/kbuild
artefacts) and the fraction whose identifier appears as a C definition-like
token in the donor tree, plus the donor directory holding most hits.
Strings are also checked (format strings unique to a driver are strong
provenance markers).

Usage: module_source_coverage.py <modules_dir> <donor_root> <out.tsv> <mod.ko>...
"""
from __future__ import annotations

import collections
import os
import re
import subprocess
import sys

SKIP = re.compile(r"^(__|init_module|cleanup_module|\$|_note_|\.L)|\.cfi|\.llvm\.")


def funcs(ko):
    out = subprocess.run(["readelf", "-sW", ko], capture_output=True, text=True).stdout
    r = []
    for l in out.splitlines():
        f = l.split()
        if len(f) >= 8 and f[3] == "FUNC" and f[6] not in ("UND", "ABS") and not SKIP.search(f[7]):
            r.append(f[7])
    return sorted(set(r))


def strings(ko):
    out = subprocess.run(["strings", "-a", "-n", "12", ko], capture_output=True, text=True).stdout
    return [s for s in out.splitlines() if "%" in s and " " in s][:400]


def main():
    mdir, donor, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    mods = sys.argv[4:]
    # index donor identifiers -> files (C/H only)
    ident = collections.defaultdict(set)
    texts = {}
    for dp, dn, fn in os.walk(donor):
        for f in fn:
            if f.endswith((".c", ".h")):
                p = os.path.join(dp, f)
                try:
                    t = open(p, errors="replace").read()
                except OSError:
                    continue
                texts[p] = t
                for m in set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]{3,})\s*\(", t)):
                    ident[m].add(p)
    with open(outp, "w") as fo:
        fo.write("module\tstock_funcs\tfuncs_named_in_donor\tpct\tbest_donor_dir\tbest_dir_hits\t"
                 "fmt_strings\tfmt_strings_in_best_dir\tmissing_examples\n")
        for m in mods:
            ko = os.path.join(mdir, m)
            fs = funcs(ko)
            hit = [f for f in fs if f in ident]
            dirs = collections.Counter()
            for f in hit:
                for p in ident[f]:
                    dirs[os.path.relpath(os.path.dirname(p), donor)] += 1
            best, bh = (dirs.most_common(1)[0] if dirs else ("", 0))
            st = strings(ko)
            bdir = os.path.join(donor, best)
            blob = "".join(t for p, t in texts.items() if p.startswith(bdir + os.sep) or
                           os.path.dirname(p) == bdir)
            sh = sum(1 for s in st if s.strip().lstrip("\x01")[1:40].strip() and
                     s.strip().lstrip("\x0123456789")[:30] in blob)
            miss = [f for f in fs if f not in ident][:12]
            pct = 100.0 * len(hit) / len(fs) if fs else 0
            fo.write(f"{m}\t{len(fs)}\t{len(hit)}\t{pct:.1f}\t{best}\t{bh}\t{len(st)}\t{sh}\t{','.join(miss)}\n")
            print(f"{m:32s} funcs {len(fs):5d} named-in-donor {len(hit):5d} ({pct:5.1f}%) best={best} "
                  f"fmt {sh}/{len(st)}")


if __name__ == "__main__":
    main()
