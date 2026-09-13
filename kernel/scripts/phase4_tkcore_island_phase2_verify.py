#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 2.

Certifies PHASE2_COMPILE_AND_COMPARE_COMPLETE.

It does NOT certify tkcore as replacement-ready, behaviorally complete, or
runtime validated. Static/offline only.
"""
import csv
import hashlib
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
K = os.path.join(REPO, "kernel")
W = os.path.join(REPO, "workspace/phase4-tkcore-island")
GKI = "/home/armol/kernel-work/gki-12901745-workspace"
ISL = os.path.join(GKI, "lieppos")

STOCK = os.path.join(W, "oracle/tkcore.stock.ko")
REBUILT = os.path.join(W, "phase2/build/tkcore.rebuilt.phase2.ko")

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
STOCK_SIZE = 221352

checks = []


def ck(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tsv(p):
    path = os.path.join(K, p)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    # ---- stock oracle integrity ---------------------------------------
    ck("stock oracle present", os.path.exists(STOCK))
    if os.path.exists(STOCK):
        ck("stock SHA256 matches", sha256(STOCK) == STOCK_SHA)
        ck("stock size matches", os.path.getsize(STOCK) == STOCK_SIZE)
    else:
        ck("stock SHA256 matches", False)
        ck("stock size matches", False)

    fn = tsv("phase4-tkcore-island-functions.tsv")
    ck("stock 122-function inventory", fn is not None and len(fn) == 122,
       f"{len(fn) if fn else 0}")

    # ---- common headers ------------------------------------------------
    hdr = os.path.join(ISL, "trustkernel/include/trustkernel")
    want = ["tee_client_api.h", "tee_clkmgr.h", "tee_core.h", "tee_shm.h",
            "tee_spi.h", "tee_supp.h", "tee_wait_queue.h", "layout-assert.h"]
    ck("all 8 common headers present",
       all(os.path.exists(os.path.join(hdr, h)) for h in want))

    # ---- layout probe ---------------------------------------------------
    lay = tsv("phase4-tkcore-island-phase2-layout-check.tsv")
    ck("layout check table exists", lay is not None)
    if lay:
        ck("every layout anchor PASS",
           all(r["status"] == "PASS" for r in lay),
           f"{sum(1 for r in lay if r['status'] == 'PASS')}/{len(lay)}")
        sizes = {r["type"]: r["actual_size"] for r in lay if r["actual_size"]}
        for t, want_sz in (("struct tee", "0x138"),
                           ("struct tee_context", "0xd0"),
                           ("TEEC_Context", "0x108"),
                           ("TEEC_Session", "0x8"),
                           ("TEEC_SharedMemory", "0x28"),
                           ("TEEC_Operation", "0x118")):
            ck(f"{t} == {want_sz}", sizes.get(t) == want_sz, sizes.get(t, "?"))
        anchors = [r for r in lay if r["anchor"] and r["expected_offset"]]
        ck("all field-offset anchors preserved",
           all(r["expected_offset"] == r["actual_offset"] for r in anchors),
           f"{len(anchors)} anchors")

    # ---- build result ---------------------------------------------------
    log = os.path.join(W, "phase2/after/build.log")
    ck("phase2 build log frozen", os.path.exists(log))
    if os.path.exists(log):
        txt = open(log, errors="ignore").read()
        ck("build completed successfully",
           "Build completed successfully" in txt)
        # island-source diagnostics only (BoringSSL signing noise excluded)
        diag = re.findall(r"/tkcore/\S+:\d+:\d+: (error|warning):", txt)
        ck("compiler warnings == 0", diag.count("warning") == 0)
        ck("compiler errors == 0", diag.count("error") == 0)
        ck("modpost warnings == 0",
           not re.search(r"WARNING: modpost", txt))
        ck("no unresolved symbols", "undefined!" not in txt)
        ck("no KBUILD_MODPOST_WARN", "KBUILD_MODPOST_WARN" not in txt)

    # ---- rebuilt ELF ----------------------------------------------------
    ck("rebuilt ELF exists", os.path.exists(REBUILT))
    oracle = os.path.join(K, "phase4-tkcore-island-phase2-rebuilt-oracle.txt")
    ck("rebuilt oracle recorded", os.path.exists(oracle))
    if os.path.exists(REBUILT) and os.path.exists(oracle):
        ck("rebuilt SHA recorded and current",
           sha256(REBUILT) in open(oracle).read())
        mi = subprocess.run(["modinfo", REBUILT], capture_output=True,
                            text=True).stdout
        dep = re.search(r"^depends:[ \t]*(.*)$", mi, re.M)
        ck("no vendor-module dependency added",
           dep is not None and dep.group(1).strip() == "",
           repr(dep.group(1) if dep else "?"))
        ck("import_ns DMA_BUF matches stock", "import_ns:      DMA_BUF" in mi)

    # ---- forbidden techniques ------------------------------------------
    mk = os.path.join(ISL, "tkcore-island/Makefile")
    raw = open(mk).read() if os.path.exists(mk) else ""
    # strip comments: the Makefile header documents which techniques are
    # forbidden, so a naive substring test would match its own prose.
    mktxt = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith("#"))
    ck("no KBUILD_MODPOST_WARN in Makefile",
       "KBUILD_MODPOST_WARN" not in mktxt)
    ck("no -Wno- warning suppression", "-Wno-" not in mktxt)
    ck("no ferror-limit measurement flag left", "ferror-limit" not in mktxt)
    ck("no fake Module.symvers",
       not os.path.exists(os.path.join(ISL, "tkcore-island/Module.symvers")))
    ck("no CRC injection / __versions editing",
       not re.search(r"__versions|kcrctab|genksyms", mktxt))

    # ---- comparison deliverables ---------------------------------------
    for label, name, minrows in (
        ("function comparison", "phase4-tkcore-island-phase2-functions.tsv", 100),
        ("function parity", "phase4-tkcore-island-phase2-function-parity.tsv", 100),
        ("KCFI table", "phase4-tkcore-island-phase2-kcfi.tsv", 100),
        ("GKI import comparison", "phase4-tkcore-island-phase2-gki-imports.tsv", 100),
        ("MODVERSION comparison", "phase4-tkcore-island-phase2-modversions.tsv", 100),
        ("export comparison", "phase4-tkcore-island-phase2-export-parity.tsv", 25),
        ("object comparison", "phase4-tkcore-island-phase2-object-parity.tsv", 50),
        ("callgraph comparison", "phase4-tkcore-island-phase2-callgraph.tsv", 100),
        ("relocation comparison", "phase4-tkcore-island-phase2-relocations.tsv", 5),
        ("strings comparison", "phase4-tkcore-island-phase2-strings.tsv", 100),
        ("donor coverage reclassified", "phase4-tkcore-island-phase2-donor-coverage.tsv", 122),
        ("port delta ledger", "phase4-tkcore-island-phase2-port-deltas.tsv", 20),
    ):
        rows = tsv(name)
        ck(f"{label} exists", rows is not None and len(rows) >= minrows,
           f"{len(rows) if rows else 0} rows")

    # ---- narrative deliverables ----------------------------------------
    for label, name in (
        ("phase2 baseline", "phase4-tkcore-island-phase2-baseline.md"),
        ("build-failure analysis", "phase4-tkcore-island-phase2-build-failures.md"),
        ("phase3 work queue", "phase4-tkcore-island-phase3-work-queue.md"),
    ):
        ck(f"{label} exists", os.path.exists(os.path.join(K, name)))

    # ---- cross-table consistency ---------------------------------------
    par = tsv("phase4-tkcore-island-phase2-function-parity.tsv")
    if par:
        stock_rows = [r for r in par if r["stock_size"]]
        ck("parity covers all 122 stock functions", len(stock_rows) == 122,
           str(len(stock_rows)))
        ck("no stock function unclassified",
           all(r["byte_status"] for r in stock_rows))
    exp = tsv("phase4-tkcore-island-phase2-export-parity.tsv")
    if exp:
        ck("export table covers 25 stock exports",
           len([r for r in exp if r["in_stock"] == "yes"]) == 25)
        ck("no export fabricated (rebuilt subset of stock)",
           all(r["in_stock"] == "yes" for r in exp))
    imp = tsv("phase4-tkcore-island-phase2-gki-imports.tsv")
    if imp:
        ck("stock undefined import count == 100",
           len([r for r in imp if r["in_stock"] == "yes"]) == 100)
        shared = [r for r in imp if r["state"] == "shared"]
        ck("every shared GKI import CRC matches",
           all(r["crc_match"] == "YES" for r in shared),
           f"{len(shared)} shared")

    # ---- report ---------------------------------------------------------
    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print("GQ5012BF1 tkcore island — Phase 2 verifier")
    print("=" * 62)
    for name, ok, detail in checks:
        print(f"[{'OK' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    print("=" * 62)
    print(f"{passed}/{total} CHECKS PASSED")
    if passed == total:
        print("PHASE2_COMPILE_AND_COMPARE_COMPLETE")
        print("NOTE: does NOT certify tkcore as replacement-ready or runtime validated.")
        return 0
    print("PHASE2 VERIFICATION FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
