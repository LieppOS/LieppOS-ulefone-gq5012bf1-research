#!/usr/bin/env python3
"""Exhaustive srcversion search over per-file source revisions.

The dependency sequence (objects in .mod order, each object's source + same-dir
deps, exactly as modpost walks it) is taken from a real build tree. Every file
in that sequence is hashed with the content of a chosen git blob; for files with
several candidate blobs all combinations are tried. Hashing is modpost's own MD4
(compiled from GKI sumversion.c into libmd4sv.so).

usage: sv_search.py <build-root> <module.mod (relative to common)> <repo.git> <target-srcversion>
                    <rev-A> <rev-B> [<rev-C> ...]
  candidate blobs per file = distinct blobs of that file at the given revisions
  a revision may be written /path/to/other-repo@rev to draw from another repository
"""
import ctypes, itertools, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcversion as SV

common, mod, repo, target, *revs = sys.argv[1:]
P = "gpu/gpu_mali/mali_avalon/mali-r44p1/"
lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../tools/sv/libmd4sv.so"))
os.chdir(common)
seq = []
for obj in open(mod).read().split():
    seq += SV.deps(obj, ".")
rel = [p.split("/mali-r44p1/")[1] for p in seq]

def split(rev):  # "rev" (default repo) or "/path/to/repo@rev"
    return rev.split("@", 1) if "@" in rev else (repo, rev)
def blob(rev, f):
    rp, rv = split(rev)
    r = subprocess.run(["git", "-C", rp, "rev-parse", f"{rv}:{P}{f}"], capture_output=True, text=True)
    return (rp, r.stdout.strip()) if r.returncode == 0 else None

cands = {}
for f in sorted(set(rel)):
    bs = []
    for r in revs:
        b = blob(r, f)
        if b and b not in bs: bs.append(b)
    if not bs: raise SystemExit(f"{f}: no blob at any revision")
    cands[f] = bs
stream = {}
def parsed(b):
    if b not in stream:
        data = subprocess.run(["git", "-C", b[0], "cat-file", "blob", b[1]], capture_output=True).stdout
        out = bytearray(); SV.parse_file(data, out); stream[b] = bytes(out)
    return stream[b]
var = [f for f in cands if len(cands[f]) > 1]
print(f"{len(seq)} sequence entries, {len(cands)} files, {len(var)} variable: {var}", flush=True)
o = ctypes.create_string_buffer(25)
hits = 0
for combo in itertools.product(*[range(len(cands[f])) for f in var]):
    choice = {f: cands[f][0] for f in cands}
    for f, i in zip(var, combo): choice[f] = cands[f][i]
    buf = b"".join(parsed(choice[f]) for f in rel)
    lib.sv(buf, len(buf), o)
    if o.value.decode() == target:
        hits += 1
        print("MATCH", {f: (choice[f][1][:10], revs[[blob(r, f) for r in revs].index(choice[f])]) for f in var}, flush=True)
print(f"done: {hits} match(es) of {target}")
