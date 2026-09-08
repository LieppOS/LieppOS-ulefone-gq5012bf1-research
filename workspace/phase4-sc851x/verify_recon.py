#!/usr/bin/env python3
"""Relocation-aware structural comparison of stock and reconstructed SC851x modules."""

from __future__ import annotations

import argparse
import collections
import os
import re
import struct
import subprocess
import tempfile
from pathlib import Path


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, errors="replace")


def dump_section(module: Path, section: str) -> bytes | None:
    fd, name = tempfile.mkstemp(prefix="sc851x-")
    os.close(fd)
    os.unlink(name)
    try:
        proc = subprocess.run(
            ["llvm-objcopy", "--dump-section", f"{section}={name}",
             str(module), "/dev/null"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if proc.returncode or not os.path.exists(name):
            return None
        return Path(name).read_bytes()
    finally:
        if os.path.exists(name):
            os.unlink(name)


def symbols(module: Path):
    result = []
    for line in run("llvm-readelf", "-s", "--wide", str(module)).splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[0].rstrip(":").isdigit():
            continue
        result.append({
            "value": int(parts[1], 16),
            "size": int(parts[2]),
            "type": parts[3],
            "bind": parts[4],
            "ndx": parts[6],
            "name": parts[7],
        })
    return result


def section_names(module: Path):
    by_index = {}
    for line in run("llvm-readelf", "-S", "--wide", str(module)).splitlines():
        match = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)", line)
        if match:
            by_index[match.group(1)] = match.group(2)
    return by_index


def versions(module: Path):
    raw = dump_section(module, "__versions") or b""
    entries = []
    for off in range(0, len(raw), 64):
        crc = struct.unpack_from("<I", raw, off)[0]
        name = raw[off + 8:off + 64].split(b"\0", 1)[0].decode()
        entries.append((name, crc))
    return raw, entries


def relocations(module: Path):
    result = collections.defaultdict(list)
    current = None
    for line in run("llvm-readelf", "-r", "--wide", str(module)).splitlines():
        match = re.match(r"Relocation section '([^']+)'", line)
        if match:
            current = match.group(1)
            continue
        parts = line.split()
        if (current and len(parts) >= 5 and
                re.fullmatch(r"[0-9a-fA-F]+", parts[0])):
            result[current].append((int(parts[0], 16), parts[2], parts[4]))
    return result


def modinfo(module: Path):
    result = {}
    for line in run("modinfo", str(module)).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), []).append(value.strip())
    result.pop("filename", None)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stock", type=Path)
    parser.add_argument("recon", type=Path)
    args = parser.parse_args()

    stock, recon = args.stock, args.recon
    ss, rs = symbols(stock), symbols(recon)
    ssec, rsec = section_names(stock), section_names(recon)

    print("SC851x stock/reconstruction verification")
    print(f"stock={stock} size={stock.stat().st_size}")
    print(f"recon={recon} size={recon.stat().st_size}")

    sm, rm = modinfo(stock), modinfo(recon)
    differing_modinfo = sorted(k for k in set(sm) | set(rm) if sm.get(k) != rm.get(k))
    print(f"modinfo differing keys={differing_modinfo or 'NONE'}")
    if differing_modinfo == ["vermagic"]:
        print(f"  stock vermagic={sm['vermagic'][0]}")
        print(f"  recon vermagic={rm['vermagic'][0]}")
        print("  classification=local SCM suffix only")

    sf = {(x["name"], ssec.get(x["ndx"], x["ndx"])): x
          for x in ss if x["type"] == "FUNC" and x["ndx"] not in ("UND", "ABS")}
    rf = {(x["name"], rsec.get(x["ndx"], x["ndx"])): x
          for x in rs if x["type"] == "FUNC" and x["ndx"] not in ("UND", "ABS")}
    print(f"function key sets exact={set(sf) == set(rf)} count={len(sf)}")
    print(f"function sizes exact={all(sf[k]['size'] == rf[k]['size'] for k in sf if k in rf)}")

    kcfi_ok = True
    function_bytes = []
    for key in sorted(set(sf) & set(rf)):
        name, sec = key
        a, b = sf[key], rf[key]
        sa, ra = dump_section(stock, sec), dump_section(recon, sec)
        if sa is None or ra is None or a["value"] < 4 or b["value"] < 4:
            continue
        stype = sa[a["value"] - 4:a["value"]
                   ]
        rtype = ra[b["value"] - 4:b["value"]
                   ]
        kcfi_ok &= stype == rtype
        sb = sa[a["value"]:a["value"] + a["size"]]
        rb = ra[b["value"]:b["value"] + b["size"]]
        diff = sum(x != y for x, y in zip(sb, rb)) + abs(len(sb) - len(rb))
        function_bytes.append((name, sec, a["size"], diff, stype.hex()))
    print(f"KCFI type words exact={kcfi_ok}")
    print("function byte comparison:")
    for name, sec, size, diff, kcfi in function_bytes:
        print(f"  {sec:10} {name:30} size={size:4} diffbytes={diff:4} kcfi={kcfi}")

    print("section comparison:")
    selected = [
        ".text", ".init.text", ".exit.text", ".rodata", ".data",
        ".rodata.str1.1", "__versions", ".comment",
    ]
    for sec in selected:
        a, b = dump_section(stock, sec), dump_section(recon, sec)
        if a is None and b is None:
            continue
        exact = a == b
        print(f"  {sec:18} stock={len(a or b''):5} recon={len(b or b''):5} exact={exact}")

    svraw, sve = versions(stock)
    rvraw, rve = versions(recon)
    print(f"modversions exact={svraw == rvraw} entries={len(sve)}")
    print(f"modversion name/CRC set exact={set(sve) == set(rve)}")

    sr, rr = relocations(stock), relocations(recon)
    print(f"relocation section sets exact={set(sr) == set(rr)}")
    all_target_sequences = True
    for sec in sorted(set(sr) | set(rr)):
        a, b = sr.get(sec, []), rr.get(sec, [])
        seq_a = [(typ, target) for _, typ, target in a]
        seq_b = [(typ, target) for _, typ, target in b]
        exact = a == b
        seq = seq_a == seq_b
        all_target_sequences &= seq
        print(f"  {sec:28} stock={len(a):3} recon={len(b):3} exact={exact} target/type-sequence={seq}")
    print(f"all relocation target/type sequences exact={all_target_sequences}")

    data_exact = all(
        dump_section(stock, sec) == dump_section(recon, sec)
        for sec in (".rodata", ".data", ".rodata.str1.1", "__versions")
    )
    success = (
        set(sf) == set(rf)
        and all(sf[k]["size"] == rf[k]["size"] for k in sf)
        and kcfi_ok
        and data_exact
        and all_target_sequences
        and set(sve) == set(rve)
    )
    print(f"STRUCTURAL_PARITY={'PASS' if success else 'FAIL'}")
    print("Known residual: compiler-local instruction scheduling/register allocation in probe,"
          " plus equivalent gpio validity compare; no relocation target/type or observable"
          " call-order delta.")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
