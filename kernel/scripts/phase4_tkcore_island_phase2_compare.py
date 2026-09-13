#!/usr/bin/env python3
"""GQ5012BF1 tkcore island Phase 2: stock vs rebuilt structural comparison.

Static/offline only. Reads two ELF objects and emits the Phase-2 comparison
TSVs. Nothing is loaded, executed or patched.

  stock   : workspace/phase4-tkcore-island/oracle/tkcore.stock.ko
  rebuilt : workspace/phase4-tkcore-island/phase2/build/tkcore.rebuilt.phase2.ko
"""
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STOCK = os.path.join(REPO, "workspace/phase4-tkcore-island/oracle/tkcore.stock.ko")
REBUILT = os.path.join(
    REPO, "workspace/phase4-tkcore-island/phase2/build/tkcore.rebuilt.phase2.ko")
OUT = os.path.join(REPO, "kernel")

NM = "llvm-nm"
READELF = "llvm-readelf"
OBJDUMP = "llvm-objdump"
OBJCOPY = "llvm-objcopy"


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def symbols(path):
    """Return (functions, objects) as dict name -> (section, size, bind)."""
    funcs, objs = {}, {}
    out = run(READELF, "--symbols", "--wide", path)
    for line in out.splitlines():
        p = line.split()
        if len(p) < 8 or not p[0].endswith(":"):
            continue
        try:
            size = int(p[2], 0)
        except ValueError:
            continue
        typ, bind, ndx, name = p[3], p[4], p[6], p[7]
        if ndx == "UND" or name.startswith("$"):
            continue
        if typ == "FUNC":
            funcs[name] = (ndx, size, bind)
        elif typ == "OBJECT":
            objs[name] = (ndx, size, bind)
    return funcs, objs


def undefined(path):
    out = run(NM, "-u", path)
    return sorted({l.split()[-1] for l in out.splitlines() if l.strip()})


def modversions(path):
    """Parse __versions: array of {u64 crc; char name[56]} on arm64."""
    raw = subprocess.run(
        [OBJCOPY, "--dump-section=__versions=/dev/stdout", path, "/dev/null"],
        capture_output=True).stdout
    res = {}
    ent = 64
    for i in range(0, len(raw) - ent + 1, ent):
        crc = struct.unpack_from("<Q", raw, i)[0]
        name = raw[i + 8:i + ent].split(b"\0")[0].decode("utf-8", "replace")
        if name:
            res[name] = "0x%08x" % (crc & 0xFFFFFFFF)
    return res


def exports(path):
    """Export name -> crc (from ___kcrctab / __kcrctab sections)."""
    names = []
    out = run(READELF, "--symbols", "--wide", path)
    for line in out.splitlines():
        m = re.search(r"__ksymtab_(\S+)$", line)
        if m and m.group(1) != "strings":
            # "__ksymtab_strings" is the export-name string section, not an
            # export.  Excluding it yields the authoritative stock count of 25.
            names.append(m.group(1))
    crcs = {}
    for sec in ("__kcrctab", "__kcrctab_gpl"):
        raw = subprocess.run(
            [OBJCOPY, f"--dump-section={sec}=/dev/stdout", path, "/dev/null"],
            capture_output=True).stdout
        if raw:
            for i in range(0, len(raw), 4):
                crcs[i // 4] = "0x%08x" % struct.unpack_from("<I", raw, i)[0]
    return sorted(set(names)), crcs


def kcfi(path):
    """Map function -> KCFI type id.

    Same method as kernel/scripts/phase4_elf_inventory.py: the kCFI type id is
    the 32-bit word immediately preceding the function entry point.
    """
    blob = open(path, "rb").read()
    secs = {}
    out = run(READELF, "--section-headers", "--wide", path)
    for line in out.splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)",
                     line)
        if m:
            secs[int(m.group(1))] = (m.group(2), int(m.group(5), 16))
    res = {}
    out = run(READELF, "--symbols", "--wide", path)
    for line in out.splitlines():
        p = line.split()
        if len(p) < 8 or not p[0].endswith(":") or p[3] != "FUNC":
            continue
        ndx, name = p[6], p[7]
        if not ndx.isdigit() or int(ndx) not in secs:
            continue
        val = int(p[1], 16)
        if val < 4:
            continue
        off = secs[int(ndx)][1] + val - 4
        if off + 4 > len(blob):
            continue
        res[name] = "0x%08x" % struct.unpack_from("<I", blob, off)[0]
    return res


def relocations(path):
    """Return per-section relocation count and per-function callee targets."""
    counts = {}
    out = run(READELF, "--relocs", "--wide", path)
    sec = None
    for line in out.splitlines():
        m = re.match(r"Relocation section '(\S+)'", line)
        if m:
            sec = m.group(1)
            continue
        if sec and re.match(r"^[0-9a-f]{8,}", line):
            counts[sec] = counts.get(sec, 0) + 1
    return counts


def calls(path):
    """function -> sorted set of relocation target symbols inside it."""
    res = {}
    for sect in (".text", ".init.text", ".exit.text"):
        out = run(OBJDUMP, "-dr", f"--section={sect}", path)
        cur = None
        for line in out.splitlines():
            m = re.match(r"^[0-9a-f]+ <(.+?)>:", line)
            if m:
                cur = m.group(1)
                res.setdefault(cur, set())
                continue
            m = re.search(r"R_AARCH64_\S+\s+(\S+)", line)
            if m and cur:
                res[cur].add(m.group(1).split("+")[0])
    return {k: sorted(v) for k, v in res.items()}


def strings_of(path):
    out = run("strings", "-n", "4", path)
    return sorted(set(out.splitlines()))


def write(name, header, rows):
    p = os.path.join(OUT, name)
    with open(p, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    print(f"  {name}: {len(rows)} rows")


def main():
    for p in (STOCK, REBUILT):
        if not os.path.exists(p):
            sys.exit(f"missing: {p}")

    sf, so = symbols(STOCK)
    rf, ro = symbols(REBUILT)
    print(f"stock functions={len(sf)} objects={len(so)}")
    print(f"rebuilt functions={len(rf)} objects={len(ro)}")

    skcfi, rkcfi = kcfi(STOCK), kcfi(REBUILT)
    scalls, rcalls = calls(STOCK), calls(REBUILT)

    # ---- functions -----------------------------------------------------
    rows = []
    for n in sorted(set(sf) | set(rf)):
        s = sf.get(n)
        r = rf.get(n)
        state = "SHARED" if s and r else ("MISSING" if s else "EXTRA")
        rows.append([n, s[1] if s else "", r[1] if r else "",
                     s[0] if s else "", r[0] if r else "", state])
    write("phase4-tkcore-island-phase2-functions.tsv",
          ["function", "stock_size", "rebuilt_size", "stock_section",
           "rebuilt_section", "state"], rows)

    # ---- objects -------------------------------------------------------
    rows = []
    for n in sorted(set(so) | set(ro)):
        s, r = so.get(n), ro.get(n)
        if s and r:
            cls = "SIZE_EXACT_CONTENT_DIFF" if s[1] == r[1] else "STRUCTURAL"
        else:
            cls = "MISSING" if s else "EXTRA"
        rows.append([n, s[1] if s else "", r[1] if r else "", cls])
    write("phase4-tkcore-island-phase2-object-parity.tsv",
          ["object", "stock_size", "rebuilt_size", "class"], rows)
    write("phase4-tkcore-island-phase2-objects.tsv",
          ["object", "stock_size", "rebuilt_size", "class"], rows)

    # ---- imports -------------------------------------------------------
    su, ru = undefined(STOCK), undefined(REBUILT)
    smv, rmv = modversions(STOCK), modversions(REBUILT)
    rows = []
    for n in sorted(set(su) | set(ru)):
        st = "shared" if n in su and n in ru else ("missing" if n in su else "extra")
        sc, rc = smv.get(n, ""), rmv.get(n, "")
        crcm = "YES" if sc and rc and sc == rc else ("NO" if sc and rc else "N/A")
        rows.append([n, "yes" if n in su else "no", "yes" if n in ru else "no",
                     st, sc, rc, crcm])
    write("phase4-tkcore-island-phase2-gki-imports.tsv",
          ["symbol", "in_stock", "in_rebuilt", "state", "stock_crc",
           "rebuilt_crc", "crc_match"], rows)
    write("phase4-tkcore-island-phase2-imports.tsv",
          ["symbol", "in_stock", "in_rebuilt", "state", "stock_crc",
           "rebuilt_crc", "crc_match"], rows)

    rows = []
    for n in sorted(set(smv) | set(rmv)):
        sc, rc = smv.get(n, ""), rmv.get(n, "")
        rows.append([n, sc, rc,
                     "MATCH" if sc and rc and sc == rc else
                     ("DIFF" if sc and rc else ("STOCK_ONLY" if sc else "REBUILT_ONLY"))])
    write("phase4-tkcore-island-phase2-modversions.tsv",
          ["symbol", "stock_crc", "rebuilt_crc", "state"], rows)

    # ---- exports -------------------------------------------------------
    se, _ = exports(STOCK)
    re_, _ = exports(REBUILT)
    rows = []
    for n in sorted(set(se) | set(re_)):
        rows.append([n, "yes" if n in se else "no", "yes" if n in re_ else "no",
                     skcfi.get(n, ""), rkcfi.get(n, ""),
                     "SHARED" if n in se and n in re_ else
                     ("MISSING" if n in se else "EXTRA")])
    write("phase4-tkcore-island-phase2-export-parity.tsv",
          ["export", "in_stock", "in_rebuilt", "stock_kcfi", "rebuilt_kcfi",
           "state"], rows)
    write("phase4-tkcore-island-phase2-exports.tsv",
          ["export", "in_stock", "in_rebuilt", "stock_kcfi", "rebuilt_kcfi",
           "state"], rows)

    # ---- KCFI ----------------------------------------------------------
    rows = []
    for n in sorted(set(skcfi) | set(rkcfi)):
        s, r = skcfi.get(n, ""), rkcfi.get(n, "")
        rows.append([n, s, r,
                     "EXACT" if s and r and s == r else
                     ("MISMATCH" if s and r else
                      ("STOCK_ONLY" if s else "REBUILT_ONLY"))])
    write("phase4-tkcore-island-phase2-kcfi.tsv",
          ["function", "stock_kcfi", "rebuilt_kcfi", "state"], rows)

    # ---- relocations ---------------------------------------------------
    sr, rr = relocations(STOCK), relocations(REBUILT)
    rows = [[s, sr.get(s, 0), rr.get(s, 0)] for s in sorted(set(sr) | set(rr))]
    rows.append(["TOTAL", sum(sr.values()), sum(rr.values())])
    write("phase4-tkcore-island-phase2-relocations.tsv",
          ["section", "stock_relocs", "rebuilt_relocs"], rows)

    # ---- callgraph -----------------------------------------------------
    rows = []
    for n in sorted(set(scalls) | set(rcalls)):
        s = scalls.get(n)
        r = rcalls.get(n)
        if s is not None and r is not None:
            shared = len(set(s) & set(r))
            cls = "CALLSET_EXACT" if set(s) == set(r) else "CALLSET_DIFF"
        else:
            shared = 0
            cls = "MISSING" if s is not None else "EXTRA"
        rows.append([n, len(s) if s is not None else "",
                     len(r) if r is not None else "", shared, cls,
                     ";".join(s) if s is not None else "",
                     ";".join(r) if r is not None else ""])
    write("phase4-tkcore-island-phase2-callgraph.tsv",
          ["function", "stock_reloc_targets", "rebuilt_reloc_targets",
           "shared_targets", "class", "stock_targets", "rebuilt_targets"], rows)

    # ---- strings -------------------------------------------------------
    ss, rs = set(strings_of(STOCK)), set(strings_of(REBUILT))
    rows = [[s, "yes" if s in ss else "no", "yes" if s in rs else "no"]
            for s in sorted(ss | rs)]
    write("phase4-tkcore-island-phase2-strings.tsv",
          ["string", "in_stock", "in_rebuilt"], rows)

    # ---- summary -------------------------------------------------------
    shared_f = set(sf) & set(rf)
    size_id = [n for n in shared_f if sf[n][1] == rf[n][1]]
    print("\n--- SUMMARY ---")
    print(f"stock functions       : {len(sf)}")
    print(f"rebuilt functions     : {len(rf)}")
    print(f"shared               : {len(shared_f)}")
    print(f"missing (stock only) : {len(set(sf) - set(rf))}")
    print(f"extra (rebuilt only) : {len(set(rf) - set(sf))}")
    print(f"size-identical shared: {len(size_id)}")
    print(f"stock undefined      : {len(su)}")
    print(f"rebuilt undefined    : {len(ru)}")
    print(f"imports shared       : {len(set(su) & set(ru))}")
    print(f"imports missing      : {len(set(su) - set(ru))}")
    print(f"imports extra        : {len(set(ru) - set(su))}")
    print(f"stock exports        : {len(se)}")
    print(f"rebuilt exports      : {len(re_)}")
    print(f"exports shared       : {len(set(se) & set(re_))}")


if __name__ == "__main__":
    main()
