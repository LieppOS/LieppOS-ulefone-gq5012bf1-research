#!/usr/bin/env python3
"""Fail-closed, read-only validator for stock identities and source-proof claims.

PASS means a complete internally verified audit, not complete source reconstruction.
G identities are retained and explicitly counted, never repaired or silently dropped.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
from inventory import ROOT, AUDIT, WORKSPACE, read_table, scan

REQUIRED=['ALL-457-MODULES.tsv','SOURCE-GAPS.tsv','SOURCE-OWNERSHIP.tsv',
          'RECONSTRUCTION-QUEUE.md','SUMMARY.md','STALE-CLAIMS.md','NEXT-CLAUDE-TASK.md']
STATUSES=set('ABCDEFG')
HEX40=re.compile(r'^[0-9a-f]{40}$')


def validate(audit=AUDIT, overrides=None, actual=None):
    """Return all detected errors. Optional row overrides support mutation tests only."""
    audit=Path(audit);overrides=overrides or {};errors=[];warnings=[]
    digest_cache={}
    def current_hash(p):
        p=Path(p).resolve()
        if p not in digest_cache:digest_cache[p]=hashlib.sha256(p.read_bytes()).hexdigest()
        return digest_cache[p]
    def problem(code,message):errors.append({'code':code,'message':str(message)})
    def table(name):
        if name in overrides:return overrides[name]
        try:return read_table(audit/name)
        except (OSError,ValueError,csv.Error) as e:
            problem('MISSING_TABLE',f'{name}: {e}');return []
    def valid_ref(value,context):
        p=(ROOT/value).resolve()
        # Research evidence may refer to the existing organized packs / maintained recipes.
        if not (p.is_relative_to(ROOT) or p.is_relative_to(WORKSPACE)):
            problem('INVALID_EVIDENCE_PATH',f'{context}: outside research/workspace: {value}');return False
        if not p.exists():problem('INVALID_EVIDENCE_PATH',f'{context}: {value}');return False
        return True
    for name in REQUIRED:
        if not (audit/name).is_file():problem('MISSING_REQUIRED_OUTPUT',name)
    try:
        baseline=json.loads((audit/'evidence/workspace-baseline.json').read_text())
        frozen=json.loads((audit/'evidence/stock-identities.json').read_text())
        review=json.loads((audit/'evidence/source-reviews.json').read_text())
        hashes=json.loads((audit/'evidence/review-input-hashes.json').read_text())
        summary=json.loads((audit/'evidence/audit-summary.json').read_text())
    except (OSError,ValueError) as e:
        problem('MISSING_EVIDENCE',e);return {'result':'FAIL','errors':errors,'warnings':warnings}
    actual=scan() if actual is None else actual
    rows=table('ALL-457-MODULES.tsv');owners=table('SOURCE-OWNERSHIP.tsv');gaps=table('SOURCE-GAPS.tsv')
    ids=[r.get('module_id','') for r in rows]
    duplicate=[i for i,n in collections.Counter(ids).items() if n>1]
    for i in duplicate:problem('DUPLICATE_IDENTITY',i)
    for i in sorted(set(actual)-set(ids)):problem('MISSING_IDENTITY',i)
    for i in sorted(set(ids)-set(actual)):problem('UNEXPECTED_IDENTITY',i)
    if set(frozen)!=set(actual):problem('STALE_FROZEN_INVENTORY','actual stock identity set changed')
    by_id={r['module_id']:r for r in rows if 'module_id' in r}
    for row in rows:
        identity=row.get('module_id','');stock=actual.get(identity)
        if stock is None:continue
        for field in ['filename','stock_sha256','stock_size']:
            if str(row.get(field,''))!=str(stock[field]):problem('STOCK_BASELINE_MISMATCH',f'{identity}: {field}')
        paths=row.get('stock_paths','').split(';')
        if set(paths)!=set(stock['stock_paths']) or len(paths)!=len(set(paths)):
            problem('STOCK_PATHS_OMITTED_OR_DUPLICATED',identity)
        if row.get('source_status') not in STATUSES:problem('INVALID_SOURCE_STATUS',identity)
        if row.get('source_status')!=review.get(identity,{}).get('source_status'):
            problem('SOURCE_REVIEW_CONFLICT',identity)
        owner=row.get('component_owner');component=baseline['components'].get(owner)
        if owner!='COVERED-GENERIC':
            if component is None:problem('STALE_COMPONENT_REFERENCE',f'{identity}: {owner}')
            elif row.get('component_status')!=component['status'] or not (ROOT/component['path']).is_dir():
                problem('STALE_COMPONENT_REFERENCE',f'{identity}: {owner}/{row.get("component_status")}')
        for field in ['component_evidence','dependency_evidence','source_review_evidence','input_hash_evidence','runtime_evidence']:
            value=row.get(field,'UNKNOWN')
            if value=='UNKNOWN':problem('MISSING_EVIDENCE_REFERENCE',f'{identity}: {field}')
            else:valid_ref(value,f'{identity}: {field}')
        if row.get('binding_evidence','UNKNOWN')!='UNKNOWN':valid_ref(row['binding_evidence'],identity)
        snapshot=row.get('source_snapshot_path','UNKNOWN')
        if snapshot!='UNKNOWN':valid_ref(snapshot,identity)
        status=row.get('source_status');proof=row.get('parity_evidence','UNKNOWN')
        if proof!='UNKNOWN':
            for value in proof.split(';'):valid_ref(value,identity)
        if status in ['A','B']:
            if proof in ['', 'UNKNOWN']:problem('VERIFIED_WITHOUT_PARITY',identity)
            if row.get('abi_status')!='VERIFIED' or row.get('crc_status')!='VERIFIED' or row.get('kcfi_status')!='VERIFIED':
                problem('VERIFIED_WITHOUT_ABI_KCFI',identity)
            if row.get('unresolved_functions')!='0':problem('VERIFIED_WITH_UNRESOLVED_FUNCTIONS',identity)
            if row.get('verified_difference_classification') in ['', 'UNKNOWN']:problem('UNEXPLAINED_VERIFIED_DIFFERENCE',identity)
            if not HEX40.fullmatch(row.get('source_commit','')):problem('MISSING_SOURCE_COMMIT',identity)
            pin=row.get('source_pin','UNKNOWN')
            if pin=='UNKNOWN' or not valid_ref(pin,identity):problem('MISSING_SOURCE_PIN',identity)
            recipe=row.get('build_script','UNKNOWN')
            if recipe=='UNKNOWN' or not valid_ref(recipe,identity):problem('MISSING_REPRODUCTION_SCRIPT',identity)
            elif Path(recipe).suffix not in ['.sh','.py']:problem('NONEXECUTABLE_VERIFIED_RECIPE',identity)
            source=row.get('source_repo','UNKNOWN')
            if source=='UNKNOWN' or not (ROOT/source).is_dir():problem('MISSING_SOURCE_LOCATION',identity)
            elif (ROOT/source/'.git').exists() and subprocess.run(['git','cat-file','-e',row.get('source_commit','')+'^{commit}'],cwd=ROOT/source,capture_output=True).returncode:
                problem('SOURCE_COMMIT_NOT_IN_REPOSITORY',identity)
            if row.get('reproduction_status') not in ['INDEPENDENT_CLEAN_CHECKOUT_B1_B2','STAMPED_SOURCE_BUILD_BAZEL_CLEAN_B1_B2']:
                problem('VERIFIED_WITHOUT_CLEAN_BUILD',identity)
            snapshot=row.get('source_snapshot_path','UNKNOWN')
            if snapshot=='UNKNOWN' or not valid_ref(snapshot,identity):problem('MISSING_PRESERVED_SOURCE_INPUT',identity)
            total=int(frozen[identity]['function_count'])
            try:
                exact=int(row['exact_functions']);equivalent=int(row['equivalent_functions'])
                if exact+equivalent!=total:problem('FUNCTION_ACCOUNTING',identity)
                if status=='A' and equivalent!=0:problem('BYTE_EXACT_WITH_EQUIVALENT_FUNCTIONS',identity)
                if status=='B' and equivalent==0:problem('SEMANTIC_WITHOUT_EQUIVALENCE_PROOF',identity)
            except (KeyError,ValueError):problem('FUNCTION_ACCOUNTING',identity)
        if status=='C':
            recipe=row.get('build_script','UNKNOWN');pin=row.get('source_pin','UNKNOWN')
            if recipe=='UNKNOWN' or not valid_ref(recipe,identity):problem('MISSING_REPRODUCTION_SCRIPT',identity)
            if not pin.startswith('sha256:'):problem('MISSING_SOURCE_PIN',identity)
            else:
                material=''.join(f'{p}\t{h}\n' for p,h in sorted(hashes.get(identity,{}).items()))
                if pin!='sha256:'+hashlib.sha256(material.encode()).hexdigest():problem('SOURCE_PIN_MISMATCH',identity)
            if proof=='UNKNOWN':problem('MISSING_INCOMPLETE_ACCEPTANCE_EVIDENCE',identity)
        if status=='D':
            path=row.get('candidate_path','UNKNOWN')
            if path=='UNKNOWN':problem('MISSING_SOURCE_CANDIDATE',identity)
            elif not path.startswith('git-object:') and not (ROOT/path).is_dir():problem('MISSING_SOURCE_CANDIDATE',identity)
            if not HEX40.fullmatch(row.get('source_commit','')):problem('MISSING_CANDIDATE_PIN',identity)
            if row.get('candidate_evidence')=='UNKNOWN':problem('MISSING_CANDIDATE_EVIDENCE',identity)
            else:valid_ref(row['candidate_evidence'],identity)
            if path.startswith('git-object:'):
                obj=json.loads((audit/'evidence/additional-candidate-git-object.json').read_text())
                if obj['commit']!=row['source_commit'] or 'git-object:'+obj['path']!=path:problem('CANDIDATE_GIT_OBJECT_CONFLICT',identity)
                content=subprocess.check_output(['git','--git-dir',obj['repository'],'show',obj['commit']+':'+obj['path']])
                if hashlib.sha256(content).hexdigest()!=obj['sha256']:problem('CANDIDATE_GIT_OBJECT_HASH',identity)
        if status=='F':
            exclusion=row.get('exclusion_justification','UNKNOWN')
            if exclusion in ['', 'UNKNOWN']:problem('EXCLUDED_WITHOUT_JUSTIFICATION',identity)
            else:valid_ref(exclusion,identity)
        if status in ['C','D','E','G'] and row.get('blocker') in ['', 'UNKNOWN','NONE']:
            problem('GAP_WITHOUT_EXACT_BLOCKER',identity)
    owner_counts=collections.Counter(r.get('module_id','') for r in owners)
    if set(owner_counts)!=set(actual):problem('OWNERSHIP_IDENTITY_SET','ownership must cover every identity')
    for r in owners:
        i=r.get('module_id');a=by_id.get(i)
        if owner_counts[i]!=1:problem('CONFLICTING_SOURCE_OWNERS',i)
        if a and (r.get('source_owner')!=a.get('source_owner') or r.get('component_owner')!=a.get('component_owner')):
            problem('CONFLICTING_SOURCE_OWNERS',i)
    expected={i for i,r in by_id.items() if r.get('source_status') not in ['A','B','F']}
    gap_ids=[r.get('module_id','') for r in gaps]
    if set(gap_ids)!=expected or len(gap_ids)!=len(set(gap_ids)):problem('SOURCE_GAPS_COMPLEMENT','unsupported, duplicated or dropped gap identity')
    for r in gaps:
        if by_id.get(r.get('module_id'))!=r:problem('GAP_ROW_CONFLICT',r.get('module_id'))
    projects=table('RECONSTRUCTION-PROJECTS.tsv');project_ids=[]
    for p in projects:
        for identity in p.get('module_ids','').split(';'):
            project_ids.append(identity)
            if identity in by_id and p['project']!=by_id[identity]['source_group']:problem('SOURCE_PROJECT_CONFLICT',identity)
    if set(project_ids)!=expected or len(project_ids)!=len(set(project_ids)):problem('SOURCE_PROJECT_COVERAGE','every gap must have one project')
    optional=table('OPTIONAL-15-REVIEW.tsv')
    if len(optional)!=15:problem('OPTIONAL_REVIEW_COUNT',len(optional))
    edges=table('DEPENDENCY-EDGES.tsv')
    if len(edges)!=sum(len(r['imports']) for r in frozen.values()):problem('DEPENDENCY_IMPORT_COUNT',len(edges))
    keys=[(r['consumer_module_id'],r['symbol']) for r in edges]
    if len(keys)!=len(set(keys)):problem('DUPLICATE_IMPORT_EDGE','dependency keys')
    for edge in edges:
        i=edge['consumer_module_id'];symbol=edge['symbol']
        crc=frozen.get(i,{}).get('imports',{}).get(symbol)
        if crc is None or edge['required_crc']!=f'0x{crc:08x}':problem('DEPENDENCY_CRC_REQUIREMENT',f'{i}: {symbol}')
    for identity,inputs in hashes.items():
        for value,expected_hash in inputs.items():
            p=ROOT/value
            if not p.is_file():problem('MISSING_PROOF_INPUT',value)
            elif current_hash(p)!=expected_hash:problem('PROOF_INPUT_HASH_CHANGED',value)
    for value,expected_hash in baseline['workspace_inputs'].items():
        if current_hash(ROOT/value)!=expected_hash:problem('UNRELATED_WORKSPACE_INPUT_CHANGED',value)
    current_components={p.name:status for status in ['DONE','PARTIAL','BLOCKED','TODO'] for p in (WORKSPACE/f'Reverse Engineer - {status}').iterdir() if p.is_dir()}
    if current_components!={n:v['status'] for n,v in baseline['components'].items()}:problem('COMPONENT_STATUS_OR_DIRECTORY_CHANGED','workspace')
    for repository,values in baseline['maintained_repositories'].items():
        path=ROOT/values['path']
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()!=values['head']:problem('VERIFIED_SOURCE_HEAD_CHANGED',repository)
        if subprocess.check_output(['git','status','--porcelain'],cwd=path,text=True)!=values['status_porcelain']:problem('VERIFIED_SOURCE_WORKTREE_CHANGED',repository)
    counts={s:sum(r.get('source_status')==s for r in rows) for s in 'ABCDEFG'}
    if counts!=summary['source_status_counts'] or len(rows)!=summary['distinct_stock_identities']:problem('SUMMARY_COUNT_CONFLICT',counts)
    if counts['G']:warnings.append({'code':'SOURCE_CLASSIFICATIONS_UNRESOLVED','count':counts['G'],'message':'Retained historical source builds require independent recipe/input evidence; not classified missing code.'})
    warnings.append({'code':'PREEXISTING_WORKSPACE_DRIFT','message':'Global manifest/canonical Mali drift documented; immutable baseline inputs unchanged.'})
    return dict(result='FAIL' if errors else 'PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES',
        distinct_stock_identities=len(actual),unique_filenames=len({r['filename'] for r in actual.values()}),stock_occurrences=sum(len(r['stock_paths']) for r in actual.values()),
        source_status_counts=counts,errors=errors,warnings=warnings)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir',type=Path,default=AUDIT)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    result=validate(args.audit_dir)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    print(text,end='')
    if args.json:args.json.write_text(text)
    raise SystemExit(bool(result['errors']))
