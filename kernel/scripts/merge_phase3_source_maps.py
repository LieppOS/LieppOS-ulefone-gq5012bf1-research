#!/usr/bin/env python3

import csv
import sys
from collections import Counter
from pathlib import Path


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {
            r["module_name"]: r
            for r in csv.DictReader(f)
        }


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: merge_phase3_source_maps.py RESEARCH"
        )

    research = Path(sys.argv[1])
    k = research / "kernel"

    normalized = load(
        k / "phase3-normalized-source-map.csv"
    )
    exact = load(
        k / "phase3-exact-target-map.csv"
    )

    rows = []

    for module in sorted(normalized):
        n = normalized[module]
        e = exact.get(module, {})

        ns = n["status"]
        es = e.get("status", "")

        if ns == "GOOGLE_GKI_ARTIFACT":
            final = "GOOGLE_GKI_ARTIFACT"
            evidence = "exact GKI build artifact"

        elif ns == "NOTHING_BUILD_TARGET":
            final = "NOTHING_BUILD_TARGET"
            evidence = "normalized Make/Kbuild target"

        elif es == "EXACT_BUILD_TARGET":
            final = "NOTHING_BUILD_TARGET"
            evidence = "exact build-definition target"

        elif es == "COMPOSITE_TARGET_EVIDENCE":
            final = "NOTHING_COMPOSITE_TARGET"
            evidence = "composite module build target"

        elif ns == "NOTHING_SOURCE_BASENAME":
            final = "NOTHING_SOURCE"
            evidence = "normalized source basename"

        elif es == "EXACT_SOURCE_BASENAME":
            final = "NOTHING_SOURCE"
            evidence = "exact source basename"

        else:
            final = "UNRESOLVED"
            evidence = ""

        rows.append({
            "module_name": module,
            "classifications": n["classifications"],
            "final_status": final,
            "evidence_kind": evidence,

            "normalized_status": ns,
            "exact_status": es,

            "nothing_target_hits":
                n["nothing_target_hits"],
            "nothing_source_hits":
                n["nothing_source_hits"],
            "mt6878_target_hits":
                n["mt6878_target_hits"],
            "mt6878_source_hits":
                n["mt6878_source_hits"],

            "normalized_target_examples":
                n["target_examples"],
            "normalized_source_examples":
                n["source_examples"],

            "exact_strong_examples":
                e.get("strong_examples", ""),
            "exact_composite_examples":
                e.get("composite_examples", ""),
            "exact_source_examples":
                e.get("source_examples", ""),
        })

    out = k / "phase3-merged-source-map.csv"

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
        )
        w.writeheader()
        w.writerows(rows)

    print("===== PHASE 3 MERGED SOURCE MAP =====")
    print("modules:", len(rows))

    c = Counter(r["final_status"] for r in rows)

    for status, count in sorted(c.items()):
        print(f"{status:28s} {count}")

    print()
    print("===== BY CLASS =====")

    classes = [
        "DIRECT_SOURCE_MATCH",
        "LIKELY_PLATFORM_MATCH",
        "NEEDS_ULEFONE_PORT",
    ]

    for cls in classes:
        subset = [
            r for r in rows
            if cls in r["classifications"].split(";")
        ]

        print()
        print(cls, len(subset))

        cc = Counter(
            r["final_status"]
            for r in subset
        )

        for status, count in sorted(cc.items()):
            print(f"  {status:26s} {count}")

    print()
    print("===== UNRESOLVED DIRECT SOURCE MATCH =====")

    direct = [
        r for r in rows
        if (
            "DIRECT_SOURCE_MATCH"
            in r["classifications"].split(";")
            and r["final_status"] == "UNRESOLVED"
        )
    ]

    print("count:", len(direct))

    for r in direct:
        print(r["module_name"])

    print()
    print("===== NEEDS ULEFONE PORT =====")

    port = [
        r for r in rows
        if "NEEDS_ULEFONE_PORT"
        in r["classifications"].split(";")
    ]

    for r in port:
        print(
            "{:<35} {}".format(
                r["module_name"],
                r["final_status"],
            )
        )

    print()
    print("===== ALL UNRESOLVED =====")

    unresolved = [
        r for r in rows
        if r["final_status"] == "UNRESOLVED"
    ]

    print("count:", len(unresolved))

    for r in unresolved:
        print(
            "{:<35} {}".format(
                r["module_name"],
                r["classifications"],
            )
        )


if __name__ == "__main__":
    main()
