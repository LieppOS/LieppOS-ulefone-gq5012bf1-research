#!/usr/bin/env python3
"""Fail-closed static verifier for GQ5012BF1 tkcore island Phase 3E.

Certifies function-set/platform-affinity reconstruction only. It does not
certify runtime behavior or final consumer acceptance.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
BEFORE = REPO / "workspace/phase4-tkcore-island/phase3e/before/tkcore.phase3d.ko"
FROZEN = REPO / "workspace/phase4-tkcore-island/phase3e/build/tkcore.phase3e.ko"
LIVE = GKI / "bazel-bin/lieppos/tkcore-island/tkcore/tkcore.ko"
ISLAND_SRC = GKI / "lieppos/tkcore-island"
SOURCE = ISLAND_SRC / "tkcore/tee_core.c"
SNAPSHOT = REPO / "workspace/phase4-tkcore-island/phase3e/source/tee_core.c"
STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
BEFORE_SHA = "c34a16e78a385a995e626c922bbc02dc756217cca9ef403253dd37999f4031b5"
PHASE3E_SHA = "caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983"
TARGETS = {
    "big_core_affinity_need_bind_cpu": (8, "0x98d3ad02"),
    "big_core_affinity_match_cpu": (36, "0x7850c00b"),
    "big_core_affinity_get_candidate_cpu": (144, "0x89fb613d"),
    "plat_cpu_is_big": (68, "0xbd7efeae"),
    "plat_tee_init": (176, "0x36b1c5a6"),
}
PHASE3D_TARGETS = {
    "tee_clkmgr_handle", "tee_spi_cfg_padsel", "tee_spi_transfer",
    "tee_spi_transfer_disable",
}
NEW_IMPORTS = {"__cpu_possible_mask", "_find_next_bit", "cpu_topology", "nr_cpu_ids"}
NEW_OBJECTS = {
    "big_core_affinity", "big_core_affinity_operations",
    "big_core_affinity_get_candidate_cpu.candidate_cpu", "large_cluster_id",
}
DOCS = [
    "phase4-tkcore-island-phase3e-baseline.md",
    "phase4-tkcore-island-phase3e-RED.md",
    "phase4-tkcore-island-phase3e-callgraph-contract.md",
    "phase4-tkcore-big-core-topology.md",
    "phase4-tkcore-plat-cpu-is-big-contract.md",
    "phase4-tkcore-big-core-match-contract.md",
    "phase4-tkcore-big-core-candidate-contract.md",
    "phase4-tkcore-big-core-bind-contract.md",
    "phase4-tkcore-affinity-mutation.md",
    "phase4-tkcore-plat-tee-init-contract.md",
    "phase4-tkcore-phase3e-init-trace.md",
    "phase4-tkcore-island-phase3e-type-recovery.md",
    "phase4-tkcore-island-phase3e-function-set-acceptance.md",
    "phase4-tkcore-island-phase3e-whole-callgraph.md",
    "phase4-tkcore-island-phase3e-init-exit-acceptance.md",
    "phase4-tkcore-island-phase3e-regression.md",
    "phase4-tkcore-island-phase3e-closure.md",
]
TSVS = [
    "functions", "kcfi", "imports", "exports", "export-parity", "objects",
    "relocations", "callgraph", "strings", "metadata", "function-progress",
]
STATUS_DOCS = [
    "zero-blob-queue.md", "module-replacement-plan.md",
    "phase4-remaining-module-triage.md",
    "phase4-remaining-module-dependency-graph.md",
    "phase4-slot-b-minimum-source-stack.md", "phase4-buildability-plan.md",
    "phase4-tkcore-island-phase3-work-queue.md",
]
checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("inv", REPO / "kernel/scripts/phase4_tkcore_inventory.py")
inv = importlib.util.module_from_spec(spec)
sys.modules["inv"] = inv
assert spec.loader
spec.loader.exec_module(inv)


def funcs(elf):
    return {s.name: s for s in elf.symbols if s.name and s.st_type == inv.STT_FUNC and s.shndx != inv.SHN_UNDEF}


def objects(elf):
    return {s.name: s for s in elf.symbols if s.name and s.st_type == inv.STT_OBJECT and s.shndx != inv.SHN_UNDEF}


def imports(elf):
    return {s.name for s in elf.symbols if s.name and s.shndx == inv.SHN_UNDEF and s.bind in (1, 2)}


def internal_edges(elf):
    fs = funcs(elf)
    by_sec: dict[int, list] = {}
    exact = {}
    for f in fs.values():
        by_sec.setdefault(f.shndx, []).append(f)
        exact[(f.shndx, f.value)] = f.name
    out = set()
    for rs in elf.sections:
        if rs.sh_type != inv.SHT_RELA:
            continue
        ent = rs.entsize or 24
        for i in range(rs.size // ent):
            off, info, addend = struct.unpack_from("<QQq", rs.data, i * ent)
            si, rtype = info >> 32, info & 0xFFFFFFFF
            if rtype != 283:  # R_AARCH64_CALL26
                continue
            owners = [f for f in by_sec.get(rs.info, []) if f.value <= off < f.value + f.size]
            if not owners:
                continue
            owner = max(owners, key=lambda f: f.value).name
            target = elf.symbols[si]
            if target.st_type == inv.STT_FUNC and target.name:
                callee = target.name
            elif target.st_type == inv.STT_SECTION:
                callee = exact.get((target.shndx, target.value + addend))
            else:
                callee = None
            if callee in fs:
                out.add((owner, callee))
    return out


def reloc_at(elf, section: str, offset: int):
    sec = next((x for x in elf.sections if x.sh_type == inv.SHT_RELA and x.info == elf.by_name[section].index), None)
    out = []
    if not sec:
        return out
    ent = sec.entsize or 24
    for i in range(sec.size // ent):
        off, info, addend = struct.unpack_from("<QQq", sec.data, i * ent)
        if off == offset:
            si, rtype = info >> 32, info & 0xFFFFFFFF
            out.append((rtype, elf.symbols[si], addend))
    return out


def main() -> int:
    ck("stock oracle exists", STOCK.is_file())
    ck("Phase-3D frozen baseline exists", BEFORE.is_file())
    candidate = FROZEN if FROZEN.is_file() else LIVE
    ck("Phase-3E ELF exists", candidate.is_file(), candidate)
    if not (STOCK.is_file() and BEFORE.is_file() and candidate.is_file()):
        return report()
    ck("stock SHA exact", sha(STOCK) == STOCK_SHA, sha(STOCK))
    ck("Phase-3D SHA exact", sha(BEFORE) == BEFORE_SHA, sha(BEFORE))
    ck("Phase-3E SHA recorded/exact", sha(candidate) == PHASE3E_SHA, sha(candidate))

    s, b, c = map(inv.ELF64LE, (STOCK, BEFORE, candidate))
    sf, bf, cf = funcs(s), funcs(b), funcs(c)
    ss, bs, cs = set(sf), set(bf), set(cf)
    ck("stock function count is 122", len(ss) == 122, len(ss))
    ck("Phase-3D coverage is 117", len(ss & bs) == 117, len(ss & bs))
    ck("Phase-3E coverage is 122", len(ss & cs) == 122, len(ss & cs))
    ck("stock-minus-island empty", not (ss - cs), sorted(ss - cs))
    ck("island-minus-stock empty", not (cs - ss), sorted(cs - ss))
    ck("exact five added", cs - bs == set(TARGETS), sorted((cs - bs) ^ set(TARGETS)))
    ck("no function removed", not (bs - cs), sorted(bs - cs))
    before_identical = sum(s.symbol_bytes(sf[n]) == b.symbol_bytes(bf[n]) for n in ss & bs)
    after_identical = sum(s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]) for n in ss & cs)
    ck("byte-identical count 47 before", before_identical == 47, before_identical)
    ck("byte-identical count 54 after", after_identical == 54, after_identical)

    for n, (size, kcfi) in TARGETS.items():
        ck(f"target present: {n}", n in cf)
        if n not in cf:
            continue
        ck(f"target absent in Phase 3D: {n}", n not in bf)
        ck(f"target size exact: {n}", sf[n].size == cf[n].size == size, cf[n].size)
        ck(f"target KCFI exact: {n}", s.kcfi(sf[n]) == c.kcfi(cf[n]) == kcfi, c.kcfi(cf[n]))
        ck(f"target binding exact: {n}", sf[n].bind == cf[n].bind)
        ck(f"target body exact: {n}", s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]))

    for n in ("init_module", "cleanup_module"):
        ck(f"{n} raw-byte identical", s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]))
    for n in sorted(PHASE3D_TARGETS):
        ck(f"Phase-3D body unchanged: {n}", b.symbol_bytes(bf[n]) == c.symbol_bytes(cf[n]))
        ck(f"Phase-3D KCFI unchanged: {n}", b.kcfi(bf[n]) == c.kcfi(cf[n]))

    si, bi, ci = imports(s), imports(b), imports(c)
    ck("Phase-3D import count 97", len(bi) == 97, len(bi))
    ck("Phase-3E import count 101", len(ci) == 101, len(ci))
    ck("new imports exact", ci - bi == NEW_IMPORTS, sorted((ci - bi) ^ NEW_IMPORTS))
    ck("new imports all stock", NEW_IMPORTS <= si)
    ck("no import removed", not (bi - ci), sorted(bi - ci))
    ck("only known non-stock import remains", ci - si == {"_dev_err"}, sorted(ci - si))
    forbidden_affinity = {"set_cpus_allowed_ptr", "sched_setaffinity", "kthread_bind", "workqueue_set_unbound_cpumask"}
    ck("no affinity mutation import", not (ci & forbidden_affinity), sorted(ci & forbidden_affinity))

    se, be, ce = map(lambda e: dict(inv.export_map(e)), (s, b, c))
    ck("stock exports 25", len(se) == 25, len(se))
    ck("Phase-3D exports 25", len(be) == 25, len(be))
    ck("Phase-3E exports 25", len(ce) == 25, len(ce))
    ck("no export loss/addition", set(ce) == set(be) == set(se), sorted(set(se) ^ set(ce)))
    ck("no Phase-3D CRC movement", ce == be)
    ck("Phase-3D target export CRCs unchanged", all(ce[n] == be[n] for n in PHASE3D_TARGETS))
    ck("no Phase-3E target exported", not (set(TARGETS) & set(ce)))

    so, bo, co = objects(s), objects(b), objects(c)
    ck("new named objects exact", set(co) - set(bo) == NEW_OBJECTS, sorted((set(co) - set(bo)) ^ NEW_OBJECTS))
    for n in sorted(NEW_OBJECTS):
        ck(f"object exists in stock/island: {n}", n in so and n in co)
        if n in so and n in co:
            ck(f"object size exact: {n}", so[n].size == co[n].size)
    ck("candidate initial -1", c.symbol_bytes(co["big_core_affinity_get_candidate_cpu.candidate_cpu"]) == b"\xff" * 4)
    ck("large_cluster_id initial -1", c.symbol_bytes(co["large_cluster_id"]) == b"\xff" * 4)
    ck("ops object 24 bytes", co["big_core_affinity_operations"].size == 24)
    ck("affinity object 16 bytes", co["big_core_affinity"].size == 16)

    td = co["tee_device_configs"]
    aff = co["big_core_affinity"]
    ops = co["big_core_affinity_operations"]
    affinity_rels = reloc_at(c, c.sections[td.shndx].name, td.value + 0x60)
    ck("tkcore_fp affinity relocation exists once", len(affinity_rels) == 1, affinity_rels)
    if len(affinity_rels) == 1:
        rt, sym, add = affinity_rels[0]
        ck("tkcore_fp affinity relocation is ABS64", rt == 257, rt)
        ck("tkcore_fp affinity resolves exact object", sym.shndx == aff.shndx and sym.value + add == aff.value)
    policy_rels = reloc_at(c, c.sections[aff.shndx].name, aff.value)
    ck("affinity-to-ops relocation exists once", len(policy_rels) == 1, policy_rels)
    if len(policy_rels) == 1:
        rt, sym, add = policy_rels[0]
        ck("affinity-to-ops resolves exact object", rt == 257 and sym.shndx == ops.shndx and sym.value + add == ops.value)
    for slot, name in enumerate(("big_core_affinity_need_bind_cpu", "big_core_affinity_match_cpu", "big_core_affinity_get_candidate_cpu")):
        rel = reloc_at(c, c.sections[ops.shndx].name, ops.value + slot * 8)
        ck(f"ops slot {slot} has one relocation", len(rel) == 1, rel)
        if len(rel) == 1:
            rt, sym, add = rel[0]
            ck(f"ops slot {slot} resolves {name}", rt == 257 and sym.shndx == cf[name].shndx and sym.value + add == cf[name].value)

    expected_strings = [
        b"\x016tkcore: candidate big cpu set to %d\n\0",
        b"\x016tkcore: tkcore: big cluster_id = %d\n\0",
    ]
    for text in expected_strings:
        ck(f"exact target string present: {text!r}", text in candidate.read_bytes())

    sedges, cedges = internal_edges(s), internal_edges(c)
    ck("stock internal direct edge count 103", len(sedges) == 103, len(sedges))
    ck("island internal direct edge count 103", len(cedges) == 103, len(cedges))
    ck("whole internal direct callgraph exact", sedges == cedges,
       f"stock-only={sorted(sedges - cedges)} island-only={sorted(cedges - sedges)}")
    ck("affinity callbacks have no executable caller",
       not any(dst in TARGETS and dst.startswith("big_core_") for _src, dst in cedges))

    v3d = REPO / "kernel/scripts/phase4_tkcore_island_phase3d_verify.py"
    ck("Phase-3D verifier exists", v3d.is_file())
    if v3d.is_file():
        p = subprocess.run([sys.executable, str(v3d)], capture_output=True, text=True)
        ck("Phase-3D verifier passes", p.returncode == 0,
           (p.stdout.strip().splitlines() or ["no output"])[-1])

    for name in DOCS:
        p = REPO / "kernel" / name
        ck(f"report exists: {name}", p.is_file() and len(p.read_text(errors="ignore")) > 80)
    for stem in TSVS:
        p = REPO / f"kernel/phase4-tkcore-island-phase3e-{stem}.tsv"
        ck(f"TSV nontrivial: {stem}", p.is_file() and len(p.read_text(errors="ignore").splitlines()) > 1)
    for name in STATUS_DOCS:
        p = REPO / "kernel" / name
        text = p.read_text(errors="ignore") if p.is_file() else ""
        ck(f"current-status doc records 122/122: {name}", "122/122" in text)

    topology = (REPO / "kernel/phase4-tkcore-big-core-topology.md").read_text(errors="ignore")
    mutation = (REPO / "kernel/phase4-tkcore-affinity-mutation.md").read_text(errors="ignore")
    initdoc = (REPO / "kernel/phase4-tkcore-plat-tee-init-contract.md").read_text(errors="ignore")
    queue = (REPO / "kernel/phase4-tkcore-island-phase3-work-queue.md").read_text(errors="ignore")
    ck("topology uses cluster_id maximum", "maximum" in topology and "cluster_id" in topology)
    ck("topology rejects hard-coded CPU guess", "not guessed" in topology)
    ck("mutation point explicitly NONE", "Result: NONE" in mutation)
    ck("plat init excludes catch-all setup", "no registration" in initdoc.lower())
    # Monotone: todo #18 is OPEN through Phase 3E, and Phase 3F is the
    # authorised task that may close it.  Either recognised state passes;
    # an absent or unrecognised todo-#18 state still fails.
    _t18_open = "Todo #18 remains **OPEN**" in queue
    _t18_closed = ("todo #18 is" in queue.lower()
                   and "CLOSED" in queue
                   and "PHASE 3F FINAL TRUSTKERNEL ISLAND STATIC ACCEPTANCE PASS" in queue)
    ck("todo #18 carries a recognised state (open, or closed by Phase 3F)",
       _t18_open or _t18_closed,
       "open" if _t18_open else ("closed-by-3F" if _t18_closed else "UNRECOGNISED"))

    summary = REPO / "workspace/phase4-tkcore-island/phase3e/build/build-summary.txt"
    ck("build summary exists", summary.is_file())
    build = summary.read_text(errors="ignore") if summary.is_file() else ""
    for token in ("BUILD_RC=0", "COMPILER_WARNINGS=0", "COMPILER_ERRORS=0",
                  "MODPOST_WARNINGS=0", "UNRESOLVED_SYMBOLS=0",
                  "DEPENDS=(empty)", "LAYOUT_PROBE=PASS", "RUNTIME_OPERATIONS=0"):
        ck(f"build summary: {token}", token in build)
    probe = REPO / "workspace/phase4-tkcore-island/phase3e/build/tk_layout_probe"
    ck("frozen layout probe exists", probe.is_file())
    ck("source snapshot exists", SNAPSHOT.is_file())
    if SNAPSHOT.is_file() and SOURCE.is_file():
        ck("source snapshot matches build source", sha(SNAPSHOT) == sha(SOURCE))

    acc = REPO / "workspace/phase4-tkcore-island/acceptance"
    # Monotone acceptance gate: empty (pre-Phase-3F) OR a complete, valid
    # Phase-3F acceptance.  Partial/witness-contaminated states still fail.
    _gspec = importlib.util.spec_from_file_location(
        "acc_gate", REPO / "kernel/scripts/phase4_tkcore_acceptance_gate.py")
    _gate = importlib.util.module_from_spec(_gspec)
    _gspec.loader.exec_module(_gate)
    ck("final acceptance directory empty or complete Phase-3F",
       _gate.ok(acc), _gate.state(acc))
    srcs = list(ISLAND_SRC.rglob("*.c")) + list(ISLAND_SRC.rglob("*.h")) + [ISLAND_SRC / "Makefile", ISLAND_SRC / "BUILD.bazel"]
    blob = "\n".join(p.read_text(errors="ignore") for p in srcs if p.is_file())
    for bad, label in (("__crc_", "CRC injection"), ("__versions", "__versions editing"),
                       ("__kcrctab", "kcrctab editing"), ("Module.symvers", "fake Module.symvers"),
                       (".incbin", "binary inclusion"), ("objcopy", "ELF patching")):
        ck(f"no {label}", bad not in blob)
    ck("no inline assembly/fake symbol", not re.search(r"\b(?:asm|__asm__)\s*\(", blob))
    ck("no KBUILD_MODPOST_WARN", not re.search(r"^\s*(?!#)\S*KBUILD_MODPOST_WARN\s*[:+]?=", blob, re.M))
    bazel = (ISLAND_SRC / "BUILD.bazel").read_text(errors="ignore")
    code = re.sub(r"#[^\n]*", "", bazel)
    srcblock = re.search(r"srcs\s*=\s*(.*?)\n\s*outs\s*=", code, re.S)
    ck("BUILD srcs parseable", srcblock is not None)
    ck("no stock object/ko linked", srcblock is not None and not re.search(r"oracle|\.ko\b|\.o\b|prebuilt", srcblock.group(1)))
    core = SOURCE.read_text(errors="ignore") if SOURCE.is_file() else ""
    ck("source uses exact topology object", "cpu_topology[cpu].cluster_id" in core)
    ck("source uses possible CPU enumeration", core.count("for_each_possible_cpu(cpu)") == 2)
    ck("source contains no affinity mutation call", not re.search(r"set_cpus_allowed|sched_setaffinity|kthread_bind", core))

    return report()


def report() -> int:
    bad = [x for x in checks if not x[1]]
    for name, ok, detail in checks:
        if not ok:
            print(f"[FAIL] {name}" + (f": {detail}" if detail else ""))
    for name, ok, detail in checks:
        if ok:
            print(f"[OK] {name}" + (f": {detail}" if detail else ""))
    print(f"\n{len(checks) - len(bad)}/{len(checks)} CHECKS PASSED")
    if bad:
        print("TKCORE_ISLAND_PHASE3E_VERIFICATION_FAILED")
        return 1
    print("TKCORE_ISLAND_PHASE3E_PLATFORM_AFFINITY_CLOSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
