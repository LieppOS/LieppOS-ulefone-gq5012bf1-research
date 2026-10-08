#!/usr/bin/env python3
"""srcversion search with a fixed on-disk base tree: every file in the modpost dependency
sequence is read from the build tree, except the --vary files, whose candidates are the
distinct blobs at the given repo@rev specs (plus the on-disk version).
usage: sv_search2.py <common> <module.mod> <target> <vary,comma,list> <repo@rev>...
"""
import ctypes, itertools, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcversion as SV
common, mod, target, vary, *specs = sys.argv[1:]
vary = vary.split(","); P = "gpu/gpu_mali/mali_avalon/mali-r44p1/"
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../tools/sv/libmd4sv.so"))
os.chdir(common)
seq = []
for obj in open(mod).read().split(): seq += SV.deps(obj, ".")
rel = [p.split("/mali-r44p1/")[1] for p in seq]
disk = {r: p for r, p in zip(rel, seq)}
def st(b): o = bytearray(); SV.parse_file(b, o); return bytes(o)
streams = {r: st(open(p, "rb").read()) for r, p in disk.items()}
cands = {}
for f in vary:
    if f not in disk: raise SystemExit(f"{f} not in sequence")
    opts = [("disk", streams[f])]
    for sp in specs:
        rp, rv = sp.split("@", 1)
        r = subprocess.run(["git", "-C", rp, "show", f"{rv}:{P}{f}"], capture_output=True)
        if r.returncode: continue
        s = st(r.stdout)
        if all(s != o[1] for o in opts): opts.append((sp.split("/")[-1], s))
    cands[f] = opts
print({f: [o[0] for o in v] for f, v in cands.items()}, flush=True)
o = ctypes.create_string_buffer(25); n = 0
for combo in itertools.product(*[range(len(cands[f])) for f in vary]):
    ch = {f: cands[f][i][1] for f, i in zip(vary, combo)}
    buf = b"".join(ch.get(r, streams[r]) for r in rel)
    lib.sv(buf, len(buf), o); n += 1
    if o.value.decode() == target:
        print("MATCH", {f: cands[f][i][0] for f, i in zip(vary, combo)}, flush=True)
print(f"done: {n} combinations")
