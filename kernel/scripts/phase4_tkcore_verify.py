#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 tkcore provider-ABI reconstruction.

Every check is an assertion against the frozen stock oracle and the rebuilt
exact-GKI artefact.  Any missing file, drifted CRC, drifted KCFI type id,
unexpected export, or attempt to publish a PROVIDER_ABI_BLOCKED symbol fails
the run (non-zero exit).  Nothing is "assumed OK" when evidence is absent.

Usage:  python3 kernel/scripts/phase4_tkcore_verify.py [--repo <path>]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

STOCK_SHA256 = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
STOCK_SIZE = 221352
STOCK_VERMAGIC = "6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64"
STOCK_SRCVERSION = "604D4583E310DBFAC768366"

# Exports whose complete genksyms type graph was recovered from the stock
# binary, so their MODVERSION CRC is regenerated naturally from C.
NATURAL = {
    "TEEC_CloseSession": "0xcb193c37",
    "TEEC_InvokeCommand": "0x202b681e",
    "TEEC_ReleaseSharedMemory": "0xc4d15e1c",
    "tee_map_cached_shm": "0x6a4e508b",
    "tee_unmap_cached_shm": "0xd793261b",
    "tee_wait_queue_init": "0x03c4c343",
    "tee_wait_queue_exit": "0xe773ba45",
    "tee_wait_queue_sleep": "0xcca24950",
    "tee_wait_queue_wakeup": "0xe2de5bad",
    "tee_clkmgr_handle": "0x6913f6b2",
    "tee_clkmgr_register": "0x7a827d74",
    "tee_spi_cfg_padsel": "0x56729869",
    "tee_spi_transfer": "0x184ce7da",
    "tee_spi_transfer_disable": "0xadb9b21c",
}

# Exports whose CRC encodes every member *name* of TrustKernel's private
# struct tee / struct tee_context (genksyms expands pointed-to definitions).
# Those names are absent from the stripped stock binary and from every public
# source tree, so the CRCs cannot be regenerated naturally.  Publishing any of
# them from the witness would mean fabricating an ABI: hard failure.
BLOCKED = {
    "TEEC_InitializeContext": "0x89b94f9a",
    "TEEC_FinalizeContext": "0x7b3bc43f",
    "TEEC_OpenSession": "0xe821e2a3",
    "TEEC_RegisterSharedMemory": "0xa7bb0a46",
    "TEEC_AllocateSharedMemory": "0x4c2f8738",
    "tee_core_alloc": "0x68aaf1dc",
    "tee_core_add": "0x74f0ee2b",
    "tee_core_del": "0xf53dbff2",
    "tee_core_free": "0x9f63c2f9",
    "__tee_get": "0xa4df7b8a",
    "tee_supp_cmd": "0x6f7dfbee",
}

CONSUMERS = {
    "tkcore_drv": 11,
    "microarray_fp_tee": 1,
    "tmem_ffa": 7,
}

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def load_elf_module(repo: Path):
    spec = importlib.util.spec_from_file_location(
        "phase4_tkcore_inventory", repo / "kernel/scripts/phase4_tkcore_inventory.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def modinfo(elf) -> dict[str, list[str]]:
    sec = elf.by_name.get(".modinfo")
    out: dict[str, list[str]] = {}
    if not sec:
        return out
    for item in sec.data.split(b"\0"):
        if not item or b"=" not in item:
            continue
        key, _, value = item.decode("utf-8", "replace").partition("=")
        out.setdefault(key, []).append(value)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    args = ap.parse_args()
    repo = Path(args.repo)
    inv = load_elf_module(repo)

    ws = repo / "workspace/phase4-tkcore"
    stock_path = ws / "oracle/tkcore.ko"
    recon_path = ws / "build/tkcore-abi-witness.ko"
    symvers_path = ws / "build/Module.symvers"
    exports_tsv = repo / "kernel/phase4-tkcore-exports.tsv"

    # ---- 1. frozen stock oracle -------------------------------------------
    check("stock oracle present", stock_path.is_file(), str(stock_path))
    if not stock_path.is_file():
        return report()
    blob = stock_path.read_bytes()
    check("stock oracle size", len(blob) == STOCK_SIZE, f"{len(blob)} bytes")
    digest = hashlib.sha256(blob).hexdigest()
    check("stock oracle sha256", digest == STOCK_SHA256, digest)

    stock = inv.ELF64LE(stock_path)
    smod = modinfo(stock)
    check("stock vermagic", smod.get("vermagic", [""])[0] == STOCK_VERMAGIC,
          smod.get("vermagic", [""])[0])
    check("stock srcversion", smod.get("srcversion", [""])[0] == STOCK_SRCVERSION,
          smod.get("srcversion", [""])[0])

    # ---- 2. stock export surface ------------------------------------------
    stock_exports = {name: f"0x{crc:08x}" for name, crc in inv.export_map(stock)}
    check("stock export count == 25", len(stock_exports) == 25, str(len(stock_exports)))
    check("stock exports == NATURAL + BLOCKED",
          set(stock_exports) == set(NATURAL) | set(BLOCKED),
          "symmetric difference: %s" % sorted(
              set(stock_exports) ^ (set(NATURAL) | set(BLOCKED))))
    crc_drift = [n for n, c in {**NATURAL, **BLOCKED}.items()
                 if stock_exports.get(n) != c]
    check("stock export CRCs match recorded classification", not crc_drift, str(crc_drift))

    gpl = stock.by_name.get("__ksymtab_gpl")
    check("stock uses plain EXPORT_SYMBOL only", gpl is None or gpl.size == 0,
          "no __ksymtab_gpl")

    # TSV inventory must agree with a fresh ELF re-parse.
    check("exports TSV present", exports_tsv.is_file(), str(exports_tsv))
    if exports_tsv.is_file():
        tsv = {r["symbol"]: (r["crc"], r["kcfi_id"])
               for r in csv.DictReader(exports_tsv.open(), delimiter="\t")}
        check("exports TSV agrees with ELF",
              {k: v[0] for k, v in tsv.items()} == stock_exports,
              f"{len(tsv)} rows")

    # ---- 3. rebuilt exact-GKI witness --------------------------------------
    check("rebuilt witness present", recon_path.is_file(), str(recon_path))
    check("rebuilt Module.symvers present", symvers_path.is_file(), str(symvers_path))
    if not (recon_path.is_file() and symvers_path.is_file()):
        return report()

    recon = inv.ELF64LE(recon_path)
    rmod = modinfo(recon)
    # The only accepted vermagic delta is the local Kleaf SCM token
    # (stock `-g945dff7bc1bf` vs local `-maybe-dirty`), matching every other
    # phase-4 reconstruction in this repo.  Release and flags must be exact.
    rver = rmod.get("vermagic", [""])[0]
    sver = smod.get("vermagic", [""])[0]
    flags = "SMP preempt mod_unload modversions aarch64"
    check("witness kernel release == stock release",
          rver.startswith("6.1.115-android14-11-") and rver.endswith(flags)
          and sver.endswith(flags), rver)
    check("vermagic delta is SCM token only",
          rver.split(" ", 1)[1:] == sver.split(" ", 1)[1:],
          f"stock {sver.split(' ')[0]} vs local {rver.split(' ')[0]}")
    check("witness is not a copy of stock srcversion",
          rmod.get("srcversion", [""])[0] != STOCK_SRCVERSION,
          rmod.get("srcversion", [""])[0])
    check("witness license is GPL", rmod.get("license", [""])[0].startswith("GPL"),
          rmod.get("license", [""])[0])

    recon_exports = {name: f"0x{crc:08x}" for name, crc in inv.export_map(recon)}
    check("witness exports exactly the NATURAL set",
          set(recon_exports) == set(NATURAL),
          "symmetric difference: %s" % sorted(set(recon_exports) ^ set(NATURAL)))

    published_blocked = sorted(set(recon_exports) & set(BLOCKED))
    check("witness publishes no PROVIDER_ABI_BLOCKED symbol",
          not published_blocked, str(published_blocked))

    natural_drift = [n for n, c in NATURAL.items() if recon_exports.get(n) != c]
    check("witness CRCs equal stock CRCs (naturally regenerated)",
          not natural_drift, str(natural_drift))

    # Module.symvers (modpost output) must agree with the ELF __kcrctab.
    sv = {}
    for line in symvers_path.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            sv[parts[1]] = parts[0]
    check("Module.symvers agrees with witness __kcrctab",
          {k: v for k, v in sv.items()} == recon_exports,
          "symmetric difference: %s" % sorted(set(sv) ^ set(recon_exports)))
    check("Module.symvers CRCs equal stock CRCs",
          all(sv.get(n) == c for n, c in NATURAL.items()),
          f"{len(sv)} rows")

    # ---- 4. KCFI type identity ---------------------------------------------
    stock_kcfi = {s.name: stock.kcfi(s) for s in stock.symbols
                  if s.name in NATURAL and stock.kcfi(s)}
    recon_kcfi = {s.name: recon.kcfi(s) for s in recon.symbols
                  if s.name in NATURAL and recon.kcfi(s)}
    check("stock KCFI ids readable for all NATURAL exports",
          len(stock_kcfi) == len(NATURAL), f"{len(stock_kcfi)}/{len(NATURAL)}")
    check("witness KCFI ids readable for all NATURAL exports",
          len(recon_kcfi) == len(NATURAL), f"{len(recon_kcfi)}/{len(NATURAL)}")
    kcfi_drift = [n for n in NATURAL if stock_kcfi.get(n) != recon_kcfi.get(n)]
    check("witness KCFI type ids equal stock (prototype identity)",
          not kcfi_drift, str(kcfi_drift))

    # ---- 5. stock consumer edges -------------------------------------------
    for mod_name, expected in CONSUMERS.items():
        tsv = ws / f"raw/{mod_name}-modversions.tsv"
        if not tsv.is_file():
            check(f"{mod_name} modversions TSV present", False, str(tsv))
            continue
        rows = [r for r in csv.DictReader(tsv.open(), delimiter="\t")
                if r["symbol"] in stock_exports]
        check(f"{mod_name} tkcore edge count == {expected}",
              len(rows) == expected, str(len(rows)))
        drift = [r["symbol"] for r in rows
                 if r["crc"].lower() != stock_exports[r["symbol"]].lower()]
        check(f"{mod_name} edge CRCs match stock provider", not drift, str(drift))
        blocked_edges = sorted({r["symbol"] for r in rows} & set(BLOCKED))
        check(f"{mod_name} blocked-edge inventory recorded", True,
              f"{len(blocked_edges)} blocked: {blocked_edges}")

    # ---- 6. classification completeness ------------------------------------
    check("classification covers every stock export",
          len(NATURAL) + len(BLOCKED) == 25 and not (set(NATURAL) & set(BLOCKED)),
          f"{len(NATURAL)} natural + {len(BLOCKED)} blocked")
    check("PROVIDER_ABI_BLOCKED is declared, not worked around",
          set(BLOCKED) == {n for n in stock_exports} - set(NATURAL),
          f"{len(BLOCKED)} symbols")

    return report()


def report() -> int:
    width = max(len(n) for n, _, _ in CHECKS)
    failed = 0
    for name, ok, detail in CHECKS:
        status = "PASS" if ok else "FAIL"
        failed += not ok
        line = f"[{status}] {name.ljust(width)}"
        if detail:
            line += f"  {detail}"
        print(line)
    print()
    print(f"{len(CHECKS) - failed}/{len(CHECKS)} checks passed")
    if failed:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS (14/25 exports naturally regenerated, "
          "11/25 declared PROVIDER_ABI_BLOCKED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
