#!/usr/bin/env python3
"""Search the full public git history for authentic source revisions whose natural modpost
srcversion equals stock (read-only; uses the unmodified upstream sumversion.c via the probe).

usage: srcversion-history-scan.py GIT_DIR PROBE OUT_JSON [SPEC_JSON]
(SPEC_JSON: {module: [stock_srcversion, [ordered input paths]]}; default: the four USB modules)

For each module, every distinct historical blob of each hashed input path (in the exact
dependency order traced by USB-TYPEC-CLOSURE) is collected from all refs. A candidate is an
input combination that actually co-existed in one commit tree (coherent snapshot), plus,
separately, per-file cross products when every other file is held at the commit's version.
Only exact digest matches are reported; nothing is forced or edited.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

GIT, PROBE, OUT = sys.argv[1:4]
MODS = {
    'charger_class': ('E4A92CD3F20A3D2142F16B6', ['drivers/power/supply/charger_class.c', 'drivers/power/supply/charger_class.h']),
    'mtk_chg_type_det': ('F7A2E5433A38379D631644F', ['drivers/power/supply/mtk_chg_type_det.c', 'drivers/power/supply/mtk_charger.h',
                          'drivers/power/supply/charger_class.h', 'drivers/power/supply/adapter_class.h',
                          'drivers/power/supply/mtk_charger_algorithm_class.h', 'drivers/power/supply/mtk_smartcharging.h']),
    'rt_pd_manager': ('C4301583FE25F39BA52E75D', ['drivers/misc/mediatek/typec/tcpc/rt_pd_manager.c']),
    'tcpc_mt6375': ('D27BCF95DDC8F09B632224B', ['drivers/misc/mediatek/typec/tcpc/tcpc_mt6375.c']),
}
g = lambda *a: subprocess.run(['git', '--git-dir', GIT, *a], capture_output=True, text=True, check=True).stdout
if len(sys.argv) > 4:
    MODS = {k: tuple(v) for k, v in json.loads(Path(sys.argv[4]).read_text()).items()}
tmp = Path(tempfile.mkdtemp(prefix='srcv-'))
blobcache = {}
def blob(sha):
    if sha not in blobcache:
        p = tmp / sha
        p.write_bytes(subprocess.run(['git', '--git-dir', GIT, 'cat-file', 'blob', sha], capture_output=True, check=True).stdout)
        blobcache[sha] = str(p)
    return blobcache[sha]
def probe(paths):
    return subprocess.run([PROBE, *paths], capture_output=True, text=True, check=True).stdout.strip()

result = {}
for mod, (stock, paths) in MODS.items():
    # all commits touching any input path, all refs
    commits = g('log', '--all', '--format=%H', '--', *paths).split()
    snapshots = {}
    for c in commits:
        ids = []
        for p in paths:
            try:
                ids.append(g('rev-parse', f'{c}:{p}').strip())
            except subprocess.CalledProcessError:
                ids.append(None)
        if None in ids:
            continue
        snapshots.setdefault(tuple(ids), c)
    # per-path version sets for one-file-at-a-time variation
    versions = [sorted({s[i] for s in snapshots}) for i in range(len(paths))]
    tried, hits = set(), []
    def test(ids, how, commit):
        if ids in tried: return
        tried.add(ids)
        v = probe([blob(x) for x in ids])
        if v == stock:
            hits.append(dict(how=how, commit=commit, blobs=list(ids)))
    for ids, c in snapshots.items():
        test(ids, 'coherent', c)
    for ids, c in snapshots.items():
        for i in range(len(paths)):
            for alt in versions[i]:
                test(ids[:i] + (alt,) + ids[i + 1:], f'vary:{paths[i]}', c)
    result[mod] = dict(stock=stock, commits=len(commits), coherent_snapshots=len(snapshots),
                       distinct_blobs_per_path=[len(v) for v in versions], combinations_tested=len(tried), hits=hits)
    print(mod, json.dumps({k: v for k, v in result[mod].items() if k != 'hits'}), 'HITS', hits, flush=True)
Path(OUT).write_text(json.dumps(result, indent=2) + '\n')
