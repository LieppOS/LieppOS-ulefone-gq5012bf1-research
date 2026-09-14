#!/usr/bin/env python3
"""Generate the frozen GQ5012BF1 tkcore Phase-3A-R three-way ELF inventory.

Static/offline only.  The script never modifies an ELF.
"""
from __future__ import annotations

import csv
import hashlib
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
PHASE3P = REPO / "workspace/phase4-tkcore-island/phase3a-r/before/tkcore.phase3p.ko"
PHASE3AR = REPO / "workspace/phase4-tkcore-island/phase3a-r/build/tkcore.phase3a-r.ko"
OUT = REPO / "kernel"


def run(*args: str, binary: bool = False):
    p = subprocess.run(args, capture_output=True, text=not binary)
    if p.returncode:
        err = p.stderr.decode(errors="replace") if binary else p.stderr
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{err}")
    return p.stdout


def write_tsv(name: str, header: list[str], rows: list[list[object]]) -> None:
    path = OUT / f"phase4-tkcore-island-phase3a-r-{name}.tsv"
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def symbols(path: Path):
    funcs, objects, undefined = {}, {}, set()
    for line in run("llvm-readelf", "-sW", str(path)).splitlines():
        p = line.split()
        if len(p) < 8 or not p[0].endswith(":"):
            continue
        typ, bind, ndx, name = p[3], p[4], p[6], p[7]
        if ndx == "UND":
            if name and name != "0":
                undefined.add(name)
            continue
        if name.startswith("$"):
            continue
        try:
            value, size = int(p[1], 16), int(p[2], 0)
        except ValueError:
            continue
        rec = {"value": value, "size": size, "section": ndx, "bind": bind}
        if typ == "FUNC":
            funcs[name] = rec
        elif typ == "OBJECT":
            objects[name] = rec
    return funcs, objects, undefined


def section(path: Path, name: str) -> bytes:
    p = subprocess.run(
        ["llvm-objcopy", f"--dump-section={name}=/dev/stdout", str(path), "/dev/null"],
        capture_output=True,
    )
    if p.returncode:
        return b""
    return p.stdout


def kcfi(text: bytes, rec: dict | None) -> str:
    if not rec or rec["value"] < 4 or rec["value"] > len(text):
        return "ABSENT"
    return f"0x{struct.unpack_from('<I', text, rec['value'] - 4)[0]:08x}"


def disassembly(path: Path):
    text = run("llvm-objdump", "-dr", str(path))
    starts = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:", text))
    blocks = {
        m.group(2): text[m.start() : starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        for i, m in enumerate(starts)
    }
    return text, blocks


def calls(block: str) -> list[str]:
    return re.findall(r"R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)", block)


def exports(path: Path) -> set[str]:
    result = set()
    for line in run("llvm-readelf", "-sW", str(path)).splitlines():
        m = re.search(r"\b__ksymtab_(\S+)$", line)
        if m and m.group(1) != "strings":
            result.add(m.group(1))
    return result


def relocations(path: Path):
    rows = []
    current = ""
    for line in run("llvm-readelf", "-rW", str(path)).splitlines():
        m = re.match(r"Relocation section '([^']+)'", line)
        if m:
            current = m.group(1)
            continue
        p = line.split()
        if len(p) >= 5 and re.fullmatch(r"[0-9a-fA-F]+", p[0]) and p[2].startswith("R_AARCH64_"):
            rows.append((current, "0x" + p[0].lower(), p[2], p[4]))
    return rows


def strings(path: Path):
    rows = []
    for line in run("strings", "-a", "-t", "x", str(path)).splitlines():
        p = line.lstrip().split(maxsplit=1)
        if len(p) == 2 and re.fullmatch(r"[0-9a-fA-F]+", p[0]):
            rows.append(("0x" + p[0].lower(), p[1]))
    return rows


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for p in (STOCK, PHASE3P, PHASE3AR):
        if not p.is_file():
            raise FileNotFoundError(p)

    labels = ["stock", "phase3p", "phase3a-r"]
    paths = [STOCK, PHASE3P, PHASE3AR]
    sym = [symbols(p) for p in paths]
    funcs = [x[0] for x in sym]
    objs = [x[1] for x in sym]
    und = [x[2] for x in sym]
    texts = [section(p, ".text") for p in paths]
    dis = [disassembly(p) for p in paths]
    exps = [exports(p) for p in paths]

    function_rows = []
    kcfi_rows = []
    for name in sorted(set().union(*(set(x) for x in funcs))):
        recs = [x.get(name) for x in funcs]
        shared = recs[0] is not None and recs[2] is not None
        byte = False
        call_equal = False
        if shared:
            chunks = [
                texts[i][recs[i]["value"] : recs[i]["value"] + recs[i]["size"]]
                for i in (0, 2)
            ]
            byte = chunks[0] == chunks[1]
            call_equal = Counter(calls(dis[0][1].get(name, ""))) == Counter(calls(dis[2][1].get(name, "")))
        if not recs[0]:
            state = "ISLAND_ONLY"
        elif not recs[2]:
            state = "MISSING"
        elif byte:
            state = "EXACT_BYTE"
        elif recs[0]["size"] == recs[2]["size"] and call_equal:
            state = "SIZE_EXACT_CALLSET_EXACT"
        elif call_equal:
            state = "CALLSET_EXACT"
        else:
            state = "PRESENT"
        function_rows.append([
            name,
            *("ABSENT" if r is None else f"0x{r['value']:x}" for r in recs),
            *("ABSENT" if r is None else r["size"] for r in recs),
            state,
        ])
        kc = [kcfi(texts[i], recs[i]) for i in range(3)]
        kcfi_rows.append([name, *kc, "EXACT" if recs[0] and recs[2] and kc[0] == kc[2] else ("MISSING" if not recs[2] else "DIFF")])

    write_tsv("functions", ["function", "stock offset", "phase3p offset", "phase3a-r offset", "stock size", "phase3p size", "phase3a-r size", "phase3a-r state"], function_rows)
    write_tsv("kcfi-all", ["function", "stock KCFI", "phase3p KCFI", "phase3a-r KCFI", "status"], kcfi_rows)

    import_rows = []
    for name in sorted(set().union(*und)):
        import_rows.append([name, *("yes" if name in x else "no" for x in und), "STOCK" if name in und[0] else "ISLAND_ONLY"])
    write_tsv("imports", ["import", *labels, "provenance"], import_rows)

    export_rows = []
    for name in sorted(set().union(*exps)):
        r0, r1, r2 = (f.get(name) for f in funcs)
        export_rows.append([name, *("yes" if name in x else "no" for x in exps), kcfi(texts[0], r0), kcfi(texts[1], r1), kcfi(texts[2], r2)])
    write_tsv("exports", ["export", *labels, "stock KCFI", "phase3p KCFI", "phase3a-r KCFI"], export_rows)

    object_rows = []
    for name in sorted(set().union(*(set(x) for x in objs))):
        recs = [x.get(name) for x in objs]
        object_rows.append([name, *("ABSENT" if r is None else r["size"] for r in recs), *("ABSENT" if r is None else r["bind"] for r in recs)])
    write_tsv("objects", ["object", "stock size", "phase3p size", "phase3a-r size", "stock bind", "phase3p bind", "phase3a-r bind"], object_rows)

    relocation_rows = []
    for label, path in zip(labels, paths):
        for sec, off, typ, target in relocations(path):
            relocation_rows.append([label, sec, off, typ, target])
    write_tsv("relocations", ["elf", "relocation section", "offset", "type", "target"], relocation_rows)

    call_rows = []
    for name in sorted(set(funcs[0]) | set(funcs[2])):
        sc, nc = calls(dis[0][1].get(name, "")), calls(dis[2][1].get(name, ""))
        call_rows.append([name, ";".join(sc), ";".join(nc), "EXACT" if Counter(sc) == Counter(nc) else "DIFF"])
    write_tsv("callgraph", ["function", "stock callees", "phase3a-r callees", "call multiset"], call_rows)

    string_maps = []
    for path in paths:
        vals = strings(path)
        string_maps.append((vals, {s for _, s in vals}))
    string_rows = []
    for off, s in string_maps[2][0]:
        string_rows.append([off, s, "yes" if s in string_maps[0][1] else "no", "yes" if s in string_maps[1][1] else "no"])
    write_tsv("strings", ["phase3a-r file offset", "string", "in stock", "in phase3p"], string_rows)

    metadata_rows = []
    for label, path in zip(labels, paths):
        metadata_rows.append([label, path.relative_to(REPO), path.stat().st_size, sha(path), len(funcs[labels.index(label)]), len(und[labels.index(label)]), len(exps[labels.index(label)])])
    write_tsv("metadata", ["elf", "path", "size", "sha256", "functions", "imports", "exports"], metadata_rows)

    shared = set(funcs[0]) & set(funcs[2])
    exact = sum(1 for r in function_rows if r[-1] == "EXACT_BYTE")
    kexact = sum(1 for r in kcfi_rows if r[-1] == "EXACT")
    print(f"STOCK_FUNCTIONS={len(funcs[0])}")
    print(f"PHASE3AR_FUNCTIONS={len(funcs[2])}")
    print(f"STOCK_COVERAGE={len(shared)}")
    print(f"STOCK_MISSING={len(set(funcs[0]) - set(funcs[2]))}")
    print(f"BYTE_IDENTICAL={exact}")
    print(f"KCFI_EXACT={kexact}")
    print(f"IMPORTS={len(und[2])}")
    print(f"EXPORTS={len(exps[2])}")
    print(f"PHASE3AR_SHA256={sha(PHASE3AR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
