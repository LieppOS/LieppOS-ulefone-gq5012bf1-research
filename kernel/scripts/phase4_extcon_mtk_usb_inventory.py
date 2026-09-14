#!/usr/bin/env python3
"""Static inventory for the stock GQ5012BF1 extcon-mtk-usb.ko oracle.

Writes an oracle/ snapshot (Phase 1) plus the Phase 2 TSV inventories:
functions, objects, imports, modversions, exports, relocations and strings.

Offline only: this script never touches a device.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(args: list[str]) -> str:
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=False)
    if p.returncode != 0 and not p.stdout:
        raise RuntimeError(f"{' '.join(args)} -> rc={p.returncode}")
    return p.stdout


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def write_txt(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


# ---------------------------------------------------------------- sections ---
SECTION_RE = re.compile(r"\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+([0-9a-f]{8,16})\s+"
                        r"([0-9a-f]{1,8})\s+([0-9a-f]{1,8})")


def sections(ko: Path) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for line in run(["llvm-readelf", "-SW", str(ko)]).splitlines():
        m = SECTION_RE.search(line)
        if m:
            idx, name, _typ, addr, off, size = m.groups()
            out[int(idx)] = {"name": name, "addr": int(addr, 16),
                             "off": int(off, 16), "size": int(size, 16)}
    return out


def symtab(ko: Path) -> list[dict[str, object]]:
    out = []
    rx = re.compile(r"\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+(\w+)\s+(\w+)\s+(\w+)\s+"
                    r"(\S+)\s+(.+)$")
    for line in run(["llvm-readelf", "-sW", str(ko)]).splitlines():
        m = rx.match(line)
        if not m:
            continue
        value, size, typ, bind, vis, ndx, name = m.groups()
        out.append({"value": int(value, 16), "size": int(size), "type": typ,
                    "bind": bind, "vis": vis, "ndx": ndx, "name": name.strip()})
    return out


def dump_section(ko: Path, name: str, dest: Path) -> bytes:
    dest.unlink(missing_ok=True)
    subprocess.run(["llvm-objcopy", "--dump-section", f"{name}={dest}", str(ko)],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return dest.read_bytes() if dest.exists() else b""


# ------------------------------------------------------------- modversions ---
def parse_versions(data: bytes, stride: int = 64) -> list[tuple[str, str]]:
    """__versions is a zero-padded array of struct modversion_info
    {unsigned long crc; char name[MOD_NAME_LEN]} -- 8 + 56 = 64 bytes on LP64."""
    rows: list[tuple[str, str]] = []
    for off in range(0, len(data) - stride + 1, stride):
        chunk = data[off:off + stride]
        crc = int.from_bytes(chunk[:8], "little")
        name_bytes = chunk[8:]
        nul = name_bytes.find(b"\0")
        name = (name_bytes if nul < 0 else name_bytes[:nul]).decode("ascii", "replace")
        if not name:
            break
        rows.append((name, f"0x{crc:08x}"))
    return rows


# ------------------------------------------------------------------- KCFI ---
KCFI_TYPEID = re.compile(r"^\s*\d+:\s+([0-9a-f]{8,16})\s+\d+\s+\w+\s+WEAK\s+\S+"
                         r"\s+ABS\s+__kcfi_typeid_(\S+)$")


def kcfi_typeids(readelf_sym: str) -> list[tuple[str, str]]:
    """Clang KCFI: every address-taken function / indirect-call target contributes a
    resolved ABS __kcfi_typeid_<fn> typeid.  These 32-bit values are an exact part of
    the stock ABI contract and must match a faithful rebuild."""
    out: list[tuple[str, str]] = []
    for line in readelf_sym.splitlines():
        m = KCFI_TYPEID.match(line)
        if m:
            val, name = m.groups()
            out.append((name, f"0x{int(val, 16):08x}"))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--ko", required=True, type=Path)
    ap.add_argument("--name", default="phase4-extcon-mtk-usb")
    args = ap.parse_args()

    repo: Path = args.repo
    ko: Path = args.ko.resolve()
    if not ko.is_file():
        print(f"FATAL: missing {ko}", file=sys.stderr)
        return 2

    oracle = repo / "workspace" / f"{args.name}" / "oracle"
    outdir = repo / "kernel"
    tmp = oracle / "raw"
    oracle.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)

    stock = oracle / ko.name
    if not stock.exists() or stock.read_bytes() != ko.read_bytes():
        shutil.copyfile(ko, stock)

    sec = sections(stock)
    syms = symtab(stock)
    by_ndx: dict[str, list[dict[str, object]]] = {}
    for s in syms:
        by_ndx.setdefault(str(s["ndx"]), []).append(s)

    # ---- disassembly (relocation aware) ----
    disasm = {}
    for sname in (".text", ".init.text", ".exit.text"):
        disasm[sname] = run(["llvm-objdump", "-dr", f"--section={sname}", str(stock)])
        write_txt(oracle / f"disasm-{sname.replace('.', '')}.txt", disasm[sname])

    write_txt(oracle / "sections.txt", run(["llvm-readelf", "-SW", str(stock)]))
    write_txt(oracle / "symbols.txt", run(["llvm-readelf", "-sW", str(stock)]))
    write_txt(oracle / "relocations.txt",
              run(["llvm-readelf", "-rW", str(stock)]))
    write_txt(oracle / "modinfo.txt",
              run(["llvm-readelf", "-p", ".modinfo", str(stock)]))
    (oracle / "strings-all.txt").write_text(
        subprocess.run(["strings", "-a", "-t", "x", str(stock)],
                       text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL, check=True).stdout)

    text_bin = dump_section(stock, ".text", tmp / ".text.bin")
    (tmp / ".init.text.bin").write_bytes(dump_section(stock, ".init.text", tmp / "i.bin"))
    (tmp / ".exit.text.bin").write_bytes(dump_section(stock, ".exit.text", tmp / "e.bin"))
    ver = dump_section(stock, "__versions", tmp / "__versions.bin")
    write_txt(oracle / "build-id-notes.txt",
              run(["llvm-readelf", "-n", str(stock)]))

    # ---- function inventory (all functions, not only uSmart ones) ----
    funcs: list[list[object]] = []
    for s in syms:
        if s["type"] == "FUNC" and isinstance(s["ndx"], str) and \
                s["ndx"].isdigit() and int(s["ndx"]) in sec:
            funcs.append([s["name"], sec[int(s["ndx"])]["name"],
                          f"0x{s['value']:x}", s["size"],
                          hashlib.sha256(bytes(
                              text_bin[s["value"]:s["value"] + max(int(s["size"]), 1)]
                          )).hexdigest()[:16] if sec[int(s["ndx"])]["name"] == ".text" else "-"])
    funcs.sort(key=lambda r: (str(r[1]), str(r[0])))
    write_tsv(outdir / f"{args.name}-functions.tsv",
              ["name", "section", "offset", "size", "body_sha256_16"], funcs)

    # ---- object inventory (all non-special sections + per-section symbol count) ----
    obj_rows = []
    for idx in sorted(sec):
        s = sec[idx]
        obj_rows.append([s["name"], f"0x{s['addr']:x}", f"0x{s['off']:x}",
                         s["size"], len(by_ndx.get(str(idx), []))])
    write_tsv(outdir / f"{args.name}-objects.tsv",
              ["section", "address", "raw_offset", "size", "symbol_count"], obj_rows)

    # ---- relocations ----
    rel_rx = re.compile(r"^([0-9a-f]{8,16})\s+([0-9a-f]{8,16})\s+(R_\S+)\s+"
                       r"([0-9a-f]{8,16})\s+(\S+)(?:\s+\+\s+(\S+))?")
    rel_rows: list[list[object]] = []
    section = ""
    for line in (oracle / "relocations.txt").read_text().splitlines():
        sm = re.match(r"Relocation section '(\S+)'", line)
        if sm:
            section = sm.group(1)
            continue
        m = rel_rx.match(line.strip())
        if m and section:
            off, _info, typ, _symval, sym, addend = m.groups()
            rel_rows.append([section, off, typ, sym, addend or "0"])
    write_tsv(outdir / f"{args.name}-relocations.tsv",
              ["section", "offset", "type", "symbol", "addend"], rel_rows)

    # ---- imports (undefined UND symbols), exports (.gnu.ksymbol*) ----
    imports = sorted({s["name"] for s in syms if s["ndx"] == "UND" and s["name"] != ""})
    write_tsv(outdir / f"{args.name}-imports.tsv", ["index", "symbol", "source"],
              [[i + 1, n, "UND"] for i, n in enumerate(imports)])

    exports: list[list[object]] = []
    kver = ""
    mi = (oracle / "modinfo.txt").read_text()
    for line in mi.splitlines():
        if line.strip().startswith("vermagic="):
            kver = line.split("=", 1)[1].strip()
    names = {s["name"] for s in sec.values()}
    for target in (".gnu.ksymbol", "__ksymtab", "__ksymtab_strings", "__ksymtab_gpl"):
        if target in names:
            pass
    ksymtab = [s for s in syms if s["type"] == "OBJ" and s["ndx"] != "UND"
               and str(s["name"]).startswith(("__kstrtab", "__ksymtab", "__kcrco"))]
    real_exports = sorted({s["name"].removeprefix("__kstrtab_").removeprefix("__ksymtab_")
                           for s in ksymtab if s["name"].startswith(("__kstrtab_", "__ksymtab_"))})
    write_tsv(outdir / f"{args.name}-exports.tsv",
              ["index", "symbol", "provenance"],
              [[i + 1, n, "ksymtab"] for i, n in enumerate(real_exports)])

    # ---- modversions ----
    vers = parse_versions(ver)
    write_tsv(outdir / f"{args.name}-modversions.tsv", ["symbol", "crc"],
              [[n, c] for n, c in vers])

    kcfi_rows: list[list[object]] = [[n, t] for n, t in kcfi_typeids(
        (oracle / "symbols.txt").read_text())]
    write_tsv(outdir / f"{args.name}-kcfi.tsv",
              ["function", "typeid"], kcfi_rows)

    # ---- strings with file offsets ----
    str_rows = []
    for line in (oracle / "strings-all.txt").read_text().splitlines():
        m = re.match(r"\s*([0-9a-f]+)\s+(.*\S)\s*$", line)
        if m:
            str_rows.append([int(m.group(1), 16), m.group(2)])
    write_tsv(outdir / f"{args.name}-strings.tsv", ["file_offset", "string"], str_rows)

    # ---- oracle notes ----
    modinfo = {}
    for line in mi.splitlines():
        line = re.sub(r"^\s*\[\s*[0-9a-f]+\]\s*", "", line)
        if "=" in line:
            k, v = line.split("=", 1)
            modinfo.setdefault(k.strip(), []).append(v.strip())
    notes = [f"stock_sha256\t{sha256(stock)}", f"stock_size\t{stock.stat().st_size}",
             f"stock_path\t{ko}"]
    for k in ("name", "vermagic", "description", "author", "license", "depends",
              "import_from", "srcversion", "staging", "retpoline", "intree",
              "alias", "softdep", "fwpath", "soft_dep"):
        for v in modinfo.get(k, []):
            notes.append(f"{k}\t{v}")
    notes.append(f"func_count\t{len(funcs)}")
    notes.append(f"import_count\t{len(imports)}")
    notes.append(f"export_count\t{len(real_exports)}")
    notes.append(f"modversion_count\t{len(vers)}")
    notes.append(f"kcfi_typeid_count\t{len(kcfi_rows)}")
    notes.append(f"reloc_count\t{len(rel_rows)}")
    notes.append(f"section_count\t{len(sec)}")
    write_txt(oracle / "notes.txt", "\n".join(notes))

    sums = []
    for p in sorted(oracle.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS":
            sums.append(f"{sha256(p)}  {p.relative_to(oracle)}")
    write_txt(oracle / "SHA256SUMS", "\n".join(sums))

    print(f"oracle\t{oracle}")
    print(f"func_count\t{len(funcs)}")
    print(f"import_count\t{len(imports)}")
    print(f"export_count\t{len(real_exports)}")
    print(f"modversion_count\t{len(vers)}")
    print(f"kcfi_typeid_count\t{len(kcfi_rows)}")
    print(f"reloc_count\t{len(rel_rows)}")
    print("exports\t" + ",".join(real_exports) if real_exports else "exports\t(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
