#!/usr/bin/env python3
"""Fail-closed verifier for GQ5012BF1 tkcore island Phase 3B.

Certifies only that the Linux-side shared-memory / dma-buf subsystem is
statically reconstructed against the stock oracle.  It does NOT certify tkcore
complete, replacement-ready, runtime validated, secure-world tested, or
naturally linked by its consumers.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KERNEL = REPO / "kernel"
PH = REPO / "workspace/phase4-tkcore-island/phase3b"
STOCK = REPO / "workspace/phase4-tkcore/oracle/tkcore.ko"
BEFORE = PH / "before/tkcore.phase3a-r.ko"
AFTER = PH / "build/tkcore.phase3b.ko"
GKI = Path("/home/armol/kernel-work/gki-12901745-workspace")
COMMON = GKI / "common"
ISLAND = GKI / "lieppos/tkcore-island"
TRUSTKERNEL = GKI / "lieppos/trustkernel"

STOCK_SHA = "03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226"
BEFORE_SHA = "9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b"
AFTER_SHA = "860ad5ee0c4da579627c202b19892b20e44ef34287054f11ab802b09e9933640"
COMMON_COMMIT = "6b18f0b574ab3267615ae6ce642d5a7c3c21ac09"
KLEAF_BYPRODUCTS = {"tools/bpf/resolve_btfids/libsubcmd/"}

DMABUF = ["__tee_shm_attach_dma_buf", "__tee_shm_detach_dma_buf",
          "__tee_shm_dma_buf_map_dma_buf", "__tee_shm_dma_buf_unmap_dma_buf",
          "__tee_shm_dma_buf_mmap", "__tee_shm_dma_buf_release"]
CACHED = ["tee_map_cached_shm", "tee_unmap_cached_shm"]
INTERNAL = ["tkcore_alloc_shm", "tkcore_shm_get", "tkcore_shm_put", "tkcore_shm_free"]
TWELVE = DMABUF + CACHED + INTERNAL
TEEC = ["TEEC_RegisterSharedMemory", "TEEC_AllocateSharedMemory",
        "TEEC_ReleaseSharedMemory"]
ACCEPTED = {"EXACT_BYTE", "SIZE_EXACT_SEMANTIC_EXACT", "CFG_EQUIVALENT",
            "SEMANTIC_HIGH_CONFIDENCE"}
# Stock dma_buf_ops slot -> callback.  Android GKI puts mmap at +0x60.
OPS_SLOTS = {0x08: "__tee_shm_attach_dma_buf", 0x10: "__tee_shm_detach_dma_buf",
             0x28: "__tee_shm_dma_buf_map_dma_buf",
             0x30: "__tee_shm_dma_buf_unmap_dma_buf",
             0x38: "__tee_shm_dma_buf_release", 0x60: "__tee_shm_dma_buf_mmap"}

checks: list[tuple[str, bool, str]] = []


def ck(name: str, ok: bool, detail: object = "") -> None:
    checks.append((name, bool(ok), str(detail)))


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(*a, cwd=None, binary=False):
    p = subprocess.run(a, cwd=cwd, capture_output=True, text=not binary)
    return (b"" if binary else "") if p.returncode else p.stdout


def elf(path: Path):
    sym = run("llvm-readelf", "-sW", str(path))
    funcs, und, exp = {}, set(), set()
    for line in sym.splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        if p[6] == "UND":
            if p[7] and p[7] != "0":
                und.add(p[7])
            continue
        if p[3] == "FUNC":
            funcs[p[7]] = (int(p[1], 16), int(p[2]), p[4])
        m = re.fullmatch(r"__ksymtab_(\S+)", p[7])
        if m and m.group(1) != "strings":
            exp.add(m.group(1))
    text = run("llvm-objcopy", "--dump-section", ".text=/dev/stdout", str(path), binary=True)
    dis = run("llvm-objdump", "-dr", str(path))
    st = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:", dis))
    blocks = {m.group(2): dis[m.start(): st[i + 1].start() if i + 1 < len(st) else len(dis)]
              for i, m in enumerate(st)}
    return funcs, text, und, exp, blocks


def kcfi(text, rec):
    return struct.unpack_from("<I", text, rec[0] - 4)[0] if rec and rec[0] >= 4 else None


def calls(blocks, n):
    return Counter(re.findall(r"R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)", blocks.get(n, "")))


def tsv(name):
    p = KERNEL / name
    if not p.is_file():
        return None
    with p.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def body(source: str, name: str) -> str:
    for m in re.finditer(r"\b" + re.escape(name) + r"\s*\(", source):
        op = source.find("(", m.start())
        depth, cp = 0, -1
        for i in range(op, len(source)):
            if source[i] == "(":
                depth += 1
            elif source[i] == ")":
                depth -= 1
                if depth == 0:
                    cp = i
                    break
        if cp < 0:
            continue
        b = cp + 1
        while b < len(source) and source[b].isspace():
            b += 1
        if b >= len(source) or source[b] != "{":
            continue
        start = source.rfind("\n", 0, m.start()) + 1
        depth = 0
        for i in range(b, len(source)):
            if source[i] == "{":
                depth += 1
            elif source[i] == "}":
                depth -= 1
                if depth == 0:
                    return source[start:i + 1]
    return ""


def ops_table(path: Path, name="tee_static_shm_dma_buf_ops"):
    """Return {slot_offset: target_function} for the ops table in `path`."""
    sym = run("llvm-readelf", "-sW", str(path))
    base = size = None
    addr2fn = {}
    for line in sym.splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        if p[3] == "FUNC" and p[6] != "UND":
            addr2fn[int(p[1], 16)] = p[7]
        if p[7] == name and p[3] == "OBJECT":
            base, size = int(p[1], 16), int(p[2], 0)
    if base is None:
        return None, None
    got, cur = {}, ""
    for line in run("llvm-readelf", "-rW", str(path)).splitlines():
        m = re.match(r"Relocation section '([^']+)'", line)
        if m:
            cur = m.group(1)
            continue
        p = line.split()
        if len(p) < 4 or not re.fullmatch(r"[0-9a-fA-F]+", p[0]) or cur != ".rela.rodata":
            continue
        off = int(p[0], 16)
        if not (base <= off < base + size):
            continue
        mm = re.search(r"([0-9a-fA-F]+)\s*$", line)
        if mm:
            got[off - base] = addr2fn.get(int(mm.group(1), 16), "?")
    return got, size


def main() -> None:
    # ---------- binary identity ----------
    for label, p, want in (("stock", STOCK, STOCK_SHA), ("Phase-3A-R", BEFORE, BEFORE_SHA),
                           ("Phase-3B", AFTER, AFTER_SHA)):
        ck(f"{label} ELF present", p.is_file())
        ck(f"{label} SHA256 exact", p.is_file() and sha256(p) == want,
           sha256(p) if p.is_file() else "missing")

    # ---------- baseline ----------
    ck("Phase-3A-R acceptance report exists",
       len(read(KERNEL / "phase4-tkcore-island-phase3a-r-acceptance.md")) > 500)
    ck("Phase-3A-R source hashes recorded",
       (REPO / "workspace/phase4-tkcore-island/phase3a-r/interrupted-checkpoint/source-hashes.tsv").is_file())
    ck("Phase-3B baseline build log frozen", len(read(PH / "before/build.log")) > 0)
    ck("Phase-3B baseline source hashes frozen", (PH / "before/source-hashes.tsv").is_file())
    ck("RED evidence preserved",
       len(read(KERNEL / "phase4-tkcore-island-phase3b-RED.md")) > 1000)

    head = run("git", "rev-parse", "HEAD", cwd=COMMON).strip()
    porcelain = [l for l in run("git", "status", "--porcelain", cwd=COMMON).splitlines() if l.strip()]
    tracked = [l for l in porcelain if not l.startswith("??")]
    untracked = {l[3:].strip() for l in porcelain if l.startswith("??")}
    ck("common at exact GKI commit", head == COMMON_COMMIT, head)
    ck("common exact-GKI tracked source unmodified", not tracked, tracked)
    ck("common untracked residue limited to known kleaf byproduct",
       untracked <= KLEAF_BYPRODUCTS, sorted(untracked - KLEAF_BYPRODUCTS))

    if not all(p.is_file() for p in (STOCK, BEFORE, AFTER)):
        report()
        return

    sf, st, su, se, sb = elf(STOCK)
    bf, bt, bu, be, bb = elf(BEFORE)
    af, at, au, ae, ab = elf(AFTER)

    # ---------- the 12 missing functions must now exist ----------
    for n in TWELVE:
        ck(f"present: {n}", n in af)
    ck("all 12 SHM targets present", all(n in af for n in TWELVE),
       [n for n in TWELVE if n not in af])

    # ---------- ABI + call parity for every in-scope function ----------
    for n in TWELVE + TEEC + ["sg_nents"]:
        if n not in af or n not in sf:
            ck(f"ABI comparable: {n}", False, "absent")
            continue
        ck(f"KCFI exact: {n}", kcfi(st, sf[n]) == kcfi(at, af[n]),
           f"stock={kcfi(st, sf[n])} island={kcfi(at, af[n])}")
        ck(f"call multiset exact: {n}", calls(sb, n) == calls(ab, n))

    # byte-identical set that must hold
    for n in DMABUF + CACHED + ["tkcore_shm_get", "TEEC_RegisterSharedMemory", "sg_nents"]:
        ok = (n in sf and n in af and
              st[sf[n][0]:sf[n][0] + sf[n][1]] == at[af[n][0]:af[n][0] + af[n][1]])
        ck(f"byte-identical: {n}", ok)

    # stock symbol binding classes
    for n in DMABUF:
        ck(f"static (LOCAL) like stock: {n}", n in af and af[n][2] == "LOCAL",
           af.get(n, ("", "", "?"))[2])
    for n in INTERNAL:
        ck(f"GLOBAL like stock: {n}", n in af and af[n][2] == "GLOBAL",
           af.get(n, ("", "", "?"))[2])

    # ---------- dma_buf_ops table ----------
    got, size = ops_table(AFTER)
    ck("ops table tee_static_shm_dma_buf_ops present", got is not None)
    if got is not None:
        ck("ops table size 144 like stock", size == 144, size)
        ck("ops table slot offsets match stock", sorted(got) == sorted(OPS_SLOTS),
           f"got={sorted(got)} want={sorted(OPS_SLOTS)}")
        for off, want in OPS_SLOTS.items():
            ck(f"ops slot +0x{off:02x} -> {want}", got.get(off) == want, got.get(off))
        ck("no vmap/vunmap slot populated (stock has none)",
           not (set(got) - set(OPS_SLOTS)), sorted(set(got) - set(OPS_SLOTS)))
    sgot, _ = ops_table(STOCK)
    ck("island ops slots equal stock ops slots",
       sgot is not None and got is not None and sorted(sgot) == sorted(got))

    # ---------- public TEEC SHM acceptance ----------
    prog = tsv("phase4-tkcore-island-phase3b-function-progress.tsv")
    ck("function-progress table exists", prog is not None)
    cls = {r["function"]: r["phase3b acceptance"] for r in prog or []}
    for n in TWELVE + TEEC:
        ck(f"accepted (not INCOMPLETE): {n}", cls.get(n) in ACCEPTED, cls.get(n, "missing"))
    ck("no in-scope function INCOMPLETE",
       not [n for n in TWELVE + TEEC if cls.get(n) == "INCOMPLETE"])

    # ---------- source-level correctness the ELF cannot show ----------
    shm_src = read(ISLAND / "tkcore/tee_shm.c")
    api_src = read(ISLAND / "tkcore/tee_kernel_api.c")
    ck("live tee_shm.c present", len(shm_src) > 10000)
    ck("live tee_kernel_api.c present", len(api_src) > 5000)
    ck("donor dma-buf names fully removed",
       not re.search(r"(?<![_\w])_tee_shm_(attach|detach|dma_buf)", shm_src))
    ck("donor vmap/vunmap callbacks removed",
       "_tee_shm_dma_buf_vmap" not in shm_src and "_tee_shm_dma_buf_vunmap" not in shm_src)
    ck("ops table is const", "const struct dma_buf_ops tee_static_shm_dma_buf_ops" in shm_src)
    ck("ops table uses designated initialisers (not hardcoded offsets)",
       ".map_dma_buf" in shm_src and ".unmap_dma_buf" in shm_src and ".mmap" in shm_src)

    alloc_io = body(shm_src, "tee_shm_alloc_io")
    ck("tee_shm_alloc_io publishes shm through shm_io->buffer",
       "shm_io->buffer = shm" in alloc_io)
    tka = body(shm_src, "tkcore_alloc_shm")
    ck("tkcore_alloc_shm assigns shm->tee guarded and last",
       "IS_ERR_OR_NULL(shm)" in tka and tka.rstrip().rindex("shm->tee = tee") > tka.rindex("sg_alloc_table_from_pages"))
    tkf = body(shm_src, "tkcore_shm_free")
    ck("tkcore_shm_free BUGs on NULL tee like stock", "BUG()" in tkf)
    tkp = body(shm_src, "tkcore_shm_put")
    ck("tkcore_shm_put validates ctx before use",
       "BUG_ON(!ctx)" in tkp and "BUG_ON(!ctx->tee)" in tkp and "BUG_ON(!shm)" in tkp)
    ck("tkcore_shm_put never frees the exporter's sg_table",
       "sg_free_table" not in tkp)

    alloc = body(api_src, "TEEC_AllocateSharedMemory")
    ck("TEEC_AllocateSharedMemory zeroes shm_io", "memset(&shm_io, 0, sizeof(shm_io))" in alloc)
    ck("TEEC_AllocateSharedMemory reads shm_io.buffer not fd_shm",
       "shm_io.buffer" in alloc and "shm_io.fd_shm" not in alloc)
    ck("TEEC_AllocateSharedMemory does not truncate the handle",
       "(long)" not in alloc and "d.fd" not in alloc)
    rel = body(api_src, "TEEC_ReleaseSharedMemory")
    ck("TEEC_ReleaseSharedMemory guards on TEEC_MEM_KAPI", "TEEC_MEM_KAPI" in rel)
    ck("TEEC_ReleaseSharedMemory checks registered BEFORE the KAPI guard",
       rel.index("registered") < rel.index("TEEC_MEM_KAPI"))
    ck("TEEC_ReleaseSharedMemory uses the 64-bit handle",
       "d.ptr" in rel and "d.fd" not in rel)
    reg = body(api_src, "TEEC_RegisterSharedMemory")
    ck("TEEC_RegisterSharedMemory clears d and sets registered",
       "d.fd = 0" in reg and "registered = 1" in reg)

    # ---------- layout ----------
    la = read(TRUSTKERNEL / "include/trustkernel/layout-assert.h")
    anchors = len(re.findall(r"(?m)^TK_ASSERT", la))
    ck("layout anchors preserved and extended (>=83)", anchors >= 83, anchors)
    for a in ("TK_ASSERT_SIZE(struct tee_shm, 0x68)",
              "TK_ASSERT_OFF(struct tee_shm, sgt, 0x50)",
              "TK_ASSERT_OFF(struct tee_shm, sdb, 0x60)",
              "TK_ASSERT_SIZE(struct tee_shm_dma_buf, 0x18)",
              "TK_ASSERT_OFF(TEEC_SharedMemory, d, 0x18)",
              "TK_ASSERT_OFF(struct dma_buf, priv, 0xa0)",
              "TK_ASSERT_OFF(struct dma_buf_ops, mmap, 0x60)"):
        ck(f"new SHM anchor present: {a}", a in la)
    for a in ("TK_ASSERT_SIZE(struct tee, 0x138)",
              "TK_ASSERT_SIZE(struct tee_context, 0xd0)",
              "TK_ASSERT_SIZE(TEEC_Context, 0x108)",
              "TK_ASSERT_SIZE(TEEC_SharedMemory, 0x28)"):
        ck(f"pre-existing anchor preserved: {a}", a in la)
    ck("island-local tee_shm_io anchors asserted in source",
       "sizeof(struct tee_shm_io) == 0x18" in shm_src)
    ck("layout probe ELF frozen", (PH / "build/tk_layout_probe.phase3b.ko").is_file())

    # ---------- exports ----------
    for n in CACHED:
        ck(f"export present: {n}", n in ae)
    ck("no fabricated export", not (ae - se), sorted(ae - se))
    ck("export count 21/25", len(ae) == 21 and len(se) == 25, f"{len(ae)}/{len(se)}")
    ep = tsv("phase4-tkcore-island-phase3b-export-parity.tsv")
    ck("export parity table exists", ep is not None)

    # ---------- static consumer traces ----------
    tmem = read(KERNEL / "phase4-tkcore-island-phase3b-tmem-shm-trace.md")
    drv = read(KERNEL / "phase4-tkcore-island-phase3b-tkcore-drv-shm-trace.md")
    ck("tmem SHM trace PASS_STATIC_SHM", "**Result: PASS_STATIC_SHM**" in tmem)
    ck("tmem trace covers Register and Release",
       "TEEC_RegisterSharedMemory" in tmem and "TEEC_ReleaseSharedMemory" in tmem)
    ck("tkcore_drv SHM trace PASS_STATIC_SHM", "**Result: PASS_STATIC_SHM**" in drv)
    ck("tkcore_drv trace accounts unreferenced export", "NOT_CALLED" in drv)
    # re-derive both traces from the frozen consumers, fail closed on mismatch
    for label, ko, fn, want in (
            ("tmem_ffa", PH / "tmem_ffa.objdump.txt", "tee_session_open",
             ["TEEC_InitializeContext", "TEEC_RegisterSharedMemory", "TEEC_OpenSession"]),
            ("tmem_ffa", PH / "tmem_ffa.objdump.txt", "tee_session_close",
             ["TEEC_CloseSession", "TEEC_ReleaseSharedMemory", "TEEC_FinalizeContext"])):
        d = read(ko)
        stt = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:", d))
        B = {m.group(2): d[m.start(): stt[i + 1].start() if i + 1 < len(stt) else len(d)]
             for i, m in enumerate(stt)}
        seq = [c for c in re.findall(r"R_AARCH64_CALL26\s+(\S+)", B.get(fn, ""))
               if c.startswith("TEEC_")]
        idx = [seq.index(w) for w in want if w in seq]
        ck(f"{label}:{fn} order {' -> '.join(want)}",
           len(idx) == len(want) and idx == sorted(idx), seq)
    ddrv = read(PH / "tkcore_drv.objdump.txt")
    ck("tkcore_drv calls tee_map_cached_shm", "tee_map_cached_shm" in ddrv)
    ck("tkcore_drv genuinely never calls tee_unmap_cached_shm",
       not re.search(r"R_AARCH64_CALL26\s+tee_unmap_cached_shm", ddrv))

    # ---------- build ----------
    env = {}
    for line in read(PH / "build/final-build-result.env").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
    for k in ("BUILD_RC", "COMPILER_WARNINGS", "COMPILER_ERRORS", "MODPOST_WARNINGS",
              "UNRESOLVED", "STATIC_ASSERT_FAILURES"):
        ck(f"final build {k}=0", env.get(k) == "0", env.get(k, "missing"))
    blog = read(PH / "build/final-build.log")
    ck("final build log frozen", len(blog) > 0)
    ck("final build reported success", "Build completed successfully" in blog)
    diags = [l for l in blog.splitlines()
             if re.search(r"(?i)\b(?:warning|error):", l) and "SSL error" not in l]
    ck("final build has no compiler diagnostics", not diags, diags[:3])
    ck("final build has no unresolved symbol", "undefined!" not in blog)
    modinfo = run("llvm-objcopy", "--dump-section", ".modinfo=/dev/stdout", str(AFTER),
                  binary=True).decode(errors="ignore")
    ck("module depends empty", any(x == "depends=" for x in modinfo.split("\x00")))
    ck("module license GPL", "license=GPL" in modinfo)

    # ---------- regression ----------
    shb, sha_ = set(sf) & set(bf), set(sf) & set(af)
    ck("stock coverage increased 91 -> 104", len(shb) == 91 and len(sha_) == 104,
       f"{len(shb)} -> {len(sha_)}")
    ck("18 stock functions remain missing", len(set(sf) - set(af)) == 18,
       len(set(sf) - set(af)))
    ck("no stock function regressed", not (shb - sha_), sorted(shb - sha_))
    ck("island defines no non-stock function", not (set(af) - set(sf)),
       sorted(set(af) - set(sf)))

    def exact(f, t):
        return {n for n in set(sf) & set(f)
                if st[sf[n][0]:sf[n][0] + sf[n][1]] == t[f[n][0]:f[n][0] + f[n][1]]}
    eb, ea = exact(bf, bt), exact(af, at)
    ck("byte-identical increased 33 -> 44", len(eb) == 33 and len(ea) == 44,
       f"{len(eb)} -> {len(ea)}")
    ck("no byte-identical regression", not (eb - ea), sorted(eb - ea))
    kb = {n for n in shb if kcfi(st, sf[n]) == kcfi(bt, bf[n])}
    ka = {n for n in sha_ if kcfi(st, sf[n]) == kcfi(at, af[n])}
    ck("no KCFI regression", not (kb - ka), sorted(kb - ka))
    ck("every new import exists in stock", not (au - bu - su), sorted(au - bu - su))
    ck("island-only imports limited to the pre-existing _dev_err",
       (au - su) <= {"_dev_err"}, sorted(au - su))
    ck("sg_nents no longer imported", "sg_nents" not in au)
    ck("regression report exists",
       len(read(KERNEL / "phase4-tkcore-island-phase3b-regression.md")) > 1000)

    # ---------- forbidden techniques ----------
    tree, binaries = "", []
    for root in (ISLAND, TRUSTKERNEL):
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in {".o", ".ko"}:
                binaries.append(str(p))
            if p.is_file() and (p.suffix in {".c", ".h", ".bazel"} or p.name == "Makefile"):
                tree += "\n" + read(p)
    ck("no CRC injection", "__crc_" not in tree and "kcrctab" not in tree)
    ck("no __versions edit", "__versions" not in tree)
    ck("no ELF patch tooling", not re.search(r"\b(?:objcopy|patchelf)\b", tree))
    ck("no KBUILD_MODPOST_WARN",
       not re.search(r"(?m)^\s*(?:export\s+)?KBUILD_MODPOST_WARN\s*[:+?]?=", tree))
    ck("no forced symvers fabrication",
       "symvers" not in tree.lower() or not re.search(r"(?m)^\s*\S*symvers\s*[:+?]?=", tree))
    ck("no stock object inclusion",
       not binaries and ".stock.ko" not in tree and "/oracle/" not in tree, binaries)
    ck("no speculative success stub in SHM sources",
       "TODO" not in shm_src and "FIXME" not in shm_src)

    # ---------- reports + frozen status ----------
    for name in ("phase4-tkcore-island-phase3b-baseline.md",
                 "phase4-tkcore-island-phase3b-RED.md",
                 "phase4-tkcore-island-phase3b-scope.tsv",
                 "phase4-tkcore-shm-layout.md",
                 "phase4-tkcore-shm-lifetime.md",
                 "phase4-tkcore-shm-dmabuf-contract.md",
                 "phase4-tkcore-shm-internal-contract.md",
                 "phase4-tkcore-cached-shm-contract.md",
                 "phase4-tkcore-teec-shm-contract.md",
                 "phase4-tkcore-shm-context-teardown.md",
                 "phase4-tkcore-island-phase3b-tmem-shm-trace.md",
                 "phase4-tkcore-island-phase3b-tkcore-drv-shm-trace.md",
                 "phase4-tkcore-island-phase3b-acceptance.md",
                 "phase4-tkcore-island-phase3b-regression.md"):
        ck(f"report present: {name}", len(read(KERNEL / name)) > 400)
    acc = read(KERNEL / "phase4-tkcore-island-phase3b-acceptance.md")
    ck("overall status still PARTIAL", "Overall tkcore: **PARTIAL**" in acc)
    ck("still NOT RUNTIME READY", "Runtime readiness: **NOT RUNTIME READY**" in acc)
    ck("stock runtime provider retained", "Runtime provider: **STOCK RUNTIME PROVIDER**" in acc)
    ck("not declared replacement ready", "Replacement ready: **NO**" in acc)
    queue = read(KERNEL / "phase4-tkcore-island-phase3-work-queue.md")
    # The work queue is a LIVE shared document that every later phase updates.
    # Pinning the literal Phase-3B count here would assert that no later phase
    # may ever record progress.  Assert instead that the queue still records a
    # coverage figure, that it never regressed below the 104/122 Phase 3B
    # achieved, and that Phase 3B's own closure is still credited.
    m = re.search(r"(\d+)(?:/122| of the 122) stock functions", queue)
    ck("work queue records a stock-function coverage figure", m is not None)
    ck("work queue coverage never regressed below Phase 3B's 104/122",
       m is not None and int(m.group(1)) >= 104,
       m.group(1) if m else "absent")
    ck("work queue still credits the Phase 3B shared-memory closure",
       "shared memory" in queue and "closed in Phase 3B" in queue)
    ck("work queue marks shared memory closed",
       "0 function(s) remaining (all 12 closed in Phase 3B)" in queue)

    report()


def report() -> None:
    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(f"[{'OK' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not ok else ""))
    print("=" * 72)
    print(f"{len(checks) - len(bad)}/{len(checks)} CHECKS PASSED")
    if bad:
        print("TKCORE_ISLAND_PHASE3B_VERIFICATION_FAILED")
        raise SystemExit(1)
    print("TKCORE_ISLAND_PHASE3B_SHARED_MEMORY_CLOSED")
    print("TKCORE_REPLACEMENT_READY=NO")
    print("STOCK_TKCORE_RUNTIME_DEPENDENCY=STILL_PRESENT")


if __name__ == "__main__":
    main()
