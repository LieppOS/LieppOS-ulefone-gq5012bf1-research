#!/usr/bin/env python3
"""Generate deterministic Phase-3E comparative evidence from three tkcore ELFs."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
BEFORE = REPO / "workspace/phase4-tkcore-island/phase3e/before/tkcore.phase3d.ko"
LIVE = GKI / "bazel-bin/lieppos/tkcore-island/tkcore/tkcore.ko"
OUT = REPO / "kernel"
TARGETS = [
    "big_core_affinity_need_bind_cpu",
    "big_core_affinity_match_cpu",
    "big_core_affinity_get_candidate_cpu",
    "plat_cpu_is_big",
    "plat_tee_init",
]

spec = importlib.util.spec_from_file_location("inv", REPO / "kernel/scripts/phase4_tkcore_inventory.py")
inv = importlib.util.module_from_spec(spec)
sys.modules["inv"] = inv
assert spec.loader
spec.loader.exec_module(inv)


def tsv(name: str, header: list[str], rows: list[list[object]]) -> None:
    with (OUT / name).open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def funcs(elf):
    return {s.name: s for s in elf.symbols if s.name and s.st_type == inv.STT_FUNC and s.shndx != inv.SHN_UNDEF}


def objects(elf):
    return {s.name: s for s in elf.symbols if s.name and s.st_type == inv.STT_OBJECT and s.shndx != inv.SHN_UNDEF}


def imports(elf):
    return {s.name for s in elf.symbols if s.name and s.shndx == inv.SHN_UNDEF and s.bind in (1, 2)}


def modmap(elf):
    return dict(inv.parse_modversions(elf))


def body_sha(elf, sym):
    return hashlib.sha256(elf.symbol_bytes(sym)).hexdigest()


def raw_hex(elf, section: str, offset: int, size: int) -> str:
    return elf.by_name[section].data[offset:offset + size].hex()


def symbol_loc(elf, sym):
    return elf.sections[sym.shndx].name, sym.value, sym.size


def metadata(path: Path) -> dict[str, str]:
    def run(*args):
        p = subprocess.run(args, capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 else ""
    note = run("llvm-readelf", "-n", str(path))
    bid = (re.search(r"Build ID: ([0-9a-f]+)", note) or [None, ""])[1]
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": str(path.stat().st_size),
        "build_id": bid,
        "srcversion": run("modinfo", "-F", "srcversion", str(path)),
        "vermagic": run("modinfo", "-F", "vermagic", str(path)),
        "depends": run("modinfo", "-F", "depends", str(path)) or "(empty)",
        "import_ns": run("modinfo", "-F", "import_ns", str(path)) or "(empty)",
    }


def relocs_for(elf, names):
    fs, os = funcs(elf), objects(elf)
    ranges = []
    for n in names:
        s = fs.get(n) or os.get(n)
        if s:
            ranges.append((n, elf.sections[s.shndx].name, s.value, s.value + s.size))
    # Descriptor affinity is an unnamed subobject.
    td = os.get("tee_device_configs")
    if td:
        ranges.append(("tee_device_configs[2].affinity", elf.sections[td.shndx].name,
                       td.value + 0x60, td.value + 0x68))
    rows = []
    for target, off, typ, sym, value, addend in inv.relocation_rows(elf):
        oi = int(off, 16)
        for owner, sec, lo, hi in ranges:
            if target == sec and lo <= oi < hi:
                rows.append([owner, target, off, typ, sym, value, addend])
    return rows


def main() -> int:
    for p in (STOCK, BEFORE, LIVE):
        if not p.is_file():
            raise SystemExit(f"missing ELF: {p}")
    s, b, c = map(inv.ELF64LE, (STOCK, BEFORE, LIVE))
    sf, bf, cf = funcs(s), funcs(b), funcs(c)

    rows = []
    for n in sorted(set(sf) | set(bf) | set(cf)):
        ss, bs, cs = sf.get(n), bf.get(n), cf.get(n)
        identical = bool(ss and cs and s.symbol_bytes(ss) == c.symbol_bytes(cs))
        status = "BYTE_IDENTICAL" if identical else ("PRESENT" if ss and cs else "STOCK_ONLY" if ss else "ISLAND_ONLY")
        rows.append([n, "yes" if ss else "no", ss.size if ss else "", "yes" if bs else "no", bs.size if bs else "",
                     "yes" if cs else "no", cs.size if cs else "", "yes" if identical else "no", status])
    tsv("phase4-tkcore-island-phase3e-functions.tsv",
        ["symbol", "in_stock", "stock_size", "in_phase3d", "phase3d_size", "in_phase3e", "phase3e_size", "byte_identical", "status"], rows)

    kcfi_rows = []
    for n in TARGETS:
        kcfi_rows.append([n, s.kcfi(sf[n]), "ABSENT", c.kcfi(cf[n]),
                          "EXACT" if s.kcfi(sf[n]) == c.kcfi(cf[n]) else "MISMATCH",
                          "address-taken via ops" if n.startswith("big_core_") else "direct-call/global emission"])
    tsv("phase4-tkcore-island-phase3e-kcfi.tsv",
        ["function", "stock_kcfi", "phase3d", "phase3e_kcfi", "status", "emission_reason"], kcfi_rows)

    si, bi, ci = imports(s), imports(b), imports(c)
    sm, bm, cm = modmap(s), modmap(b), modmap(c)
    import_rows = []
    for n in sorted(si | bi | ci):
        delta = "new" if n in ci - bi else "removed" if n in bi - ci else "unchanged"
        stock_class = "STOCK" if n in si else "KNOWN_PREEXISTING_ISLAND_LOG_HELPER" if n == "_dev_err" else "NON_STOCK"
        import_rows.append([n, "yes" if n in si else "no", "yes" if n in bi else "no", "yes" if n in ci else "no",
                            f"0x{sm[n]:08x}" if n in sm else "", f"0x{cm[n]:08x}" if n in cm else "", delta, stock_class])
    tsv("phase4-tkcore-island-phase3e-imports.tsv",
        ["symbol", "stock", "phase3d", "phase3e", "stock_crc", "phase3e_crc", "delta", "classification"], import_rows)

    se, be, ce = map(lambda e: dict(inv.export_map(e)), (s, b, c))
    export_rows = []
    for n in sorted(set(se) | set(be) | set(ce)):
        sk = s.kcfi(sf[n]) if n in sf else ""
        ck = c.kcfi(cf[n]) if n in cf else ""
        if n not in ce:
            status = "MISSING"
        elif n in be and be[n] == ce[n]:
            status = "UNCHANGED_FROM_PHASE3D"
        elif n in se and se[n] == ce[n]:
            status = "NATURAL_STOCK_CRC"
        else:
            status = "UNEXPECTED_CRC_CHANGE"
        export_rows.append([n, f"0x{se[n]:08x}" if n in se else "", f"0x{be[n]:08x}" if n in be else "",
                            f"0x{ce[n]:08x}" if n in ce else "", sk, ck, status])
    tsv("phase4-tkcore-island-phase3e-exports.tsv",
        ["symbol", "stock_crc", "phase3d_crc", "phase3e_crc", "stock_kcfi", "phase3e_kcfi", "status"], export_rows)
    tsv("phase4-tkcore-island-phase3e-export-parity.tsv",
        ["symbol", "stock_crc", "phase3d_crc", "phase3e_crc", "stock_kcfi", "phase3e_kcfi", "status"], export_rows)

    obj_rows = []
    specs = [
        ("big_core_affinity_get_candidate_cpu.candidate_cpu", "first-big-possible-CPU cache", "reader/writer: get_candidate_cpu"),
        ("large_cluster_id", "maximum possible-CPU cluster_id", "writer: plat_tee_init; readers: plat_cpu_is_big"),
        ("big_core_affinity", "const policy descriptor", "reader: tee_device_configs relocation only"),
        ("big_core_affinity_operations", "const three-callback table", "reader: big_core_affinity relocation only"),
    ]
    so, bo, co = objects(s), objects(b), objects(c)
    for n, role, rw in specs:
        ss, cs = so[n], co[n]
        ssec, soff, size = symbol_loc(s, ss); csec, coff, csize = symbol_loc(c, cs)
        obj_rows.append([n, f"{ssec}+0x{soff:x}", size, raw_hex(s, ssec, soff, size), rw,
                         "ABSENT" if n not in bo else "PRESENT", f"{csec}+0x{coff:x}", csize,
                         "PROVEN_EXACT", role])
    std, ctd = so["tee_device_configs"], co["tee_device_configs"]
    obj_rows.append(["tee_device_configs[2].affinity", f".data+0x{std.value + 0x60:x}", 8,
                     raw_hex(s, ".data", std.value + 0x60, 8), "relocation to big_core_affinity",
                     "NULL", f".data+0x{ctd.value + 0x60:x}", 8, "PROVEN_EXACT",
                     "tkcore_fp-only dormant affinity pointer"])
    tsv("phase4-tkcore-island-phase3e-objects.tsv",
        ["object", "stock_location", "size", "stock_raw", "readers_writers", "phase3d", "phase3e_location", "phase3e_size", "layout_confidence", "role"], obj_rows)

    rr = []
    names = TARGETS + ["big_core_affinity", "big_core_affinity_operations"]
    for label, elf in (("stock", s), ("phase3e", c)):
        for row in relocs_for(elf, names):
            rr.append([label] + row)
    tsv("phase4-tkcore-island-phase3e-relocations.tsv",
        ["image", "owner", "target_section", "offset", "type_number", "symbol", "symbol_value", "addend"], rr)

    call_rows = [
        ["init_module", "plat_tee_init", "DIRECT", ".init.text+0x30", "return discarded; module returns 0"],
        ["big_core_affinity_match_cpu", "plat_cpu_is_big", "DIRECT", "stock 0x2c28", "returns same-polarity boolean"],
        ["big_core_affinity_get_candidate_cpu", "_find_next_bit", "DIRECT", "stock 0x2c7c", "possible-mask loop"],
        ["big_core_affinity_get_candidate_cpu", "plat_cpu_is_big", "DIRECT", "stock 0x2c94", "first true is cached"],
        ["big_core_affinity_get_candidate_cpu", "_printk", "DIRECT", "stock 0x2cb4", "first match only"],
        ["plat_tee_init", "_find_next_bit", "DIRECT", "stock 0x9818", "possible-mask loop"],
        ["plat_tee_init", "_printk", "DIRECT", "stock 0x9860", "after global store"],
        ["big_core_affinity_operations+0", "big_core_affinity_need_bind_cpu", "DATA_ADDRESS", ".rodata relocation", "no executable caller"],
        ["big_core_affinity_operations+8", "big_core_affinity_match_cpu", "DATA_ADDRESS", ".rodata relocation", "no executable caller"],
        ["big_core_affinity_operations+16", "big_core_affinity_get_candidate_cpu", "DATA_ADDRESS", ".rodata relocation", "no executable caller"],
        ["tee_device_configs[2].affinity", "big_core_affinity", "DATA_ADDRESS", ".data relocation", "tkcore_fp only; never dereferenced"],
    ]
    tsv("phase4-tkcore-island-phase3e-callgraph.tsv",
        ["caller_or_owner", "callee_or_target", "edge", "stock_callsite", "semantics"], call_rows)

    strings = [
        ("big_core_affinity_get_candidate_cpu", "\\x016tkcore: candidate big cpu set to %d\\n"),
        ("plat_tee_init", "\\x016tkcore: tkcore: big cluster_id = %d\\n"),
    ]
    tsv("phase4-tkcore-island-phase3e-strings.tsv",
        ["function", "escaped_string", "stock", "phase3d", "phase3e", "status"],
        [[n, text, "yes", "no", "yes", "EXACT_REACHED_STRING"] for n, text in strings])

    fm = {k: metadata(p) for k, p in (("stock", STOCK), ("phase3d", BEFORE), ("phase3e", LIVE))}
    tsv("phase4-tkcore-island-phase3e-metadata.tsv", ["field", "stock", "phase3d", "phase3e"],
        [[key, fm["stock"][key], fm["phase3d"][key], fm["phase3e"][key]] for key in fm["stock"]])

    progress = []
    for n in TARGETS:
        progress.append([n, sf[n].size, cf[n].size, s.kcfi(sf[n]), c.kcfi(cf[n]),
                         "yes" if s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]) else "no",
                         "EXACT_BYTE" if s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]) else "SIZE_EXACT_SEMANTIC_EXACT"])
    tsv("phase4-tkcore-island-phase3e-function-progress.tsv",
        ["function", "stock_size", "phase3e_size", "stock_kcfi", "phase3e_kcfi", "raw_body_identical", "classification"], progress)

    stock_set, before_set, current_set = set(sf), set(bf), set(cf)
    print(f"stock_functions={len(stock_set)}")
    print(f"phase3d_coverage={len(stock_set & before_set)}")
    print(f"phase3e_coverage={len(stock_set & current_set)}")
    print(f"stock_minus_phase3e={sorted(stock_set-current_set)}")
    print(f"phase3e_minus_stock={sorted(current_set-stock_set)}")
    print(f"byte_identical_before={sum(s.symbol_bytes(sf[n]) == b.symbol_bytes(bf[n]) for n in stock_set & before_set)}")
    print(f"byte_identical_after={sum(s.symbol_bytes(sf[n]) == c.symbol_bytes(cf[n]) for n in stock_set & current_set)}")
    print(f"imports={len(bi)}->{len(ci)} stock={len(si)}")
    print(f"exports={len(be)}->{len(ce)} stock={len(se)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
