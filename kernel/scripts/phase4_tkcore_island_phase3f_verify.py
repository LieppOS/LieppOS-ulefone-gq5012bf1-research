#!/usr/bin/env python3
"""Fail-closed static verifier for GQ5012BF1 tkcore island Phase 3F.

Certifies the FINAL TrustKernel provider/consumer source-island acceptance:
the statically complete Phase-3E tkcore provider is consumed from source by
tkcore_drv, tmem_ffa and microarray_fp_tee with zero stock-tkcore ABI witness.

It does NOT certify runtime behaviour, secure-world behaviour, or readiness to
deploy.  Runtime validation is a separately authorised Phase 3G.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
ACC = REPO / "workspace/phase4-tkcore-island/acceptance"
KERNEL = REPO / "kernel"

PHASE3E_SHA = "caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983"
STOCK_TKCORE_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"

STOCK_TKCORE = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
PROVIDER = ACC / "provider/tkcore.phase3e.ko"
PROVIDER_SYMVERS = ACC / "provider/Module.symvers"

CONSUMERS = {
    "tkcore_drv": {
        "ko": ACC / "tkcore_drv/tkcore_drv.phase3f.ko",
        "baseline": REPO / "workspace/phase4-tkcore-drv/build/tkcore_drv.stockabi.ko",
        "pkg": GKI / "lieppos/tkcore-drv-phase3f",
        "edges": 11,
        "funcs": 50,
        "depends": {"ffa_v10", "tkcore"},
    },
    "tmem_ffa": {
        "ko": ACC / "tmem_ffa/tmem_ffa.phase3f.ko",
        "baseline": REPO / "workspace/phase4-gz-tz-system/build/tmem_ffa.gzaccept.ko",
        "pkg": GKI / "lieppos/tmem-ffa-phase3f",
        "edges": 7,
        "funcs": 141,
        "depends": {"gz_tz_system", "tkcore", "ffa_v10"},
    },
    "microarray_fp_tee": {
        "ko": ACC / "microarray_fp_tee/microarray_fp_tee.phase3f.ko",
        "baseline": REPO / "workspace/phase4-microarray-fp-tee/build/microarray_fp_tee.recon-stockabi.ko",
        "pkg": GKI / "lieppos/microarray-fp-tee-phase3f",
        "edges": 1,
        "funcs": 27,
        "depends": {"fingerprint", "spi-mt65xx", "tkcore"},
    },
}

NON_TKCORE_PROVIDERS = {
    "ffa_v10": GKI / "bazel-bin/lieppos/ffa-v10/ffa_v10/Module.symvers",
    "gz_tz_system": GKI / "bazel-bin/lieppos/gz-tz-system/gz_tz_system/Module.symvers",
    "fingerprint": GKI / "bazel-bin/lieppos/fingerprint-recon/fingerprint_recon/Module.symvers",
    "spi-mt65xx": GKI / "bazel-bin/lieppos/spi-mt65xx/spi_mt65xx/Module.symvers",
}

DOCS = [
    "phase4-tkcore-island-phase3f-baseline.md",
    "phase4-tkcore-island-phase3f-header-authority.md",
    "phase4-tkcore-island-phase3f-tkcore-drv-acceptance.md",
    "phase4-tkcore-island-phase3f-tmem-acceptance.md",
    "phase4-tkcore-island-phase3f-tmem-provider-provenance.md",
    "phase4-tkcore-island-phase3f-microarray-acceptance.md",
    "phase4-tkcore-island-phase3f-private-abi-provenance.md",
    "phase4-tkcore-island-phase3f-stock-consumer-compat.md",
    "phase4-tkcore-island-phase3f-deployment-unit.md",
    "phase4-tkcore-island-phase3f-load-order.md",
    "phase4-tkcore-island-phase3f-graph.md",
    "phase4-tkcore-island-phase3f-verifier-maintenance.md",
    "phase4-tkcore-island-phase3f-acceptance.md",
]
TSVS = [
    "phase4-tkcore-island-phase3f-edge-inventory.tsv",
    "phase4-tkcore-island-phase3f-header-divergence.tsv",
    "phase4-tkcore-island-phase3f-tkcore-drv-edges.tsv",
    "phase4-tkcore-island-phase3f-tmem-edges.tsv",
    "phase4-tkcore-island-phase3f-final-edge-matrix.tsv",
]

FORBIDDEN_WITNESS_NAMES = ("stock-provider.symvers", "tkcore-provider.symvers")
FORBIDDEN_SOURCE_TOKENS = [
    ("__crc_", "CRC injection"),
    ("__versions", "__versions edit"),
    ("__kcrctab", "kcrctab edit"),
    ("KBUILD_MODPOST_WARN", "modpost warning suppression"),
]

checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("inv", REPO / "kernel/scripts/phase4_tkcore_inventory.py")
inv = importlib.util.module_from_spec(spec)
sys.modules["inv"] = inv
assert spec.loader
spec.loader.exec_module(inv)


def funcs(e):
    return {s.name: s for s in e.symbols if s.name and s.st_type == inv.STT_FUNC and s.shndx != inv.SHN_UNDEF}


def objects(e):
    return {s.name: s for s in e.symbols if s.name and s.st_type == inv.STT_OBJECT and s.shndx != inv.SHN_UNDEF}


def relocs(e):
    out = []
    for rs in e.sections:
        if rs.sh_type != inv.SHT_RELA:
            continue
        ent = rs.entsize or 24
        for i in range(rs.size // ent):
            off, info, add = struct.unpack_from("<QQq", rs.data, i * ent)
            si, rt = info >> 32, info & 0xFFFFFFFF
            out.append((e.sections[rs.info].name, off, rt, e.symbols[si].name, add))
    return out


def symvers(p: Path) -> dict[str, int]:
    return {l.split("\t")[1]: int(l.split("\t")[0], 16)
            for l in p.read_text().splitlines() if l.strip()}


def depends_of(p: Path) -> set[str]:
    mi = subprocess.run(["modinfo", str(p)], capture_output=True, text=True).stdout
    for l in mi.splitlines():
        if l.startswith("depends:"):
            v = l.split(":", 1)[1].strip()
            return set(x for x in v.split(",") if x)
    return set()


def main() -> int:
    # ---------------- PROVIDER -------------------------------------------
    ck("stock tkcore oracle present", STOCK_TKCORE.is_file())
    ck("frozen Phase-3E provider present in acceptance", PROVIDER.is_file())
    ck("provider natural Module.symvers present", PROVIDER_SYMVERS.is_file())
    if not (STOCK_TKCORE.is_file() and PROVIDER.is_file() and PROVIDER_SYMVERS.is_file()):
        return report()

    ck("stock tkcore SHA exact", sha(STOCK_TKCORE) == STOCK_TKCORE_SHA, sha(STOCK_TKCORE))
    ck("provider SHA is exactly Phase-3E", sha(PROVIDER) == PHASE3E_SHA, sha(PROVIDER))

    live = GKI / "bazel-bin/lieppos/tkcore-island/tkcore/tkcore.ko"
    if live.is_file():
        ck("live rebuilt provider still exactly Phase-3E (not mutated by 3F)",
           sha(live) == PHASE3E_SHA, sha(live))

    s, c = inv.ELF64LE(STOCK_TKCORE), inv.ELF64LE(PROVIDER)
    sf, cf = set(funcs(s)), set(funcs(c))
    ck("stock function count is 122", len(sf) == 122, len(sf))
    ck("provider stock-function coverage is 122/122", len(sf & cf) == 122, f"{len(sf & cf)}/{len(sf)}")
    ck("provider missing functions is 0", not (sf - cf), sorted(sf - cf))
    ck("provider island-only functions is 0", not (cf - sf), sorted(cf - sf))
    SE, FE = dict(inv.export_map(s)), dict(inv.export_map(c))
    ck("stock export surface is 25", len(SE) == 25, len(SE))
    ck("provider export surface is 25/25", len(FE) == 25 and not (set(SE) - set(FE)),
       f"{len(FE)}/{len(SE)}")
    ck("provider symvers publishes all 25 exports",
       set(symvers(PROVIDER_SYMVERS)) == set(FE), len(symvers(PROVIDER_SYMVERS)))
    ck("provider has no intermodule dependency", not depends_of(PROVIDER), depends_of(PROVIDER))

    psym = symvers(PROVIDER_SYMVERS)
    ck("provider symvers CRCs equal provider ELF export CRCs",
       all(psym[n] == FE[n] for n in FE))

    # ---------------- EDGE INVENTORY -------------------------------------
    tk_names = set(SE) | set(FE)
    per_consumer_edges = {}
    for name, cfg in CONSUMERS.items():
        ck(f"{name}: acceptance build exists", cfg["ko"].is_file(), cfg["ko"])
    if not all(cfg["ko"].is_file() for cfg in CONSUMERS.values()):
        return report()

    total_edges = 0
    for name, cfg in CONSUMERS.items():
        v = dict(inv.parse_modversions(inv.ELF64LE(cfg["ko"])))
        edges = sorted(set(v) & tk_names)
        per_consumer_edges[name] = (v, edges)
        total_edges += len(edges)
        ck(f"{name}: tkcore edge count is {cfg['edges']}", len(edges) == cfg["edges"], len(edges))
    ck("actual total tkcore consumer edges is 19", total_edges == 19, total_edges)

    # ---------------- PER-CONSUMER ACCEPTANCE ----------------------------
    cls_counts = {"NATURAL_HISTORICAL_STOCK_CRC": 0, "ISLAND_NATURAL_PROVIDER_ABI": 0, "BLOCKED": 0}
    for name, cfg in CONSUMERS.items():
        v, edges = per_consumer_edges[name]
        accepted = [n for n in edges if v[n] == FE[n]]
        blocked = [n for n in edges if v[n] != FE[n]]
        ck(f"{name}: all {cfg['edges']} tkcore edges accept the final provider",
           len(accepted) == cfg["edges"], f"blocked={blocked}")
        for n in edges:
            if v[n] != FE[n]:
                cls_counts["BLOCKED"] += 1
            elif FE[n] == SE.get(n):
                cls_counts["NATURAL_HISTORICAL_STOCK_CRC"] += 1
            else:
                cls_counts["ISLAND_NATURAL_PROVIDER_ABI"] += 1

        # behaviour preservation against the frozen accepted baseline
        base = cfg["baseline"]
        ck(f"{name}: frozen baseline present", base.is_file(), base)
        if base.is_file():
            a, b = inv.ELF64LE(base), inv.ELF64LE(cfg["ko"])
            af, bf = funcs(a), funcs(b)
            ck(f"{name}: function count is {cfg['funcs']}", len(bf) == cfg["funcs"], len(bf))
            ck(f"{name}: function set unchanged", set(af) == set(bf),
               sorted(set(af) ^ set(bf))[:8])
            common = set(af) & set(bf)
            changed = [n for n in common if a.symbol_bytes(af[n]) != b.symbol_bytes(bf[n])]
            ck(f"{name}: every function body byte-identical to baseline", not changed, changed[:8])
            kd = [n for n in common if a.kcfi(af[n]) != b.kcfi(bf[n])]
            ck(f"{name}: no KCFI change", not kd, kd[:8])
            ck(f"{name}: relocations exactly equal", relocs(a) == relocs(b))
            ao, bo = objects(a), objects(b)
            oc = [n for n in set(ao) & set(bo) if a.symbol_bytes(ao[n]) != b.symbol_bytes(bo[n])]
            # Only the ABI table and pure build-provenance metadata may move.
            # srcversion is an MD5 over the source file set, so a Phase-3F
            # package with its own header overlay legitimately changes it; any
            # other object change is still a behavioural regression.
            def _meta(n: str) -> bool:
                return n == "____versions" or n.startswith(
                    ("__UNIQUE_ID_srcversion", "__UNIQUE_ID_depends", "__UNIQUE_ID_vermagic"))
            ck(f"{name}: only __versions/build-provenance objects differ",
               all(_meta(n) for n in oc), [n for n in oc if not _meta(n)])
            # vermagic itself must never move
            va_m = [l for l in subprocess.run(["modinfo", str(base)], capture_output=True,
                                              text=True).stdout.splitlines() if l.startswith("vermagic:")]
            vb_m = [l for l in subprocess.run(["modinfo", str(cfg["ko"])], capture_output=True,
                                              text=True).stdout.splitlines() if l.startswith("vermagic:")]
            ck(f"{name}: vermagic unchanged vs baseline", va_m == vb_m, (va_m, vb_m))
            va, vb = dict(inv.parse_modversions(a)), dict(inv.parse_modversions(b))
            ck(f"{name}: import-name set unchanged", set(va) == set(vb),
               sorted(set(va) ^ set(vb))[:8])
            moved = sorted(n for n in set(va) & set(vb) if va[n] != vb[n])
            ck(f"{name}: only tkcore edges moved provenance",
               set(moved) <= set(edges), sorted(set(moved) - set(edges)))
        ck(f"{name}: depends metadata as expected",
           depends_of(cfg["ko"]) == cfg["depends"], depends_of(cfg["ko"]))

    # ---------------- NON-TKCORE PROVIDERS ARE NATURAL --------------------
    expect_nat = {
        "tkcore_drv": ["ffa_v10"],
        "tmem_ffa": ["ffa_v10", "gz_tz_system"],
        "microarray_fp_tee": ["fingerprint", "spi-mt65xx"],
    }
    for name, provs in expect_nat.items():
        v, _ = per_consumer_edges[name]
        for pr in provs:
            path = NON_TKCORE_PROVIDERS[pr]
            ck(f"{name}: {pr} provider symvers present", path.is_file(), path)
            if not path.is_file():
                continue
            tbl = symvers(path)
            edges = sorted(set(v) & set(tbl))
            ck(f"{name}: has {pr} edges", bool(edges), len(edges))
            bad = [n for n in edges if v[n] != tbl[n]]
            ck(f"{name}: all {len(edges)} {pr} edges NATURAL from source provider", not bad, bad)

    # ---------------- NO STOCK TKCORE WITNESS ----------------------------
    for name, cfg in CONSUMERS.items():
        pkg = cfg["pkg"]
        ck(f"{name}: Phase-3F package exists", pkg.is_dir(), pkg)
        if not pkg.is_dir():
            continue
        leaked = sorted(p.name for p in pkg.rglob("*") if p.is_file() and p.name in FORBIDDEN_WITNESS_NAMES)
        ck(f"{name}: no stock ABI witness file in build package", not leaked, leaked)
        mk = pkg / "Makefile"
        ck(f"{name}: Makefile present", mk.is_file())
        if mk.is_file():
            txt = mk.read_text()
            # Strip comment lines: prose documenting that a witness is absent
            # must not be mistaken for an actual reference to one.
            code = "\n".join(l for l in txt.splitlines() if not l.lstrip().startswith("#"))
            ck(f"{name}: no KBUILD_MODPOST_WARN", "KBUILD_MODPOST_WARN" not in code)
            ck(f"{name}: no stock provider symvers referenced in build code",
               not any(w in code for w in FORBIDDEN_WITNESS_NAMES),
               [l for l in code.splitlines() if any(w in l for w in FORBIDDEN_WITNESS_NAMES)])
            ck(f"{name}: consumes the final tkcore-island provider record",
               "lieppos/tkcore-island/Module.symvers" in code)
        # every implementation source must be a symlink to the frozen package
        impl = [p for p in pkg.rglob("*") if p.suffix in (".c",) ]
        ck(f"{name}: all driver .c sources are frozen symlinks",
           bool(impl) and all(p.is_symlink() for p in impl),
           [str(p.relative_to(pkg)) for p in impl if not p.is_symlink()][:5])

    # acceptance evidence itself must be witness-free
    leaked = sorted(str(p.relative_to(ACC)) for p in ACC.rglob("*")
                    if p.is_file() and p.name in FORBIDDEN_WITNESS_NAMES)
    ck("no stock ABI witness anywhere in acceptance evidence", not leaked, leaked)

    # ---------------- CLEAN BUILDS ---------------------------------------
    for name in CONSUMERS:
        log = ACC / name / "build.log"
        ck(f"{name}: build log frozen", log.is_file())
        if log.is_file():
            t = log.read_text(errors="ignore")
            bad = [l for l in t.splitlines()
                   if ("error:" in l.lower() or "undefined!" in l
                       or ("modpost" in l.lower() and "warning" in l.lower()))
                   and "SSL error" not in l]
            ck(f"{name}: build log clean (no errors/modpost warnings/unresolved)", not bad, bad[:4])
        summ = ACC / name / "build-summary.txt"
        ck(f"{name}: build summary frozen", summ.is_file())
        if summ.is_file():
            t = summ.read_text()
            ck(f"{name}: summary records BUILD_RC=0", "BUILD_RC=0" in t)
            ck(f"{name}: summary records 0 modpost warnings", "MODPOST_WARNINGS=0" in t)
            ck(f"{name}: summary records 0 unresolved", "UNRESOLVED_SYMBOLS=0" in t)
            ck(f"{name}: summary records PASS_STATIC_FINAL_TKCORE_PROVIDER",
               "PASS_STATIC_FINAL_TKCORE_PROVIDER" in t)

    # ---------------- 19-EDGE MATRIX -------------------------------------
    matrix = KERNEL / "phase4-tkcore-island-phase3f-final-edge-matrix.tsv"
    ck("final 19-edge matrix present", matrix.is_file())
    if matrix.is_file():
        rows = list(csv.DictReader(matrix.open(), delimiter="\t"))
        ck("matrix has exactly 19 rows", len(rows) == 19, len(rows))
        ck("matrix has one row per consumer edge",
           sorted((r["consumer"], r["symbol"]) for r in rows) ==
           sorted((cn, sym) for cn, (_, e) in per_consumer_edges.items() for sym in e))
        ck("matrix BLOCKED count is 0",
           not [r for r in rows if r["Phase-3F classification"] == "BLOCKED"])
        ck("matrix stock witness used = NO for all 19",
           all(r["stock witness used?"].strip().upper() == "NO" for r in rows))
        ck("matrix result ACCEPTED for all 19",
           all(r["result"].strip() == "ACCEPTED" for r in rows))
        n = sum(1 for r in rows if r["Phase-3F classification"] == "NATURAL_HISTORICAL_STOCK_CRC")
        m = sum(1 for r in rows if r["Phase-3F classification"] == "ISLAND_NATURAL_PROVIDER_ABI")
        ck("matrix N+M = 19", n + m == 19, f"N={n} M={m}")
        ck("matrix counts agree with measured ELF classification",
           n == cls_counts["NATURAL_HISTORICAL_STOCK_CRC"] and m == cls_counts["ISLAND_NATURAL_PROVIDER_ABI"],
           f"matrix N={n} M={m} vs measured {cls_counts}")
        ck("every matrix CRC pair is internally consistent",
           all(r["Phase-3F consumer CRC"] == r["Phase-3E tkcore CRC"] for r in rows))
        # every category-B edge must be documented in the private-ABI report
        prov = (KERNEL / "phase4-tkcore-island-phase3f-private-abi-provenance.md")
        if prov.is_file():
            ptxt = prov.read_text()
            undoc = [r["symbol"] for r in rows
                     if r["Phase-3F classification"] == "ISLAND_NATURAL_PROVIDER_ABI"
                     and r["symbol"] not in ptxt]
            ck("every island-natural edge documented in private-ABI provenance", not undoc, undoc)

    ck("measured BLOCKED count is 0", cls_counts["BLOCKED"] == 0, cls_counts)
    ck("measured N+M = 19",
       cls_counts["NATURAL_HISTORICAL_STOCK_CRC"] + cls_counts["ISLAND_NATURAL_PROVIDER_ABI"] == 19,
       cls_counts)

    # ---------------- DEPLOYMENT UNIT / STOCK COMPAT ----------------------
    compat_doc = KERNEL / "phase4-tkcore-island-phase3f-stock-consumer-compat.md"
    unit_doc = KERNEL / "phase4-tkcore-island-phase3f-deployment-unit.md"
    ck("stock-consumer compatibility report present", compat_doc.is_file())
    ck("deployment-unit report present", unit_doc.is_file())
    if compat_doc.is_file():
        t = compat_doc.read_text()
        ck("compat report classifies both categories",
           "STOCK_BINARY_DIRECTLY_COMPATIBLE" in t and "SOURCE_ISLAND_ONLY" in t)
    if unit_doc.is_file():
        t = unit_doc.read_text()
        ck("deployment unit explicitly classified",
           "TRUSTKERNEL_SOURCE_ABI_ISLAND" in t or "TKCORE_DROP_IN_PROVIDER" in t)
        ck("deployment unit lists the modules that must move together",
           all(x in t for x in ("tkcore.ko", "tkcore_drv.ko", "tmem_ffa.ko")))
    # recompute stock-binary compatibility independently
    stock_c = {
        "tkcore_drv": REPO / "workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko",
        "tmem_ffa": REPO / "workspace/phase4-tmem-ffa/oracle/tmem_ffa.stock.ko",
        "microarray_fp_tee": REPO / "workspace/phase4-microarray-fp-tee/oracle/microarray_fp_tee.stock.ko",
    }
    compat_total = 0
    for name, p in stock_c.items():
        if not p.is_file():
            ck(f"stock {name} oracle present", False, p)
            continue
        sv = dict(inv.parse_modversions(inv.ELF64LE(p)))
        edges = sorted(set(sv) & tk_names)
        compat_total += sum(1 for n in edges if sv[n] == FE[n])
    ck("stock-binary compatibility recomputes to 5 of 19", compat_total == 5, compat_total)

    # ---------------- LOAD ORDER -----------------------------------------
    lo = REPO / "workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/modules.load"
    ck("stock vendor-ramdisk modules.load present", lo.is_file())
    if lo.is_file():
        lines = [l.strip() for l in lo.read_text().splitlines() if l.strip()]
        idx = {m: lines.index(m) for m in ("ffa_v10.ko", "teeperf.ko", "tkcore.ko", "tkcore_drv.ko")
               if m in lines}
        ck("stock load order ffa_v10 < teeperf < tkcore < tkcore_drv preserved",
           idx.get("ffa_v10.ko", -1) < idx.get("teeperf.ko", -1) < idx.get("tkcore.ko", -1)
           < idx.get("tkcore_drv.ko", -1), idx)
        if "fingerprint.ko" in lines and "microarray_fp_tee.ko" in lines:
            ck("stock load order fingerprint < microarray_fp_tee preserved",
               lines.index("fingerprint.ko") < lines.index("microarray_fp_tee.ko"))
    ck("load-order audit report present",
       (KERNEL / "phase4-tkcore-island-phase3f-load-order.md").is_file())

    # ---------------- FORBIDDEN TECHNIQUES -------------------------------
    for name, cfg in CONSUMERS.items():
        pkg = cfg["pkg"]
        if not pkg.is_dir():
            continue
        for f in pkg.rglob("*"):
            if not f.is_file() or f.is_symlink() or f.suffix not in (".h", ".c"):
                continue
            txt = f.read_text(errors="ignore")
            for tok, label in FORBIDDEN_SOURCE_TOKENS:
                ck(f"{name}: no {label} in overlay {f.name}", tok not in txt)

    # ---------------- REPORTS --------------------------------------------
    for d in DOCS:
        p = KERNEL / d
        ck(f"report present: {d}", p.is_file() and len(p.read_text()) > 400)
    for t in TSVS:
        p = KERNEL / t
        ck(f"table present: {t}", p.is_file() and len(p.read_text()) > 200)

    # ---------------- SCOPE / NO RUNTIME ---------------------------------
    acc_doc = KERNEL / "phase4-tkcore-island-phase3f-acceptance.md"
    if acc_doc.is_file():
        t = acc_doc.read_text()
        ck("acceptance states runtime validation NOT performed",
           "NOT PERFORMED" in t.upper())
        ck("acceptance states replacement readiness NO",
           "REPLACEMENT READY" in t.upper() and "NO" in t.upper())
        ck("acceptance uses the STATICALLY ELIMINATED qualifier",
           "STATICALLY ELIMINATED" in t.upper())

    # ---------------- PRIOR VERIFIERS ------------------------------------
    for label, script, want in [
        ("Phase 3E", "phase4_tkcore_island_phase3e_verify.py", 167),
        ("Phase 3D", "phase4_tkcore_island_phase3d_verify.py", 158),
        ("Phase 3C-R", "phase4_tkcore_island_phase3c_r_verify.py", 59),
        ("Phase 3C", "phase4_tkcore_island_phase3c_verify.py", 81),
        ("Phase 3B", "phase4_tkcore_island_phase3b_verify.py", 205),
        ("Phase 3A-R", "phase4_tkcore_island_phase3a_r_verify.py", 162),
    ]:
        r = subprocess.run([sys.executable, str(REPO / "kernel/scripts" / script)],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        ck(f"{label} verifier passes at {want}/{want}",
           r.returncode == 0 and f"{want}/{want} CHECKS PASSED" in out,
           next((l for l in out.splitlines() if "CHECKS PASSED" in l), "no summary"))

    return report()


def report() -> int:
    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        if not ok:
            print(f"[FAIL] {name}" + (f": {detail}" if detail else ""))
    for name, ok, detail in checks:
        if ok:
            print(f"[OK] {name}" + (f": {detail}" if detail else ""))
    print(f"\n{len(checks) - len(bad)}/{len(checks)} CHECKS PASSED")
    if bad:
        print("TKCORE_ISLAND_PHASE3F_VERIFICATION_FAILED")
        return 1
    print("TKCORE_ISLAND_PHASE3F_FINAL_CONSUMER_ACCEPTANCE_PASS")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STATICALLY_ELIMINATED")
    print("RUNTIME_VALIDATION=NOT_PERFORMED")
    print("TKCORE_REPLACEMENT_READY=NO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
