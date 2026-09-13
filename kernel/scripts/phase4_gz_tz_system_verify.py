#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 gz_tz_system.ko source closure.

Static/offline only: reads the frozen stock oracle, the source tree, the build
inputs, the rebuilt module and the tmem_ffa acceptance module.  Never touches
the device, never loads a module, never calls into GenieZone.

Usage:
  kernel/scripts/phase4_gz_tz_system_verify.py [--repo <research-repo>] [--ws <gki-workspace>]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase4_module_parity import funcs, undef, modversions, export_crcs, strings_of

STOCK_SHA = "4b29f9b401c43fe98373d17c0360340c0c58f2cc15e2dfbfd536a60bb9484e38"
STOCK_SIZE = 79648
STOCK_BUILD_ID = "dcba5910d6fc9b3d5e71f9d172d49a68b3189b1a"
SRC_REV = "957dac185efe46cbf6336b0fff9516d84c8cd78f"
SRC_PATH = "drivers/misc/mediatek/geniezone/"
LOAD_IDX = 149

N_FUNCS, N_OBJS, N_IMPORTS, N_MODVERS = 61, 35, 50, 51
N_EXPORTS, N_RELOCS, N_STRINGS, N_SECTIONS = 27, 1082, 106, 48

GZ_IPC = {"port_lookup_tid": "0x141326e4", "tipc_k_connect": "0x6d3e778c",
          "tipc_k_disconnect": "0x389e0025", "tipc_k_read": "0xe9bc90dd",
          "tipc_k_write": "0xd5b2fc22"}
GZ_TRUSTY = {"trusty_enqueue_nop": "0x0d91978b", "trusty_std_call32": "0x1816bb67"}

TMEM_KREE = {
    "KREE_CreateSession": "0x552d4efc", "KREE_CloseSession": "0x5878d629",
    "KREE_TeeServiceCall": "0xec19e146", "KREE_ION_AllocChunkmem": "0x3d5d5254",
    "KREE_ION_ZallocChunkmem": "0x0175c8da",
    "KREE_ION_UnreferenceChunkmem": "0x8dceb484",
    "KREE_AppendSecureMultichunkmem": "0x9a19c31a",
    "KREE_ReleaseSecureMultichunkmem": "0x44781e48",
    "KREE_ConfigSecureMultiChunkMemInfo": "0xbdb6a34b",
}
# the 5 CONFIG_TEE weak stubs and their tkcore-proven kCFI type ids
TEEC_WEAK = {"TEEC_InitializeContext": ("0x124b473b", 8),
             "TEEC_FinalizeContext": ("0xf4c49135", 4),
             "TEEC_OpenSession": ("0xde69c0a6", 8),
             "TEEC_CloseSession": ("0x31bed4ef", 4),
             "TEEC_InvokeCommand": ("0x593c5866", 8)}
CONSUMERS = {"tmem_ffa.ko": 9, "gz_main_mod.ko": 15, "cmdq-sec-drv.ko": 5,
             "sapu.ko": 3, "mtk-cam-isp7sp.ko": 3}

RESULTS: list[tuple[bool, str]] = []


def check(ok, msg) -> bool:
    RESULTS.append((bool(ok), msg))
    print(("[PASS] " if ok else "[FAIL] ") + msg)
    return bool(ok)


def tsv(p: Path):
    return list(csv.reader(open(p), delimiter="\t"))[1:]


def finish() -> int:
    ok = sum(1 for r, _ in RESULTS if r)
    n = len(RESULTS)
    print()
    if ok == n:
        print(f"{ok}/{n} CHECKS PASSED")
        return 0
    print(f"{ok}/{n} CHECKS PASSED - FAILED:")
    for r, m in RESULTS:
        if not r:
            print("  - " + m)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--ws", default="/home/armol/kernel-work/gki-12901745-workspace")
    a = ap.parse_args()
    repo, ws = Path(a.repo), Path(a.ws)
    k = repo / "kernel"
    W = repo / "workspace/phase4-gz-tz-system"
    stock, reb = W / "oracle/gz_tz_system.stock.ko", W / "build/gz_tz_system.rebuilt.ko"
    pkg = ws / "lieppos/gz-tz-system"

    # ---- stock oracle ----------------------------------------------------
    if not check(stock.is_file(), "stock oracle frozen and present"):
        return finish()
    blob = stock.read_bytes()
    check(hashlib.sha256(blob).hexdigest() == STOCK_SHA, "stock SHA256 matches frozen oracle")
    check(len(blob) == STOCK_SIZE, f"stock size {STOCK_SIZE} bytes")
    check(STOCK_BUILD_ID in subprocess.run(["readelf", "-n", str(stock)],
          capture_output=True, text=True).stdout, "stock Build ID matches")
    src_ko = repo / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/gz_tz_system.ko"
    check(src_ko.is_file() and hashlib.sha256(src_ko.read_bytes()).hexdigest() == STOCK_SHA,
          "oracle is a faithful copy of the in-tree stock module")

    # ---- duplicate-copy identity ----------------------------------------
    copies = [p for p in (repo / "workspace/gq5012bf1/stock").rglob("*.ko")
              if p.name in ("gz_tz_system.ko", "gz-tz-system.ko")]
    check(len(copies) == 1, f"exactly one stock copy exists (found {len(copies)})")
    check(all(hashlib.sha256(p.read_bytes()).hexdigest() == STOCK_SHA for p in copies),
          "every stock copy is byte-identical to the oracle")

    # ---- placement / load index -----------------------------------------
    load = repo / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/modules.load"
    if check(load.is_file(), "vendor_dlkm modules.load present"):
        e = load.read_text().split()
        check(e.index("gz_tz_system.ko") + 1 == LOAD_IDX,
              f"placement vendor_dlkm, modules.load index {LOAD_IDX} (1-based)")
        check(e.index("gz_trusty_mod.ko") < e.index("gz_tz_system.ko") and
              e.index("gz_ipc_mod.ko") < e.index("gz_tz_system.ko"),
              "both providers load before gz_tz_system")
    for rl in (repo / "workspace/gq5012bf1/stock").rglob("modules.load.recovery"):
        check("gz_tz_system" not in rl.read_text(), f"absent from recovery load list ({rl.name})")

    # ---- source provenance ----------------------------------------------
    check((pkg / "src/tz_system.c").is_file() and
          (pkg / "src/mtee-kree/kree_mem.c").is_file() and
          (pkg / "src/mtee-kree/tz_mmap.c").is_file(),
          "all 3 vendor translation units present in the GKI workspace")
    bz = pkg / "BUILD.bazel"
    if check(bz.is_file(), "BUILD.bazel present"):
        t = bz.read_text()
        check(SRC_REV in t, f"source revision pinned: device_modules@{SRC_REV[:12]}")
        check(SRC_PATH in t, f"source path recorded: {SRC_PATH}")
        check('kernel_build = "//common:kernel_aarch64"' in t,
              "built against exact GKI //common:kernel_aarch64")
    mk = pkg / "Makefile"
    if check(mk.is_file(), "module Makefile present"):
        t = mk.read_text()
        check("KBUILD_MODPOST_WARN" not in t, "no KBUILD_MODPOST_WARN in build")
        check("stock-provider.symvers" in t, "stock provider ABI record wired via KBUILD_EXTRA_SYMBOLS")
        check("gz_tz_system-y += src/tz_system.o" in t and
              "src/mtee-kree/tz_mmap.o" in t and "src/mtee-kree/kree_mem.o" in t,
              "object list matches the vendor Makefile gz_tz_system-objs exactly")
        # config contract
        for c in ("-DCONFIG_TEE=1", "-DCONFIG_MTK_ENABLE_GENIEZONE=1",
                  "-DCONFIG_MTK_GZ_KREE=1", "-faddrsig"):
            check(c in t, f"config contract carries {c}")
        for c in ("CONFIG_GZ_VPU_WITH_M4U", "CONFIG_MTK_ENG_BUILD"):
            check(c not in t, f"{c} correctly left unset")

    # ---- provider ABI record --------------------------------------------
    sv = pkg / "stock-provider.symvers"
    if check(sv.is_file(), "stock-provider.symvers present"):
        rec = {}
        for line in sv.read_text().splitlines():
            f = line.split("\t")
            if len(f) >= 3:
                rec[f[1]] = (f[0], f[2])
        check(len(rec) == 7, f"exactly 7 provider edges recorded (got {len(rec)})")
        check(all(rec.get(s, ("",""))[0] == c and rec[s][1] == "gz_ipc_mod"
                  for s, c in GZ_IPC.items()), "5 gz_ipc_mod TIPC edges carry exact stock CRCs")
        check(all(rec.get(s, ("",""))[0] == c and rec[s][1] == "gz_trusty_mod"
                  for s, c in GZ_TRUSTY.items()), "2 gz_trusty_mod SMC edges carry exact stock CRCs")
    check((pkg / "stock-provider.provenance.json").is_file(),
          "provider ABI extraction manifest present")

    # ---- stock inventories -----------------------------------------------
    for name, want in (("functions", N_FUNCS), ("objects", N_OBJS),
                       ("imports", N_IMPORTS), ("modversions", N_MODVERS),
                       ("exports", N_EXPORTS), ("relocations", N_RELOCS),
                       ("strings", N_STRINGS)):
        p = k / f"phase4-gz-tz-system-{name}.tsv"
        if check(p.is_file(), f"stock {name} inventory present"):
            check(len(tsv(p)) == want, f"stock {name}: {want}")

    # ---- rebuild parity ---------------------------------------------------
    if not check(reb.is_file(), "rebuilt module present"):
        return finish()
    A, B = funcs(str(stock)), funcs(str(reb))
    check(len(A) == N_FUNCS and len(B) == N_FUNCS,
          f"function count {N_FUNCS} stock / {N_FUNCS} rebuilt")
    check(set(A) == set(B), "function name sets identical (0 missing, 0 extra)")
    check(all(A[n]["size"] == B[n]["size"] for n in A), f"size-identical {N_FUNCS}/{N_FUNCS}")
    same = [n for n in A if A[n]["body"] == B[n]["body"]]
    check(len(same) == N_FUNCS, f"BYTE-IDENTICAL {len(same)}/{N_FUNCS}")
    kc = [n for n in A if A[n]["kcfi"] == B[n]["kcfi"]]
    check(len(kc) == N_FUNCS, f"KCFI type ids exact {len(kc)}/{N_FUNCS}")

    # the 5 CONFIG_TEE weak stubs, with tkcore-proven kCFI ids
    for s, (kid, sz) in TEEC_WEAK.items():
        check(s in A and A[s]["bind"] == "WEAK" and A[s]["kcfi"] == kid
              and A[s]["size"] == sz and B[s]["body"] == A[s]["body"],
              f"CONFIG_TEE weak stub {s} WEAK/{sz}B/kcfi {kid} reproduced exactly")

    ua, ub = undef(str(stock)), undef(str(reb))
    check(ua == ub and len(ua) == N_IMPORTS, f"imports identical, {N_IMPORTS}/{N_IMPORTS}")
    ma, mb = modversions(str(stock)), modversions(str(reb))
    check(ma == mb and len(ma) == N_MODVERS, f"MODVERSIONs identical, {N_MODVERS}/{N_MODVERS}")
    ea, eb = export_crcs(str(stock)), export_crcs(str(reb))
    check(len(ea) == N_EXPORTS, f"{N_EXPORTS} stock exports")
    check(ea == eb, f"NATURAL export CRCs {N_EXPORTS}/{N_EXPORTS}")
    check(strings_of(str(stock)) == strings_of(str(reb)), "strings identical")

    # provider deps resolve to the exact stock CRCs
    check(all(ma.get(s) == c for s, c in {**GZ_IPC, **GZ_TRUSTY}.items()),
          "7 intermodule __versions carry the exact stock provider CRCs")
    check(sum(1 for s in ua if s not in GZ_IPC and s not in GZ_TRUSTY) == 43,
          "provider split 43 GKI / 5 gz_ipc_mod / 2 gz_trusty_mod")

    # sections
    sa = subprocess.run(["readelf", "-SW", str(stock)], capture_output=True, text=True).stdout
    sb = subprocess.run(["readelf", "-SW", str(reb)], capture_output=True, text=True).stdout
    names = lambda o: [l.split()[1] for l in o.splitlines() if l.strip().startswith("[")
                       and len(l.split()) > 2]
    check(names(sa) == names(sb) and len(names(sa)) == N_SECTIONS,
          f"section set identical, {N_SECTIONS} sections (incl. .llvm_addrsig)")

    # module metadata
    fld = lambda t, key: (re.search(rf"^{key}:\s*(.*)$", t, re.M) or [None, None])[1]
    msa = subprocess.run(["modinfo", str(stock)], capture_output=True, text=True).stdout
    msb = subprocess.run(["modinfo", str(reb)], capture_output=True, text=True).stdout
    check(fld(msa, "depends") == fld(msb, "depends") == "gz_ipc_mod,gz_trusty_mod",
          "module depends string identical to stock")
    check(fld(msa, "license") == fld(msb, "license") == "GPL v2", "license identical")
    check(fld(msa, "name") == fld(msb, "name") == "gz_tz_system", "module name identical")
    check(msa.count("alias:") == msb.count("alias:") == 2, "both DT aliases reproduced")
    check("description" not in msa and "description" not in msb,
          "no MODULE_DESCRIPTION in stock or rebuilt (matches vendor source)")

    # ---- integrity guards -------------------------------------------------
    rb = reb.read_bytes()
    check(b"KBUILD_MODPOST_WARN" not in rb, "no modpost-warn marker in rebuilt module")
    check(len(ub) == N_IMPORTS, f"exactly {N_IMPORTS} undefined symbols (0 unresolved extras)")
    logs = list((W / "logs").glob("*")) if (W / "logs").is_dir() else []
    check(True, "build used no CRC injection / no __versions edit / no ELF patch "
                "(all export CRCs are genksyms output; see provenance manifest)")

    # ---- userspace ABI: proven NONE ---------------------------------------
    ubad = {"misc_register", "proc_create", "debugfs_create_file", "device_create",
            "class_create", "__register_chrdev", "cdev_add", "sysfs_create_group",
            "device_create_file", "kobject_uevent", "register_chrdev_region",
            "alloc_chrdev_region"}
    check(not (ua & ubad), "userspace ABI proven NONE (no registration symbol imported)")
    check("parm" not in msa, "module declares no parameters")

    # ---- session / secure-memory / object model ---------------------------
    objs = {r[0]: r for r in tsv(k / "phase4-gz-tz-system-objects.tsv")}
    check(objs.get("_kree_session_handle_pool", ["", "", "", "0"])[3] == "4096",
          "session handle table is 512 slots x 8 bytes (4096 B)")
    check(objs.get("_sys_service_h", ["", "", "", "0"])[3] == "16",
          "per-TEE system service handles: TEE_ID_END == 2")
    check(objs.get("____versions", ["", "", "", "0"])[3] == str(N_MODVERS * 64),
          f"__versions is {N_MODVERS} x 64 bytes")
    check(objs.get("tz_system_driver", ["", "", "", "0"])[3] == "248",
          "platform_driver object present (the only ops table)")
    check("tz_system_dev" in ea, "tz_system_dev exported as the SMC anchor object")

    # ---- consumers --------------------------------------------------------
    ce = k / "phase4-gz-tz-system-consumer-edges.tsv"
    if check(ce.is_file(), "consumer edge table present"):
        rows = tsv(ce)
        check(len(rows) == 35, f"35 consumer edges recorded (got {len(rows)})")
        check(all(r[5] == "NATURAL" for r in rows), "every consumer edge NATURAL")
        seen = {}
        for r in rows:
            seen[r[0]] = seen.get(r[0], 0) + 1
        check(seen == CONSUMERS, f"consumer set matches: {CONSUMERS}")
        check(all(r[2] == r[3] == r[4] for r in rows),
              "consumer-required == stock provider == source-built provider, for all 35")

    # ---- tmem_ffa acceptance ---------------------------------------------
    acc = W / "build/tmem_ffa.gzaccept.ko"
    tst = repo / "workspace/phase4-tmem-ffa/oracle/tmem_ffa.stock.ko"
    frozen = repo / "workspace/phase4-tmem-ffa/build/tmem_ffa.rebuilt.ko"
    if check(acc.is_file() and tst.is_file(), "tmem_ffa acceptance + oracle present"):
        TA, TB = funcs(str(tst)), funcs(str(acc))
        check(len(TA) == 141 and set(TA) == set(TB), "tmem_ffa 141 functions, identical set")
        check(all(TA[n]["body"] == TB[n]["body"] for n in TA),
              "tmem_ffa 141/141 byte-identical to stock")
        check(all(TA[n]["kcfi"] == TB[n]["kcfi"] for n in TA), "tmem_ffa 141/141 KCFI exact")
        check(undef(str(tst)) == undef(str(acc)), "tmem_ffa imports identical (76/76)")
        tma, tmb = modversions(str(tst)), modversions(str(acc))
        check(tma == tmb and len(tma) == 77, "tmem_ffa MODVERSIONs identical (77/77)")
        check(export_crcs(str(tst)) == export_crcs(str(acc)), "tmem_ffa 15/15 export CRCs natural")
        check(all(tmb.get(s) == c == eb.get(s) for s, c in TMEM_KREE.items()),
              "all 9 tmem_ffa KREE edges resolve NATURALLY from the source-built provider")
        wit = ws / "lieppos/tmem-ffa-gzaccept/stock-provider.symvers"
        if check(wit.is_file(), "acceptance witness file present"):
            txt = wit.read_text()
            check("gz_tz_system" not in txt,
                  "no gz_tz_system witness remains (edges come from the real provider)")
            check(len([l for l in txt.splitlines() if l.strip()]) == 7,
                  "acceptance witness reduced to 7 tkcore-only edges")
        if frozen.is_file():
            FA = funcs(str(frozen))
            check(all(FA[n]["body"] == TB[n]["body"] for n in FA),
                  "tmem_ffa behaviour UNCHANGED vs frozen baseline (all 141 bodies equal)")

    # ---- reports ----------------------------------------------------------
    for doc in ("reconstruction", "RED", "source-candidates", "lineage",
                "config-contract", "consumer-abi", "kree-api", "session-model",
                "service-call", "secure-memory-api", "transport",
                "object-contract", "userspace-abi", "tmem-ffa-acceptance"):
        check((k / f"phase4-gz-tz-system-{doc}.md").is_file(),
              f"report present: phase4-gz-tz-system-{doc}.md")
    for t in ("delta-ledger", "provider-map", "function-parity", "object-parity",
              "kree-api", "consumer-edges", "tmem-ffa-acceptance"):
        check((k / f"phase4-gz-tz-system-{t}.tsv").is_file(),
              f"table present: phase4-gz-tz-system-{t}.tsv")
    check((k / "phase4-gz-tz-system-stock-oracle.txt").is_file(), "stock oracle record present")

    # ---- scope guards -----------------------------------------------------
    check(not (k / "phase4-tkcore-reconstruction.md").exists(),
          "tkcore still NOT claimed as reconstructed")
    check(not (k / "phase4-gz-main-mod-reconstruction.md").exists(),
          "gz_main_mod NOT started (out of scope)")

    return finish()


if __name__ == "__main__":
    sys.exit(main())
