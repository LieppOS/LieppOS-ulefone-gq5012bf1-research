#!/usr/bin/env python3
"""Apply AUDIT-DELTA.tsv to an isolated scratch clone of the canonical audit and verify it.

  test-delta.py <scratch-dir>

* clones this worktree's committed HEAD into <scratch-dir> (never touches the live canonical checkout);
* field-level apply: for each delta row, the scratch ALL-457-MODULES.tsv row with the same module_id
  must exist exactly once with source_status == old_source_status, else abort;
* only the mapped fields change (source_status, source_group, source_owner, source_repo,
  source_commit, parity_evidence, build_script, reproduction_status);
* asserts 458 identities, exact projected counts, every unselected row byte-identical, and no overlap
  with AUDIO-BATCH-01 or PLATFORM-BATCH-04;
* mutation tests: a delta whose old class is wrong, whose module_id is unknown, or that is applied
  twice (double counting) must abort.
"""
import csv, subprocess, sys, json, shutil, collections, copy
from pathlib import Path

P = Path(__file__).resolve().parents[1]; R = P.parents[2]
S = Path(sys.argv[1]).resolve()
if S.exists(): shutil.rmtree(S)
subprocess.check_call(['git', 'clone', '-q', '--no-hardlinks', str(R), str(S)])
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=S, text=True).strip()
AUD = S / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
raw = AUD.read_text().splitlines(keepends=True); hdr = raw[0].rstrip('\n').split('\t')
rows = [dict(zip(hdr, l.rstrip('\n').split('\t'))) for l in raw[1:]]
delta = list(csv.DictReader((P / 'AUDIT-DELTA.tsv').open(), delimiter='\t'))

def apply(rows, delta):
    rows = copy.deepcopy(rows); idx = collections.defaultdict(list)
    for i, r in enumerate(rows): idx[r['module_id']].append(i)
    for d in delta:
        hits = idx.get(d['module_id'], [])
        if len(hits) != 1: raise ValueError('identity not unique/absent: ' + d['module_id'])
        r = rows[hits[0]]
        if r['source_status'] != d['old_source_status']: raise ValueError('old class mismatch (concurrent change or double apply): ' + d['filename'])
        repo, commit = d['new_source_owner'].split('@')
        r.update(source_status=d['new_source_status'], source_group=d['new_source_group'], source_owner=d['new_source_group'],
                 source_repo='../' + repo, source_commit=commit, parity_evidence=d['new_parity_evidence'],
                 build_script='../' + d['new_build_script'], reproduction_status=d['new_reproduction'])
    return rows

new = apply(rows, delta)
assert len(new) == 458 and len({r['module_id'] for r in new}) == 458
ids = {d['module_id'] for d in delta}
changed_fields = collections.Counter()
for a, b in zip(rows, new):
    if a['module_id'] not in ids: assert a == b
    else: changed_fields.update(k for k in hdr if a[k] != b[k])
assert set(changed_fields) <= {'source_status', 'source_group', 'source_owner', 'source_repo', 'source_commit', 'parity_evidence', 'build_script', 'reproduction_status'}, changed_fields
cnt = collections.Counter(r['source_status'] for r in new)
assert dict(cnt) == {'A': 236, 'B': 1, 'C': 12, 'D': 98, 'G': 111}, cnt
b4 = {r['module_id'] for r in csv.DictReader((S / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
au = {r['module_id'] for r in csv.DictReader((R.parent / 'ulefone-gq5012bf1-research-codex-audio/reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01/AUDIT-DELTA.tsv').open(), delimiter='\t')}
assert not ids & b4 and not ids & au
# combined projection with the (unmerged) audio delta: disjoint, so additive
audio_delta = list(csv.DictReader((R.parent / 'ulefone-gq5012bf1-research-codex-audio/reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01/AUDIT-DELTA.tsv').open(), delimiter='\t'))
both = apply(new, audio_delta); cb = collections.Counter(r['source_status'] for r in both)
# mutation tests
muts = {}
for name, d in [('wrong_old_class', [dict(delta[0], old_source_status='D')]),
                ('unknown_identity', [dict(delta[0], module_id='nope.ko@00')]),
                ('double_apply', delta + delta[:1])]:
    try: apply(rows, d); muts[name] = 'NOT_REJECTED'
    except ValueError: muts[name] = 'REJECTED'
assert all(v == 'REJECTED' for v in muts.values()), muts
AUD.write_text(''.join(['\t'.join(hdr) + '\n'] + ['\t'.join(r[k] for k in hdr) + '\n' for r in new]))
diffstat = subprocess.check_output(['git', 'diff', '--numstat'], cwd=S, text=True).strip()
out = dict(scratch_head=head, rows=458, changed_rows=len(ids), changed_fields=dict(changed_fields), counts_after_this_delta=dict(cnt),
           certified_after_this_delta=cnt['A'] + cnt['B'], counts_after_this_and_audio_delta=dict(cb), certified_after_both=cb['A'] + cb['B'],
           mutation_tests=muts, scratch_git_numstat=diffstat, live_canonical_touched=False)
(P / 'evidence/audit-delta-test.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=1))
