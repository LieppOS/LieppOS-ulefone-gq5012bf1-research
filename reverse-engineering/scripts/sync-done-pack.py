#!/usr/bin/env python3
"""Refresh an existing `Reverse Engineer - DONE/<COMP>` pack from its research directory.

usage: sync-done-pack.py <COMP> <research-dir> <research-commit> [--note TEXT]

Uses the copy mapping of promote-to-done.py (top-level files -> notes/, README.md -> README.md,
stale-claims.md -> notes/stale-claims.md, STATUS.md -> notes/research-STATUS.md,
directories copied as-is), plus SOURCE.md -> SOURCE.md at the pack root.
Only new or changed files are copied; files promote-to-done.py generated (EVIDENCE-INDEX,
PROVENANCE, CLASSIFICATION-CHANGE) are never overwritten. Files that exist only in the pack (historical evidence)
are left alone. COPY-MANIFEST.tsv rows are upserted for every copied file, and
evidence/EVIDENCE-INDEX.md gets a dated addendum listing them.
"""
import csv, hashlib, os, shutil, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
comp, rdir, commit = sys.argv[1:4]
note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
D = os.path.join(W, "Reverse Engineer - DONE", comp)
assert os.path.isdir(D), "DONE pack missing"
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
# Pack files generated or amended by promote-to-done.py; never overwritten from research.
GENERATED = {"evidence/EVIDENCE-INDEX.md", "notes/PROVENANCE.md", "notes/CLASSIFICATION-CHANGE.md"}
TOP = {"README.md": "README.md", "SOURCE.md": "SOURCE.md", "stale-claims.md": "notes/stale-claims.md",
       "STATUS.md": "notes/research-STATUS.md"}

mapping = {}
for name in sorted(os.listdir(rdir)):
    src = os.path.join(rdir, name)
    if name == "__pycache__":
        continue
    if os.path.isdir(src):
        for dp, dn, fns in os.walk(src):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for fn in fns:
                a = os.path.join(dp, fn)
                mapping[os.path.relpath(a, rdir)] = a
    else:
        mapping[TOP.get(name, "notes/" + name)] = src

changed = []
for rel, src in sorted(mapping.items()):
    if rel in GENERATED:
        continue
    dst = os.path.join(D, rel)
    b = open(src, "rb").read()
    if os.path.exists(dst) and open(dst, "rb").read() == b:
        continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    changed.append(rel)

date = datetime.date.today().isoformat()
ei = os.path.join(D, "evidence/EVIDENCE-INDEX.md")
if changed:
    with open(ei, "a", encoding="utf-8") as f:
        f.write(f"\n## {date} refresh (research commit `{commit}`)\n\n{note}\n\n"
                + "".join(f"- `../{k}`\n" for k in changed))

mf = os.path.join(W, "COPY-MANIFEST.tsv")
with open(mf, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f, delimiter="\t"); fields = rdr.fieldnames; rows = list(rdr)
root = f"Reverse Engineer - DONE/{comp}/"
byp = {x["local_path"]: x for x in rows}
touched = set(changed) | {"evidence/EVIDENCE-INDEX.md"}
for rel in sorted(touched):
    lp = root + rel
    b = open(os.path.join(D, rel), "rb").read()
    x = byp.get(lp) or {k: "" for k in fields}
    if rel in mapping and rel not in GENERATED:
        x.update(artifact_origin="research-derived", original_path=mapping[rel],
                 original_repo="ulefone-gq5012bf1-research", relevant_commit=commit,
                 original_sha256=sha(open(mapping[rel], "rb").read()),
                 kind_or_provenance=rel.split("/")[0] if "/" in rel else "closure")
    else:
        x.update(kind_or_provenance=(x.get("kind_or_provenance") or "evidence") + f"; amended {date}")
    x.update(status="DONE", component=comp, local_path=lp, current_sha256=sha(b), bytes=str(len(b)))
    if lp not in byp:
        rows.append(x); byp[lp] = x
first = min(i for i, x in enumerate(rows) if x["component"] == comp)
mine = sorted((x for x in rows if x["component"] == comp), key=lambda x: x["local_path"])
rest = [x for x in rows if x["component"] != comp]
rows = rest[:first] + mine + rest[first:]
with open(mf, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(f"{comp}: {len(changed)} files refreshed; manifest rows for {comp}: {len(mine)}")
for k in changed:
    print("  ", k)
