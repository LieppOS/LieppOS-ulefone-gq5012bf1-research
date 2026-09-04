#!/usr/bin/env python3

import csv
import subprocess
import sys
from pathlib import Path


def run_rg(root, term):
    cmd = [
        "rg",
        "-n",
        "-i",
        "--no-heading",
        "--glob", "*.c",
        "--glob", "*.h",
        "--glob", "Makefile",
        "--glob", "Kbuild",
        "--glob", "Kconfig",
        "--glob", "Android.bp",
        "--glob", "BUILD.bazel",
        term,
        str(root),
    ]

    # Some published vendor source files contain non-UTF-8 bytes.
    # Preserve the search result instead of failing the entire research pass.
    p = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    return p.stdout.splitlines()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: search_phase3_semantic_families.py RESEARCH NOTHING"
        )

    research = Path(sys.argv[1])
    nothing = Path(sys.argv[2])

    manifest = research / "kernel/phase3-unresolved-families.tsv"
    output = research / "kernel/phase3-semantic-family-hits.txt"

    with manifest.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    out = []

    for r in rows:
        out += [
            "=" * 80,
            f"MODULE: {r['module']}",
            f"CLASS:  {r['classification']}",
            f"FAMILY: {r['family']}",
            "=" * 80,
            "",
        ]

        terms = [
            x.strip()
            for x in r["search_terms"].split(",")
            if x.strip()
        ]

        seen = set()

        for term in terms:
            hits = run_rg(nothing, term)

            # Remove exact duplicate lines across overlapping terms.
            unique = []

            for h in hits:
                if h in seen:
                    continue
                seen.add(h)
                unique.append(h)

            out.append(f"--- term: {term} ({len(unique)} new hits) ---")

            # Keep the research artifact readable.
            for h in unique[:60]:
                out.append(h)

            if len(unique) > 60:
                out.append(
                    f"... {len(unique) - 60} additional hits omitted ..."
                )

            out.append("")

    output.write_text(
        "\n".join(out) + "\n",
        encoding="utf-8",
    )

    print("modules:", len(rows))
    print("output:", output)


if __name__ == "__main__":
    main()
