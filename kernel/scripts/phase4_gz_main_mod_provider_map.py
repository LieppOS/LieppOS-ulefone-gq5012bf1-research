#!/usr/bin/env python3
"""Generate the gz_main_mod provider map and provider provenance tables.

Every one of the stock module's imported symbols is classified against the
REAL source-built GenieZone provider stack plus exact GKI ab/12901745.  The
only permitted non-source provider is mtk_sec_heap, which is genuinely stock
on GQ5012BF1 and is declared explicitly.

Read-only: parses committed stock ELFs and build outputs, writes two TSVs.
"""
from __future__ import annotations

import collections
import csv
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
GKI = pathlib.Path(
    "/home/armol/kernel-work/gki-12901745-workspace/out/bazel/output_user_root/"
    "f6aacad13134379f473094d049402ee4/execroot/__main__/bazel-out/k8-fastbuild/"
    "bin"
)

# provider label -> (exports tsv, rebuilt Module.symvers, source status)
PROVIDERS = [
    (
        "gz_tz_system",
        "kernel/phase4-gz-tz-system-exports.tsv",
        GKI / "lieppos/gz-tz-system-accept/gz_tz_system_accept/Module.symvers",
        "source-built (SOURCE_DELTA_RECONSTRUCTION_EXACT / FROZEN FOR RE)",
        "GZ_TZ_SYSTEM_NATURAL",
    ),
    (
        "gz_trusty_mod",
        "kernel/phase4-gz-trusty-mod-exports.tsv",
        GKI / ("kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/"
               "gz-trusty/gz_transport/Module.symvers"),
        "source-built (DIRECT_SOURCE_MATCH / FROZEN FOR RE)",
        "GZ_TRUSTY_NATURAL",
    ),
    (
        "gz_ipc_mod",
        "kernel/phase4-gz-ipc-mod-exports.tsv",
        GKI / ("kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/"
               "gz-trusty/gz_transport/Module.symvers"),
        "source-built (DIRECT_SOURCE_MATCH / FROZEN FOR RE)",
        "GZ_IPC_NATURAL",
    ),
    (
        "ffa_v10",
        "kernel/phase4-ffa-v10-exports.tsv",
        GKI / "lieppos/ffa-v10/ffa_v10/Module.symvers",
        "source-built (DIRECT_SOURCE_MATCH / FROZEN FOR RE)",
        "FFA_V10_NATURAL",
    ),
    (
        "tmem_ffa",
        "kernel/phase4-tmem-ffa-exports.tsv",
        GKI / "lieppos/tmem-ffa-gzaccept/tmem_ffa_gzaccept/Module.symvers",
        "source-built (SOURCE_NOW / FROZEN FOR RE)",
        "TMEM_FFA_NATURAL",
    ),
]

STOCK_PROVIDER = {
    "dmabuf_to_secure_handle": (
        "mtk_sec_heap",
        "0x59f9c814",
        "STOCK RUNTIME PROVIDER - not reconstructed in this task",
        "STOCK_RUNTIME_PROVIDER",
    )
}


def read_tsv(path: pathlib.Path) -> list[dict]:
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def symvers(path: pathlib.Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text().splitlines():
        fields = line.split("\t")
        if len(fields) >= 2:
            out[fields[1]] = fields[0].lower()
    return out


def main() -> int:
    imports = {
        row["symbol"]: row["modversion_crc"].lower()
        for row in read_tsv(REPO / "kernel/phase4-gz-main-mod-imports.tsv")
    }
    relocs = read_tsv(REPO / "kernel/phase4-gz-main-mod-relocations.tsv")
    sites = collections.Counter(row["symbol"] for row in relocs)

    gki = symvers(GKI / "common/kernel_aarch64/Module.symvers")

    owner: dict[str, tuple] = {}
    for label, exports, rebuilt_path, status, cls in PROVIDERS:
        rebuilt = symvers(rebuilt_path)
        for row in read_tsv(REPO / exports):
            owner.setdefault(
                row["symbol"],
                (label, row["crc"].lower(), status,
                 rebuilt.get(row["symbol"], ""), cls),
            )

    rows = []
    counts: collections.Counter = collections.Counter()
    for symbol in sorted(imports):
        stock_crc = imports[symbol]
        if symbol in owner:
            provider, pcrc, status, rebuilt_crc, cls = owner[symbol]
            note = "resolved in-build from the real source-built provider"
        elif symbol in STOCK_PROVIDER:
            provider, pcrc, status, cls = STOCK_PROVIDER[symbol]
            rebuilt_crc = pcrc
            note = ("declared stock runtime provider ABI record read from the "
                    "provider's own __kcrctab_gpl")
        elif symbol in gki:
            provider, pcrc = "GKI (kernel_aarch64 ab/12901745)", gki[symbol]
            status, rebuilt_crc, cls = "exact GKI", gki[symbol], "GKI_NATURAL"
            note = "exact-GKI symbol"
        else:
            provider = pcrc = status = rebuilt_crc = ""
            cls, note = "UNKNOWN", "no provider found"

        ok = rebuilt_crc == stock_crc and rebuilt_crc != ""
        counts[cls] += 1
        rows.append({
            "symbol": symbol,
            "stock_crc": stock_crc,
            "provider": provider,
            "provider_stock_crc": pcrc,
            "provider_source_status": status,
            "provider_rebuilt_crc": rebuilt_crc,
            "status": "EXACT" if ok else "MISMATCH",
            "call_sites": sites.get(symbol, 0),
            "kcfi": "n/a (imported symbol; KCFI ids are per defined function)",
            "class": cls,
            "notes": note,
        })

    out = REPO / "kernel/phase4-gz-main-mod-provider-map.tsv"
    with open(out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]),
                                delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    prov = REPO / "kernel/phase4-gz-main-mod-provider-provenance.tsv"
    with open(prov, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["symbol", "class", "provider", "stock_crc",
                         "accepted_crc", "status"])
        for row in rows:
            writer.writerow([row["symbol"], row["class"], row["provider"],
                             row["stock_crc"], row["provider_rebuilt_crc"],
                             row["status"]])

    mismatches = [r for r in rows if r["status"] != "EXACT"]
    print(f"imports: {len(rows)}")
    for cls, n in sorted(counts.items()):
        print(f"  {cls:26s} {n}")
    print(f"mismatches: {len(mismatches)}")
    print(f"UNKNOWN: {counts.get('UNKNOWN', 0)}")
    return 1 if mismatches or counts.get("UNKNOWN") else 0


if __name__ == "__main__":
    sys.exit(main())
