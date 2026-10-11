#!/usr/bin/env python3
"""Independent re-validation of USB-TYPEC-CLOSURE after stock-inventory repair.

usage: revalidate-usb-closure.py OPERAND_ROOT CLOSURE_COPY PROOF_ROOT SCRATCH OUT_JSON

OPERAND_ROOT  research checkout with independently verified intact stock operands
CLOSURE_COPY  `git archive codex/usb-typec-closure` extraction of USB-TYPEC-CLOSURE (never the live worktree)
PROOF_ROOT    preserved four-build proof root (read only)
SCRATCH       private output directory for verifier outputs / stock symlinks / comparisons

Nothing here certifies a module.  Strict verifier, comparison and mutation scripts are the
committed ones from the recovered source clones / closure branch, run unchanged.
"""
import csv, hashlib, io, json, os, subprocess, sys
from pathlib import Path

OPER, CL, PROOF, S, OUT = (Path(a).resolve() for a in sys.argv[1:6])
WS = OPER.parent
BASE = 'f61ebf03275ba2d3f6aa4f9d5aebe18e12922263'
FIVE = ['charger_class', 'mtk_chg_type_det', 'rt_pd_manager', 'tcpc_mt6375', 'tcpc_class']
TAGS = ['F0-B1', 'F0-B2', 'F1-B1', 'F1-B2']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
git = lambda *a, cwd=OPER: subprocess.check_output(['git', *a], cwd=cwd, text=True).strip()
res = {}

state = json.loads((CL / 'STATE.json').read_text())
# 1. committed source commits still valid
src = {}
for repo, key in [('android_kernel_modules_usb_typec_ulefone_gq5012bf1-usb-typec-closure', 'typec_commit'),
                  ('android_kernel_modules_charging_battery_ulefone_gq5012bf1-usb-typec-closure', 'charging_commit')]:
    r = WS / repo; c = state[key]
    bundles = sorted((CL / 'evidence/bundles').glob(repo.removesuffix('-usb-typec-closure') + '*.bundle'))
    bv = [subprocess.run(['git', '-C', str(r), 'bundle', 'verify', str(b)], capture_output=True, text=True).returncode == 0 for b in bundles]
    src[repo] = dict(commit=c, head=git('rev-parse', 'HEAD', cwd=r), clean=git('status', '--porcelain', cwd=r) == '',
                     commit_object=subprocess.run(['git', '-C', str(r), 'cat-file', '-e', c + '^{commit}']).returncode == 0,
                     fsck=subprocess.run(['git', '-C', str(r), 'fsck', '--full', '--no-progress'], capture_output=True).returncode == 0,
                     bundles=[b.name for b in bundles], bundles_verify=bv)
    assert src[repo]['head'] == c and src[repo]['clean'] and src[repo]['commit_object'] and src[repo]['fsck'] and bv and all(bv), src[repo]
res['source_commits'] = src

# 2. stock operands for the 30 Batch04 identities from the independently verified operand root
rows = list(csv.DictReader(io.StringIO(git('show', f'{BASE}:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')), delimiter='\t'))
audit = {r['module_id']: r for r in rows}
man = list(csv.DictReader((PROOF / 'F0-B1/recipe/reference/BATCH-MANIFEST.tsv').open(), delimiter='\t'))
assert len(man) == 30
stock = S / 'stock-operands'; stock.mkdir(parents=True, exist_ok=False)
parts = {}
for m in man:
    a = audit[m['module_id']]
    p = OPER / a['stock_paths'].split(';')[0]
    assert sha(p) == a['stock_sha256'] == m['stock_sha256'], m['module_id']
    (stock / m['filename']).symlink_to(p)
    parts[a['partitions']] = parts.get(a['partitions'], 0) + 1
res['batch04_stock_partitions'] = parts
res['batch04_targets_in_system_dlkm'] = sum(v for k, v in parts.items() if 'system_dlkm' in k)

# 3. cross-run byte determinism of all 30 raw + 30 stripped modules (own hashing)
outs = {t: Path(json.loads((CL / f'evidence/fresh-clones/{t}.json').read_text())['output']) for t in TAGS}
mods = sorted(p.stem for p in outs['F0-B1'].glob('*.ko'))
assert len(mods) == 30
det = {}
for m in mods:
    for suf in ['.ko', '.stripped']:
        det[m + suf] = len({sha(outs[t] / (m + suf)) for t in TAGS}) == 1
res['raw_and_stripped_identical_across_4_builds'] = sum(det.values())
assert all(det.values()), [k for k, v in det.items() if not v]

# 4. strict stock acceptance re-run: 30 modules x 4 builds, unchanged committed verifier
acc = {}
for t in TAGS:
    N = PROOF / t / 'recipe'
    acc[t] = {}
    for m in mods:
        o = S / 'accepted' / t / m
        p = subprocess.run(['python3', str(N / 'scripts/verify.py'), str(outs[t]), str(stock), str(o)],
                           env=dict(env, LIEPPOS_VERIFY_JOINT='1', LIEPPOS_VERIFY_MODULE=m), capture_output=True, text=True)
        (S / 'logs').mkdir(exist_ok=True); (S / 'logs' / f'{t}-{m}-strict.log').write_text(p.stdout + p.stderr)
        acc[t][m] = p.returncode
    recorded = {o['module']: o['strict_verifier_exit'] for o in json.loads((CL / f'evidence/fresh-clones/{t}.json').read_text())['outcomes']}
    assert {m for m, e in acc[t].items() if e == 0} == set(mods) - set(FIVE), (t, acc[t])
    assert {m for m, e in acc[t].items() if e != 0} == set(FIVE), (t, acc[t])
    assert {m: e == 0 for m, e in acc[t].items()} == {m: e == 0 for m, e in recorded.items()}, t
res['strict_acceptance'] = {t: dict(accepted=sum(e == 0 for e in v.values()), rejected=sorted(m for m, e in v.items() if e)) for t, v in acc.items()}

# 5. five-target comparison recomputed from the verified operand root (unchanged compare-five.py)
cmp_summary = {}
for t in ['F0-B1', 'F1-B1']:
    D = S / 'five-comparison' / t
    p = subprocess.run(['python3', str(CL / 'scripts/compare-five.py'), str(PROOF / t / 'recipe'), str(OPER), str(outs[t]), str(D)],
                       env=env, capture_output=True, text=True)
    (S / 'logs' / f'{t}-compare-five.log').write_text(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr[-2000:]
    cmp_summary[t] = json.loads((D / 'summary.json').read_text())
same = cmp_summary['F0-B1'] == cmp_summary['F1-B1']
committed = json.loads((CL / 'evidence/final/full-acceptance/summary.json').read_text())
strip = lambda s: [{k: v for k, v in x.items() if k not in ('evidence', 'paths')} for x in s]
five = {}
for x in cmp_summary['F0-B1']:
    f, d = x['axes']['functions'], x['axes']['data']
    five[x['module']] = dict(final_class=x['final_class'], strict_exit=x['strict_stock_verifier_exit'], whole_parity=x['whole_permitted_stock_parity'],
                             functions=f"{f['body_and_position_exact']}/{f['stock_count']}", data=f"{d['body_and_position_exact']}/{d['stock_count']}",
                             unmatched_data=d['unmatched'], import_crc=x['import_crc_exact'], export_crc=x['export_crc_and_license_exact'], kcfi=x['kcfi_abs_exact'])
    assert x['final_class'] == 'C' and x['strict_stock_verifier_exit'] != 0 and not x['whole_permitted_stock_parity']
assert five['tcpc_class']['functions'] == '709/709'
res['five_targets'] = five
res['five_comparison_identical_F0_F1'] = same
res['five_comparison_axes_equal_committed_final'] = [ (a['module'], a['axes']) for a in cmp_summary['F0-B1']] == [(b['module'], b['axes']) for b in committed]

# 6. committed closure revalidators and ELF mutation tests, run in the archive copy only
for name, args in [('validate-cleancheck', [str(PROOF)]), ('validate-preserved-evidence', ['--proof-root', str(PROOF)]),
                   ('test-acceptance', [str(PROOF / 'F0-B1/recipe'), str(outs['F0-B1']), str(stock)])]:
    p = subprocess.run(['python3', str(CL / f'scripts/{name}.py'), *args], env=env, capture_output=True, text=True)
    (S / 'logs' / f'{name}.log').write_text(p.stdout + p.stderr)
    res[name] = dict(exit=p.returncode, tail=(p.stdout + p.stderr).strip().splitlines()[-1][:300])
    assert p.returncode == 0, (name, p.stdout[-1500:], p.stderr[-1500:])
mt = json.loads((CL / 'evidence/mutation-tests/result.json').read_text())
res['elf_mutation_tests'] = dict(count=mt['count'], all_pass=mt['all_pass'])
assert mt['count'] == 23 and mt['all_pass']

# 7. audit proposal against its intended baseline (not applied)
delta = list(csv.DictReader((CL / 'AUDIT-DELTA.tsv').open(), delimiter='\t'))
bad = [d for d in delta if audit[d['module_id']].get(d['field']) != d['expected_before']]
res['audit_delta'] = dict(rows=len(delta), fields=sorted({d['field'] for d in delta}),
                          baseline_file_equals_f61ebf03=sha(CL / 'evidence/baseline/ALL-458-MODULES.tsv') == hashlib.sha256(git('show', f'{BASE}:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').encode() + b'\n').hexdigest(),
                          expected_before_matches_f61ebf03=not bad, mismatches=[(d['module_id'], d['field']) for d in bad],
                          touches_source_status=any(d['field'] == 'source_status' for d in delta),
                          promotions=0, applied=False)
assert len(delta) == 22 and not bad and not res['audit_delta']['touches_source_status']
res['newly_certified'] = 0
res['result'] = 'PASS_REVALIDATED_25A_PRESERVED_5C_UNCHANGED_NO_PROMOTION'
OUT.write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps({k: v for k, v in res.items() if k not in ('source_commits', 'five_targets')}, indent=2))
print(json.dumps(res['five_targets'], indent=1))
