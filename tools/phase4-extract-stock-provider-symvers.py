#!/usr/bin/env python3
"""Extract the authoritative provider ABI record from stock provider ELFs.

This does NOT invent, guess or patch anything.  It reads the CRCs that the
stock vendor modules themselves publish in their own `__kcrctab` section,
pairs them with the names in `__ksymtab_strings` using the `__ksymtab_<name>`
symbol table entries, and emits kbuild `Module.symvers` lines.

Rationale: a provider's export CRCs are produced by genksyms during the
*provider's* build, against MediaTek vendor headers.  Exact-GKI headers
provably cannot regenerate them (control experiment: MediaTek's verbatim
`void mtk_spi_set_autosuspend_delay(struct spi_device *, int)` yields
0x063a223e under exact GKI but stock spi-mt65xx.ko publishes 0xd3e99558).
Therefore the only honest source for those three CRCs is the stock ELF itself.

Usage:
  phase4-extract-stock-provider-symvers.py \
      --elf spi-mt65xx.ko --sym mt_spi_enable_master_clk \
      --sym mt_spi_disable_master_clk \
      --elf tkcore.ko --sym tee_spi_transfer \
      --out stock-provider.symvers --manifest stock-provider.provenance.json
"""

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys


def sections(blob):
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        off = e_shoff + i * shentsize
        return struct.unpack_from("<IIQQQQIIQQ", blob, off)

    stroff = raw(shstrndx)[4]
    out = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz, lk, inf, al, ent = raw(i)
        end = blob.index(b"\0", stroff + nm)
        out[blob[stroff + nm:end].decode()] = dict(
            index=i, off=off, size=sz, type=ty)
    return out


def symbol_offsets(path, prefix):
    """Map `<prefix><name>` local symbols to (section_name, value)."""
    out = subprocess.run(["readelf", "-sW", path], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[7].startswith(prefix):
            try:
                res[f[7][len(prefix):]] = (int(f[6]), int(f[1], 16))
            except ValueError:
                continue
    return res


def section_name_by_index(path, index):
    out = subprocess.run(["readelf", "-SW", path], capture_output=True,
                         text=True, check=True).stdout
    for line in out.splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)", line)
        if m and int(m.group(1)) == index:
            return m.group(2)
    return None


def extract(path, wanted):
    blob = open(path, "rb").read()
    sec = sections(blob)
    crc_syms = symbol_offsets(path, "__crc_")
    out = {}
    for name in wanted:
        if name not in crc_syms:
            raise SystemExit("%s: no __crc_%s in provider" % (path, name))
        sidx, value = crc_syms[name]
        sname = section_name_by_index(path, sidx)
        # Providers built with EXPORT_SYMBOL_GPL keep their CRCs in
        # __kcrctab_gpl (e.g. stock ffa_v10.ko); plain EXPORT_SYMBOL
        # providers use __kcrctab (e.g. stock tkcore.ko).
        if sname not in ("__kcrctab", "__kcrctab_gpl"):
            raise SystemExit("%s: __crc_%s not in a __kcrctab* section (%s)"
                             % (path, name, sname))
        base = sec[sname]["off"]
        crc, = struct.unpack_from("<I", blob, base + value)
        gpl = sname == "__kcrctab_gpl"
        out[name] = {
            "crc": crc,
            "export": "EXPORT_SYMBOL_GPL" if gpl else "EXPORT_SYMBOL",
            "kcrctab_section": sname,
            "kcrctab_offset": value,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", action="append", required=True)
    ap.add_argument("--sym", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    # Assign each requested symbol to the ELF that actually publishes it.
    lines = []
    manifest = {"method": ("read-only extraction of __kcrctab paired via "
                           "__crc_<symbol> symbol table entries"),
                "providers": {}}
    remaining = list(args.sym)
    for elf in args.elf:
        blob = open(elf, "rb").read()
        have = [s for s in remaining
                if s in symbol_offsets(elf, "__crc_")]
        if not have:
            continue
        data = extract(elf, have)
        modname = os.path.basename(elf)
        if modname.endswith(".ko"):
            modname = modname[:-3]
        manifest["providers"][elf] = {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "size": len(blob),
            "module": modname,
            "symbols": {k: {"crc": "0x%08x" % v["crc"],
                            "export": v["export"],
                            "kcrctab_section": v["kcrctab_section"],
                            "kcrctab_offset": v["kcrctab_offset"]}
                        for k, v in data.items()},
        }
        for name, v in data.items():
            lines.append("0x%08x\t%s\t%s\t%s\t"
                         % (v["crc"], name, modname, v["export"]))
            remaining.remove(name)

    if remaining:
        raise SystemExit("symbols not published by any provider: %s"
                         % ", ".join(remaining))

    with open(args.out, "w") as fh:
        fh.write("\n".join(sorted(lines)) + "\n")
    with open(args.manifest, "w") as fh:
        fh.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print("\n".join(sorted(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
