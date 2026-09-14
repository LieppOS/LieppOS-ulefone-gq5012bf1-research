#!/usr/bin/env python3
"""Generate the GQ5012BF1 tkcore Phase-3B three-way ELF inventory.

Static/offline only.  Compares stock, Phase-3A-R and Phase-3B.
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
BEFORE = REPO / "workspace/phase4-tkcore-island/phase3b/before/tkcore.phase3a-r.ko"
AFTER = REPO / "workspace/phase4-tkcore-island/phase3b/build/tkcore.phase3b.ko"
OUT = REPO / "kernel"

TARGETS = [
    "__tee_shm_attach_dma_buf", "__tee_shm_detach_dma_buf",
    "__tee_shm_dma_buf_map_dma_buf", "__tee_shm_dma_buf_unmap_dma_buf",
    "__tee_shm_dma_buf_mmap", "__tee_shm_dma_buf_release",
    "tee_map_cached_shm", "tee_unmap_cached_shm",
    "tkcore_alloc_shm", "tkcore_shm_get", "tkcore_shm_put", "tkcore_shm_free",
]
TEEC = ["TEEC_RegisterSharedMemory", "TEEC_AllocateSharedMemory",
        "TEEC_ReleaseSharedMemory"]
HELPERS = ["sg_nents", "tee_shm_alloc_io", "tee_shm_free_io",
           "tee_shm_alloc_from_rpc", "tee_shm_free_from_rpc",
           "tee_shm_fd_for_rpc", "tee_context_alloc_shm_tmp"]


def run(*a, binary=False):
    p = subprocess.run(a, capture_output=True, text=not binary)
    return p.stdout if p.returncode == 0 else (b"" if binary else "")


def load(path: Path):
    sym = run("llvm-readelf", "-sW", str(path))
    funcs, objs, und, exp = {}, {}, set(), set()
    for line in sym.splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        if p[6] == "UND":
            if p[7] and p[7] != "0":
                und.add(p[7])
            continue
        if p[7].startswith("$"):
            continue
        try:
            val, size = int(p[1], 16), int(p[2], 0)
        except ValueError:
            continue
        if p[3] == "FUNC":
            funcs[p[7]] = (val, size, p[4])
        elif p[3] == "OBJECT":
            objs[p[7]] = (val, size, p[4])
        m = re.fullmatch(r"__ksymtab_(\S+)", p[7])
        if m and m.group(1) != "strings":
            exp.add(m.group(1))
    text = run("llvm-objcopy", "--dump-section", ".text=/dev/stdout", str(path), binary=True)
    dis = run("llvm-objdump", "-dr", str(path))
    starts = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:", dis))
    blocks = {m.group(2): dis[m.start(): starts[i + 1].start() if i + 1 < len(starts) else len(dis)]
              for i, m in enumerate(starts)}
    return dict(funcs=funcs, objs=objs, und=und, exp=exp, text=text, blocks=blocks)


def kcfi(text: bytes, rec):
    if not rec or rec[0] < 4 or rec[0] > len(text):
        return "ABSENT"
    return "0x%08x" % struct.unpack_from("<I", text, rec[0] - 4)[0]


def calls(blocks, name):
    return Counter(re.findall(r"R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)", blocks.get(name, "")))


def write(name, header, rows):
    path = OUT / f"phase4-tkcore-island-phase3b-{name}.tsv"
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def classify(s, b, a, sb, ab):
    """Acceptance class for a Phase-3B function."""
    if not a:
        return "INCOMPLETE"
    if not s:
        return "ISLAND_ONLY"
    byte = sb == ab
    if byte:
        return "EXACT_BYTE"
    if s[1] == a[1]:
        return "SIZE_EXACT_SEMANTIC_EXACT"
    return "CFG_EQUIVALENT"


def main():
    for p in (STOCK, BEFORE, AFTER):
        if not p.is_file():
            raise FileNotFoundError(p)
    S, B, A = load(STOCK), load(BEFORE), load(AFTER)

    def chunk(E, n):
        r = E["funcs"].get(n)
        return E["text"][r[0]:r[0] + r[1]] if r else None

    # ---- functions (three-way) ----
    rows = []
    for n in sorted(set(S["funcs"]) | set(A["funcs"])):
        s, b, a = S["funcs"].get(n), B["funcs"].get(n), A["funcs"].get(n)
        cls = classify(s, b, a, chunk(S, n), chunk(A, n)) if (s and a) else (
            "MISSING" if s and not a else "ISLAND_ONLY")
        rows.append([n,
                     "ABSENT" if not s else s[1],
                     "ABSENT" if not b else b[1],
                     "ABSENT" if not a else a[1],
                     "yes" if b else "no", "yes" if a else "no", cls])
    write("functions", ["function", "stock size", "phase3a-r size", "phase3b size",
                        "in phase3a-r", "in phase3b", "class"], rows)

    # ---- KCFI (targets + TEEC + helpers) ----
    krows = []
    for n in TARGETS + TEEC + HELPERS:
        s, b, a = S["funcs"].get(n), B["funcs"].get(n), A["funcs"].get(n)
        ks, kb, ka = kcfi(S["text"], s), kcfi(B["text"], b), kcfi(A["text"], a)
        status = "EXACT" if (s and a and ks == ka) else ("MISSING" if not a else "DIFF")
        krows.append([n, ks, kb, ka, status])
    write("kcfi", ["function", "stock KCFI", "phase3a-r KCFI", "phase3b KCFI", "status"], krows)

    # ---- export parity ----
    erows = []
    for n in sorted(S["exp"] | A["exp"]):
        s, a = S["funcs"].get(n), A["funcs"].get(n)
        erows.append([n,
                      "yes" if n in S["exp"] else "no",
                      "yes" if n in B["exp"] else "no",
                      "yes" if n in A["exp"] else "no",
                      kcfi(S["text"], s), kcfi(A["text"], a),
                      "PRESENT" if n in A["exp"] else "MISSING"])
    write("export-parity", ["export", "in stock", "in phase3a-r", "in phase3b",
                            "stock KCFI", "phase3b KCFI", "status"], erows)

    # ---- imports ----
    irows = []
    for n in sorted(S["und"] | A["und"]):
        prov = "STOCK" if n in S["und"] else "ISLAND_ONLY"
        new = "yes" if (n in A["und"] and n not in B["und"]) else "no"
        irows.append([n, "yes" if n in S["und"] else "no",
                      "yes" if n in B["und"] else "no",
                      "yes" if n in A["und"] else "no", new, prov])
    write("imports", ["import", "in stock", "in phase3a-r", "in phase3b",
                      "new in phase3b", "provenance"], irows)

    # ---- objects ----
    orows = []
    for n in sorted(set(S["objs"]) | set(A["objs"])):
        s, b, a = S["objs"].get(n), B["objs"].get(n), A["objs"].get(n)
        orows.append([n, "ABSENT" if not s else s[1], "ABSENT" if not b else b[1],
                      "ABSENT" if not a else a[1]])
    write("objects", ["object", "stock size", "phase3a-r size", "phase3b size"], orows)

    # ---- callgraph for the Phase-3B surface ----
    crows = []
    for n in TARGETS + TEEC + HELPERS:
        sc, ac = calls(S["blocks"], n), calls(A["blocks"], n)
        crows.append([n, ";".join(sorted(sc.elements())), ";".join(sorted(ac.elements())),
                      "EXACT" if sc == ac else "DIFF"])
    write("callgraph", ["function", "stock callees", "phase3b callees", "call multiset"], crows)

    # ---- function progress ----
    prows = []
    for n in TARGETS + TEEC:
        s, b, a = S["funcs"].get(n), B["funcs"].get(n), A["funcs"].get(n)
        cls = classify(s, b, a, chunk(S, n), chunk(A, n))
        prows.append([n, "TARGET_DMABUF" if n.startswith("__tee_shm") else
                      ("TARGET_CACHED_EXPORT" if "cached" in n else
                       ("TARGET_TEEC" if n.startswith("TEEC_") else "TARGET_INTERNAL")),
                      "ABSENT" if not b else "PRESENT",
                      s[1] if s else "-", a[1] if a else "-",
                      kcfi(S["text"], s), kcfi(A["text"], a),
                      "EXACT" if calls(S["blocks"], n) == calls(A["blocks"], n) else "DIFF",
                      cls])
    write("function-progress", ["function", "class", "phase3a-r state", "stock size",
                                "phase3b size", "stock KCFI", "phase3b KCFI",
                                "call multiset", "phase3b acceptance"], prows)

    # ---- metadata ----
    mrows = []
    for label, p, E in (("stock", STOCK, S), ("phase3a-r", BEFORE, B), ("phase3b", AFTER, A)):
        mrows.append([label, p.relative_to(REPO), p.stat().st_size,
                      hashlib.sha256(p.read_bytes()).hexdigest(),
                      len(E["funcs"]), len(E["und"]), len(E["exp"]), len(E["objs"])])
    write("metadata", ["elf", "path", "size", "sha256", "functions", "imports",
                       "exports", "objects"], mrows)

    # ---- summary ----
    shb = set(S["funcs"]) & set(B["funcs"])
    sha_ = set(S["funcs"]) & set(A["funcs"])

    def exact(E):
        return {n for n in set(S["funcs"]) & set(E["funcs"])
                if chunk(S, n) == chunk(E, n)}
    eb, ea = exact(B), exact(A)
    print("STOCK_FUNCTIONS=%d" % len(S["funcs"]))
    print("COVERAGE_BEFORE=%d" % len(shb))
    print("COVERAGE_AFTER=%d" % len(sha_))
    print("MISSING_AFTER=%d" % len(set(S["funcs"]) - set(A["funcs"])))
    print("NEW_STOCK_FUNCTIONS=%s" % sorted(sha_ - shb))
    print("BYTE_IDENTICAL_BEFORE=%d" % len(eb))
    print("BYTE_IDENTICAL_AFTER=%d" % len(ea))
    print("BYTE_REGRESSED=%s" % sorted(eb - ea))
    print("EXPORTS=%d/%d" % (len(A["exp"]), len(S["exp"])))
    print("IMPORTS_AFTER=%d" % len(A["und"]))
    print("NON_STOCK_IMPORTS=%s" % sorted(A["und"] - S["und"]))
    print("TARGETS_INCOMPLETE=%s" % [r[0] for r in prows if r[-1] == "INCOMPLETE"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
