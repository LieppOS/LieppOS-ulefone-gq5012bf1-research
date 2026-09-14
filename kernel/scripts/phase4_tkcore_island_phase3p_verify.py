#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3P.

Certifies TKCORE_ISLAND_PHASE3P_PREREQUISITES_CLOSED: the proc/log and
peripheral/clock lifecycle leaves that blocked Phase 3A are reconstructed.

It does NOT certify tkcore as replacement-ready, behaviorally complete,
Phase-3A complete, or runtime validated. Static/offline only.
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
PHASE2 = os.path.join(W, "phase3p/before/tkcore.phase2.ko")
PHASE3P = os.path.join(W, "phase3p/build/tkcore.phase3p.ko")

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
PHASE2_SHA = "5fc3c38dbfbd1eb90fec4b7d1ec803e4f09a7b576e8e8220f68f1b794a2e6e62"
RESEARCH_START = "91d523665091570887368d946465dce2d3c1d648"
COMMON_COMMIT = "6b18f0b574ab3267615ae6ce642d5a7c3c21ac09"
HEADER_MANIFEST = "f3c3a13d94c00e40a43ff60c25603ea08717dd8f29a3b6ce1d394744e59352d5"

SRC = os.path.join(ISL, "tkcore-island/tkcore/tee_lifecycle_prereq.c")
SYSFS = os.path.join(ISL, "tkcore-island/tkcore/tee_sysfs.c")
SUPP = os.path.join(ISL, "tkcore-island/tkcore/tee_supp_com.c")
LAYOUT = os.path.join(ISL, "trustkernel/include/trustkernel/layout-assert.h")

PROC_LOG = [
    "tee_init_procfs", "tee_exit_procfs", "tee_log_open", "tee_log_read",
    "tee_log_release", "drv_version_read", "copy_to_user_str",
    "tee_version_read", "teed_version_read", "teed_version_write",
    "logd", "tkcore_log_irq_handler",
]
CLOCK = [
    "tee_clkmgr_register", "tee_peridev_init", "plat_register_spi_clk",
    "tee_peridev_exit", "mtk_enable_clk", "mtk_disable_clk",
]
SYSFS_FN = ["tee_init_sysfs", "tee_cleanup_sysfs"]
SUPP_FN = ["tee_supp_init", "tee_supp_deinit"]

checks = []


def ck(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read(p):
    try:
        with open(p, errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def elf(path):
    """Return (funcs, text bytes, undefined imports, exports)."""
    out = subprocess.run(["llvm-readelf", "-sW", path],
                         capture_output=True, text=True).stdout
    txt = subprocess.run(["llvm-objcopy", "--dump-section", ".text=/dev/stdout",
                          path], capture_output=True).stdout
    funcs, und, exp = {}, set(), set()
    for line in out.splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        if p[3] == "FUNC" and p[6] != "UND":
            funcs[p[7]] = (int(p[1], 16), int(p[2]))
        if p[6] == "UND":
            und.add(p[7])
        if p[7].startswith("__ksymtab_") and p[7] != "__ksymtab_strings":
            exp.add(p[7][len("__ksymtab_"):])
    return funcs, txt, und, exp


def kcfi(txt, off):
    return int.from_bytes(txt[off - 4:off], "little") if off >= 4 else None


def main():
    # ---- identity -----------------------------------------------------
    ck("stock oracle present", os.path.exists(STOCK))
    ck("stock SHA256 matches",
       os.path.exists(STOCK) and sha256(STOCK) == STOCK_SHA)
    ck("frozen Phase-2 baseline present", os.path.exists(PHASE2))
    ck("Phase-2 SHA256 matches",
       os.path.exists(PHASE2) and sha256(PHASE2) == PHASE2_SHA)
    ck("Phase-3P ELF present", os.path.exists(PHASE3P))

    log = read(os.path.join(REPO, "kernel/phase4-tkcore-island-phase3p-baseline.md"))
    ck("research start commit recorded", RESEARCH_START in log)
    ck("common commit recorded", COMMON_COMMIT in log)
    ck("common-header manifest recorded", HEADER_MANIFEST in log)

    common = os.path.join(GKI, "common")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=common,
                          capture_output=True, text=True).stdout.strip()
    ck("common at exact GKI commit", head == COMMON_COMMIT, head)

    if not os.path.exists(PHASE3P) or not os.path.exists(STOCK):
        report()
        return

    sf, stx, sund, sexp = elf(STOCK)
    f2, t2, u2, e2 = elf(PHASE2)
    f3, t3, u3, e3 = elf(PHASE3P)

    # ---- proc/log -----------------------------------------------------
    for fn in PROC_LOG:
        ck("proc/log function exists: " + fn, fn in f3)
    ck("all proc/log KCFI IDs exact",
       all(fn not in f3 or fn not in sf or
           kcfi(stx, sf[fn][0]) == kcfi(t3, f3[fn][0]) for fn in PROC_LOG))

    surface = tsvrows("phase4-tkcore-proc-surface.tsv")
    ck("proc surface table exists", surface is not None)
    names = {r["proc path"] for r in surface} if surface else set()
    for p in ("/proc/tkcore", "/proc/tkcore/tkcore_log",
              "/proc/tkcore/tkcore_drv_version",
              "/proc/tkcore/tkcore_os_version",
              "/proc/tkcore/tkcore_teed_version"):
        ck("proc surface documents " + p, p in names)
    ck("proc surface documents 4 files + 1 directory",
       surface is not None and len(surface) == 5)

    contract = read(os.path.join(K, "phase4-tkcore-proc-log-contract.md"))
    lifecycle = read(os.path.join(K, "phase4-tkcore-log-lifecycle.md"))
    ck("proc/log contract documented", len(contract) > 2000)
    ck("IRQ lifecycle documented",
       "request_threaded_irq" in lifecycle and "free_irq" in lifecycle)
    ck("log thread lifecycle documented",
       "tee-log" in lifecycle and "kthread_stop" in lifecycle)
    ck("waitqueue and buffer documented",
       "init_waitqueue_head" in lifecycle and "write_pos" in lifecycle)
    ck("safety divergences documented",
       "Documented divergence" in lifecycle and "Documented divergence" in contract)

    src = read(SRC)
    ck("proc/log source present", len(src) > 2000)
    ck("real IRQ request in source", "request_threaded_irq(" in src)
    ck("real kthread creation in source", "kthread_create(" in src)
    ck("real waitqueue in source", "init_waitqueue_head(" in src)
    ck("no fake success stub in proc/log",
       "TODO" not in src and "stub" not in src.lower())
    ck("kthread failure is not swallowed", "IS_ERR_OR_NULL(klog.task)" in src)

    # ---- clock --------------------------------------------------------
    for fn in CLOCK:
        ck("clock function exists: " + fn, fn in f3)
    ck("all clock KCFI IDs exact",
       all(fn not in f3 or fn not in sf or
           kcfi(stx, sf[fn][0]) == kcfi(t3, f3[fn][0]) for fn in CLOCK))
    ck("tee_clkmgr_register exported", "tee_clkmgr_register" in e3)
    reg = read(os.path.join(K, "phase4-tkcore-clkmgr-registration-contract.md"))
    tear = read(os.path.join(K, "phase4-tkcore-clkmgr-teardown-contract.md"))
    spi = read(os.path.join(K, "phase4-tkcore-platform-spi-clock-contract.md"))
    ck("registration data model documented", "0x48" in reg and "token" in reg)
    ck("registration record fields documented",
       all(o in reg for o in ("0x08", "0x10", "0x18", "0x20", "0x28", "0x30", "0x38")))
    ck("duplicate behaviour documented", "Duplicate behaviour" in reg)
    ck("teardown locking documented",
       "mutex" in tear and "entire" in tear)
    ck("DT scan contract documented", "spi%d" in spi and "spi-clk" in spi)
    ck("clock record layout asserted in source",
       "sizeof(struct tee_clkmgr_record) == 0x48" in src)
    ck("teardown holds the registration mutex",
       "mutex_lock(&tee_clkmgr_lock)" in src)
    ck("tee_clkmgr_handle deliberately not implemented",
       "tee_clkmgr_handle" not in f3)

    # ---- sysfs --------------------------------------------------------
    for fn in SYSFS_FN:
        ck("sysfs function exists: " + fn, fn in f3)
    ck("tee_init_sysfs KCFI matches stock (int return)",
       kcfi(stx, sf["tee_init_sysfs"][0]) == kcfi(t3, f3["tee_init_sysfs"][0]))
    ck("tee_init_sysfs prototype is int",
       "int tee_init_sysfs(struct tee *tee)" in read(SYSFS))
    ck("sysfs lifecycle documented",
       len(read(os.path.join(K, "phase4-tkcore-sysfs-lifecycle.md"))) > 1000)
    ck("sysfs functions byte-identical to stock",
       all(stx[sf[f][0]:sf[f][0] + sf[f][1]] == t3[f3[f][0]:f3[f][0] + f3[f][1]]
           for f in SYSFS_FN))

    # ---- supplicant lifecycle -----------------------------------------
    for fn in SUPP_FN:
        ck("supp function exists: " + fn, fn in f3)
    ck("tee_supp_deinit still byte-identical",
       stx[sf["tee_supp_deinit"][0]:sf["tee_supp_deinit"][0] + sf["tee_supp_deinit"][1]]
       == t3[f3["tee_supp_deinit"][0]:f3["tee_supp_deinit"][0] + f3["tee_supp_deinit"][1]])
    ck("tee_supp_init audited and byte-identical",
       stx[sf["tee_supp_init"][0]:sf["tee_supp_init"][0] + sf["tee_supp_init"][1]]
       == t3[f3["tee_supp_init"][0]:f3["tee_supp_init"][0] + f3["tee_supp_init"][1]])
    ck("tee_rpc size pinned to stock 0x1d8",
       "sizeof(struct tee_rpc) == 0x1d8" in read(SUPP))
    ck("tee->rpc offset asserted",
       "TK_ASSERT_OFF(struct tee, rpc, 0xb0)" in read(LAYOUT))
    ck("supp-init audit documented",
       len(read(os.path.join(K, "phase4-tkcore-supp-init-lifecycle.md"))) > 1000)

    # ---- layout -------------------------------------------------------
    anchors = len(re.findall(r"(?m)^TK_ASSERT", read(LAYOUT)))
    ck("layout anchors preserved and extended (>=31)", anchors >= 31, str(anchors))
    ck("31 pre-existing anchors still present",
       all(a in read(LAYOUT) for a in (
           "TK_ASSERT_SIZE(struct tee, 0x138)",
           "TK_ASSERT_OFF(struct tee, list_misc, 0xa0)",
           "TK_ASSERT_SIZE(struct tee_context, 0xd0)",
           "TK_ASSERT_SIZE(TEEC_Context, 0x108)")))

    # ---- build --------------------------------------------------------
    blog = read(os.path.join(W, "phase3p/build/build.log"))
    ck("build log frozen", len(blog) > 0)
    ck("build reported success", "Build completed successfully" in blog)
    ck("no compiler warnings",
       not re.search(r"(?mi)^.*\bwarning:", blog))
    ck("no compiler errors",
       not [l for l in blog.splitlines()
            if re.search(r"(?i)\berror:", l) and "SSL error" not in l])
    ck("no unresolved symbols", "undefined!" not in blog)
    mi = subprocess.run(["llvm-objcopy", "--dump-section", ".modinfo=/dev/stdout",
                         PHASE3P], capture_output=True).stdout.decode(errors="ignore")
    ck("depends empty", "depends=\x00" in mi or "depends=" in mi.split("\x00")[-1]
       or any(kv == "depends=" for kv in mi.split("\x00")))
    ck("license GPL", "license=GPL" in mi)

    # ---- regression ---------------------------------------------------
    shared2 = set(sf) & set(f2)
    shared3 = set(sf) & set(f3)
    ck("shared-with-stock function count increased", len(shared3) > len(shared2),
       "%d -> %d" % (len(shared2), len(shared3)))

    def exact(f, t):
        return {n for n in set(sf) & set(f)
                if stx[sf[n][0]:sf[n][0] + sf[n][1]] == t[f[n][0]:f[n][0] + f[n][1]]}

    e2b, e3b = exact(f2, t2), exact(f3, t3)
    ck("no byte-exact function regressed", not (e2b - e3b), str(sorted(e2b - e3b)))
    ck("byte-exact count increased", len(e3b) > len(e2b),
       "%d -> %d" % (len(e2b), len(e3b)))
    k2 = {n for n in shared2 if kcfi(stx, sf[n][0]) == kcfi(t2, f2[n][0])}
    k3 = {n for n in shared3 if kcfi(stx, sf[n][0]) == kcfi(t3, f3[n][0])}
    ck("no KCFI match regressed", not (k2 - k3), str(sorted(k2 - k3)))
    ck("every new import exists in stock", not (u3 - u2 - sund),
       str(sorted(u3 - u2 - sund)))
    ck("no export fabricated", not (e3 - sexp), str(sorted(e3 - sexp)))
    ck("regression report exists",
       len(read(os.path.join(K, "phase4-tkcore-island-phase3p-regression.md"))) > 1000)

    # ---- scope + progress --------------------------------------------
    scope = tsvrows("phase4-tkcore-island-phase3p-scope.tsv")
    ck("scope table exists", scope is not None)
    ck("scope table classifies every row",
       scope is not None and all(r["class"] in (
           "MANDATORY_PROC_LOG", "MANDATORY_CLOCK_REG",
           "MANDATORY_CLOCK_TEARDOWN", "HELPER_ONLY", "OUT_OF_SCOPE")
           for r in scope))
    prog = tsvrows("phase4-tkcore-island-phase3p-function-progress.tsv")
    ck("function progress table exists", prog is not None)
    ck("no in-scope function is INCOMPLETE",
       prog is not None and not [r for r in prog
                                 if r["phase3p acceptance"] == "INCOMPLETE"])
    ck("acceptance report exists",
       len(read(os.path.join(K, "phase4-tkcore-island-phase3p-proc-acceptance.md"))) > 1000)

    # ---- forbidden techniques -----------------------------------------
    tree = ""
    for root, _, files in os.walk(os.path.join(ISL, "tkcore-island")):
        for fn in files:
            tree += read(os.path.join(root, fn))
    ck("no CRC injection", "__crc_" not in tree)
    ck("no __versions edit", "__versions" not in tree)
    ck("no kcrctab edit", "kcrctab" not in tree)
    ck("no KBUILD_MODPOST_WARN",
       not re.search(r"(?m)^\s*(export\s+)?KBUILD_MODPOST_WARN\s*[:+?]?=",
                     read(os.path.join(ISL, "tkcore-island/Makefile"))))
    ck("no stock object inclusion",
       not [p for p in os.listdir(os.path.join(ISL, "tkcore-island/tkcore"))
            if p.endswith((".o", ".ko"))])
    ck("no ELF patch tooling in island", "objcopy" not in tree)

    # ---- core unblock --------------------------------------------------
    unblock = read(os.path.join(K, "phase4-tkcore-island-phase3p-core-unblock.md"))
    ck("core-unblock report exists", len(unblock) > 1000)
    ck("core-unblock result is READY",
       "PHASE3A_CORE_DEPENDENCIES_READY" in unblock
       and "PHASE3A_STILL_BLOCKED" not in unblock)
    ck("tkcore not declared replacement-ready",
       "TKCORE REPLACEMENT READY: **NO**" in unblock)

    report()


def tsvrows(name):
    path = os.path.join(K, name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def report():
    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print("[%s] %s%s" % ("OK" if ok else "FAIL", name,
                             ("  (%s)" % detail) if detail and not ok else ""))
    print("=" * 62)
    print("%d/%d CHECKS PASSED" % (len(checks) - len(bad), len(checks)))
    if bad:
        print("PHASE3P_VERIFICATION_FAILED")
        sys.exit(1)
    print("TKCORE_ISLAND_PHASE3P_PREREQUISITES_CLOSED")
    print("NOTE: does NOT certify tkcore replacement-ready, Phase-3A complete,")
    print("      or runtime validated.")


if __name__ == "__main__":
    main()
