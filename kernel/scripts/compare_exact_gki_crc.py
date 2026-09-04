#!/usr/bin/env python3

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def normalize_crc(value):
    value = value.strip()
    if not value:
        return ""
    return f"0x{int(value, 16):08x}"


def load_symvers(path):
    symbols = defaultdict(set)

    with open(path, encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.split()

            if len(parts) < 2:
                continue

            try:
                crc = normalize_crc(parts[0])
            except ValueError:
                continue

            symbol = parts[1]
            symbols[symbol].add(crc)

    return symbols


def compare_csv(src, dst, symvers):
    with open(src, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError(f"no rows in {src}")

    if "symbol" not in rows[0] or "crc" not in rows[0]:
        raise RuntimeError(
            f"{src} must contain symbol and crc columns; "
            f"found {list(rows[0].keys())}"
        )

    out = []

    for r in rows:
        symbol = r["symbol"].strip()
        required = normalize_crc(r["crc"])
        actual = sorted(symvers.get(symbol, set()))

        if not actual:
            status = "MISSING"
        elif required in actual:
            status = "MATCH"
        else:
            status = "MISMATCH"

        x = dict(r)
        x["required_stock_crc"] = required
        x["exact_gki_crc"] = ";".join(actual)
        x["exact_gki_crc_status"] = status
        out.append(x)

    fields = list(out[0].keys())

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    counts = Counter(
        r["exact_gki_crc_status"]
        for r in out
    )

    return out, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--symvers", required=True)
    args = ap.parse_args()

    research = Path(args.research)
    k = research / "kernel"

    symvers = load_symvers(args.symvers)

    duplicate_crc_names = {
        symbol: crcs
        for symbol, crcs in symvers.items()
        if len(crcs) > 1
    }

    print("===== VMLINUX SYMVERS =====")
    print("unique symbols:", len(symvers))
    print(
        "symbols with multiple CRCs:",
        len(duplicate_crc_names)
    )

    jobs = [
        (
            "FULL STOCK KERNEL ABI",
            k / "stock-kernel-kmi-requirements.csv",
            k / "exact-gki-full-crc-comparison.csv",
        ),
        (
            "TRANSITION BINARY ABI",
            k / "proprietary-kmi-requirements.csv",
            k / "exact-gki-transition-crc-comparison.csv",
        ),
        (
            "HARD ULEFONE-ONLY ABI",
            k / "ulefone-only-kmi-requirements.csv",
            k / "exact-gki-ulefone-only-crc-comparison.csv",
        ),
    ]

    results = []

    for name, src, dst in jobs:
        rows, counts = compare_csv(
            src,
            dst,
            symvers,
        )

        results.append(
            (name, len(rows), counts)
        )

        print()
        print(f"===== {name} =====")
        print("total:", len(rows))
        print("MATCH:", counts["MATCH"])
        print("MISMATCH:", counts["MISMATCH"])
        print("MISSING:", counts["MISSING"])

    hard_csv = (
        k / "exact-gki-ulefone-only-crc-comparison.csv"
    )

    with open(hard_csv, newline="", encoding="utf-8") as f:
        hard = list(csv.DictReader(f))

    failures = [
        r for r in hard
        if r["exact_gki_crc_status"] != "MATCH"
    ]

    print()
    print("===== HARD ABI NON-MATCHES =====")

    if not failures:
        print("NONE")
    else:
        for r in failures:
            print(
                "{:<42} required={} gki={} status={}".format(
                    r["symbol"],
                    r["required_stock_crc"],
                    r["exact_gki_crc"] or "-",
                    r["exact_gki_crc_status"],
                )
            )

    md = [
        "# Exact Android GKI CRC comparison",
        "",
        "Baseline:",
        "",
        "- Android Common tag: `android14-6.1-2024-12_r4`",
        "- common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`",
        "- Android CI target: `kernel_aarch64`",
        "- Android CI build: `12901745`",
        "- Linux version: `6.1.115`",
        f"- vmlinux.symvers symbols: {len(symvers)}",
        "",
    ]

    for name, total, counts in results:
        md += [
            f"## {name}",
            "",
            f"- requirements: {total}",
            f"- exact CRC matches: {counts['MATCH']}",
            f"- CRC mismatches: {counts['MISMATCH']}",
            f"- missing symbols: {counts['MISSING']}",
            "",
        ]

    md += [
        "## Interpretation",
        "",
        "A MATCH means both the symbol name and CONFIG_MODVERSIONS CRC",
        "required by the stock Ulefone module agree with Google's exact",
        "GKI build 12901745.",
        "",
        "A MISMATCH means the symbol exists in the exact GKI but its",
        "generated ABI CRC differs.",
        "",
        "A MISSING result means the symbol is not present in that",
        "vmlinux.symvers export table.",
        "",
    ]

    (k / "exact-gki-crc-summary.md").write_text(
        "\n".join(md),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
