#!/usr/bin/env python3
"""Per-partition Android-side consumer ledger for GQ5012BF1.
Partition names come from the live by-name listings in slot-b-investigation; consumers are stock files
(any partition image tree) that reference `by-name/<name>` (optionally _a/_b or 1/2 suffixed). AVB rollback locations are decoded from the device vbmeta dumps.
usage: partition_consumers.py <research-root> <fstab> <out.tsv>"""
import collections, glob, os, re, struct, subprocess, sys
RR, FSTAB, OUT = sys.argv[1:4]
SB = os.path.join(RR, "slot-b-investigation"); P = os.path.join(RR, "workspace/gq5012bf1/stock/partitions")
names = set()
for f in glob.glob(os.path.join(SB, "*.txt")) + glob.glob(os.path.join(SB, "*/*.txt")):
    names |= set(re.findall(r"by-name/([A-Za-z0-9_]+)", open(f, errors="replace").read()))
names -= {"sda", "sdb", "sdc", "rootdisk"}
base = lambda n: re.sub(r"(_a|_b|_?1|_?2)$", "", n) if n not in ("protect1", "protect2", "sec1") else n
groups = collections.defaultdict(set)
for n in names: groups[base(n)].add(n)
fst = {}
for l in open(FSTAB):
    p = l.split()
    if len(p) >= 3 and p[0].startswith("/dev/block/by-name/"): fst[p[0].split("/")[-1]] = (p[1], p[2])
pats = sorted({f"by-name/{n}" for n in names})  # mount-point strings are too collision-prone (e.g. "/misc", "/para")
pf = "/tmp/pc-pats.txt"; open(pf, "w").write("\n".join(pats) + "\n")
# app payloads (apk/dex/oat/jar/art/js) are excluded: mount-point strings like "/para" collide there
out = subprocess.run(["rg", "-uuu", "-a", "-o", "-F", "-f", pf, "--with-filename"] +
                     [x for g in ("*.apk", "*.vdex", "*.odex", "*.oat", "*.art", "*.jar", "*.js", "*.capex", "*.apex", "*.html", "*.dat") for x in ("-g", "!" + g)] +
                     ["vendor", "system", "system_ext", "product", "vendor_dlkm", "odm_dlkm", "system_dlkm"], cwd=P, capture_output=True, text=True, errors="replace").stdout
hits = collections.defaultdict(set)
for l in out.splitlines():
    f, _, m = l.rpartition(":")
    if m.startswith("by-name/"):
        hits[base(m[8:])].add(f)
    else:
        for n, (mp, _) in fst.items():
            if mp == m: hits[base(n)].add(f)
# AVB rollback locations (from chain descriptors in vbmeta_b) + values
D = os.path.join(SB, "device-dumps")
def vb(path):
    b = open(path, "rb").read()
    if b[:4] != b"AVB0": f = b[-64:]; o, vo, vs = struct.unpack(">QQQ", f[12:36]); b = b[vo:vo + vs]
    ri, fl, loc = struct.unpack(">QII", b[112:128]); return ri, fl
loc = {"vbmeta": 0}
b = open(os.path.join(D, "vbmeta_b.img"), "rb").read()
auth, aux = struct.unpack(">QQ", b[12:28]); doff, dsz = struct.unpack(">QQ", b[96:112]); d = b[256 + auth + doff:256 + auth + doff + dsz]; p = 0
while p < len(d):
    tag, nb = struct.unpack(">QQ", d[p:p + 16]); body = d[p + 16:p + 16 + nb]
    if tag == 4:
        rli, pnl = struct.unpack(">II", body[0:8]); loc[body[76:76 + pnl].decode()] = rli
    p += 16 + nb
rows = []
for g in sorted(groups):
    members = sorted(groups[g]); ab = "A/B" if any(m.endswith(("_a", "_b")) for m in members) else ("dual-copy 1/2" if any(re.search(r"[12]$", m) for m in members) and g not in ("protect1", "protect2") else "single")
    mp, fs = fst.get(g, fst.get(g + "1", ("", "")))
    c = sorted(hits.get(g, ()))
    rb = ""
    if g in loc:
        ri, fl = vb(os.path.join(D, f"{g}_b.img")) if os.path.exists(os.path.join(D, f"{g}_b.img")) else ("?", "?")
        rb = f"location {loc[g]}, index {ri}"
    decl = re.compile(r"(fstab|_contexts$|ueventd\.rc$|build\.prop$)")
    code = [x for x in c if not decl.search(x)]
    owner = ("Android code/rc consumer(s): " + ";".join(code[:4])) if code else ("declared only (fstab/sepolicy/ueventd); no Android code reads it -> bootloader/firmware-owned" if c else None)
    owner = owner or "no Android-side consumer: bootloader/firmware-owned (preloader/lk/TEE images not in the dump set)"
    rows.append((g, ",".join(members), ab, mp, fs, str(len(c)), ";".join(c[:6]) + (";..." if len(c) > 6 else ""), rb, owner))
with open(OUT, "w") as o:
    o.write("partition\tblock_names\tslotting\tfstab_mount\tfstab_type\tconsumer_files\tconsumers\tavb_rollback\towner_class\n")
    for r in rows: o.write("\t".join(r) + "\n")
print(f"{len(rows)} partition groups ({len(names)} by-name entries); with Android consumer: {sum(1 for r in rows if r[5] != '0')}; rollback locations: {loc}")
