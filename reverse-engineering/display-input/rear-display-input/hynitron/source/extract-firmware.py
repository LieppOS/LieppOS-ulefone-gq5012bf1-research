#!/usr/bin/env python3
"""Privately regenerate firmware headers from a locally owned stock hynitron.ko.

The proprietary bytes are deliberately not committed.  This tool is offline and
read-only with respect to the stock module.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

IMAGES = {
    "cst8xx_fw": (15419, "0566ea7799d6f8bbce026639d9dbb89f0e629ab533d1d90e4901c81d5611e1d8",
                   "capacitive_hynitron_cst8xx_update.h"),
    "cst816t_fw": (15410, "0d02fde67223c1e7aa6c4ce1d1e522bcbe79d4d58decf1aa79b865cb2e504de3",
                    "capacitive_hynitron_cst816t_update.h"),
}


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} STOCK_HYNITRON.KO")
    ko = Path(sys.argv[1])
    raw = ko.read_bytes()
    sections = {}
    for line in run("llvm-readelf", "-SW", str(ko)).splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
        if m:
            sections[int(m.group(1))] = (m.group(2), int(m.group(3), 16), int(m.group(4), 16))
    symbols = {}
    for line in run("llvm-readelf", "-sW", str(ko)).splitlines():
        p = line.split()
        if len(p) >= 8 and p[0].rstrip(":").isdigit() and p[3] == "OBJECT" and p[6].isdigit():
            symbols[p[7]] = (int(p[1], 16), int(p[2]), int(p[6]))
    outdir = Path(__file__).resolve().parent / "firmware"
    outdir.mkdir(exist_ok=True)
    for symbol, (expected_size, expected_sha, filename) in IMAGES.items():
        value, size, shndx = symbols[symbol]
        secname, fileoff, secsize = sections[shndx]
        if secname != ".data" or size != expected_size or value + size > secsize:
            raise SystemExit(f"unexpected {symbol} placement: {secname}+{value:#x}, size={size}")
        blob = raw[fileoff + value:fileoff + value + size]
        sha = hashlib.sha256(blob).hexdigest()
        if sha != expected_sha:
            raise SystemExit(f"{symbol} SHA-256 mismatch: {sha}")
        lines = ["/* PRIVATE: extracted from stock hynitron.ko; proprietary Hynitron image. Do not publish. */",
                 f"static unsigned char {symbol}[] = {{"]
        for i in range(0, len(blob), 12):
            lines.append("  " + ", ".join(f"0x{x:02x}" for x in blob[i:i + 12]) + ",")
        lines += ["};", ""]
        (outdir / filename).write_text("\n".join(lines))
        print(f"wrote private {filename}: {size} bytes sha256={sha}")


if __name__ == "__main__":
    main()
