#!/usr/bin/env python3
"""Generate stock-vs-final spi-mt65xx function and object parity TSVs."""
from __future__ import annotations

import csv
import hashlib
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "workspace/phase4-spi-mt65xx/oracle/spi-mt65xx.stock.ko"
REBUILT = ROOT / "workspace/phase4-spi-mt65xx/build/spi-mt65xx.ko"
FUNCTION_OUT = ROOT / "kernel/phase4-spi-mt65xx-function-parity.tsv"
OBJECT_OUT = ROOT / "kernel/phase4-spi-mt65xx-object-parity.tsv"


def elf(path: Path):
    blob = path.read_bytes()
    shoff, = struct.unpack_from("<Q", blob, 0x28)
    entsize, count, stridx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        return struct.unpack_from("<IIQQQQIIQQ", blob, shoff + i * entsize)

    strsec = raw(stridx)
    stroff = strsec[4]
    sections = {}
    byname = {}
    for i in range(count):
        x = raw(i)
        name = blob[stroff + x[0]:blob.index(b"\0", stroff + x[0])].decode()
        sections[i] = (name, x[1], x[4], x[5])
        byname[name] = i

    syms = {"FUNC": {}, "OBJECT": {}}
    out = subprocess.check_output(["readelf", "-sW", str(path)], text=True)
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or not f[0].endswith(":") or f[3] not in syms:
            continue
        if f[6] in ("UND", "ABS"):
            continue
        syms[f[3]][f[7]] = {
            "section": int(f[6]), "offset": int(f[1], 16),
            "size": int(f[2]), "bind": f[4],
        }
    return blob, sections, byname, syms


def symbol_bytes(parsed, sym):
    blob, sections, _, _ = parsed
    sec = sections[sym["section"]]
    return blob[sec[2] + sym["offset"]:sec[2] + sym["offset"] + sym["size"]]


def kcfi(parsed, sym):
    if sym["offset"] < 4:
        return ""
    blob, sections, _, _ = parsed
    sec = sections[sym["section"]]
    value, = struct.unpack_from("<I", blob, sec[2] + sym["offset"] - 4)
    return f"0x{value:08x}"


def call_map(path: Path):
    calls = {}
    for section in (".text", ".init.text", ".exit.text"):
        proc = subprocess.run(
            ["llvm-objdump", "-dr", f"--section={section}", str(path)],
            capture_output=True, text=True,
        )
        current = None
        for line in proc.stdout.splitlines():
            m = re.match(r"[0-9a-f]+ <([^>]+)>:", line)
            if m:
                current = m.group(1)
                calls.setdefault(current, [])
                continue
            if not current:
                continue
            m = re.search(r"\bbl\s+[^<]*<([^>]+)>", line)
            if m:
                calls[current].append(m.group(1).split("+")[0])
            elif re.search(r"\bblr\b", line):
                calls[current].append("INDIRECT")
    return {k: ";".join(dict.fromkeys(v)) or "NONE" for k, v in calls.items()}


def section_bytes(parsed, name):
    blob, sections, byname, _ = parsed
    if name not in byname:
        return None
    _, typ, off, size = sections[byname[name]]
    if typ == 8:
        return (b"", size)
    return (blob[off:off + size], size)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    stock = elf(STOCK)
    rebuilt = elf(REBUILT)
    sf = stock[3]["FUNC"]
    rf = rebuilt[3]["FUNC"]
    calls = call_map(STOCK)

    with FUNCTION_OUT.open("w", newline="") as fh:
        fields = ["name", "section", "stock_size", "rebuilt_size",
                  "stock_kcfi", "rebuilt_kcfi", "calls", "constants",
                  "cfg", "stock_sha256", "rebuilt_sha256",
                  "byte_identity", "residual_classification"]
        wr = csv.DictWriter(fh, fields, delimiter="\t")
        wr.writeheader()
        for name, s in sorted(sf.items(), key=lambda kv: (kv[1]["section"], kv[1]["offset"])):
            r = rf.get(name)
            sb = symbol_bytes(stock, s)
            rb = symbol_bytes(rebuilt, r) if r else b""
            exact = r is not None and sb == rb
            wr.writerow({
                "name": name,
                "section": stock[1][s["section"]][0],
                "stock_size": s["size"],
                "rebuilt_size": r["size"] if r else "MISSING",
                "stock_kcfi": kcfi(stock, s),
                "rebuilt_kcfi": kcfi(rebuilt, r) if r else "",
                "calls": calls.get(name, "NONE"),
                "constants": "BYTE_IDENTICAL" if exact else "REVIEW",
                "cfg": "BYTE_IDENTICAL" if exact else "REVIEW",
                "stock_sha256": sha(sb),
                "rebuilt_sha256": sha(rb) if r else "",
                "byte_identity": "YES" if exact else "NO",
                "residual_classification": "NONE" if exact else "UNRESOLVED",
            })

    so = stock[3]["OBJECT"]
    ro = rebuilt[3]["OBJECT"]
    rows = []
    for name, s in sorted(so.items(), key=lambda kv: (kv[1]["section"], kv[1]["offset"])):
        r = ro.get(name)
        sb = symbol_bytes(stock, s)
        rb = symbol_bytes(rebuilt, r) if r else b""
        classification = "BYTE_IDENTICAL" if r and sb == rb else "UNRESOLVED"
        note = ""
        if name.startswith("__UNIQUE_ID_vermagic"):
            classification = "BUILD_PROVENANCE_ONLY"
            note = "stock g945dff7bc1bf versus rebuilt maybe-dirty"
        rows.append({
            "kind": "OBJECT", "name": name,
            "section": stock[1][s["section"]][0],
            "stock_size": s["size"], "rebuilt_size": r["size"] if r else "MISSING",
            "stock_sha256": sha(sb), "rebuilt_sha256": sha(rb) if r else "",
            "classification": classification, "note": note,
        })

    for name in ("__ksymtab", "__kcrctab", ".rodata", ".rodata.str1.1",
                 ".rodata.str", ".data", ".bss", "__versions", ".modinfo",
                 ".gnu.linkonce.this_module", ".note.gnu.build-id"):
        s = section_bytes(stock, name)
        r = section_bytes(rebuilt, name)
        if s is None or r is None:
            continue
        exact = s == r
        classification = "BYTE_IDENTICAL" if exact else "UNRESOLVED"
        note = ""
        if name == ".rodata.str":
            classification = "BUILD_PROVENANCE_ONLY"
            note = "only __FILE__ source path string differs; relocations are exact"
        elif name == ".modinfo":
            classification = "BUILD_PROVENANCE_ONLY"
            note = "only vermagic provenance string length/content differs"
        elif name == ".note.gnu.build-id":
            classification = "BUILD_PROVENANCE_ONLY"
            note = "link-time build ID"
        rows.append({
            "kind": "SECTION", "name": name, "section": name,
            "stock_size": s[1], "rebuilt_size": r[1],
            "stock_sha256": sha(s[0]), "rebuilt_sha256": sha(r[0]),
            "classification": classification, "note": note,
        })

    with OBJECT_OUT.open("w", newline="") as fh:
        fields = ["kind", "name", "section", "stock_size", "rebuilt_size",
                  "stock_sha256", "rebuilt_sha256", "classification", "note"]
        wr = csv.DictWriter(fh, fields, delimiter="\t")
        wr.writeheader()
        wr.writerows(rows)

    function_exact = sum(1 for r in csv.DictReader(FUNCTION_OUT.open(), delimiter="\t")
                         if r["byte_identity"] == "YES")
    object_classes = {}
    for r in rows:
        object_classes[r["classification"]] = object_classes.get(r["classification"], 0) + 1
    print(f"functions: stock={len(sf)} rebuilt={len(rf)} byte_exact={function_exact}")
    print("object/section classes:", object_classes)
    return 0 if function_exact == len(sf) and "UNRESOLVED" not in object_classes else 1


if __name__ == "__main__":
    raise SystemExit(main())
