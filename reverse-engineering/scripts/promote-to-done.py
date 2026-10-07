#!/usr/bin/env python3
"""Move one organized-workspace component PARTIAL -> DONE.

usage: promote-to-done.py COMPONENT RESEARCH_DIR COMMIT ROW_FILE LOG_FILE [--reason TEXT]

* mv  'Reverse Engineer - PARTIAL/C' -> 'Reverse Engineer - DONE/C'  (refuses if target exists)
* copies RESEARCH_DIR into the pack:
    README.md -> README.md, stale-claims.md -> notes/stale-claims.md,
    STATUS.md -> notes/research-STATUS.md, every sub-directory verbatim
* writes notes/CLASSIFICATION-CHANGE.md, evidence/EVIDENCE-INDEX.md, PROVENANCE addendum
* REVERSE-ENGINEERING-STATUS.md: removes the PARTIAL row, appends ROW_FILE's row at the end of
  the DONE table, appends LOG_FILE's line after the last '- 2026-' log entry, recomputes totals
* COPY-MANIFEST.tsv: rebuilds the component block (unchanged historical rows keep provenance;
  research copies are 'research-derived' at COMMIT; generated files 'generated-index')
"""
import csv
import hashlib
import os
import re
import shutil
import sys

W = "/home/armol/androido_dalykai/LieppOS custom ROM"
comp, rdir, commit, rowf, logf = sys.argv[1:6]
reason = sys.argv[sys.argv.index("--reason") + 1] if "--reason" in sys.argv else ""
P = os.path.join(W, "Reverse Engineer - PARTIAL", comp)
D = os.path.join(W, "Reverse Engineer - DONE", comp)
assert os.path.isdir(P) and not os.path.exists(D), "bad source/target state"
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731

shutil.move(P, D)
mapping = {}  # pack-relative -> research abs path
for name in sorted(os.listdir(rdir)):
    src = os.path.join(rdir, name)
    if name == "__pycache__":
        continue
    if os.path.isdir(src):
        for dp, dn, fns in os.walk(src):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for fn in fns:
                a = os.path.join(dp, fn)
                rel = os.path.relpath(a, rdir)
                os.makedirs(os.path.dirname(os.path.join(D, rel)), exist_ok=True)
                shutil.copy2(a, os.path.join(D, rel))
                mapping[rel] = a
    else:
        rel = {"README.md": "README.md", "stale-claims.md": "notes/stale-claims.md",
               "STATUS.md": "notes/research-STATUS.md"}.get(name, "notes/" + name)
        os.makedirs(os.path.dirname(os.path.join(D, rel)), exist_ok=True)
        shutil.copy2(src, os.path.join(D, rel))
        mapping[rel] = src
for dp, dn, fns in os.walk(D):
    for d in list(dn):
        if d == "__pycache__":
            shutil.rmtree(os.path.join(dp, d))
            dn.remove(d)

rr = os.path.relpath(rdir, os.path.join(W, "ulefone-gq5012bf1-research"))
os.makedirs(os.path.join(D, "notes"), exist_ok=True)
open(os.path.join(D, "notes/CLASSIFICATION-CHANGE.md"), "w").write(
    f"# Classification change — {comp}\n\nDate: 2026-10-07\n\n"
    f"`Reverse Engineer - PARTIAL/{comp}` → `Reverse Engineer - DONE/{comp}` (moved, not copied).\n\n"
    f"{reason}\n\nAuthoritative closure: `../README.md`; corrections: `stale-claims.md`.\n"
    f"Research source: `ulefone-gq5012bf1-research/{rr}/` commit `{commit}`.\n")
os.makedirs(os.path.join(D, "evidence"), exist_ok=True)
cur = sorted(k for k in mapping if k not in ("README.md",))
open(os.path.join(D, "evidence/EVIDENCE-INDEX.md"), "w").write(
    "# Evidence index\n\n"
    f"Authoritative closure: `../README.md`. Research source: `ulefone-gq5012bf1-research/{rr}/` "
    f"at commit `{commit}`.\n\n## Current closure files (copied from research)\n\n"
    + "".join(f"- `../{k}`\n" for k in cur)
    + "\n## Historical evidence retained\n\nAll other files in this pack come from earlier passes. "
    "Where they conflict with `../README.md` or `../notes/stale-claims.md`, the newer closure is "
    "authoritative. No proprietary binary, firmware or raw private dump is copied into this pack.\n")
pv = os.path.join(D, "notes/PROVENANCE.md")
add = (f"\n## 2026-10-07 closure addendum (authoritative)\n\nPack moved to `Reverse Engineer - DONE/{comp}`. "
       f"Closure files were copied from `ulefone-gq5012bf1-research/{rr}/` commit `{commit}` (listed in "
       "`../evidence/EVIDENCE-INDEX.md`). Older entries above are historical; their `PARTIAL` path "
       "prefixes refer to the pre-move location.\n")
open(pv, "a").write(add) if os.path.exists(pv) else open(pv, "w").write("# Copied-file provenance\n" + add)

# ---- status index
st = os.path.join(W, "REVERSE-ENGINEERING-STATUS.md")
s = open(st, encoding="utf-8").read()
row = open(rowf, encoding="utf-8").read().strip("\n")
log = open(logf, encoding="utf-8").read().strip("\n")
old = re.search(r"^\| \[`" + re.escape(comp) + r"`\]\(<Reverse Engineer - PARTIAL/.*\n", s, re.M)
assert old, "PARTIAL row not found"
s = s[:old.start()] + s[old.end():]
i = s.index("\n## PARTIAL")
s = s[:i].rstrip("\n") + "\n" + row + "\n" + s[i:]
logs = list(re.finditer(r"^- 2026-.*\n", s, re.M))
j = logs[-1].end()
s = s[:j] + log + "\n" + s[j:]
cnt = {}
for k, nxt in (("DONE", "PARTIAL"), ("PARTIAL", "BLOCKED"), ("BLOCKED", "TODO")):
    a = s.index(f"\n## {k}\n")
    b = s.index(f"\n## {nxt}\n") if f"\n## {nxt}\n" in s else len(s)
    cnt[k] = len(re.findall(r"^\| \[`", s[a:b], re.M))
for k in cnt:
    s = re.sub(rf"^\| {k} \| \d+ \|$", f"| {k} | {cnt[k]} |", s, count=1, flags=re.M)
open(st, "w", encoding="utf-8").write(s)

# ---- manifest
mf = os.path.join(W, "COPY-MANIFEST.tsv")
with open(mf, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f, delimiter="\t")
    fields = rdr.fieldnames
    rows = list(rdr)
oldroot = f"Reverse Engineer - PARTIAL/{comp}/"
newroot = f"Reverse Engineer - DONE/{comp}/"
old_rows = {x["local_path"][len(oldroot):]: x for x in rows if x["component"] == comp
            and x["local_path"].startswith(oldroot)}
new = []
for dp, _, fns in os.walk(D):
    for fn in fns:
        a = os.path.join(dp, fn)
        rel = os.path.relpath(a, D)
        b = open(a, "rb").read()
        h = sha(b)
        x = {k: "" for k in fields}
        base = old_rows.get(rel)
        if base and base["current_sha256"] == h:
            x = dict(base)
        elif rel in mapping:
            x.update(artifact_origin="research-derived", original_path=mapping[rel],
                     original_repo="ulefone-gq5012bf1-research", relevant_commit=commit,
                     original_sha256=sha(open(mapping[rel], "rb").read()),
                     kind_or_provenance=rel.split("/")[0] if "/" in rel else "closure")
        else:
            x.update(artifact_origin="generated-index", original_repo="organized workspace",
                     kind_or_provenance="generated or amended during 2026-10-07 status closure")
        x.update(status="DONE", component=comp, local_path=newroot + rel, current_sha256=h, bytes=str(len(b)))
        new.append(x)
new.sort(key=lambda x: x["local_path"])
first = [i for i, x in enumerate(rows) if x["component"] == comp]
first = first[0] if first else len(rows)
out = [x for x in rows[:first] if x["component"] != comp] + new + [x for x in rows[first:] if x["component"] != comp]
with open(mf, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(out)
print(f"{comp}: moved; {len(old_rows)} old rows -> {len(new)} DONE rows; totals {cnt}")
