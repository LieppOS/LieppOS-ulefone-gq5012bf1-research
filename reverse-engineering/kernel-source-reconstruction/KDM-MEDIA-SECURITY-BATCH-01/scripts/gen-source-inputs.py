#!/usr/bin/env python3
"""Record every C/header/generated input actually compiled into each target, from Kbuild .cmd records.

usage: gen-source-inputs.py <B-workspace> <repo-manifest.tsv> <out-dir>
Origin: KDM (assembled ALPS+patches tree, git blob id), COMMON (GKI common pin, git blob id),
GENERATED (prepared kout/native-kout, sha256).
"""
import csv, hashlib, re, subprocess, sys, collections
from pathlib import Path

WS, MAN, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
KDM, COMMON, KOUT, NK = WS / 'src/kdm', WS / 'common', WS / 'kout', WS / 'native-kout'


def blob(p):
    return subprocess.check_output(['git', 'hash-object', str(p)], text=True).strip()


def origin(p):
    p = Path(p).resolve()
    for name, root, kind in [('KDM', KDM, 'git-blob'), ('COMMON', COMMON, 'git-blob'), ('GENERATED', KOUT, 'sha256'), ('GENERATED', NK, 'sha256')]:
        if p.is_relative_to(root):
            h = blob(p) if kind == 'git-blob' else hashlib.sha256(p.read_bytes()).hexdigest()
            return name, str(p.relative_to(root)), kind + ':' + h
    if 'clang-r487747c' in str(p):
        return 'TOOLCHAIN', str(p).split('clang-r487747c/', 1)[1], 'pinned-clang-tree'
    raise SystemExit(f'unclassified input {p}')


def cmd_inputs(cmd):
    t = cmd.read_text(errors='replace')
    src = re.findall(r'^source_\S+ := (\S+)', t, re.M)
    deps = re.search(r'^deps_\S+ := \\\n(.*?)\n\n', t, re.M | re.S)
    items = list(src)
    if deps:
        # Kconfig stamps $(wildcard include/config/X) are dependency markers, not compiled inputs
        for tok in re.sub(r'\$\(wildcard [^)]*\)', ' ', deps.group(1)).split():
            if tok in ('\\',) or tok.startswith('$(wildcard'):
                continue
            items.append(tok)
    return items


rows, summary, missing = [], collections.Counter(), []
for r in csv.DictReader(MAN.open(), delimiter='\t'):
    m, d = r['filename'][:-3], r['candidate_directory']
    if r['build_domain'] == 'KDM':
        base = KDM / d
        mod = base / (m + '.mod')
        objs = [base / o for o in mod.read_text().split()] if mod.exists() else [base / (m + '.o')]
        cwd = COMMON
    else:
        base = NK / d
        mod = base / (m + '.mod')
        objs = [NK / o if not Path(o).is_absolute() else Path(o) for o in mod.read_text().split()] if mod.exists() else [base / (m + '.o')]
        objs = [o if o.exists() else base / o.name for o in objs]
        cwd = NK
    for o in objs:
        cmd = o.with_name('.' + o.name + '.cmd')
        assert cmd.exists(), cmd
        seen = set()
        for item in cmd_inputs(cmd):
            cands = [Path(item)] if Path(item).is_absolute() else [KOUT / item if cwd == COMMON else NK / item, cwd / item, COMMON / item]
            p = next((c for c in cands if c.exists()), None)
            if p is None:
                missing.append((r['filename'], o.name, item)); continue
            if p in seen:
                continue
            seen.add(p)
            kind, rel, digest = origin(p)
            rows.append(dict(module=r['filename'], object=o.name, origin=kind, path=rel, digest=digest))
            summary[(r['filename'], kind)] += 1
with (OUT / 'SOURCE-INPUTS.tsv').open('w') as f:
    w = csv.DictWriter(f, list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
assert not missing, missing[:10]
for (m, k), n in sorted(summary.items()):
    print(m, k, n)
