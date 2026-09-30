#!/usr/bin/env python3
"""Generate the vdcmd (class, op) registry header from the extracted evidence TSV.

The InfiRay vdcmd request space is *two-dimensional*: a 16-bit group/class field
(e.g. 0x0101, 0x0410, 0x1010) plus an 8-bit operation code inside that group
(e.g. 0x41, 0x81).  A register is therefore addressed by the pair, and this tool
emits exactly that pair table -- it deliberately does NOT flatten the pairs into
one dense `VDCMD_OPCODE_<n>` space, because a missing pair then looks like a hole
in a linear range that never existed.

Rows are emitted in TSV order, one per helper, so a (class, op) pair that several
helpers claim stays visible as several rows *and* is summarised in the ambiguity
block at the end.  `--allow-ambiguous N` turns that count into a regression gate.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
from collections import defaultdict

FIELDS = ("class_id", "op", "name", "builder")

PREAMBLE = """/**
 * vdm-opcode-registry.h — generated; DO NOT EDIT.
 *
 * vdcmd (class, op) registry for the InfiRay M32 thermal module, rebuilt from the
 * unstripped vendor payload library by qwen-thermal/tools/gen-vdm-opcode-registry.py.
 * One row per exported helper that builds a frame with that pair; a pair claimed
 * by more than one helper appears once per helper and is also listed in the
 * ambiguity block, because at most one of those names can be the register's real
 * purpose.  See ../findings/vdm-opcode-recovery.md for the method and limits.
 *
 * The request space is a (class, op) pair, not a linear opcode range: never treat
 * a missing pair as evidence of an unrelated subsystem.
 */
#ifndef VDM_OPCODE_REGISTRY_H
#define VDM_OPCODE_REGISTRY_H

#include <stdint.h>

struct vdm_opcode_desc {
    uint16_t class_id;
    uint8_t op;
    uint8_t builder; /* enum VDM_FRAME_BUILDER */
    const char *name;
};

"""

BUILDERS = """/* Frame builder shapes observed in the vendor library. */
enum vdm_frame_builder {
    VDM_FRAME_STD_READ = 1,     /* vdcmd_std_header read  (std.read)        */
    VDM_FRAME_STD_WRITE = 2,    /* vdcmd_std_header write (std.write)       */
    VDM_FRAME_STD_WRITE_NORD = 3, /* std.write_nord: no reply expected      */
    VDM_FRAME_SHORT_READ = 4,   /* vdcmd_short_header read                  */
    VDM_FRAME_SHORT_WRITE = 5,  /* vdcmd_short_header write                 */
    VDM_FRAME_LONG_READ = 6,    /* vdcmd_long_header read                   */
    VDM_FRAME_LONG_WRITE = 7    /* vdcmd_long_header write                  */
};

"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", default="libircmd020.so")
    ap.add_argument("--allow-ambiguous", type=int, default=None,
                    help="fail when the number of multiply-claimed (class, op) pairs differs from N")
    a = ap.parse_args()

    rows = list(csv.DictReader(pathlib.Path(a.tsv).read_text().splitlines(), delimiter="\t"))
    if not rows:
        raise SystemExit(f"no rows in {a.tsv}")
    unnamed = [r["symbol"] for r in rows if not r["op"]]
    rows = [r for r in rows if r["op"]]

    by_key = defaultdict(list)
    for r in rows:
        by_key[(int(r["class"], 16), int(r["op"], 16))].append(r["symbol"])
    ambiguous = {k: sorted(set(v)) for k, v in by_key.items() if len(set(v)) > 1}
    if a.allow_ambiguous is not None and len(ambiguous) != a.allow_ambiguous:
        raise SystemExit(f"{len(ambiguous)} ambiguous pairs, expected {a.allow_ambiguous}")

    out = [PREAMBLE,
           f"/* Source: {a.source}; evidence {a.tsv} — {len(rows)} helper rows, "
           f"{len(by_key)} distinct (class, op) pairs, {len(ambiguous)} of them multiply claimed. */\n\n",
           BUILDERS,
           f"/* Helpers whose frame carried no operation code: "
           f"{', '.join(unnamed) if unnamed else 'none'}. */\n\n",
           "static const struct vdm_opcode_desc vdm_opcode_table[] = {\n"]
    for r in rows:
        out.append(f'    {{{int(r["class"], 16):#07x}, {int(r["op"], 16):#05x}, '
                   f'{r["builder"].upper().replace(".", "_")}, "{r["symbol"]}"}},\n')
    out.append("};\n\n")
    out.append(f"#define VDM_OPCODE_TABLE_LEN {len(rows)}u\n")
    out.append(f"#define VDM_OPCODE_PAIR_COUNT {len(by_key)}u\n\n")
    out.append("/* Ambiguous pairs: more than one exported helper builds this (class, op).\n")
    for (cls, op) in sorted(ambiguous):
        out.append(f" * ({cls:#06x}, {op:#04x}) " + ", ".join(ambiguous[(cls, op)]) + "\n")
    out.append(" */\n\n#endif /* VDM_OPCODE_REGISTRY_H */\n")

    path = pathlib.Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out))
    print(f"{path}: rows={len(rows)} pairs={len(by_key)} ambiguous={len(ambiguous)} "
          f"unnamed-op-helpers={len(unnamed)}")


if __name__ == "__main__":
    main()
