#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3A-R.

Certifies only core + TEEC context/session static closure.  It does not certify
runtime readiness, shared memory, InvokeCommand, RPC commands, or secure SPI.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KERNEL = REPO / "kernel"
PHASE = REPO / "workspace/phase4-tkcore-island/phase3a-r"
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
PHASE3P = PHASE / "before/tkcore.phase3p.ko"
FINAL = PHASE / "build/tkcore.phase3a-r.ko"
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
COMMON = GKI / "common"
ISLAND = GKI / "lieppos/tkcore-island"
TRUSTKERNEL = GKI / "lieppos/trustkernel"

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
PHASE3P_SHA = "a5c1a06c68de6791c3ab5d73ec67c51ba297f1ff6f0f69edbe77eee87a097b2d"
FINAL_SHA = "9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b"
COMMON_COMMIT = "6b18f0b574ab3267615ae6ce642d5a7c3c21ac09"

CORE = ["tee_core_alloc", "tee_core_add", "tee_core_del", "tee_core_free", "__tee_get"]
IDR = ["tee_core_alloc_uuid", "tee_core_uuid2ptr", "tee_core_free_uuid"]
TEEC = ["TEEC_InitializeContext", "TEEC_FinalizeContext", "TEEC_OpenSession", "TEEC_CloseSession"]
TARGETS = CORE + IDR + TEEC
EXPECTED_KCFI = {
    "tee_core_alloc": 0x89819660,
    "tee_core_add": 0xA1200A70,
    "tee_core_del": 0xA1200A70,
    "tee_core_free": 0xA1200A70,
    "__tee_get": 0xA1200A70,
    "tee_core_alloc_uuid": 0x89FB613D,
    "tee_core_uuid2ptr": 0xB382E080,
    "tee_core_free_uuid": 0x019C0CAC,
    "TEEC_InitializeContext": 0x124B473B,
    "TEEC_FinalizeContext": 0xF4C49135,
    "TEEC_OpenSession": 0xDE69C0A6,
    "TEEC_CloseSession": 0x31BED4EF,
}

checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def read(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def command(*args: str, cwd: Path | None = None, binary: bool = False):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=not binary)
    if p.returncode:
        return b"" if binary else ""
    return p.stdout


def elf(path: Path):
    sym = command("llvm-readelf", "-sW", str(path))
    text = command("llvm-objcopy", "--dump-section", ".text=/dev/stdout", str(path), binary=True)
    objdump = command("llvm-objdump", "-dr", str(path))
    funcs, undefined, exports = {}, set(), set()
    for line in sym.splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        if p[3] == "FUNC" and p[6] != "UND":
            funcs[p[7]] = (int(p[1], 16), int(p[2]))
        if p[6] == "UND":
            undefined.add(p[7])
        if p[7].startswith("__ksymtab_") and p[7] != "__ksymtab_strings":
            exports.add(p[7][len("__ksymtab_"):])
    starts = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:", objdump))
    blocks = {
        m.group(2): objdump[m.start() : starts[i + 1].start() if i + 1 < len(starts) else len(objdump)]
        for i, m in enumerate(starts)
    }
    return funcs, text, undefined, exports, blocks


def kcfi(text: bytes, rec: tuple[int, int]) -> int | None:
    off = rec[0]
    return int.from_bytes(text[off - 4:off], "little") if off >= 4 else None


def body(source: str, name: str) -> str:
    """Return a C function definition, ignoring calls and comment mentions."""
    for match in re.finditer(r"\b" + re.escape(name) + r"\s*\(", source):
        open_paren = source.find("(", match.start())
        depth = 0
        close_paren = -1
        for i in range(open_paren, len(source)):
            if source[i] == "(":
                depth += 1
            elif source[i] == ")":
                depth -= 1
                if depth == 0:
                    close_paren = i
                    break
        if close_paren < 0:
            continue
        brace = close_paren + 1
        while brace < len(source) and source[brace].isspace():
            brace += 1
        if brace >= len(source) or source[brace] != "{":
            continue
        start = source.rfind("\n", 0, match.start()) + 1
        depth = 0
        for i in range(brace, len(source)):
            if source[i] == "{":
                depth += 1
            elif source[i] == "}":
                depth -= 1
                if depth == 0:
                    return source[start:i + 1]
    return ""


def tsv(name: str):
    path = KERNEL / name
    if not path.is_file():
        return None
    with path.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def env_file(path: Path):
    result = {}
    for line in read(path).splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            result[k] = v
    return result


def main() -> None:
    # Identity and exact-GKI baseline.
    for name, path, expected in (
        ("stock", STOCK, STOCK_SHA),
        ("Phase-3P", PHASE3P, PHASE3P_SHA),
        ("Phase-3A-R", FINAL, FINAL_SHA),
    ):
        ck(f"{name} ELF present", path.is_file())
        ck(f"{name} SHA256 exact", path.is_file() and sha256(path) == expected,
           sha256(path) if path.is_file() else "missing")
    ck("Phase-3A-R size exact", FINAL.is_file() and FINAL.stat().st_size == 164032,
       FINAL.stat().st_size if FINAL.is_file() else "missing")

    head = command("git", "rev-parse", "HEAD", cwd=COMMON).strip()
    porcelain = [l for l in command("git", "status", "--porcelain", cwd=COMMON).splitlines() if l.strip()]
    tracked = [l for l in porcelain if not l.startswith("??")]
    untracked = [l[3:].strip() for l in porcelain if l.startswith("??")]
    # The kleaf sandbox regenerates this build byproduct inside common/; it is
    # removed before every build.  It is NOT a source modification, but nothing
    # else may appear either.
    KLEAF_BYPRODUCTS = {"tools/bpf/resolve_btfids/libsubcmd/"}
    ck("common at exact GKI commit", head == COMMON_COMMIT, head)
    ck("common exact-GKI tracked source unmodified", not tracked, tracked)
    ck("common untracked residue limited to known kleaf byproduct",
       set(untracked) <= KLEAF_BYPRODUCTS, sorted(set(untracked) - KLEAF_BYPRODUCTS))

    if not all(p.is_file() for p in (STOCK, PHASE3P, FINAL)):
        report()
        return

    sf, st, su, se, sb = elf(STOCK)
    pf, pt, pu, pe, pb = elf(PHASE3P)
    ff, ft, fu, fe, fb = elf(FINAL)

    # Core, IDR, and TEEC closure from the ELF itself.
    for fn in TARGETS:
        ck(f"target present: {fn}", fn in sf and fn in ff)
        if fn in sf and fn in ff:
            ck(f"target KCFI exact: {fn}",
               kcfi(st, sf[fn]) == kcfi(ft, ff[fn]) == EXPECTED_KCFI[fn],
               f"stock={kcfi(st, sf[fn])!r} island={kcfi(ft, ff[fn])!r}")
            sc = Counter(re.findall(r"R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)", sb.get(fn, "")))
            fc = Counter(re.findall(r"R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)", fb.get(fn, "")))
            ck(f"target call multiset exact: {fn}", sc == fc, f"stock={sc} island={fc}")

    for fn in ("tee_core_del", "tee_core_free", "TEEC_CloseSession") + tuple(IDR):
        ok = fn in sf and fn in ff and st[sf[fn][0]:sf[fn][0] + sf[fn][1]] == ft[ff[fn][0]:ff[fn][0] + ff[fn][1]]
        ck(f"byte-identical target: {fn}", ok)
    ck("TEEC_OpenSession size exact", sf.get("TEEC_OpenSession", (0, -1))[1] == ff.get("TEEC_OpenSession", (0, -2))[1] == 412)

    scope = tsv("phase4-tkcore-island-phase3a-r-scope.tsv")
    ck("scope ledger present", scope is not None)
    states = {r["function"]: r["phase3a-r state"] for r in scope or []}
    for fn in CORE + TEEC + IDR:
        ck(f"scope ledger closes: {fn}", states.get(fn) in {"CFG_EQUIVALENT", "SIZE_EXACT_SEMANTIC_EXACT", "EXACT_BYTE"}, states.get(fn, "missing"))

    # Source-level handle and lifecycle requirements.
    core_src = read(ISLAND / "tkcore/tee_core.c")
    api_src = read(ISLAND / "tkcore/tee_kernel_api.c")
    hdr_src = read(TRUSTKERNEL / "include/trustkernel/tee_core.h")
    ck("live core source present", len(core_src) > 10000)
    ck("live TEEC source present", len(api_src) > 5000)
    ck("IDR positive start and unbounded end", "idr_alloc(&tee_idr, ptr, 1, 0, GFP_NOWAIT)" in core_src)
    ck("IDR preload uses GFP_KERNEL", "idr_preload(GFP_KERNEL)" in core_src)
    ck("IDR allocation protected by spinlock", "spin_lock(&tee_idr_lock)" in core_src and "spin_unlock(&tee_idr_lock)" in core_src)
    ck("IDR lookup and remove present", "idr_find(&tee_idr, uuid)" in core_src and "idr_remove(&tee_idr, uuid)" in core_src)
    ck("correct __tee_get prototype", "int __tee_get(struct tee *tee)" in core_src and "int __tee_get(struct tee *tee);" in hdr_src)

    expected_tokens = {
        "tee_core_alloc": ["tee_supp_init", "devm_kzalloc", "snprintf"],
        "tee_core_add": ["misc_register", "tee_init_procfs", "tee_init_sysfs", "tee_peridev_init"],
        "tee_core_del": ["tee_peridev_exit", "tee_cleanup_sysfs", "tee_supp_deinit"],
        "tee_core_free": ["tee_supp_deinit", "devm_kfree"],
        "__tee_get": ["try_module_get", "get_device", "ops->start"],
    }
    for fn, tokens in expected_tokens.items():
        b = body(core_src, fn)
        ck(f"no speculative success stub: {fn}", len(b) > 80 and all(t in b for t in tokens))
    expected_teec = {
        "TEEC_InitializeContext": ["tee_get_tee", "tee_context_create", "tee_core_alloc_uuid"],
        "TEEC_FinalizeContext": ["tee_core_uuid2ptr", "tee_core_free_uuid", "tee_context_destroy"],
        "TEEC_OpenSession": ["tee_core_uuid2ptr", "tee_session_create_and_open", "tee_core_alloc_uuid", "tee_session_close_and_destroy"],
        "TEEC_CloseSession": ["tee_core_uuid2ptr", "tee_core_free_uuid", "tee_session_close_and_destroy"],
    }
    for fn, tokens in expected_teec.items():
        b = body(api_src, fn)
        ck(f"no speculative success stub: {fn}", len(b) > 80 and all(t in b for t in tokens))
        ck(f"no pointer/int handle cast: {fn}", "uintptr_t" not in b and "(long)" not in b)
    fin = body(api_src, "TEEC_FinalizeContext")
    close = body(api_src, "TEEC_CloseSession")
    ck("context handle freed before destruction", fin.find("tee_core_free_uuid") < fin.find("tee_context_destroy"))
    ck("session handle freed before destruction", close.find("tee_core_free_uuid") < close.find("tee_session_close_and_destroy"))
    ck("stock default client name", '#define TEE_TZ_DEVICE_NAME\t"tkcore_client"' in api_src)

    # Layout table and compile-time probe.
    layout = tsv("phase4-tkcore-island-phase3a-r-layout-check.tsv")
    ck("layout ledger has 51 assertions", layout is not None and len(layout) == 51, len(layout or []))
    ck("all layout assertions build-enforced", layout is not None and all(r["build-enforced"] == "YES" for r in layout))
    layout_map = {(r["type"], r["member"]): r["expected"] for r in layout or []}
    ck("TEEC_Context size 0x108", layout_map.get(("TEEC_Context", "(total size)")) == "0x108")
    ck("TEEC_Session size 8", layout_map.get(("TEEC_Session", "(total size)")) in {"8", "0x08", "0x8"})
    ck("tee_context size 0xd0", layout_map.get(("struct tee_context", "(total size)")) == "0xd0")
    ck("layout probe ELF frozen", (PHASE / "build/tk_layout_probe.phase3a-r.ko").is_file())

    # Static consumer traces.
    tmem = read(KERNEL / "phase4-tkcore-island-phase3a-r-tmem-trace.md")
    drv = read(KERNEL / "phase4-tkcore-island-phase3a-r-tkcore-drv-trace.md")
    trace = read(PHASE / "static-trace-check.txt")
    ck("tmem trace PASS_STATIC", "Result: PASS_STATIC" in tmem and "TMEM_RESULT=PASS_STATIC" in trace)
    ck("tmem lifecycle order documented", "TEEC_InitializeContext\n  → TEEC_OpenSession\n  → TEEC_CloseSession\n  → TEEC_FinalizeContext" in tmem)
    ck("tkcore_drv trace PASS_STATIC", "Result: PASS_STATIC" in drv and "TKCORE_DRV_RESULT=PASS_STATIC" in trace)
    ck("tkcore_drv natural constructor order", "TKCORE_TEE_TZ_NEW=tee_core_alloc;tee_core_add;__tee_get;tee_core_del" in trace)
    ck("unreferenced tee_core_free accounted", "TEE_CORE_FREE=NOT_CALLED" in trace and "NOT_CALLED" in drv)

    # Clean final build and module metadata.
    result = env_file(PHASE / "build/final-build-result.env")
    for key in ("BUILD_RC", "COMPILER_WARNINGS", "COMPILER_ERRORS", "MODPOST_WARNINGS", "UNRESOLVED", "STATIC_ASSERT_FAILURES"):
        ck(f"final build {key}=0", result.get(key) == "0", result.get(key, "missing"))
    ck("final build hash recorded", result.get("TKCORE_SHA256") == FINAL_SHA)
    blog = read(PHASE / "build/final-build.log")
    ck("final build log frozen", len(blog) > 0)
    ck("final build reported success", "Build completed successfully" in blog)
    diagnostics = [l for l in blog.splitlines() if re.search(r"(?i)\b(?:warning|error):", l) and "SSL error" not in l]
    ck("final build has no compiler diagnostics", not diagnostics, diagnostics[:3])
    ck("final build has no modpost warning", not re.search(r"(?i)modpost.*warning|WARNING: modpost", blog))
    ck("final build has no unresolved symbol", "undefined!" not in blog)
    modinfo = command("llvm-objcopy", "--dump-section", ".modinfo=/dev/stdout", str(FINAL), binary=True).decode(errors="ignore")
    ck("module depends empty", any(x == "depends=" for x in modinfo.split("\x00")))
    ck("module license GPL", "license=GPL" in modinfo)

    # Three-way regression and regenerated inventories.
    shared_p = set(sf) & set(pf)
    shared_f = set(sf) & set(ff)
    ck("stock function coverage 91/122", len(sf) == 122 and len(shared_f) == 91, f"{len(shared_f)}/{len(sf)}")
    ck("31 stock functions remain", len(set(sf) - set(ff)) == 31)
    ck("Phase-3A-R adds six stock functions", len(shared_f - shared_p) == 6, sorted(shared_f - shared_p))
    ck("no stock function regressed", not (shared_p - shared_f), sorted(shared_p - shared_f))

    def exact(funcs, text):
        return {n for n in set(sf) & set(funcs) if st[sf[n][0]:sf[n][0] + sf[n][1]] == text[funcs[n][0]:funcs[n][0] + funcs[n][1]]}

    exact_p, exact_f = exact(pf, pt), exact(ff, ft)
    ck("33 byte-identical stock functions", len(exact_f) == 33, len(exact_f))
    ck("no byte-identical regression", not (exact_p - exact_f), sorted(exact_p - exact_f))
    kp = {n for n in shared_p if kcfi(st, sf[n]) == kcfi(pt, pf[n])}
    kf = {n for n in shared_f if kcfi(st, sf[n]) == kcfi(ft, ff[n])}
    ck("83 KCFI-exact shared functions", len(kf) == 83, len(kf))
    ck("no KCFI regression", not (kp - kf), sorted(kp - kf))
    ck("every new import exists in stock", not (fu - pu - su), sorted(fu - pu - su))
    ck("no export fabricated", not (fe - se), sorted(fe - se))
    ck("19/25 exports present", len(fe) == 19 and len(se) == 25, f"{len(fe)}/{len(se)}")

    inventories = ["functions", "kcfi-all", "imports", "exports", "objects", "relocations", "callgraph", "strings", "metadata"]
    for name in inventories:
        ck(f"inventory regenerated: {name}", (KERNEL / f"phase4-tkcore-island-phase3a-r-{name}.tsv").is_file())

    # Source snapshot and forbidden techniques.
    snapshot = PHASE / "source"
    source_manifest = tsv_path(PHASE / "interrupted-checkpoint/source-hashes.tsv")
    ck("modified-source manifest has four files", source_manifest is not None and len(source_manifest) == 4, len(source_manifest or []))
    for row in source_manifest or []:
        live = GKI / row["path"]
        archived = snapshot / row["path"]
        expected = row["sha256"]
        ck(f"live source hash preserved: {row['path']}", live.is_file() and sha256(live) == expected)
        ck(f"source snapshot hash preserved: {row['path']}", archived.is_file() and sha256(archived) == expected)

    text_tree = ""
    forbidden_binary = []
    for root in (ISLAND, TRUSTKERNEL):
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in {".o", ".ko"}:
                forbidden_binary.append(str(p))
            if p.is_file() and (p.suffix in {".c", ".h", ".bazel"} or p.name == "Makefile"):
                text_tree += "\n" + read(p)
    ck("no CRC injection", "__crc_" not in text_tree and "kcrctab" not in text_tree)
    ck("no __versions editing", "__versions" not in text_tree)
    ck("no KBUILD_MODPOST_WARN", not re.search(r"(?m)^\s*(?:export\s+)?KBUILD_MODPOST_WARN\s*[:+?]?=", text_tree))
    ck("no ELF patch tooling", not re.search(r"\b(?:objcopy|patchelf)\b", text_tree))
    ck("no stock object inclusion", not forbidden_binary and ".stock.ko" not in text_tree and "/oracle/" not in text_tree, forbidden_binary)

    # Reports and frozen status boundary.
    for report_name in (
        "phase4-tkcore-island-phase3a-r-interrupted-checkpoint.md",
        "phase4-tkcore-island-phase3a-r-core-acceptance.md",
        "phase4-tkcore-idr-handle-contract.md",
        "phase4-tkcore-context-contract.md",
        "phase4-tkcore-session-contract.md",
        "phase4-tkcore-island-phase3a-r-acceptance.md",
    ):
        ck(f"report present: {report_name}", len(read(KERNEL / report_name)) > 500)
    acceptance = read(KERNEL / "phase4-tkcore-island-phase3a-r-acceptance.md")
    ck("overall status remains PARTIAL", "Overall tkcore: **PARTIAL**" in acceptance)
    ck("not runtime ready", "Runtime readiness: **NOT RUNTIME READY**" in acceptance)
    ck("stock runtime provider retained", "Runtime provider: **STOCK RUNTIME PROVIDER**" in acceptance)
    ck("next phase is shared memory", "PHASE 3B SHARED-MEMORY RECONSTRUCTION" in acceptance)

    report()


def tsv_path(path: Path):
    if not path.is_file():
        return None
    with path.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def report() -> None:
    bad = [x for x in checks if not x[1]]
    for name, ok, detail in checks:
        suffix = f"  ({detail})" if detail and not ok else ""
        print(f"[{'OK' if ok else 'FAIL'}] {name}{suffix}")
    print("=" * 72)
    print(f"{len(checks) - len(bad)}/{len(checks)} CHECKS PASSED")
    if bad:
        print("TKCORE_ISLAND_PHASE3A_R_VERIFICATION_FAILED")
        raise SystemExit(1)
    print("TKCORE_ISLAND_PHASE3A_R_CORE_CONTEXT_SESSION_STATIC_PASS")
    print("TKCORE_REPLACEMENT_READY=NO")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STILL_PRESENT")


if __name__ == "__main__":
    main()
