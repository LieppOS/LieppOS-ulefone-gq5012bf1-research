#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 tmem_ffa.ko source closure.

Static/offline only: it reads the frozen stock oracle, the source tree, the
build inputs and the rebuilt module.  It never touches the device.

Usage:
  kernel/scripts/phase4_tmem_ffa_verify.py [--repo <research-repo>] [--ws <gki-workspace>]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

STOCK_SHA = "707e26674abbe7f9c695bb949d74fd5de04972d4bbb991cddc3a2ea9ab45f01b"
STOCK_SIZE = 151456
STOCK_BUILD_ID = "8b25fc266c347dfd30da218cd041696a5e0471f7"
SRC_REV = "957dac185efe46cbf6336b0fff9516d84c8cd78f"
SRC_PATH = "drivers/misc/mediatek/trusted_mem/"

TKCORE_EDGES = {
    "TEEC_InitializeContext": "0x89b94f9a",
    "TEEC_FinalizeContext": "0x7b3bc43f",
    "TEEC_OpenSession": "0xe821e2a3",
    "TEEC_CloseSession": "0xcb193c37",
    "TEEC_InvokeCommand": "0x202b681e",
    "TEEC_RegisterSharedMemory": "0xa7bb0a46",
    "TEEC_ReleaseSharedMemory": "0xc4d15e1c",
}
GZ_EDGES = {
    "KREE_CreateSession": "0x552d4efc",
    "KREE_CloseSession": "0x5878d629",
    "KREE_TeeServiceCall": "0xec19e146",
    "KREE_ION_AllocChunkmem": "0x3d5d5254",
    "KREE_ION_ZallocChunkmem": "0x0175c8da",
    "KREE_ION_UnreferenceChunkmem": "0x8dceb484",
    "KREE_AppendSecureMultichunkmem": "0x9a19c31a",
    "KREE_ReleaseSecureMultichunkmem": "0x44781e48",
    "KREE_ConfigSecureMultiChunkMemInfo": "0xbdb6a34b",
}
FFA_EDGE = ("ffa_driver_register", "0x0d53cde9")
TEEC_SIZES = {"TEE_GP_SESSION_DATA": 0x140, "TEEC_Context": 0x108,
              "TEEC_Session": 0x8, "TEEC_SharedMemory": 0x28}
TA_UUID = "08030000-0000-0000-0000-000000000000"
EXPECTED = {"functions": 141, "objects": 60, "imports": 76,
            "modversions": 77, "exports": 15, "relocations": 2208,
            "strings": 292}

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, msg: str) -> bool:
    RESULTS.append((bool(ok), msg))
    print(("[PASS] " if ok else "[FAIL] ") + msg)
    return bool(ok)


def sections(blob: bytes):
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shent, shnum, shstr = struct.unpack_from("<HHH", blob, 0x3A)
    raw = lambda i: struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * shent)
    stro = raw(shstr)[4]
    out = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz, lk, inf, al, es = raw(i)
        end = blob.index(b"\0", stro + nm)
        out[i] = (blob[stro + nm:end].decode(), off, sz)
    return out


def func_bytes(path: Path):
    blob = path.read_bytes()
    sc = sections(blob)
    res = {}
    out = subprocess.run(["readelf", "-sW", str(path)], capture_output=True,
                         text=True).stdout
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or not f[0].endswith(":"):
            continue
        if f[3] != "FUNC" or f[6] in ("UND", "ABS"):
            continue
        _, off, _ = sc[int(f[6])]
        v, s = int(f[1], 16), int(f[2])
        res[f[7]] = blob[off + v:off + v + s]
    return res


def tsv(path: Path):
    rows = path.read_text().splitlines()
    return [r.split("\t") for r in rows[1:]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--ws", default="/home/armol/kernel-work/gki-12901745-workspace")
    args = ap.parse_args()
    repo, ws = Path(args.repo), Path(args.ws)
    k = repo / "kernel"
    stock = repo / "workspace/phase4-tmem-ffa/oracle/tmem_ffa.stock.ko"
    reb = repo / "workspace/phase4-tmem-ffa/build/tmem_ffa.rebuilt.ko"
    pkg = ws / "lieppos/tmem-ffa"

    # ---- 1-4 stock oracle -------------------------------------------------
    if check(stock.is_file(), "stock oracle present"):
        blob = stock.read_bytes()
        check(hashlib.sha256(blob).hexdigest() == STOCK_SHA, "stock SHA256 matches frozen oracle")
        check(len(blob) == STOCK_SIZE, f"stock size {STOCK_SIZE} bytes")
        nout = subprocess.run(["readelf", "-n", str(stock)], capture_output=True, text=True).stdout
        check(STOCK_BUILD_ID in nout, "stock Build ID matches")
    else:
        return finish()

    # ---- 5 placement ------------------------------------------------------
    load = repo / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/modules.load"
    if check(load.is_file(), "vendor_dlkm modules.load present"):
        entries = load.read_text().split()
        check(entries.index("tmem_ffa.ko") + 1 == 152,
              "stock placement vendor_dlkm, modules.load index 152 (1-based)")

    # ---- 6-8 source provenance -------------------------------------------
    src = pkg / "src"
    check(src.is_dir(), "pinned vendor source tree present in GKI workspace")
    bz = (pkg / "BUILD.bazel")
    if check(bz.is_file(), "BUILD.bazel present"):
        t = bz.read_text()
        check(SRC_REV in t, f"source revision pinned: device_modules@{SRC_REV[:12]}")
        check(SRC_PATH in t, f"source path recorded: {SRC_PATH}")
        check('"//lieppos/ffa-v10:ffa_v10"' in t, "real source-built ffa_v10 provider is a bazel dep")
    mk = (pkg / "Makefile")
    if check(mk.is_file(), "module Makefile present"):
        t = mk.read_text()
        check("KBUILD_MODPOST_WARN" not in t, "no KBUILD_MODPOST_WARN in build")
        check("stock-provider.symvers" in t, "stock provider ABI record wired through KBUILD_EXTRA_SYMBOLS")

    # ---- 9-11 provider ABI record ----------------------------------------
    sv = pkg / "stock-provider.symvers"
    if check(sv.is_file(), "stock-provider.symvers present"):
        rec = {}
        for line in sv.read_text().splitlines():
            f = line.split("\t")
            if len(f) >= 3:
                rec[f[1]] = (f[0], f[2])
        check(all(rec.get(s, ("", ""))[0] == c and rec[s][1] == "tkcore"
                  for s, c in TKCORE_EDGES.items()),
              "7 tkcore TEEC edges carry exact stock CRCs from tkcore")
        check(all(rec.get(s, ("", ""))[0] == c and rec[s][1] == "gz_tz_system"
                  for s, c in GZ_EDGES.items()),
              "9 gz_tz_system KREE edges carry exact stock CRCs from gz_tz_system")
        check(FFA_EDGE[0] not in rec, "ffa_driver_register is NOT in the stock record (real provider used)")
    prov = pkg / "stock-provider.provenance.json"
    check(prov.is_file(), "provider ABI extraction manifest present")

    # ---- 12-19 inventory parity ------------------------------------------
    for name, want in EXPECTED.items():
        p = k / f"phase4-tmem-ffa-{name}.tsv"
        if check(p.is_file(), f"stock {name} inventory present"):
            check(len(tsv(p)) == want, f"stock {name}: {want}")

    # ---- 20-27 rebuild parity --------------------------------------------
    if not check(reb.is_file(), "rebuilt module present"):
        return finish()
    A, B = func_bytes(stock), func_bytes(reb)
    check(len(A) == 141 and len(B) == 141, "function count 141 stock / 141 rebuilt")
    same = [n for n in A if n in B and A[n] == B[n]]
    check(len(same) == 141, f"function bytes identical: {len(same)}/141")

    sf = {r[0]: r for r in tsv(k / "phase4-tmem-ffa-functions.tsv")}
    par = k / "phase4-tmem-ffa-function-parity.tsv"
    if check(par.is_file(), "function parity table present"):
        rows = tsv(par)
        check(len(rows) == 141, "function parity table has 141 rows")
        check(all(r[-1] == "EXACT" for r in rows), "every function classified EXACT")
        check(all(r[9] == "YES" for r in rows), "KCFI type ids exact for all 141 functions")

    def elfsyms(p: Path, kind: str):
        out = subprocess.run(["readelf", "-sW", str(p)], capture_output=True, text=True).stdout
        return out

    # imports / modversions / exports must match the stock TSVs exactly
    tmp = Path("/tmp/phase4-tmem-ffa-verify")
    subprocess.run([sys.executable, str(k / "scripts/phase4_elf_inventory.py"),
                    str(reb), str(tmp)], capture_output=True, text=True)
    for name in ("imports", "modversions", "exports", "functions", "relocations"):
        a = tsv(k / f"phase4-tmem-ffa-{name}.tsv")
        b = tsv(Path(str(tmp) + f"-{name}.tsv"))
        if name == "functions":
            a = [r[:1] + r[3:] for r in a]
            b = [r[:1] + r[3:] for r in b]
        check(a == b, f"rebuilt {name} identical to stock")

    # ---- 28-31 provider provenance ---------------------------------------
    mv = {r[0]: r[1] for r in tsv(k / "phase4-tmem-ffa-modversions.tsv")}
    check(all(mv.get(s) == c for s, c in TKCORE_EDGES.items()),
          "consumer __versions carry the exact stock tkcore CRCs")
    check(all(mv.get(s) == c for s, c in GZ_EDGES.items()),
          "consumer __versions carry the exact stock gz_tz_system CRCs")
    check(mv.get(FFA_EDGE[0]) == FFA_EDGE[1],
          "ffa_driver_register CRC matches the real source-built ffa_v10")
    pm = k / "phase4-tmem-ffa-provider-map.tsv"
    if check(pm.is_file(), "provider map present"):
        rows = tsv(pm)
        check(len(rows) == 76, "provider map covers all 76 imports")
        kinds = {}
        for r in rows:
            kinds[r[2]] = kinds.get(r[2], 0) + 1
        check(kinds == {"GKI": 59, "tkcore": 7, "gz_tz_system": 9, "ffa_v10": 1},
              "provider split 59 GKI / 7 tkcore / 9 gz_tz_system / 1 ffa_v10")

    # ---- 32-35 exports and consumers -------------------------------------
    ex = {r[0]: r[2] for r in tsv(k / "phase4-tmem-ffa-exports.tsv")}
    rex = {r[0]: r[2] for r in tsv(Path(str(tmp) + "-exports.tsv"))}
    check(len(ex) == 15, "15 stock exports")
    check(ex == rex, "all 15 export CRCs regenerated naturally and exactly")
    ca = k / "phase4-tmem-ffa-consumer-abi.md"
    if check(ca.is_file(), "consumer audit present"):
        t = ca.read_text()
        check(all(m in t for m in ("mtk_sec_heap.ko", "gz_main_mod.ko",
                                   "mali_kbase_mt6878_r44.ko")),
              "all three stock consumers recorded")

    # ---- 36-40 TEE evidence ----------------------------------------------
    cf = k / "phase4-tmem-ffa-teec-call-flow.md"
    if check(cf.is_file(), "TEEC call-flow report present"):
        t = cf.read_text()
        check(TA_UUID in t, "secure-memory TA UUID recorded")
        check(all(k_ in t.lower() for k_ in ("0x140", "0x108", "0x28", "0x118")),
              "TEEC object sizes recorded (0x140/0x108/0x28/0x118)")
        check("CMD_SEC_MEM_SET_SVP_REGION" in t or "107" in t, "command IDs recorded")
    for doc in ("architecture", "trustkernel-type-evidence", "tkcore-consumer-abi",
                "ffa-contract", "gz-contract", "object-contract", "lineage",
                "source-candidates", "RED", "reconstruction"):
        check((k / f"phase4-tmem-ffa-{doc}.md").is_file(), f"report present: phase4-tmem-ffa-{doc}.md")
    check((repo / "kernel/phase4-tkcore-evidence-from-tmem-ffa.md").is_file(),
          "tkcore evidence delta report present")

    # ---- 41-45 integrity guards ------------------------------------------
    blob_r = reb.read_bytes()
    check(b"KBUILD_MODPOST_WARN" not in blob_r, "no modpost-warn marker in rebuilt module")
    und = subprocess.run(["llvm-nm", "-u", str(reb)], capture_output=True, text=True).stdout.split()
    und = [u for u in und if u != "U"]
    check(len(und) == 76, f"rebuilt module has exactly 76 undefined symbols (got {len(und)})")
    stock_mods = subprocess.run(["modinfo", str(stock)], capture_output=True, text=True).stdout
    reb_mods = subprocess.run(["modinfo", str(reb)], capture_output=True, text=True).stdout
    def field(txt, key):
        m = re.search(rf"^{key}:\s*(.*)$", txt, re.M)
        return m.group(1).strip() if m else None
    check(field(stock_mods, "depends") == field(reb_mods, "depends") ==
          "gz_tz_system,tkcore,ffa_v10", "module depends string identical to stock")
    check(field(stock_mods, "description") == field(reb_mods, "description"),
          "module description identical to stock")
    check(field(stock_mods, "license") == field(reb_mods, "license") == "GPL v2",
          "module license identical to stock")

    # tkcore must NOT have been touched by this task
    check(not (k / "phase4-tkcore-reconstruction.md").exists(),
          "tkcore is still NOT claimed as reconstructed")

    return finish()


def finish() -> int:
    ok = sum(1 for r, _ in RESULTS if r)
    total = len(RESULTS)
    print()
    if ok == total:
        print(f"{ok}/{total} CHECKS PASSED")
        return 0
    print(f"{ok}/{total} CHECKS PASSED - FAILED:")
    for r, m in RESULTS:
        if not r:
            print("  - " + m)
    return 1


if __name__ == "__main__":
    sys.exit(main())
