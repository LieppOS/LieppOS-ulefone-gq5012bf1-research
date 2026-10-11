#!/usr/bin/env python3
"""Generate CANONICAL-INTEGRATION-01 identity tables from committed audits and package manifests.
Read-only with respect to the audit; writes only tables inside this package."""
import collections, csv, io, json, subprocess
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
K = R / 'reverse-engineering/kernel-source-reconstruction'
AUD = 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
show = lambda c, p: subprocess.check_output(['git', 'show', f'{c}:{p}'], cwd=R, text=True)
rd = lambda text: {r['module_id']: r for r in csv.DictReader(io.StringIO(text), delimiter='\t')}
f61 = rd(show('f61ebf03275ba2d3f6aa4f9d5aebe18e12922263', AUD))
staged = rd(show('437ebd5762afa2512fe1ba10102e6b4f4d6beba9', AUD))
final = rd((R / AUD).read_text())
tab = lambda p: list(csv.DictReader(p.open(), delimiter='\t'))
pkg = {}
for m in tab(K / 'COMPLETED-BATCHES-INTEGRATION-01/COMBINED-MANIFEST.tsv'):
    pkg[m['module_id']] = [m['batch'] + ' via COMPLETED-BATCHES-INTEGRATION-01 (55dab18a)']
for m in tab(K / 'NEXT-DG-BATCH-01/BATCH-MANIFEST.tsv'):
    pkg.setdefault(m['module_id'], []).append('NEXT-DG-BATCH-01 (437ebd57)')
plan = tab(P / 'CAS-PLAN.tsv')
for d in plan:
    label = {'4-ALL-C': 'ALL-C-TO-A-CLOSURE (652e4195) promotion', '5-SOURCE-SUPERSEDE': 'ALL-C verified recipe supersede (no class change)',
             '6-USB-TYPEC-CLOSURE': 'USB-TYPEC-CLOSURE (7e196c32) C evidence (no class change)'}[d['stage']]
    if label not in pkg.setdefault(d['module_id'], []): pkg[d['module_id']].append(label)
out = []
for i in sorted(final):
    a, s, b = f61[i], staged[i], final[i]
    if a == b: continue
    out.append(dict(module_id=i, filename=b['filename'], partitions=b['partitions'], class_f61=a['source_status'],
                    class_staged_437ebd57=s['source_status'], class_final=b['source_status'],
                    packages=' + '.join(pkg.get(i, ['UNATTRIBUTED'])), source_owner=b['source_owner'],
                    source_repo=b['source_repo'], source_commit=b['source_commit'],
                    fields_changed=len([k for k in b if a[k] != b[k]]), primary_parity_evidence=b['parity_evidence'].split(';')[0]))
assert all(o['packages'] != 'UNATTRIBUTED' for o in out), [o['module_id'] for o in out if o['packages'] == 'UNATTRIBUTED']
assert all(final[i] == f61[i] for i in final if i not in {o['module_id'] for o in out})
w = lambda name, rows: (lambda f: (csv.DictWriter(f, list(rows[0]), delimiter='\t', lineterminator='\n').writeheader(),
                                   csv.DictWriter(f, list(rows[0]), delimiter='\t', lineterminator='\n').writerows(rows)))((P / name).open('w'))
w('COMBINED-MANIFEST.tsv', out)
c = [dict(module_id=i, filename=r['filename'], partitions=r['partitions'], class_f61=f61[i]['source_status'],
          source_owner=r['source_owner'], source_repo=r['source_repo'], source_commit=r['source_commit'],
          exact_functions=r['exact_functions'], unresolved_functions=r['unresolved_functions'], blocker=r['blocker'],
          parity_evidence=r['parity_evidence']) for i, r in sorted(final.items()) if r['source_status'] == 'C']
assert len(c) == 10
w('CATEGORY-C-REMAINING.tsv', c)
trans = collections.Counter((o['class_f61'], o['class_final']) for o in out)
print(f'COMBINED-MANIFEST {len(out)} changed identities; transitions {dict(trans)}; C remaining {len(c)}')
