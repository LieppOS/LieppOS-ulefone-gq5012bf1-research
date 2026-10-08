#!/usr/bin/env python3
"""MALI-GPU-KERNEL acceptance: stock (A) vs clean source build B1 (stripped of debug info,
as vendor_dlkm modules are installed). Writes machine-readable ledgers:

  stock-baseline.tsv   per module: every section (name, type, flags, size, sha256) and
                       summary rows (function/data/import/export/KCFI/relocation counts,
                       vermagic, srcversion, build-id, compiler)
  function-parity.tsv  every STT_FUNC symbol-table entry (same-named statics kept apart)
  data-parity.tsv      every sized data object (incl. .bss shape), section + size + bytes
  section-parity.tsv   every section: identical / differs (+ differing byte count)
  abi-parity.tsv       __versions imports (name, CRC), __ksymtab/__kcrctab exports
                       (name, bucket, CRC), KCFI type-id symbols, .modinfo keys
  relocation-parity.tsv per RELA section: semantic multiset (offset, type, symbol name,
                       addend) equality and raw byte equality
  residue.tsv          every differing byte attributed to its section

usage: mali_acceptance.py <stock-dir> <b1-dir> <out-dir>
"""
import collections, hashlib, importlib.util, os, struct, sys
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("kpp", os.environ.get(
    "KPP", "/home/armol/kernel-work/accelerator-mali-gpu-kernel/research/reverse-engineering/scripts/ko-pair-parity.py"))
kpp = importlib.util.module_from_spec(spec); spec.loader.exec_module(kpp)
SDIR, BDIR, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
MODS = ["mtk_gpu_hal", "mtk_gpu_qos", "mtk_gpufreq_wrapper", "mtk_gpufreq_mt6878", "ged",
        "mali_mgm_mt6878_r44", "mali_prot_alloc_mt6878_r44", "mali_kbase_mt6878_r44"]
sha = lambda b: hashlib.sha256(b).hexdigest()
def modinfo(ko):
    d = collections.OrderedDict()
    for x in ko.data(".modinfo").split(b"\0"):
        if b"=" in x:
            k, v = x.decode(errors="replace").split("=", 1); d.setdefault(k, []).append(v)
    return d
def note_buildid(ko):
    b = ko.data(".note.gnu.build-id"); return b[16:].hex() if b else ""
def comment(ko):
    return ko.data(".comment").replace(b"\0", b" ").decode(errors="replace").strip()
def kcfi(ko):
    return {s["n"]: s["val"] & 0xffffffff for s in ko.syms if s["n"].startswith("__kcfi_typeid_")}
def rela_sem(ko):
    out = {}
    for s in ko.secs:
        if s["type"] == 4:
            out[s["n"]] = (collections.Counter((o, i & 0xffffffff, ko.sym_name(i >> 32), a) for o, i, a in ko.rela_entries(s)),
                           ko.b[s["off"]:s["off"] + s["size"]])
    return out
F = {n: open(os.path.join(OUT, n), "w") for n in ["stock-baseline.tsv", "function-parity.tsv", "data-parity.tsv",
     "section-parity.tsv", "abi-parity.tsv", "relocation-parity.tsv", "residue.tsv"]}
F["stock-baseline.tsv"].write("module\trow\tname\ttype\tflags\tsize\tsha256_or_value\n")
F["function-parity.tsv"].write("module\tfunction\tsection+offset\tstock_size\tb1_size\tstock_sha16\tb1_sha16\tresult\n")
F["data-parity.tsv"].write("module\tobject\tstock_section\tb1_section\tstock_size\tb1_size\tstock_sha16\tb1_sha16\tresult\n")
F["section-parity.tsv"].write("module\tsection\tstock_size\tb1_size\tresult\tdiffering_bytes\n")
F["abi-parity.tsv"].write("module\taxis\tname\tstock\tb1\tresult\n")
F["relocation-parity.tsv"].write("module\trela_section\tentries\tsemantic\traw_bytes\n")
F["residue.tsv"].write("module\tsection\tdiffering_bytes\tclassification\n")
summary = []
for m in MODS:
    A = kpp.KO(os.path.join(SDIR, m + ".ko")); B = kpp.KO(os.path.join(BDIR, m + ".stripped"))
    fa, fb = kpp.functions(A), kpp.functions(B); oa, ob = kpp.objects(A), kpp.objects(B)
    va, _ = kpp.versions(A); vb, _ = kpp.versions(B); ea, eb = kpp.exports(A), kpp.exports(B)
    ma, mb = modinfo(A), modinfo(B); ka, kb = kcfi(A), kcfi(B); ra, rb = rela_sem(A), rela_sem(B)
    bl = F["stock-baseline.tsv"]
    for s in A.secs[1:]:
        bl.write(f"{m}\tsection\t{s['n']}\t{s['type']}\t-\t{s['size']}\t{'-' if s['type'] == 8 else sha(A.data(s['n']))}\n")
    for k, v in [("sha256", sha(A.b)), ("bytes", len(A.b)), ("functions", len(fa)), ("data_objects", len(oa)),
                 ("imports", len(va)), ("exports", len(ea)), ("kcfi_typeid_symbols", len(ka)),
                 ("rela_entries", sum(sum(c.values()) for c, _ in ra.values())),
                 ("vermagic", ma.get("vermagic", [""])[0]), ("srcversion", ma.get("srcversion", [""])[0]),
                 ("build_id", note_buildid(A)), ("compiler", comment(A)),
                 ("llvm_addrsig", ".llvm_addrsig" in A.sec_by_name), ("signed", A.b.endswith(b"~Module signature appended~\n"))]:
        bl.write(f"{m}\tsummary\t{k}\t-\t-\t-\t{v}\n")
    def funcs(ko):  # every STT_FUNC entry (same-named statics kept apart), keyed by (section, offset)
        r = {}
        for y in ko.syms:
            if y["info"] & 0xf != 2 or y["shndx"] in (0, 0xfff1): continue
            sec = ko.secs[y["shndx"]]
            r[(sec["n"], y["val"], y["n"])] = (y["size"], ko.b[sec["off"] + y["val"]:sec["off"] + y["val"] + y["size"]])
        return r
    fa, fb = funcs(A), funcs(B)
    nf = collections.Counter()
    for key in sorted(set(fa) | set(fb)):
        a, b = fa.get(key), fb.get(key)
        r = "MISSING_IN_B1" if not b else "UNEXPECTED_IN_B1" if not a else "BYTE_IDENTICAL" if a == b else "SIZE_ONLY" if a[0] == b[0] else "DIFFERENT"
        nf[r] += 1
        F["function-parity.tsv"].write(f"{m}\t{key[2]}\t{key[0]}+{key[1]:#x}\t{a[0] if a else '-'}\t{b[0] if b else '-'}\t"
                                       f"{sha(a[1])[:16] if a else '-'}\t{sha(b[1])[:16] if b else '-'}\t{r}\n")
    nd = collections.Counter()
    for n in sorted(set(oa) | set(ob)):
        a, b = oa.get(n), ob.get(n)
        r = "MISSING_IN_B1" if not b else "UNEXPECTED_IN_B1" if not a else "IDENTICAL" if a == b else "DIFFERENT"
        if r == "DIFFERENT" and n.startswith("__UNIQUE_ID_srcversion"): r = "DIFFERENT(srcversion)"
        nd[r] += 1
        F["data-parity.tsv"].write(f"{m}\t{n}\t{a[0] if a else '-'}\t{b[0] if b else '-'}\t{a[1] if a else '-'}\t{b[1] if b else '-'}\t{a[2] if a else '-'}\t{b[2] if b else '-'}\t{r}\n")
    ns = collections.Counter(); res = collections.Counter()
    for s in A.secs[1:]:
        t = B.sec(s["n"]); da = A.data(s["n"]); db = B.data(s["n"]) if t else b""
        if not t: r, d = "MISSING_IN_B1", s["size"]
        elif s["type"] == 8: r, d = ("IDENTICAL" if s["size"] == t["size"] else "DIFFERENT"), 0
        else:
            d = sum(x != y for x, y in zip(da, db)) + abs(len(da) - len(db)); r = "IDENTICAL" if da == db else "DIFFERENT"
        ns[r] += 1
        F["section-parity.tsv"].write(f"{m}\t{s['n']}\t{s['size']}\t{t['size'] if t else '-'}\t{r}\t{d}\n")
    for s in B.secs[1:]:
        if not A.sec(s["n"]): ns["UNEXPECTED_IN_B1"] += 1; F["section-parity.tsv"].write(f"{m}\t{s['n']}\t-\t{s['size']}\tUNEXPECTED_IN_B1\t{s['size']}\n")
    # residue: every differing file byte -> section
    if len(A.b) == len(B.b):
        spans = sorted((s["off"], s["off"] + (0 if s["type"] == 8 else s["size"]), s["n"]) for s in A.secs[1:])
        for i, (x, y) in enumerate(zip(A.b, B.b)):
            if x != y:
                res[next((n for lo, hi, n in spans if lo <= i < hi), "<ELF/section headers>")] += 1
    else:
        res["<size differs>"] = abs(len(A.b) - len(B.b))
    for sec, n in sorted(res.items()):
        cls = {".note.gnu.build-id": "PROVENANCE: GNU build-id (sha1 over the linked output incl. build-host DWARF paths)",
               ".modinfo": "PROVENANCE: srcversion (MD4 of source text; see source-lineage.md)"}.get(sec, "UNEXPLAINED")
        F["residue.tsv"].write(f"{m}\t{sec}\t{n}\t{cls}\n")
    ab = F["abi-parity.tsv"]; na = collections.Counter()
    for n in sorted(set(va) | set(vb)):
        r = "IDENTICAL" if va.get(n) == vb.get(n) else "DIFFERENT"; na["import:" + r] += 1
        ab.write(f"{m}\timport_crc\t{n}\t{va.get(n, '-') if n not in va else hex(va[n])}\t{hex(vb[n]) if n in vb else '-'}\t{r}\n")
    for n in sorted(set(ea) | set(eb)):
        r = "IDENTICAL" if ea.get(n) == eb.get(n) else "DIFFERENT"; na["export:" + r] += 1
        ab.write(f"{m}\texport\t{n}\t{ea.get(n)}\t{eb.get(n)}\t{r}\n")
    for n in sorted(set(ka) | set(kb)):
        r = "IDENTICAL" if ka.get(n) == kb.get(n) else "DIFFERENT"; na["kcfi:" + r] += 1
        ab.write(f"{m}\tkcfi_typeid\t{n}\t{hex(ka[n]) if n in ka else '-'}\t{hex(kb[n]) if n in kb else '-'}\t{r}\n")
    for k in sorted(set(ma) | set(mb)):
        r = "IDENTICAL" if ma.get(k) == mb.get(k) else "DIFFERENT"; na["modinfo:" + r] += 1
        ab.write(f"{m}\tmodinfo\t{k}\t{';'.join(ma.get(k, []))[:200]}\t{';'.join(mb.get(k, []))[:200]}\t{r}\n")
    nr = collections.Counter()
    for n in sorted(set(ra) | set(rb)):
        a, b = ra.get(n), rb.get(n)
        sem = "IDENTICAL" if a and b and a[0] == b[0] else "DIFFERENT"; raw = "IDENTICAL" if a and b and a[1] == b[1] else "DIFFERENT"
        nr[sem] += 1
        F["relocation-parity.tsv"].write(f"{m}\t{n}\t{sum(a[0].values()) if a else '-'}\t{sem}\t{raw}\n")
    summary.append((m, len(fa), dict(nf), dict(nd), dict(ns), dict(na), dict(nr), dict(res)))
for f in F.values(): f.close()
for m, n, nf, nd, ns, na, nr, res in summary:
    print(f"{m}: functions={n} {nf} | data {nd} | sections {ns} | abi {na} | rela {nr} | residue {res}")
