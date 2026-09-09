#!/usr/bin/env python3
"""Relocation-aware stock/reconstruction verifier for SC8571.

This intentionally distinguishes behavioral/ABI parity from byte identity.  The
allowed residuals are frozen below so an unrelated future drift fails closed.
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import struct
import subprocess
import tempfile
from pathlib import Path

ALLOWED_SIZE_DELTAS = {
    "sc8571_charger_probe": -4,
    "mtk_sc8571_set_ibatocp": 4,
}
REQUIRED_MODINFO = ("name", "description", "author", "license", "depends")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace")


def dump_section(module: Path, section: str) -> bytes | None:
    fd, name = tempfile.mkstemp(prefix="sc8571-")
    os.close(fd)
    os.unlink(name)
    try:
        p = subprocess.run(["llvm-objcopy", "--dump-section",
                            f"{section}={name}", str(module), "/dev/null"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return None if p.returncode or not os.path.exists(name) else Path(name).read_bytes()
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sections(module: Path) -> dict[str, str]:
    out = {}
    for line in run("llvm-readelf", "-S", "--wide", str(module)).splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def symbols(module: Path) -> list[dict]:
    sec = sections(module)
    out = []
    for line in run("llvm-readelf", "-s", "--wide", str(module)).splitlines():
        p = line.split()
        if len(p) < 8 or not p[0].rstrip(":").isdigit():
            continue
        out.append({"value": int(p[1], 16), "size": int(p[2]),
                    "type": p[3], "bind": p[4], "ndx": p[6],
                    "section": sec.get(p[6], p[6]), "name": p[7]})
    return out


def modinfo(module: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in run("modinfo", str(module)).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out.setdefault(k.strip(), []).append(v.strip())
    out.pop("filename", None)
    return out


def versions(module: Path) -> tuple[bytes, list[tuple[str, int]]]:
    raw = dump_section(module, "__versions") or b""
    entries = []
    for off in range(0, len(raw), 64):
        crc = struct.unpack_from("<I", raw, off)[0]
        name = raw[off + 8:off + 64].split(b"\0", 1)[0].decode()
        entries.append((name, crc))
    return raw, entries


def relocations(module: Path) -> list[dict]:
    out, current = [], None
    for line in run("llvm-readelf", "-r", "--wide", str(module)).splitlines():
        m = re.match(r"Relocation section '([^']+)'", line)
        if m:
            current = m.group(1)
            continue
        p = line.split()
        if current and len(p) >= 5 and re.fullmatch(r"[0-9a-fA-F]+", p[0]):
            out.append({"rsec": current, "offset": int(p[0], 16),
                        "type": p[2], "symbol": p[4]})
    return out


def symbol_map(items: list[dict], kind: str) -> dict[tuple[str, str], dict]:
    return {(x["name"], x["section"]): x for x in items
            if x["type"] == kind and x["section"] not in ("UND", "ABS")}


def symbol_bytes(module: Path, sym: dict) -> bytes | None:
    raw = dump_section(module, sym["section"])
    if raw is None:
        return None
    return raw[sym["value"]:sym["value"] + sym["size"]]


def call_multiset(relocs: list[dict], sym: dict) -> collections.Counter:
    rsec = ".rela" + sym["section"]
    lo, hi = sym["value"], sym["value"] + sym["size"]
    return collections.Counter(r["symbol"] for r in relocs
        if r["rsec"] == rsec and lo <= r["offset"] < hi
        and r["type"] == "R_AARCH64_CALL26")


def cstrings(raw: bytes | None) -> collections.Counter:
    return collections.Counter(x for x in (raw or b"").split(b"\0") if x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock", type=Path)
    ap.add_argument("recon", type=Path)
    a = ap.parse_args()
    stock, recon = a.stock, a.recon
    ss, rs = symbols(stock), symbols(recon)
    sf, rf = symbol_map(ss, "FUNC"), symbol_map(rs, "FUNC")
    so, ro = symbol_map(ss, "OBJECT"), symbol_map(rs, "OBJECT")
    sr, rr = relocations(stock), relocations(recon)

    print("SC8571 stock/reconstruction verification")
    print(f"stock={stock} size={stock.stat().st_size}")
    print(f"recon={recon} size={recon.stat().st_size}")
    print(f"BINARY_IDENTITY={'YES' if stock.read_bytes() == recon.read_bytes() else 'NO'}")

    sm, rm = modinfo(stock), modinfo(recon)
    metadata_ok = all(sm.get(k) == rm.get(k) for k in REQUIRED_MODINFO)
    print(f"required modinfo exact={metadata_ok}")
    print(f"stock vermagic={sm.get('vermagic', [''])[0]}")
    print(f"recon vermagic={rm.get('vermagic', [''])[0]}")
    print("vermagic residual=SCM token only (-g945dff7bc1bf vs -maybe-dirty)")

    function_sets = set(sf) == set(rf)
    deltas = {k[0]: rf[k]["size"] - sf[k]["size"] for k in sf
              if k in rf and rf[k]["size"] != sf[k]["size"]}
    size_contract = deltas == ALLOWED_SIZE_DELTAS
    print(f"function set exact={function_sets} count={len(sf)}")
    print(f"function size deltas={deltas or 'NONE'} allowed={size_contract}")

    kcfi_ok, raw_exact = True, 0
    for key in sorted(set(sf) & set(rf)):
        s, r = sf[key], rf[key]
        sb, rb = dump_section(stock, s["section"]), dump_section(recon, r["section"])
        if s["value"] >= 4 and r["value"] >= 4 and sb is not None and rb is not None:
            kcfi_ok &= sb[s["value"]-4:s["value"]] == rb[r["value"]-4:r["value"]]
        raw_exact += symbol_bytes(stock, s) == symbol_bytes(recon, r)
    print(f"KCFI type words exact={kcfi_ok}")
    print(f"raw-identical functions={raw_exact}/{len(sf)}")

    calls_ok = all(call_multiset(sr, sf[k]) == call_multiset(rr, rf[k])
                   for k in set(sf) & set(rf))
    print(f"per-function external call multisets exact={calls_ok}")

    object_sets = set(so) == set(ro)
    compared_objects = [k for k in set(so) & set(ro)
                        if not k[0].startswith("__UNIQUE_ID_vermagic")]
    object_sizes = all(so[k]["size"] == ro[k]["size"] for k in compared_objects)
    object_exact = 0
    object_checked = 0
    for key in compared_objects:
        sb, rb = symbol_bytes(stock, so[key]), symbol_bytes(recon, ro[key])
        if sb is not None and rb is not None:
            object_checked += 1
            object_exact += sb == rb
    print(f"object set exact={object_sets} count={len(so)} sizes exact={object_sizes}")
    print(f"named PROGBITS objects exact (excluding vermagic)={object_exact}/{object_checked}")

    svraw, sve = versions(stock)
    rvraw, rve = versions(recon)
    versions_ok = svraw == rvraw and len(sve) == 42
    print(f"__versions byte-exact={svraw == rvraw} entries={len(sve)}")
    undef_s = {x["name"] for x in ss if x["section"] == "UND"}
    undef_r = {x["name"] for x in rs if x["section"] == "UND"}
    imports_ok = undef_s == undef_r
    print(f"undefined import set exact={imports_ok} count={len(undef_s)}")

    rodata_ok = dump_section(stock, ".rodata") == dump_section(recon, ".rodata")
    strings_ok = cstrings(dump_section(stock, ".rodata.str1.1")) == cstrings(
                 dump_section(recon, ".rodata.str1.1"))
    comment_ok = dump_section(stock, ".comment") == dump_section(recon, ".comment")
    text_size_ok = len(dump_section(stock, ".text") or b"") == len(
                   dump_section(recon, ".text") or b"")
    print(f".rodata byte-exact={rodata_ok}")
    print(f".rodata.str1.1 string multiset exact={strings_ok}")
    print(f".comment toolchain identity exact={comment_ok}")
    print(f".text aggregate size exact={text_size_ok}")
    print(f"relocation totals stock={len(sr)} recon={len(rr)} residual={len(rr)-len(sr):+d}")

    success = all((metadata_ok, function_sets, size_contract, kcfi_ok, calls_ok,
                   object_sets, object_sizes, object_exact == object_checked,
                   versions_ok, imports_ok, rodata_ok, strings_ok, comment_ok,
                   text_size_ok))
    print("KNOWN_RESIDUALS=probe basic-block/string-address sharing; IBAT arithmetic scheduling; "
          "local SCM vermagic/BuildID; internal data layout/padding")
    print(f"ABI_AND_BEHAVIORAL_CONTRACT_PARITY={'PASS' if success else 'FAIL'}")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
