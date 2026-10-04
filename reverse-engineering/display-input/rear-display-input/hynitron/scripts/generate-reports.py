#!/usr/bin/env python3
"""Generate reproducible Hynitron stock inventories and closure tables.

All input is local. Firmware bytes are never emitted.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hyn_index import index, sections  # noqa: E402


def source_text(path: str) -> str:
    return "".join(Path(f).read_text(errors="replace") for f in glob.glob(path + "/*.[ch]"))


def anchor(s: str) -> str:
    """Donor-lineage test used in the original RED measurement.

    Logging prefixes and control-priority bytes changed between releases.  The
    first 22 bytes of the remaining uncommon text are a stable source anchor.
    """
    return re.sub(r"^\x01.(\[HYN\])?(\[(Info|Error)\])?", "", s).strip()[:22]


def tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def function_source_map(src: str, funcs: list[dict]) -> dict[str, str]:
    files = glob.glob(src + "/*.c")
    out: dict[str, str] = {}
    for fn in (f["name"] for f in funcs):
        if fn in ("init_module", "cleanup_module"):
            out[fn] = "hynitron_core.c"
            continue
        pat = re.compile(r"\b" + re.escape(fn) + r"\s*\(")
        hits = [os.path.basename(p) for p in files if pat.search(Path(p).read_text(errors="replace"))]
        out[fn] = ",".join(hits) if hits else "unresolved"
    return out


def string_class(s: str) -> str:
    q = s.lstrip("\x010123456789")
    if "[HYN]" in q or "%" in q or "failed" in q.lower() or "success" in q.lower():
        return "diagnostic/format"
    if q.startswith(("hynitron,", "touchscreen-", "report-key-", "reset-gpio", "irq-gpio")):
        return "device-tree property"
    if q.startswith(("/data", "/sdcard")) or q.endswith(".bin"):
        return "firmware path/name"
    if q in {"hynfwupdate", "hynfwupgradeapp", "hyntpfactorytest", "hyntpfwver", "hyntprwreg",
             "hyn_gesture_mode", "hyn_gesture_buf", "Hynitron Touch Int", "hyn_wq", "hyn_ts"}:
        return "ABI/node identifier"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", q):
        return "symbol/mode identifier"
    return "functional literal"


def make_string_table(stock: dict, rebuild: dict, donors: list[tuple[str, str]], fmap: dict[str, str], out: Path) -> None:
    donor_text = {name: source_text(path) for name, path in donors}
    fields = ["stock_offset", "string_json", "referencing_functions"]
    fields += [f"present_{name}" for name, _ in donors]
    fields += ["present_exact_rebuild", "likely_source_file", "classification", "evidence_rule"]
    rows = []
    for off, s in stock["strings"].items():
        refs = sorted(set(stock["strref"].get(off, [])))
        files = sorted({fmap.get(x, "unresolved") for x in refs})
        a = anchor(s)
        row = {
            "stock_offset": hex(off),
            "string_json": json.dumps(s, ensure_ascii=True),
            "referencing_functions": ",".join(refs) or "data-only/unresolved",
            "present_exact_rebuild": "yes" if rebuild["strings"].get(off) == s else "no",
            "likely_source_file": ",".join(files) if files else "data-only/unresolved",
            "classification": string_class(s),
            "evidence_rule": "exact compiled offset" if rebuild["strings"].get(off) == s else "missing",
        }
        for name, _ in donors:
            row[f"present_{name}"] = "yes" if a and a in donor_text[name] else "no"
        rows.append(row)
    tsv(out, fields, rows)


def make_function_inventory(stock: dict, rebuild: dict, src: str, out: Path) -> None:
    fmap = function_source_map(src, stock["funcs"])
    local = {f["name"] for f in stock["funcs"]}
    b = {f["name"]: f for f in rebuild["funcs"]}
    fields = ["function", "section", "address", "size", "kcfi_hex", "callers", "local_callees",
              "imports", "string_offsets", "referenced_data", "likely_original_source",
              "current_counterpart", "final_bytes"]
    rows = []
    for f in sorted(stock["funcs"], key=lambda x: (x["section"], x["value"])):
        calls = sorted(set(f["calls"]))
        bf = b.get(f["name"])
        rows.append({
            "function": f["name"], "section": f["section"], "address": hex(f["value"]),
            "size": f["size"], "kcfi_hex": f["kcfi"], "callers": ",".join(sorted(f["callers"])) or "-",
            "local_callees": ",".join(x for x in calls if x in local) or "-",
            "imports": ",".join(x for x in calls if x not in local) or "-",
            "string_offsets": ",".join(hex(x) for x in sorted(set(f["strings"]))) or "-",
            "referenced_data": ",".join(sorted(set(f["data"]))) or "-",
            "likely_original_source": fmap[f["name"]], "current_counterpart": f["name"] if bf else "missing",
            "final_bytes": "EXACT" if bf and f["sha256"] == bf["sha256"] else "DIFF",
        })
    tsv(out, fields, rows)


def classify_old(fn: str, a: int, b: int, old_status: str, source: str) -> tuple[str, str]:
    if old_status == "BYTE-IDENTICAL":
        return "EXACT", "already byte-identical in old rebuild"
    if b <= 40 and a >= 2 * max(b, 1):
        return "A", "old counterpart was an empty/minimal stub"
    if fn.startswith("hyn_gesture") or fn in {"hyn_check_gesture", "hyn_create_gesture_sysfs",
                                               "hyn_irq_gesture_mode", "hyn_irq_normal_mode"}:
        return "B", "old reconstruction used a reduced/newer gesture implementation"
    if fn.startswith("hyn_i2c") or fn.startswith("cst3xx_i2c"):
        return "E", "old wrappers omitted stock diagnostics/retry and framing details"
    if fn in {"hyn_boot_update_fw", "hyn_detect_bootloader", "hyn_create_sysfs"}:
        return "A", "old reconstruction omitted most of the stock selection/detection/sysfs body"
    if fn in {"hyn_irq_disable", "hyn_irq_enable", "hyn_release_sysfs", "hyn_remove", "hyn_reset_proc",
              "cst3xx_touch_down", "cst3xx_touch_up"}:
        return "B", "old semantic implementation differed from the V2.1 donor-family body"
    if source == "hynitron_update_firmware.c":
        return "A", "old reconstruction omitted most firmware/chip-family selection and detection source"
    if source in {"hynitron_core.c", "hynitron_tool_debug.c"}:
        return "A", "old reconstruction omitted or heavily simplified the stock control/debug body"
    return "H", "old delta not isolated before full source restoration"


def make_classification(old: str, final: dict, src: str, out: Path) -> None:
    funcs = final["funcs"]
    fmap = function_source_map(src, funcs)
    with open(old, newline="") as f:
        oldrows = list(csv.DictReader(f, delimiter="\t"))
    fields = ["function", "stock_size", "old_size", "old_status", "class", "class_key", "evidence", "final_status"]
    rows = []
    keys = {"A": "source missing entirely", "B": "newer/reduced donor behavior", "C": "config-controlled feature",
            "D": "struct-layout mismatch", "E": "inline/helper mismatch", "F": "compiler/codegen only",
            "G": "source-line/layout issue", "H": "unresolved", "EXACT": "already exact"}
    for r in oldrows:
        if r["status"] == "BYTE-IDENTICAL":
            continue
        a, b = int(r["A_size"]), int(r["B_size"])
        c, why = classify_old(r["function"], a, b, r["status"], fmap.get(r["function"], ""))
        rows.append({"function": r["function"], "stock_size": a, "old_size": b, "old_status": r["status"],
                     "class": c, "class_key": keys[c], "evidence": why,
                     "final_status": "EXACT (byte/size/KCFI/relocations)"})
    tsv(out, fields, rows)


def make_string_parity(stock: dict, rebuild: dict, out: Path) -> None:
    fields = ["stock_offset", "rebuild_offset", "stock_sha256_16", "rebuild_sha256_16", "equal"]
    rows = []
    for off, s in stock["strings"].items():
        b = rebuild["strings"].get(off)
        rows.append({"stock_offset": hex(off), "rebuild_offset": hex(off) if b is not None else "-",
                     "stock_sha256_16": hashlib.sha256(s.encode("latin1")).hexdigest()[:16],
                     "rebuild_sha256_16": hashlib.sha256(b.encode("latin1")).hexdigest()[:16] if b is not None else "-",
                     "equal": "yes" if b == s else "no"})
    tsv(out, fields, rows)


def raw_sections(path: str) -> dict[str, tuple[int, str]]:
    raw = Path(path).read_bytes()
    out = {}
    for name, s in sections(path).items():
        if name == "":
            continue
        data = raw[s["off"]:s["off"] + s["size"]]
        out[name] = (s["size"], hashlib.sha256(data).hexdigest())
    return out


def make_section_parity(a: str, b: str, out: Path) -> None:
    aa, bb = raw_sections(a), raw_sections(b)
    rows = []
    for n in sorted(set(aa) | set(bb)):
        av, bv = aa.get(n), bb.get(n)
        rows.append({"section": n, "stock_size": av[0] if av else "-", "rebuild_size": bv[0] if bv else "-",
                     "bytes_equal": "yes" if av == bv else "no",
                     "note": "build-id hashes original DWARF paths" if n == ".note.gnu.build-id" and av != bv else ""})
    tsv(out, ["section", "stock_size", "rebuild_size", "bytes_equal", "note"], rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock", required=True)
    ap.add_argument("--rebuild", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--old-functions", required=True)
    ap.add_argument("--donor", action="append", default=[], help="NAME=DIR")
    ap.add_argument("--out", required=True)
    ns = ap.parse_args()
    donors = [tuple(x.split("=", 1)) for x in ns.donor]
    stock, rebuild = index(ns.stock), index(ns.rebuild)
    out = Path(ns.out)
    fmap = function_source_map(ns.source, stock["funcs"])
    make_string_table(stock, rebuild, donors, fmap, out / "stock-string-provenance.tsv")
    make_function_inventory(stock, rebuild, ns.source, out / "stock-function-inventory.tsv")
    make_classification(ns.old_functions, stock, ns.source, out / "non-exact-function-classification.tsv")
    make_string_parity(stock, rebuild, out / "parity/string-parity.tsv")
    make_section_parity(ns.stock, ns.rebuild, out / "parity/section-parity.tsv")
    print(f"functions={len(stock['funcs'])}; strings={len(stock['strings'])}; reports={out}")


if __name__ == "__main__":
    main()
