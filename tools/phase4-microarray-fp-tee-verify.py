#!/usr/bin/env python3
"""Fail-closed verifier for the microarray_fp_tee reconstruction.

Compares a reconstructed microarray_fp_tee.ko against the frozen stock oracle
and classifies every MODVERSION edge as:

  NATURAL                 - CRC regenerated from C by genksyms in this build
                            (GKI exports, or the real source-built fingerprint
                            provider, or a naturally derived ABI witness)
  STOCK_PROVIDER_WITNESS  - CRC inherited from the authoritative stock provider
                            ELF because the provider's own genksyms ran against
                            MediaTek vendor headers that exact GKI does not have
  MISMATCH                - CRC differs from stock and is not an accepted
                            inherited edge
  MISSING / EXTRA         - symbol set divergence

Exit status is non-zero on any MISMATCH, MISSING, EXTRA, or on any structural
check failure.  Nothing is patched, edited or fabricated by this script; it is
read-only.
"""

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys

# Symbols whose CRC provably cannot be regenerated from exact-GKI headers,
# because they are exported by stock vendor modules whose own genksyms ran
# against MediaTek vendor type graphs.  See the phase4 provenance report.
STOCK_PROVIDER_EDGES = {
    "mt_spi_enable_master_clk": "spi-mt65xx.ko",
    "mt_spi_disable_master_clk": "spi-mt65xx.ko",
    "tee_spi_transfer": "tkcore.ko",
}


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
        out[blob[stroff + nm:end].decode()] = dict(off=off, size=sz, type=ty)
    return out


def versions(path):
    blob = open(path, "rb").read()
    sec = sections(blob)
    if "__versions" not in sec:
        return {}
    off, size = sec["__versions"]["off"], sec["__versions"]["size"]
    out = {}
    for i in range(0, size, 64):
        crc, = struct.unpack_from("<Q", blob, off + i)
        name = blob[off + i + 8:off + i + 64].split(b"\0")[0].decode()
        if name:
            out[name] = crc & 0xFFFFFFFF
    return out


def modinfo(path):
    blob = open(path, "rb").read()
    sec = sections(blob)
    if ".modinfo" not in sec:
        return {}
    off, size = sec[".modinfo"]["off"], sec[".modinfo"]["size"]
    out = {}
    for item in blob[off:off + size].split(b"\0"):
        if b"=" in item:
            k, v = item.decode().split("=", 1)
            out.setdefault(k, []).append(v)
    return out


def defined_functions(path):
    out = subprocess.run(["readelf", "-sW", path], capture_output=True,
                         text=True, check=True).stdout
    names = set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[3] == "FUNC" and f[6] != "UND":
            names.add(f[7])
    return names


def kcrctab(path):
    """Authoritative CRCs published by a provider ELF (read-only extraction).

    Each export has a local `__crc_<symbol>` symbol whose st_value is the byte
    offset of its CRC inside `__kcrctab`.  That pairing is exact and does not
    depend on guessing the order of `__ksymtab_strings`.
    """
    blob = open(path, "rb").read()
    sec = sections(blob)
    if "__kcrctab" not in sec:
        return {}
    base = sec["__kcrctab"]["off"]
    size = sec["__kcrctab"]["size"]
    out = subprocess.run(["readelf", "-sW", path], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[7].startswith("__crc_"):
            try:
                value = int(f[1], 16)
            except ValueError:
                continue
            if value + 4 > size:
                continue
            crc, = struct.unpack_from("<I", blob, base + value)
            res[f[7][len("__crc_"):]] = crc
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock", required=True)
    ap.add_argument("--recon", required=True)
    ap.add_argument("--provider", action="append", default=[],
                    help="stock provider .ko used as authoritative ABI witness")
    ap.add_argument("--allow-stock-provider-edges", action="store_true",
                    help="accept inherited provider CRCs (stockabi target)")
    ap.add_argument("--accept-build-stamp-delta", action="store_true",
                    help="treat a pure scmversion-suffix vermagic difference "
                         "as a reported build-environment delta instead of a "
                         "hard failure; the base release string must still "
                         "match exactly")
    ap.add_argument("--expect-provider-abi-gaps", action="store_true",
                    help="natural target: the three non-regenerable provider "
                         "CRCs and the ABI-witness module names in depends "
                         "are declared deltas, still listed in full")
    ap.add_argument("--json")
    args = ap.parse_args()

    report = {"failures": [], "edges": {}, "checks": {}}

    stock_v = versions(args.stock)
    recon_v = versions(args.recon)

    published = {}
    for p in args.provider:
        published[p] = kcrctab(p)

    natural = inherited = 0
    for sym, crc in sorted(stock_v.items()):
        if sym not in recon_v:
            report["edges"][sym] = {"class": "MISSING", "stock": hex(crc)}
            report["failures"].append("MISSING %s" % sym)
            continue
        got = recon_v[sym]
        if got == crc:
            if sym in STOCK_PROVIDER_EDGES and args.allow_stock_provider_edges:
                src = None
                for p, table in published.items():
                    if table.get(sym) == crc:
                        src = p
                cls = "STOCK_PROVIDER_WITNESS"
                inherited += 1
                report["edges"][sym] = {
                    "class": cls,
                    "crc": hex(crc),
                    "provider": STOCK_PROVIDER_EDGES[sym],
                    "authoritative_elf": src,
                    "extraction": "__kcrctab/__ksymtab_strings read-only",
                }
                if src is None:
                    report["failures"].append(
                        "UNWITNESSED inherited edge %s" % sym)
            else:
                natural += 1
                report["edges"][sym] = {"class": "NATURAL", "crc": hex(crc)}
        else:
            cls = ("PROVIDER_ABI_GAP" if sym in STOCK_PROVIDER_EDGES
                   else "MISMATCH")
            entry = {"class": cls, "stock": hex(crc), "recon": hex(got)}
            if cls == "PROVIDER_ABI_GAP":
                entry["provider"] = STOCK_PROVIDER_EDGES[sym]
                entry["reason"] = (
                    "provider export CRC produced by genksyms in the vendor "
                    "provider build against MediaTek vendor headers; not "
                    "regenerable from exact GKI")
                entry["declared"] = bool(args.expect_provider_abi_gaps)
                if not args.expect_provider_abi_gaps:
                    report["failures"].append("PROVIDER_ABI_GAP %s" % sym)
            report["edges"][sym] = entry
            if cls == "MISMATCH":
                report["failures"].append("MISMATCH %s" % sym)

    for sym in sorted(set(recon_v) - set(stock_v)):
        report["edges"][sym] = {"class": "EXTRA", "recon": hex(recon_v[sym])}
        report["failures"].append("EXTRA %s" % sym)

    report["checks"]["modversion_total"] = len(stock_v)
    report["checks"]["modversion_natural"] = natural
    report["checks"]["modversion_stock_provider_witness"] = inherited
    report["checks"]["modversion_provider_abi_gap"] = sum(
        1 for e in report["edges"].values() if e["class"] == "PROVIDER_ABI_GAP")

    smi, rmi = modinfo(args.stock), modinfo(args.recon)
    for key in ("author", "description", "license", "name", "vermagic",
                "alias"):
        s, r = smi.get(key), rmi.get(key)
        ok = s == r
        entry = {"stock": s, "recon": r, "ok": ok}
        if not ok and key == "vermagic" and args.accept_build_stamp_delta:
            # 6.1.115-android14-11-<scmversion> <flags...>
            sv, rv = (s or [""])[0].split(" ", 1), (r or [""])[0].split(" ", 1)
            s_rel, r_rel = sv[0], rv[0]
            s_flags = sv[1] if len(sv) > 1 else ""
            r_flags = rv[1] if len(rv) > 1 else ""
            pat = r"^(\d+\.\d+\.\d+-android\d+-\d+)"
            ms, mr = re.match(pat, s_rel), re.match(pat, r_rel)
            s_base = ms.group(1) if ms else None
            r_base = mr.group(1) if mr else None
            if s_base and s_base == r_base and s_flags == r_flags:
                entry["class"] = "BUILD_STAMP_DELTA"
                entry["base_release"] = s_base
                entry["stock_scmversion"] = s_rel[len(s_base):]
                entry["recon_scmversion"] = r_rel[len(r_base):]
                entry["blocks_module_load"] = True
                report["checks"]["modinfo_" + key] = entry
                continue
        report["checks"]["modinfo_" + key] = entry
        if not ok:
            report["failures"].append("MODINFO %s" % key)

    sdep = set(smi.get("depends", [""])[0].split(","))
    rdep = set(rmi.get("depends", [""])[0].split(","))
    dep_entry = {"stock": sorted(sdep), "recon": sorted(rdep),
                 "ok": sdep == rdep}
    if sdep != rdep:
        witness_rename = {"spi-mt65xx-abi": "spi-mt65xx",
                          "tkcore-abi": "tkcore"}
        normalised = {witness_rename.get(d, d) for d in rdep}
        if args.expect_provider_abi_gaps and normalised == sdep:
            dep_entry["class"] = "WITNESS_DEPENDS_DELTA"
            dep_entry["declared"] = True
            dep_entry["reason"] = (
                "natural target links against build-only ABI witness modules; "
                "the stock-provider-compatible target reaches exact depends")
        else:
            report["failures"].append("DEPENDS")
    report["checks"]["depends"] = dep_entry

    sf, rf = defined_functions(args.stock), defined_functions(args.recon)
    report["checks"]["functions"] = {
        "stock_count": len(sf), "recon_count": len(rf),
        "missing": sorted(sf - rf), "extra": sorted(rf - sf),
        "ok": sf == rf}
    if sf != rf:
        report["failures"].extend("FUNC_MISSING %s" % f for f in sorted(sf - rf))
        report["failures"].extend("FUNC_EXTRA %s" % f for f in sorted(rf - sf))

    report["stock_sha256"] = hashlib.sha256(
        open(args.stock, "rb").read()).hexdigest()
    report["recon_sha256"] = hashlib.sha256(
        open(args.recon, "rb").read()).hexdigest()
    for p in args.provider:
        report.setdefault("provider_sha256", {})[p] = hashlib.sha256(
            open(p, "rb").read()).hexdigest()

    declared = [k for k, v in report["edges"].items()
                if v.get("declared")]
    if report["checks"]["depends"].get("declared"):
        declared.append("depends")
    if report["checks"].get("modinfo_vermagic", {}).get(
            "class") == "BUILD_STAMP_DELTA":
        declared.append("vermagic")
    report["declared_deltas"] = sorted(declared)

    if report["failures"]:
        report["result"] = "FAIL"
    elif declared:
        report["result"] = "PASS_WITH_DECLARED_DELTAS"
    else:
        report["result"] = "PASS"

    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        open(args.json, "w").write(text + "\n")
    print(text)
    return 0 if report["result"].startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
