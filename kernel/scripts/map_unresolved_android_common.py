#!/usr/bin/env python3

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def norm(s):
    s = Path(s).stem.lower()
    s = s.replace("-", "_")
    s = s.replace(".", "_")
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: map_unresolved_android_common.py RESEARCH ACOMMON"
        )

    research = Path(sys.argv[1])
    acommon = Path(sys.argv[2])
    k = research / "kernel"

    with open(
        k / "phase3-merged-source-map.csv",
        newline="",
        encoding="utf-8",
    ) as f:
        unresolved = [
            r for r in csv.DictReader(f)
            if r["final_status"] == "UNRESOLVED"
        ]

    source_index = defaultdict(list)
    target_index = defaultdict(list)
    composite_index = defaultdict(list)

    print("indexing Android Common source...")

    for p in acommon.rglob("*"):
        if not p.is_file():
            continue

        if p.suffix in {".c", ".cc", ".S"}:
            source_index[norm(p.name)].append(
                str(p.relative_to(acommon))
            )

    print("indexing Android Common build targets...")

    object_re = re.compile(
        r"([A-Za-z0-9_.+\-]+)\.o\b"
    )

    composite_re = re.compile(
        r"^\s*([A-Za-z0-9_.+\-]+)"
        r"-(?:objs|y|m|\$\([^)]+\))\s*[:+?]?="
    )

    for name in ("Makefile", "Kbuild"):
        for p in acommon.rglob(name):
            try:
                lines = p.read_text(
                    encoding="utf-8",
                    errors="replace",
                ).splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()

                if re.match(r"^obj-[^=]*[+:?]?=", stripped):
                    for obj in object_re.findall(stripped):
                        target_index[norm(obj)].append(
                            f"{p.relative_to(acommon)}:"
                            f"{lineno}:{stripped}"
                        )

                m = composite_re.match(stripped)

                if m:
                    composite_index[norm(m.group(1))].append(
                        f"{p.relative_to(acommon)}:"
                        f"{lineno}:{stripped}"
                    )

    rows = []

    for r in unresolved:
        module = r["module_name"]
        n = norm(module)

        targets = target_index.get(n, [])
        composites = composite_index.get(n, [])
        sources = source_index.get(n, [])

        if targets:
            status = "ANDROID_COMMON_BUILD_TARGET"
        elif composites:
            status = "ANDROID_COMMON_COMPOSITE"
        elif sources:
            status = "ANDROID_COMMON_SOURCE"
        else:
            status = "STILL_UNRESOLVED"

        rows.append({
            "module_name": module,
            "classifications": r["classifications"],
            "status": status,
            "target_hits": len(targets),
            "composite_hits": len(composites),
            "source_hits": len(sources),
            "target_examples": " || ".join(targets[:5]),
            "composite_examples": " || ".join(composites[:5]),
            "source_examples": " || ".join(sources[:5]),
        })

    out = k / "phase3-android-common-unresolved-map.csv"

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
        )
        w.writeheader()
        w.writerows(rows)

    print()
    print("===== ANDROID COMMON RESOLUTION =====")
    print("input unresolved:", len(rows))

    counts = Counter(r["status"] for r in rows)

    for status, count in sorted(counts.items()):
        print(f"{status:32s} {count}")

    print()
    print("===== DIRECT_SOURCE_MATCH =====")

    for r in rows:
        if "DIRECT_SOURCE_MATCH" in r["classifications"].split(";"):
            print(
                f"{r['module_name']:35s} {r['status']}"
            )

    print()
    print("===== STILL UNRESOLVED =====")

    left = [
        r for r in rows
        if r["status"] == "STILL_UNRESOLVED"
    ]

    print("count:", len(left))

    for r in left:
        print(
            f"{r['module_name']:35s} "
            f"{r['classifications']}"
        )


if __name__ == "__main__":
    main()
