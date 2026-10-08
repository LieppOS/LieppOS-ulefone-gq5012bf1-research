#!/usr/bin/env python3
"""For files taken from a newer revision (NEW) on top of an older base (OLD), list the
atomic (-U0) hunks, drop those invisible to modpost's srcversion parser, and for the
rest test whether reverting the hunk alone changes the compiled module (stripped .ko,
excluding .modinfo srcversion and build-id). Hunks that change neither code nor data
but do change srcversion are the free variables of the srcversion search.

usage: hunk_probe.py <tree-midgard-dir> <old-rev> <new-rev> <relpath>... > report.tsv
"""
import os, re, subprocess, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcversion as SV
W = "/home/armol/kernel-work/accelerator-mali-gpu-kernel"
N = "/home/armol/kernel-work/public-mtk/nkm.git"
P = "gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/gpu/arm/midgard/"
T, OLD, NEW, *files = sys.argv[1:]
tree = T.split("/gpu_mali/")[0]
CLANG = "/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin"
KO = os.path.join(T, "mali_kbase_mt6878_r44.ko")

def show(rev, f): return subprocess.run(["git", "-C", N, "show", f"{rev}:{P}{f}"], capture_output=True).stdout
def stream(b): o = bytearray(); SV.parse_file(b, o); return bytes(o)
def build():
    r = subprocess.run([f"{W}/scripts/kb.sh", "gpu", "-j16", "modules",
                        f"KBUILD_EXTRA_SYMBOLS={W}/build/kdm/Module.symvers {W}/symvers/stock-external-provider.symvers"],
                       env=dict(os.environ, GPU_DIR=tree), capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stdout[-3000:] + r.stderr[-3000:])
    subprocess.run([f"{CLANG}/llvm-strip", "--strip-debug", "-o", "/tmp/hp.ko", KO], check=True)
    subprocess.run([f"{CLANG}/llvm-objcopy", "--remove-section=.modinfo", "--remove-section=.note.gnu.build-id", "/tmp/hp.ko", "/tmp/hp2.ko"], check=True)
    return hashlib.sha256(open("/tmp/hp2.ko", "rb").read()).hexdigest()

base = build()
print("file\thunk\told_lines\tnew_lines\tsrcversion_visible\tcode_visible\tsummary", flush=True)
for f in files:
    old = show(OLD, f).decode(errors="surrogateescape").split("\n")
    new = show(NEW, f).decode(errors="surrogateescape").split("\n")
    diff = subprocess.run(["git", "-C", N, "diff", "-U0", OLD, NEW, "--", P + f], capture_output=True, text=True, errors="surrogateescape").stdout
    hunks = [tuple(int(x or 1) if x != "" else 1 for x in m.groups()) for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", diff, re.M)]
    raw = re.findall(r"^@@ -(\d+)(,\d+)? \+(\d+)(,\d+)? @@", diff, re.M)
    path = os.path.join(T, f); cur = open(path, "rb").read()
    assert cur == show(NEW, f), f"{f}: tree file is not the {NEW} version"
    for i, (os_, oc, ns, nc) in enumerate(raw):
        os_, ns = int(os_), int(ns); oc = 1 if oc == "" else int(oc[1:]); nc = 1 if nc == "" else int(nc[1:])
        o0 = os_ - 1 if oc else os_; n0 = ns - 1 if nc else ns
        variant = new[:n0] + old[o0:o0 + oc] + new[n0 + nc:]
        vb = "\n".join(variant).encode(errors="surrogateescape")
        svis = stream(vb) != stream(cur)
        summ = (" | ".join(l.strip() for l in old[o0:o0 + oc]) + " => " + " | ".join(l.strip() for l in new[n0:n0 + nc]))[:160]
        if not svis:
            print(f"{f}\t{i}\t{oc}\t{nc}\tno\t-\t{summ}", flush=True); continue
        open(path, "wb").write(vb)
        try:
            cvis = build() != base
        finally:
            open(path, "wb").write(cur)
        print(f"{f}\t{i}\t{oc}\t{nc}\tyes\t{'yes' if cvis else 'no'}\t{summ}", flush=True)
build()
