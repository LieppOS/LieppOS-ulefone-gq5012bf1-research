#!/usr/bin/env python3
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_.$]*$")

def pick(fieldnames, *candidates):
    for c in candidates:
        if c in fieldnames:
            return c
    raise KeyError(f"none of {candidates!r} found in columns {fieldnames!r}")

def read_tsv(path):
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        rows = list(r)
        return r.fieldnames or [], rows

def parse_symbol_list(path):
    syms = set()
    if not path.is_file():
        return syms
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("[") or line in {"{", "}"}:
            continue
        # Android ABI lists are normally one symbol per line. Be conservative:
        # take the first token only if it looks like a symbol.
        tok = line.split()[0]
        if IDENT.match(tok):
            syms.add(tok)
    return syms

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", type=Path, required=True)
    ap.add_argument("--nothing", type=Path, required=True)
    args = ap.parse_args()

    k = args.research.resolve() / "kernel"
    nothing = args.nothing.resolve()

    imp_fields, imports = read_tsv(k / "stock-module-imports.tsv")
    exp_fields, exports = read_tsv(k / "stock-module-exports.tsv")

    i_symbol = pick(imp_fields, "symbol")
    i_crc = pick(imp_fields, "crc")
    i_mod = pick(imp_fields, "module_name", "module")
    i_sha = next((x for x in ("sha256", "module_sha256") if x in imp_fields), None)

    e_symbol = pick(exp_fields, "symbol")
    e_mod = pick(exp_fields, "module_name", "module")
    e_sha = next((x for x in ("sha256", "module_sha256") if x in exp_fields), None)

    providers = defaultdict(set)
    provider_shas = defaultdict(set)
    for r in exports:
        providers[r[e_symbol]].add(r[e_mod])
        if e_sha:
            provider_shas[r[e_symbol]].add(r[e_sha])

    consumers = defaultdict(set)
    consumer_shas = defaultdict(set)
    crcs = defaultdict(set)
    records = defaultdict(int)

    for r in imports:
        s = r[i_symbol]
        consumers[s].add(r[i_mod])
        if i_sha:
            consumer_shas[s].add(r[i_sha])
        crcs[s].add(r[i_crc])
        records[s] += 1

    conflicts = {s: xs for s, xs in crcs.items() if len(xs) != 1}
    if conflicts:
        raise SystemExit(
            f"ERROR: {len(conflicts)} imported symbols have multiple CRCs; "
            "refusing to flatten the ABI contract"
        )

    list_paths = {
        "kernel_base": nothing / "kernel/android/abi_gki_aarch64",
        "kernel_mtk": nothing / "kernel/android/abi_gki_aarch64_mtk",
        "kernel_nothing": nothing / "kernel/android/abi_gki_aarch64_nothing",
        "device_base": nothing / "device_modules/android/abi_gki_aarch64",
        "device_mtk": nothing / "device_modules/android/abi_gki_aarch64_mtk",
    }
    lists = {name: parse_symbol_list(path) for name, path in list_paths.items()}

    # Useful published-list unions. These are name-surface comparisons only,
    # not CRC equivalence claims.
    device_mtk_union = lists["device_base"] | lists["device_mtk"]
    kernel_nothing_union = (
        lists["kernel_base"] | lists["kernel_mtk"] | lists["kernel_nothing"]
    )
    published_union = device_mtk_union | kernel_nothing_union

    out = []
    for s in sorted(consumers):
        pmods = sorted(providers.get(s, ()))
        provider_kind = "STOCK_MODULE" if pmods else "KERNEL_OR_BUILTIN"
        crc = next(iter(crcs[s]))
        row = {
            "symbol": s,
            "crc": crc,
            "provider_kind": provider_kind,
            "provider_modules": ";".join(pmods),
            "provider_module_count": len(pmods),
            "consumer_modules": ";".join(sorted(consumers[s])),
            "consumer_module_count": len(consumers[s]),
            "import_record_count": records[s],
            "in_kernel_base": int(s in lists["kernel_base"]),
            "in_kernel_mtk": int(s in lists["kernel_mtk"]),
            "in_kernel_nothing": int(s in lists["kernel_nothing"]),
            "in_device_base": int(s in lists["device_base"]),
            "in_device_mtk": int(s in lists["device_mtk"]),
            "in_device_mtk_union": int(s in device_mtk_union),
            "in_kernel_nothing_union": int(s in kernel_nothing_union),
            "in_any_published_nothing_list": int(s in published_union),
        }
        out.append(row)

    fields = list(out[0].keys()) if out else []
    with (k / "stock-kmi-requirements.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    intermodule = [r for r in out if r["provider_kind"] == "STOCK_MODULE"]
    kernel_req = [r for r in out if r["provider_kind"] == "KERNEL_OR_BUILTIN"]

    with (k / "stock-intermodule-abi.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(intermodule)

    with (k / "stock-kernel-kmi-requirements.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(kernel_req)

    missing_device = [r for r in kernel_req if not r["in_device_mtk_union"]]
    missing_kernel = [r for r in kernel_req if not r["in_kernel_nothing_union"]]
    missing_any = [r for r in kernel_req if not r["in_any_published_nothing_list"]]

    md = [
        "# Stock KMI requirement split",
        "",
        f"- raw import records: {len(imports)}",
        f"- unique imported symbols: {len(out)}",
        f"- CRC-conflicting imported symbols: 0",
        f"- stock-module-provided symbols: {len(intermodule)}",
        f"- kernel/builtin-required symbols: {len(kernel_req)}",
        "",
        "## Published Nothing symbol-list coverage",
        "",
    ]
    for name, path in list_paths.items():
        md.append(f"- {name}: {len(lists[name])} symbols (`{path.relative_to(nothing)}`)")
    md += [
        "",
        f"- device MTK union (device_base + device_mtk): {len(device_mtk_union)}",
        f"- kernel Nothing union (kernel_base + kernel_mtk + kernel_nothing): {len(kernel_nothing_union)}",
        f"- all published-list union: {len(published_union)}",
        "",
        "## Stock kernel/builtin requirement coverage by symbol name",
        "",
        f"- required symbols: {len(kernel_req)}",
        f"- covered by device MTK union: {len(kernel_req) - len(missing_device)}",
        f"- missing from device MTK union: {len(missing_device)}",
        f"- covered by kernel Nothing union: {len(kernel_req) - len(missing_kernel)}",
        f"- missing from kernel Nothing union: {len(missing_kernel)}",
        f"- covered by any published Nothing list: {len(kernel_req) - len(missing_any)}",
        f"- missing from all published Nothing lists: {len(missing_any)}",
        "",
        "Name coverage does not prove CRC compatibility. A Nothing build's "
        "`Module.symvers` (or equivalent built artifacts) is required for an "
        "exact CRC-to-CRC comparison.",
        "",
    ]
    (k / "stock-kmi-split-summary.md").write_text("\n".join(md), encoding="utf-8")

    print("===== STOCK ABI SPLIT =====")
    print("raw import records:", len(imports))
    print("unique imported symbols:", len(out))
    print("stock-module-provided symbols:", len(intermodule))
    print("kernel/builtin-required symbols:", len(kernel_req))
    print()
    print("===== NOTHING PUBLISHED SYMBOL LISTS =====")
    for name in list_paths:
        print(f"{name:22s} {len(lists[name])}")
    print()
    print("===== KERNEL/Builtin NAME COVERAGE =====")
    print("device MTK union covered:", len(kernel_req) - len(missing_device))
    print("device MTK union missing:", len(missing_device))
    print("kernel Nothing union covered:", len(kernel_req) - len(missing_kernel))
    print("kernel Nothing union missing:", len(missing_kernel))
    print("any published list covered:", len(kernel_req) - len(missing_any))
    print("any published list missing:", len(missing_any))
    print()
    if missing_any:
        print("===== FIRST 100 MISSING FROM ALL PUBLISHED LISTS =====")
        for r in missing_any[:100]:
            print(r["symbol"], r["crc"])

if __name__ == "__main__":
    main()
