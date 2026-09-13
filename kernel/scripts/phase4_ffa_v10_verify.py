#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 ffa_v10.ko source closure.

ffa_v10 is an ABI PROVIDER, so the standard is absolute: every one of its five
export CRCs must be produced by genksyms from real C.  No witness, no copied
CRC, no __versions edit, no ELF patch, no KBUILD_MODPOST_WARN.  This verifier
therefore refuses to pass if:

  * any export CRC in the rebuilt Module.symvers is absent or wrong
  * the rebuilt module is not a genuine build (its __kcrctab_gpl must agree
    with the Module.symvers text, which is only true for genksyms output)
  * any stock consumer edge would fail to resolve against the rebuilt provider
  * a stock-provider witness file is used anywhere in the ffa_v10 build

Checks:
  1.  canonical stock oracle: sha256, size, all copies byte-identical
  2.  stock module metadata (vermagic, name, alias, license, depends)
  3.  donor provenance: the four vendor sources are byte-identical to the
      pinned Nothing MT6878 tree
  4.  export surface: 5 names, all EXPORT_SYMBOL_GPL, no more, no fewer
  5.  NATURAL export CRC gate: rebuilt == stock for all five, including the
      two hard gates ffa_driver_register / ffa_driver_unregister
  6.  the CRCs really come from this build (Module.symvers == __kcrctab_gpl)
  7.  no witness/CRC-injection artefact anywhere in the build package
  8.  function parity: same 34 functions, byte-identical, kCFI-identical
  9.  import parity: identical 40 imports + 41 MODVERSION CRCs
 10.  every discovered stock consumer edge resolves against the rebuilt CRCs
 11.  tkcore_drv acceptance: builds against the real provider, unchanged

Usage:
  python3 kernel/scripts/phase4_ffa_v10_verify.py [--repo <path>] [--ws <path>]
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import subprocess
import sys
from pathlib import Path

STOCK_SHA = "2f8341d3f920418f3d9f4b8f64299acf97e591ad232a6bbbf6298b63231eebde"
STOCK_SIZE = 38688
STOCK_VERMAGIC = ("6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload "
                  "modversions aarch64")
STOCK_MODINFO = {
    "name": "ffa_v10",
    "alias": "arm-ffa",
    "license": "GPL v2",
    "description": "Arm FF-A interface driver",
    "author": "Sudeep Holla <sudeep.holla@arm.com>",
    "depends": "",
}

# All five stock exports.  Every one of these must be NATURAL.
STOCK_EXPORTS = {
    "ffa_bus_type": 0x82C0DED3,
    "ffa_device_register": 0xA400C46E,
    "ffa_device_unregister": 0x85B1F074,
    "ffa_driver_register": 0x0D53CDE9,      # hard gate (tkcore_drv, tmem_ffa,
    "ffa_driver_unregister": 0x3C660E4C,    # gz_main_mod)
}
HARD_GATES = ("ffa_driver_register", "ffa_driver_unregister")

# Exact vendor donor: device_modules 957dac185efe46cbf6336b0fff9516d84c8cd78f,
# drivers/misc/mediatek/trusted_mem/ffa_v10/
DONOR_SHA = {
    "bus.c": "3cda7cc57a774e1b0c138acd8a5fc8fb12e4255fd81b0e96675a290be40bf8a6",
    "driver.c": "6b14f18ee44e4966810d55b00eaa3d32163da1c82b8290e78cd30f3fb66306c5",
    "smccc.c": "3701a267eaad251847e25fefa80ba1a6495e57c3af3bc095ac73e50288cd49a3",
    "common.h": "84883f2fefa4d64c51f5491e37388ac29e75925e138acc1a3fac51d3baf196f5",
    "Kconfig": "c47ebe5ba1b43a6e1225c59ea48812a5a0821f2b2e2b87afc04fb8f913e8c78c",
}

# Every consumer of an ffa_v10 export found by scanning all 471 stock modules.
STOCK_CONSUMERS = {
    "tkcore_drv.ko": {"ffa_driver_register": 0x0D53CDE9,
                      "ffa_driver_unregister": 0x3C660E4C},
    "tmem_ffa.ko": {"ffa_driver_register": 0x0D53CDE9},
    "gz_main_mod.ko": {"ffa_driver_register": 0x0D53CDE9},
}

# Build-provenance-only difference, project-wide: GKI commit 945dff7bc1bf is
# absent from this mirror, so kleaf stamps "-maybe-dirty".  Identical delta for
# every module rebuilt in this workspace.
SCMVERSION_NOTE = "-maybe-dirty"

FAILURES: list[str] = []
CHECKS = 0


def check(cond, msg) -> bool:
    global CHECKS
    CHECKS += 1
    if cond:
        print("  [ok]   %s" % msg)
        return True
    print("  [FAIL] %s" % msg)
    FAILURES.append(msg)
    return False


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sections(blob: bytes):
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        return struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * shentsize)

    stroff = raw(shstrndx)[4]
    out = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz = raw(i)[:6]
        end = blob.index(b"\0", stroff + nm)
        out[blob[stroff + nm:end].decode()] = (off, sz, i)
    return out


def modinfo(p: Path) -> dict:
    blob = p.read_bytes()
    sec = sections(blob)
    off, size, _ = sec[".modinfo"]
    out = {}
    for item in blob[off:off + size].split(b"\0"):
        if b"=" in item:
            k, v = item.decode(errors="replace").split("=", 1)
            out[k] = v
    return out


def modversions(p: Path) -> dict:
    blob = p.read_bytes()
    sec = sections(blob)
    if "__versions" not in sec:
        return {}
    off, size, _ = sec["__versions"]
    out = {}
    for i in range(off, off + size, 64):
        rec = blob[i:i + 64]
        if len(rec) < 64:
            break
        crc, = struct.unpack_from("<I", rec, 0)
        out[rec[8:].split(b"\0")[0].decode()] = crc
    return out


def kcrctab(p: Path) -> dict:
    """The module's own published export CRCs, read from __kcrctab*."""
    blob = p.read_bytes()
    sec = sections(blob)
    shnames = {v[2]: k for k, v in sec.items()}
    out = subprocess.run(["readelf", "-sW", str(p)], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[7].startswith("__crc_"):
            try:
                idx, value = int(f[6]), int(f[1], 16)
            except ValueError:
                continue
            name = shnames.get(idx)
            if name not in ("__kcrctab", "__kcrctab_gpl"):
                continue
            base = sec[name][0]
            crc, = struct.unpack_from("<I", blob, base + value)
            res[f[7][len("__crc_"):]] = (crc, name)
    return res


def funcs(p: Path) -> dict:
    blob = p.read_bytes()
    sec = sections(blob)
    offs = {v[2]: v[0] for v in sec.values()}
    out = subprocess.run(["readelf", "-sW", str(p)], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or f[3] != "FUNC" or f[6] in ("UND", "ABS"):
            continue
        try:
            value, size, idx = int(f[1], 16), int(f[2]), int(f[6])
        except ValueError:
            continue
        base = offs[idx]
        kc = (struct.unpack_from("<I", blob, base + value - 4)[0]
              if value >= 4 else 0)
        res[f[7].split(".")[0]] = (size, blob[base + value:base + value + size],
                                   kc)
    return res


def parse_symvers(p: Path) -> dict:
    out = {}
    for line in p.read_text().splitlines():
        f = line.split("\t")
        if len(f) >= 4 and f[0].startswith("0x"):
            out[f[1]] = (int(f[0], 16), f[2], f[3])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--ws", default="/home/armol/kernel-work/"
                                    "gki-12901745-workspace")
    args = ap.parse_args()
    repo, ws = Path(args.repo), Path(args.ws)

    oracle = repo / "workspace/phase4-ffa-v10/oracle/ffa_v10.ko"
    built = repo / "workspace/phase4-ffa-v10/build/ffa_v10.ko"
    symvers = repo / "workspace/phase4-ffa-v10/build/Module.symvers"
    pkg = ws / "lieppos/ffa-v10"
    donor = Path("/home/armol/androido_dalykai/LieppOS custom ROM/"
                 "kernel-research/nothing-mt6878/device_modules/drivers/misc/"
                 "mediatek/trusted_mem/ffa_v10")

    print("1. canonical stock oracle frozen")
    if check(oracle.is_file(), "oracle present"):
        check(sha256(oracle) == STOCK_SHA,
              "sha256 %s" % sha256(oracle)[:32])
        check(oracle.stat().st_size == STOCK_SIZE,
              "size %d B" % oracle.stat().st_size)
    copies = sorted((repo / "workspace").rglob("ffa_v10.ko"))
    stock_copies = [c for c in copies if "build" not in c.parts]
    check(all(sha256(c) == STOCK_SHA for c in stock_copies),
          "all %d stock copies byte-identical" % len(stock_copies))

    print("2. stock module metadata")
    mi = modinfo(oracle)
    check(mi.get("vermagic") == STOCK_VERMAGIC, "vermagic")
    for k, v in sorted(STOCK_MODINFO.items()):
        check(mi.get(k, "") == v, "%s=%s" % (k, v))
    check("srcversion" not in mi, "no srcversion (stock has none)")

    print("3. donor provenance (exact MediaTek vendor source)")
    for name, want in sorted(DONOR_SHA.items()):
        d, b = donor / name, pkg / name
        ok = d.is_file() and b.is_file() and sha256(d) == want == sha256(b)
        check(ok, "%s byte-identical to the pinned vendor tree" % name)

    print("4. export surface")
    se = kcrctab(oracle)
    check(set(se) == set(STOCK_EXPORTS),
          "stock exports exactly %d symbols" % len(STOCK_EXPORTS))
    check(all(tab == "__kcrctab_gpl" for _, tab in se.values()),
          "every export is EXPORT_SYMBOL_GPL")

    print("5. NATURAL export CRC gate (no witnesses allowed)")
    if check(symvers.is_file(), "rebuilt Module.symvers present"):
        sv = parse_symvers(symvers)
        check(set(sv) == set(STOCK_EXPORTS),
              "rebuilt publishes exactly the stock export set")
        for name, crc in sorted(STOCK_EXPORTS.items()):
            gate = " [HARD GATE]" if name in HARD_GATES else ""
            check(name in sv and sv[name][0] == crc,
                  "%s naturally regenerated as 0x%08x%s" % (name, crc, gate))
        check(all(cls == "EXPORT_SYMBOL_GPL" for _, _, cls in sv.values()),
              "export classes match stock (all GPL)")

    print("6. CRCs really come from this build")
    if check(built.is_file(), "rebuilt module present"):
        be = kcrctab(built)
        check({k: v[0] for k, v in be.items()} == STOCK_EXPORTS,
              "rebuilt __kcrctab_gpl equals the stock CRC record")
        sv = parse_symvers(symvers) if symvers.is_file() else {}
        check(all(be[k][0] == sv[k][0] for k in be if k in sv),
              "__kcrctab_gpl agrees with Module.symvers (genksyms output)")

    print("7. no CRC injection / witness artefacts in the provider build")
    stray = [p.name for p in pkg.iterdir()
             if p.suffix == ".symvers" or "witness" in p.name
             or p.name.endswith(".patch")]
    check(not stray, "no symvers/witness/patch files in the package%s"
          % (" (found %s)" % stray if stray else ""))
    mk = (pkg / "Makefile").read_text()
    check("KBUILD_MODPOST_WARN" not in mk, "no KBUILD_MODPOST_WARN")
    check("KBUILD_EXTRA_SYMBOLS" not in mk, "no external symbol record at all")

    print("8. function parity")
    sf, bf = funcs(oracle), funcs(built)
    common = sorted(set(sf) & set(bf))
    check(set(sf) == set(bf), "same %d functions (missing %s, extra %s)"
          % (len(sf), sorted(set(sf) - set(bf)), sorted(set(bf) - set(sf))))
    check(all(sf[n][1] == bf[n][1] for n in common),
          "all %d functions byte-identical" % len(common))
    check(all(sf[n][2] == bf[n][2] for n in common),
          "all %d kCFI type ids identical" % len(common))

    print("9. import parity")
    smv, bmv = modversions(oracle), modversions(built)
    check(set(smv) == set(bmv), "same %d __versions entries" % len(smv))
    check(smv == bmv, "every imported MODVERSION CRC identical")

    print("10. stock consumer edges resolve against the rebuilt provider")
    roots = [repo / "workspace/gq5012bf1/stock/vendor-ramdisks/"
                    "platform-extracted/lib/modules",
             repo / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/"
                    "lib/modules"]
    sv = parse_symvers(symvers) if symvers.is_file() else {}
    for name, edges in sorted(STOCK_CONSUMERS.items()):
        path = next((r / name for r in roots if (r / name).is_file()), None)
        if not check(path is not None, "consumer %s found" % name):
            continue
        mv = modversions(path)
        bad = [s for s, c in edges.items()
               if mv.get(s) != c or sv.get(s, (None,))[0] != c]
        check(not bad, "%s: %d/%d edge(s) match the rebuilt provider%s"
              % (name, len(edges) - len(bad), len(edges),
                 " (bad: %s)" % bad if bad else ""))

    print("11. tkcore_drv acceptance (rebuilt against the real provider)")
    tk = repo / "workspace/phase4-tkcore-drv/build/tkcore_drv.stockabi.ko"
    if check(tk.is_file(), "tkcore_drv stock-ABI module present"):
        tmv = modversions(tk)
        check(all(tmv.get(s) == c for s, c in
                  {k: STOCK_EXPORTS[k] for k in HARD_GATES}.items()),
              "both FF-A edges carry the naturally regenerated CRCs")
        d = modinfo(tk).get("depends", "")
        check(set(d.split(",")) == {"tkcore", "ffa_v10"},
              "depends=%s unchanged" % d)
        stock_tk = repo / "workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko"
        check(len(funcs(tk)) == len(funcs(stock_tk)) == 50,
              "tkcore_drv function set still 50/50 (behaviour not reopened)")
        tkstock = modversions(stock_tk)
        check(not [s for s in tmv if s in tkstock and tmv[s] != tkstock[s]],
              "tkcore_drv still has zero CRC mismatches vs stock")

    print()
    print("residual (documented, build-provenance only): rebuilt vermagic "
          "carries '%s'" % SCMVERSION_NOTE)
    print("%d/%d CHECKS PASSED" % (CHECKS - len(FAILURES), CHECKS))
    if FAILURES:
        for f in FAILURES:
            print("  FAILED: %s" % f)
        return 1
    print("RESULT: ffa_v10 SOURCE-CLOSED - all 5 export CRCs NATURAL, "
          "no provider witnesses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
