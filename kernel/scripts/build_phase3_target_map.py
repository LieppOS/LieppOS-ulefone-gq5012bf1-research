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

BUILD_NAMES = {
    "Makefile",
    "Kbuild",
    "Kconfig",
    "Android.bp",
    "BUILD.bazel",
}


def token_pattern(name, suffix=""):
    esc = re.escape(name + suffix)
    return re.compile(
        rf"(?<![A-Za-z0-9_.+\-]){esc}(?![A-Za-z0-9_.+\-])"
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: build_phase3_target_map.py RESEARCH NOTHING"
        )

    research = Path(sys.argv[1])
    nothing = Path(sys.argv[2])

    module_map = research / "kernel/module-map.csv"
    output = research / "kernel/phase3-exact-target-map.csv"

    classes = defaultdict(set)

    with module_map.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cls = r["classification"]

            if cls in WANTED:
                classes[r["module_name"]].add(cls)

    modules = sorted(classes)

    # Index build-definition files.
    build_files = []

    for root in (
        nothing / "device_modules",
        nothing / "kernel_modules",
    ):
        for p in root.rglob("*"):
            if p.is_file() and p.name in BUILD_NAMES:
                build_files.append(p)

    # Index exact source basenames, e.g. foo.c -> module foo.
    source_by_stem = defaultdict(list)

    for root in (
        nothing / "device_modules",
        nothing / "kernel_modules",
    ):
        for p in root.rglob("*"):
            if not p.is_file():
                continue

            if p.suffix not in {".c", ".cc", ".S"}:
                continue

            source_by_stem[p.stem].append(p)

    rows = []

    for module in modules:
        exact_o = token_pattern(module, ".o")
        exact_ko = token_pattern(module, ".ko")
        exact_plain = token_pattern(module)

        strong = []
        composite = []
        mentions = []
        mt6878 = []

        composite_re = re.compile(
            rf"^\s*{re.escape(module)}"
            r"-(?:objs|y|\$\([^)]+\))\s*[:+?]?="
        )

        name_re = re.compile(
            rf"""\bname\s*[:=]\s*["']{re.escape(module)}["']"""
        )

        for p in build_files:
            try:
                lines = p.read_text(
                    encoding="utf-8",
                    errors="replace",
                ).splitlines()
            except OSError:
                continue

            rel = p.relative_to(nothing)

            for lineno, line in enumerate(lines, 1):
                if not exact_plain.search(line):
                    continue

                hit = f"{rel}:{lineno}:{line.strip()}"
                mentions.append(hit)

                is_strong = False

                if p.name in {"Makefile", "Kbuild"}:
                    # Output object declared through obj-* += foo.o
                    if (
                        re.match(r"^\s*obj-[^=]*\+?=", line)
                        and exact_o.search(line)
                    ):
                        is_strong = True

                    # Composite module definition:
                    # foo-objs += ...
                    if composite_re.search(line):
                        composite.append(hit)

                elif p.name in {"BUILD.bazel", "Android.bp"}:
                    if exact_ko.search(line) or name_re.search(line):
                        is_strong = True

                if exact_ko.search(line):
                    is_strong = True

                if is_strong:
                    strong.append(hit)

                path_l = str(rel).lower()
                line_l = line.lower()

                if (
                    "/mt6878/" in f"/{path_l}"
                    or "mt6878" in line_l
                ):
                    mt6878.append(hit)

        source_paths = [
            str(p.relative_to(nothing))
            for p in source_by_stem.get(module, [])
        ]

        if strong:
            status = "EXACT_BUILD_TARGET"
        elif composite:
            status = "COMPOSITE_TARGET_EVIDENCE"
        elif source_paths:
            status = "EXACT_SOURCE_BASENAME"
        elif mentions:
            status = "MENTION_ONLY"
        else:
            status = "NO_EXACT_EVIDENCE"

        rows.append({
            "module_name": module,
            "classifications": ";".join(sorted(classes[module])),
            "status": status,
            "strong_target_hits": len(strong),
            "composite_target_hits": len(composite),
            "exact_source_files": len(source_paths),
            "build_mentions": len(mentions),
            "mt6878_context_hits": len(mt6878),
            "strong_examples": " || ".join(strong[:5]),
            "composite_examples": " || ".join(composite[:5]),
            "source_examples": " || ".join(source_paths[:5]),
            "mt6878_examples": " || ".join(mt6878[:5]),
        })

    fields = list(rows[0].keys())

    with output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("===== PHASE 3 EXACT TARGET MAP =====")
    print("candidate names:", len(rows))
    print("build-definition files:", len(build_files))

    status_counts = Counter(r["status"] for r in rows)

    print()
    print("===== STATUS =====")

    for status, count in sorted(status_counts.items()):
        print(f"{status:28s} {count}")

    print()
    print("===== BY CLASSIFICATION =====")

    for cls in sorted(WANTED):
        subset = [
            r for r in rows
            if cls in r["classifications"].split(";")
        ]

        print()
        print(cls, "modules:", len(subset))

        c = Counter(r["status"] for r in subset)

        for status, count in sorted(c.items()):
            print(f"  {status:26s} {count}")

    print()
    print("===== NEEDS_ULEFONE_PORT =====")

    for r in rows:
        if "NEEDS_ULEFONE_PORT" in r["classifications"].split(";"):
            print(
                f"{r['module_name']:35s} "
                f"{r['status']:28s} "
                f"strong={r['strong_target_hits']} "
                f"source={r['exact_source_files']} "
                f"mt6878={r['mt6878_context_hits']}"
            )

    print()
    print("===== NO EXACT EVIDENCE =====")

    none = [
        r for r in rows
        if r["status"] == "NO_EXACT_EVIDENCE"
    ]

    print("count:", len(none))

    for r in none:
        print(
            f"{r['module_name']:35s} "
            f"{r['classifications']}"
        )


if __name__ == "__main__":
    main()
