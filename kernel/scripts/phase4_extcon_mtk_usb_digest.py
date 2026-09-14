#!/usr/bin/env python3
"""Per-function structural parity check: stock .ko vs the reconstruction.

For each named function this prints, in program order, the resolved call targets
and the string/object operands materialised by ADRP+ADD pairs, plus the
conditional-branch count and the function size. Sizes alone are not a parity
signal -- clang's inliner moves whole blocks between callers (stock inlines
mtk_usb_extcon_set_vbus into its two callers, for instance) -- so the digests
are compared side by side, which is the mechanical half of the acceptance check.

  ./check.py --stock oracle/extcon-mtk-usb.ko --recon <build>/extcon_mtk_usb.ko \
             mtk_extcon_tcpc_notifier mtk_usb_extcon_psy_detector
"""
import re
import subprocess
import sys
from pathlib import Path

OBJDUMP = "llvm-objdump"
RELELF = "llvm-readelf"


def sh(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0 and not r.stdout:
        sys.exit(f"{' '.join(args[:2])} failed: {r.stderr.strip()[:200]}")
    return r.stdout


RELS = re.compile(
    r"^[0-9a-f]{8,16}\s+[0-9a-f]+\s+(R_AARCH64_\w+)\s+[0-9a-f]+\s+(\S+)( \+ (\S+))?$")
FUNC = re.compile(r"^\s*\d+:\s+([0-9a-f]{8,16})\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+"
                  r"(\S+)\s+(.+)$")
SECT = re.compile(r"^\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)")


def funcs(path):
    """symbol -> (section-relative addr, size, section name).

    Offsets in a relocatable module are section-relative and several text
    sections restart at 0, so the owning section has to travel with the address.
    """
    names = {i: n for i, n in section_names(path).items()}
    out = {}
    for line in sh([RELELF, "-sW", path]).splitlines():
        m = FUNC.match(line)
        if not m:
            continue
        addr, size, ndx, name = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        if ndx == "UND" or name.startswith("$"):
            continue
        try:
            sec = names.get(int(ndx), ".text")
        except ValueError:
            sec = ".text"
        out[name] = (int(addr, 16), int(size, 16), sec)
    return out


def section_names(path):
    """section index -> name (from the section header table)."""
    out = {}
    for i, line in enumerate(sh([RELELF, "-SW", path]).splitlines()):
        m = re.match(r"^\s*\[\s*(\d+)\]\s+(\S+)", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def sections(path):
    """section name -> (file offset, size)."""
    out = {}
    for line in sh([RELELF, "-SW", path]).splitlines():
        m = SECT.match(line)
        if m:
            out[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
    for extra in (".text", ".init.text", ".exit.text"):
        out.setdefault(extra, (0, 0))
    return out


def text_relocs(path):
    """text offset -> resolved target description."""
    blob = Path(path).read_bytes()
    secs = sections(path)

    def cstr(sec, off):
        if sec not in secs:
            return f"<{sec}+{off}>"
        base, _size = secs[sec]
        o = base + int(off, 16)
        end = blob.find(b"\0", o)
        raw = blob[o:end if end > o else o + 32]
        txt = raw.decode("utf-8", "replace")
        return txt if raw and sum(c.isprintable() or c == "\n" for c in txt) > len(txt) * 0.8 else None

    per = {}
    sec = None
    for line in sh([RELELF, "-rW", path]).splitlines():
        if line.startswith("Relocation section"):
            name = line.split("'")[1]
            sec = name[len(".rela."):] if name.startswith(".rela.") else None
            if sec:
                per.setdefault(sec, {})
            continue
        if sec is None:
            continue
        m = RELS.match(line.strip())
        if not m:
            continue
        typ, sym, addend = m.group(1), m.group(2), (m.group(4) or "0")
        off = int(line.split()[0], 16)
        out = per[sec]
        if typ == "R_AARCH64_CALL26":
            out[off] = ("call", sym)
        elif typ in ("R_AARCH64_ADR_PREL_PG_HI21", "R_AARCH64_ADD_ABS_LO12_NC"):
            if sym.startswith((".rodata", ".data", ".bss", ".sdt")):
                out.setdefault(off, ("ref", cstr(sym, addend)))
            else:
                out.setdefault(off, ("ref", sym))
    return per


BR = re.compile(r"^(b\.\w+|cbz|cbnz|tbz|tbnz)$")


def body(path, name):
    f = funcs(path)
    if name not in f:
        return None
    addr, size, sec = f[name]
    text = sh([OBJDUMP, "-d", "--no-show-raw-insn", f"--section={sec}",
               f"--start-address={hex(addr)}", f"--stop-address={hex(addr + max(size, 4))}", path])
    rels = text_relocs(path).get(sec.lstrip("."), {})
    # intra-module bl targets have no relocation: resolve them by address range so
    # that "calls set_vbus()" is visible instead of a bare hex offset
    byrange = sorted(((a, a + max(sz, 4), n) for n, (a, sz, s2) in f.items()
                      if s2 == sec), key=lambda x: x[0])

    def local(target):
        try:
            t = int(target, 16)
        except ValueError:
            return None
        for lo, hi, n in byrange:
            if lo <= t < hi and n != name:
                return n
        return None

    calls, refs, branches = [], [], 0
    for line in text.splitlines():
        m = re.match(r"^\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if not m:
            continue
        off, op = int(m.group(1), 16), m.group(2)
        if op == "bl":
            t = rels.get(off)
            raw = m.group(3).split()[0].lstrip("#") if m.group(3).split() else "?"
            if t and t[0] == "call":
                calls.append(t[1])
            else:
                calls.append(local(raw) or raw)
        elif BR.match(op):
            branches += 1
        elif op in ("adrp", "add"):
            t = rels.get(off)
            if t and t[0] == "ref" and t[1] and (not refs or refs[-1] != t[1]):
                refs.append(t[1])
    return size, calls, branches, refs


def main():
    argv = sys.argv[1:]
    images = {}
    names = []
    i = 0
    while i < len(argv):
        if argv[i].startswith("--"):
            images[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            names.append(argv[i])
            i += 1
    if not images:
        sys.exit(__doc__)
    for fn in names:
        print(f"\n===== {fn} " + "=" * max(0, 60 - len(fn)))
        for label, path in images.items():
            r = body(path, fn)
            if r is None:
                print(f"  {label.upper():6s} <absent>")
                continue
            size, calls, branches, refs = r
            print(f"  {label.upper():6s} {size:5d}B  branches={branches}  calls={len(calls)}")
            print(f"         calls: {' '.join(calls)}")
            for s in refs[:12]:
                print(f"         str:   {s[:86]}")


if __name__ == "__main__":
    main()
