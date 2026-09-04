#!/usr/bin/env python3

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


WANTED = {
    "DIRECT_SOURCE_MATCH",
    "LIKELY_PLATFORM_MATCH",
    "NEEDS_ULEFONE_PORT",
}


def norm(s):
    s = Path(s).stem.lower()
    s = s.replace("-", "_")
    s = s.replace(".", "_")
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: build_phase3_normalized_map.py RESEARCH NOTHING"
        )

    research = Path(sys.argv[1])
    nothing = Path(sys.argv[2])

    classes = defaultdict(set)

    with open(research / "kernel/module-map.csv") as f:
        for r in csv.DictReader(f):
            if r["classification"] in WANTED:
                classes[r["module_name"]].add(
                    r["classification"]
                )

    roots = [
        nothing / "device_modules",
        nothing / "kernel_modules",
    ]

    # Exact normalized source basenames.
    source_index = defaultdict(list)

    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file():
                continue

            if p.suffix not in {
                ".c",
                ".cc",
                ".S",
            }:
                continue

            source_index[norm(p.name)].append(
                str(p.relative_to(nothing))
            )

    # Output targets from obj-* Make/Kbuild declarations.
    target_index = defaultdict(list)

    obj_line = re.compile(
        r"^\s*obj-[^=]*[+:?]?="
    )

    object_token = re.compile(
        r"([A-Za-z0-9_.+\-]+)\.o\b"
    )

    for root in roots:
        for name in ("Makefile", "Kbuild"):
            for p in root.rglob(name):
                try:
                    lines = p.read_text(
                        encoding="utf-8",
                        errors="replace",
                    ).splitlines()
                except OSError:
                    continue

                for lineno, line in enumerate(lines, 1):
                    if not obj_line.search(line):
                        continue

                    for token in object_token.findall(line):
                        target_index[norm(token)].append(
                            "{}:{}:{}".format(
                                p.relative_to(nothing),
                                lineno,
                                line.strip(),
                            )
                        )

    # Exact GKI artifacts.
    gki_file = (
        research /
        "kernel/exact-gki-module-artifacts.txt"
    )

    gki = set()

    if gki_file.exists():
        gki = {
            norm(x.strip())
            for x in gki_file.read_text().splitlines()
            if x.strip()
        }

    rows = []

    for module in sorted(classes):
        n = norm(module)

        sources = source_index.get(n, [])
        targets = target_index.get(n, [])

        if n in gki:
            status = "GOOGLE_GKI_ARTIFACT"
        elif targets:
            status = "NOTHING_BUILD_TARGET"
        elif sources:
            status = "NOTHING_SOURCE_BASENAME"
        else:
            status = "UNRESOLVED"

        mt6878_sources = [
            p for p in sources
            if "mt6878" in p.lower()
        ]

        mt6878_targets = [
            p for p in targets
            if "mt6878" in p.lower()
        ]

        rows.append({
            "module_name": module,
            "normalized_name": n,
            "classifications":
                ";".join(sorted(classes[module])),
            "status": status,
            "nothing_target_hits": len(targets),
            "nothing_source_hits": len(sources),
            "mt6878_target_hits": len(mt6878_targets),
            "mt6878_source_hits": len(mt6878_sources),
            "target_examples":
                " || ".join(targets[:5]),
            "source_examples":
                " || ".join(sources[:5]),
        })

    out = (
        research /
        "kernel/phase3-normalized-source-map.csv"
    )

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
        )
        w.writeheader()
        w.writerows(rows)

    print("===== NORMALIZED PHASE 3 MAP =====")
    print("modules:", len(rows))

    counts = Counter(
        r["status"] for r in rows
    )

    for status, count in sorted(counts.items()):
        print(f"{status:28s} {count}")

    print()
    print("===== BY CLASS =====")

    for cls in sorted(WANTED):
        subset = [
            r for r in rows
            if cls in r["classifications"].split(";")
        ]

        print()
        print(cls, len(subset))

        c = Counter(r["status"] for r in subset)

        for status, count in sorted(c.items()):
            print(f"  {status:26s} {count}")

    print()
    print("===== NEEDS_ULEFONE_PORT =====")

    for r in rows:
        if (
            "NEEDS_ULEFONE_PORT"
            in r["classifications"].split(";")
        ):
            print(
                "{:<35} {:<26} target={} src={}".format(
                    r["module_name"],
                    r["status"],
                    r["nothing_target_hits"],
                    r["nothing_source_hits"],
                )
            )

    print()
    print("===== UNRESOLVED DIRECT MATCHES =====")

    unresolved_direct = [
        r for r in rows
        if (
            "DIRECT_SOURCE_MATCH"
            in r["classifications"].split(";")
            and r["status"] == "UNRESOLVED"
        )
    ]

    print("count:", len(unresolved_direct))

    for r in unresolved_direct:
        print(r["module_name"])


if __name__ == "__main__":
    main()
