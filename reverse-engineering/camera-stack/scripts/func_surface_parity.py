#!/usr/bin/env python3
"""Compare the function *surface* (names + size multiset) of two images.

Usage: func_surface_parity.py <a.ko> <b.ko> [--filter SUBSTR] [--details]

This is neither of the two axes used for `imgsensor.ko` closure:
  * it is not byte parity, so it cannot certify code equivalence, and
  * it is not reproducibility, because either operand may be the shipped module.
It answers a narrower and cheaper question: does the candidate expose exactly the
same set of functions as the reference, at the same sizes? A missing or resized
function is a hard failure; an identical surface is necessary-but-not-sufficient
evidence that nothing in the function inventory was lost.

Function-local statics carry a clang occurrence suffix (`foo.__func___rs.84`)
whose number depends on how many such statics preceded it in the TU, so names are
compared with that suffix folded away and occurrences counted per folded name.
"""
from __future__ import annotations

import collections
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
import elfmini  # noqa: E402

STT_FUNC = 2
LOCAL_SUFFIX = re.compile(r"\.\d+$")


def surface(path: str, filt: str | None) -> dict[str, list[int]]:
    out: dict[str, list[int]] = collections.defaultdict(list)
    for sym in elfmini.Elf(path).symbols:
        if sym.type != STT_FUNC or sym.size <= 0:
            continue
        if filt and filt not in sym.name:
            continue
        out[LOCAL_SUFFIX.sub("", sym.name)].append(sym.size)
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__.strip())
        return 2
    a_path, b_path = argv[1], argv[2]
    filt = argv[argv.index("--filter") + 1] if "--filter" in argv else None
    details = "--details" in argv

    a, b = surface(a_path, filt), surface(b_path, filt)
    names = sorted(set(a) | set(b))
    only_a = [n for n in names if n not in b]
    only_b = [n for n in names if n not in a]
    both = [n for n in names if n in a and n in b]
    sizediff = [n for n in both if sorted(a[n]) != sorted(b[n])]

    la, lb = sum(len(v) for v in a.values()), sum(len(v) for v in b.values())
    print(f"# function surface: {a_path.rsplit('/', 1)[-1]} vs {b_path.rsplit('/', 1)[-1]}")
    if filt:
        print(f"* filter: `{filt}`")
    print(f"* functions with size>0: A={la} B={lb}")
    print(f"* name multiset: shared={len(both)}" f" A-only={len(only_a)} B-only={len(only_b)}")
    print(f"* size multiset equal: {len(both) - len(sizediff)}/{len(both)}")
    for label, lst in (("A-only", only_a), ("B-only", only_b), ("size-differing", sizediff)):
        if not lst:
            continue
        print(f"\n## {label} ({len(lst)})\n")
        print("| function | A sizes | B sizes |")
        print("|---|---|---|")
        for n in lst if details else lst[:40]:
            print(f"| `{n}` | {sorted(a.get(n, []))} | {sorted(b.get(n, []))} |")
        if not details and len(lst) > 40:
            print(f"\n* {len(lst) - 40} further rows suppressed (pass --details)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
