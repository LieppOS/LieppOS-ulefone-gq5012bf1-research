#!/usr/bin/env python3
"""Clang kCFI prototype solver.

Clang emits a kCFI type id in the word immediately before every function entry.
That id hashes the *whole prototype*, including the struct tag names of pointer
parameters.  So for a stripped vendor module you can:

  1. read the stock id for a function,
  2. emit N candidate prototypes into one throwaway kernel module,
  3. build it once against the exact GKI tree (~12 s),
  4. read all N ids back and look for the stock id.

A hit proves the prototype exactly - return type, argument types, and the
struct tag names the vendor used - without any vendor source.  A miss over a
large, well-chosen candidate set is itself evidence: it bounds the claim the
way `tkcore`'s member-name search did.

This is how the GQ5012BF1 `tkcore_drv` reconstruction proved that TrustKernel's
private types really are spelled `struct tee`, `struct tee_session`,
`struct tee_cmd` and `struct tee_shm`, and that the CPU-affinity callbacks take
`void *arg` rather than `unsigned long arg` (20/21 ids matched stock; the 21st,
`run_tee_task`, stayed unresolved after 3,690 candidates).

Usage
-----
  # 1. generate candidates into the kleaf package
  python3 gen_kcfi_probe.py --out <ws>/lieppos/kcfi-probe

  # 2. build once
  cd <ws> && tools/bazel build //lieppos/kcfi-probe:kcfi_probe

  # 3. solve
  python3 gen_kcfi_probe.py --solve <ws>/bazel-bin/lieppos/kcfi-probe/\\
      kcfi_probe/kcfi_probe.ko --sigs <out>/sigs.json --target 0xc2052128

Edit RETS/ARGS below (or import build_candidates) to shape the search space.
"""
from __future__ import annotations

import argparse
import itertools
import json
import struct
import subprocess
import sys
from pathlib import Path

# Default search space: tune per target before generating.
RETS = ["void", "int"]
ARG_SLOTS = [
    ["struct tee_tz *", "struct tee *", "void *"],
    ["struct smc_param *", "struct arm_smccc_res *", "void *"],
    ["struct tee_affinity *", "const struct tee_affinity *", "void *"],
]


def build_candidates(rets=None, slots=None):
    rets = rets or RETS
    slots = slots or ARG_SLOTS
    return [(r, list(a)) for r in rets for a in itertools.product(*slots)]


def emit(cands, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    tags = set()
    for _, args in cands:
        for t in args:
            t = t.replace("const ", "")
            if t.startswith("struct ") and t != "struct arm_smccc_res *":
                tags.add(t.replace(" *", "").split()[1])

    lines = ["#include <linux/module.h>", "#include <linux/types.h>",
             "#include <linux/arm-smccc.h>", ""]
    lines += ["struct %s;" % t for t in sorted(tags)]
    lines.append("")

    sigs = []
    for i, (ret, args) in enumerate(cands):
        name = "probe_%04d" % i
        params = ", ".join("%s%sa%d" % (t, "" if t.endswith("*") else " ", j)
                           for j, t in enumerate(args))
        body = "" if ret == "void" else "return 0;"
        lines.append("%s %s(%s) { %s }" % (ret, name, params, body))
        lines.append("EXPORT_SYMBOL(%s);" % name)
        sigs.append((name, ret, args))

    lines += ["",
              "static int __init probe_init(void) { return 0; }",
              "static void __exit probe_exit(void) { }",
              "module_init(probe_init);",
              "module_exit(probe_exit);",
              'MODULE_LICENSE("GPL");']

    (out / "kcfi_probe.c").write_text("\n".join(lines) + "\n")
    (out / "sigs.json").write_text(json.dumps(sigs))

    here = Path(__file__).resolve().parent
    for f in ("Makefile", "BUILD.bazel"):
        (out / f).write_text((here / f).read_text())
    return len(sigs)


def kcfi_ids(ko: Path) -> dict:
    """name -> kCFI type id (the word immediately before the entry point)."""
    blob = ko.read_bytes()
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 0x3A)
    offs = {i: struct.unpack_from("<IIQQQQIIQQ", blob,
                                  e_shoff + i * shentsize)[4]
            for i in range(shnum)}
    out = subprocess.run(["readelf", "-sW", str(ko)], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or f[3] != "FUNC" or f[6] in ("UND", "ABS"):
            continue
        try:
            value, idx = int(f[1], 16), int(f[6])
        except ValueError:
            continue
        if value < 4:
            continue
        res[f[7].split(".")[0]], = struct.unpack_from("<I", blob,
                                                      offs[idx] + value - 4)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="generate candidates into this package dir")
    ap.add_argument("--solve", help="built kcfi_probe.ko to read ids from")
    ap.add_argument("--sigs", help="sigs.json written by --out")
    ap.add_argument("--target", help="stock kCFI id to search for, e.g. 0xc2052128")
    args = ap.parse_args()

    if args.out:
        n = emit(build_candidates(), Path(args.out))
        print("wrote %d candidates to %s" % (n, args.out))

    if args.solve:
        ids = kcfi_ids(Path(args.solve))
        sigs = json.loads(Path(args.sigs).read_text())
        print("read %d/%d probe ids" % (sum(1 for n, _, _ in sigs if n in ids),
                                        len(sigs)))
        if args.target:
            want = int(args.target, 16)
            hits = [(r, a) for n, r, a in sigs if ids.get(n) == want]
            if hits:
                for ret, argv in hits:
                    print("HIT: %s(%s)" % (ret, ", ".join(argv)))
            else:
                print("no hit for 0x%08x over %d candidates" % (want, len(sigs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
