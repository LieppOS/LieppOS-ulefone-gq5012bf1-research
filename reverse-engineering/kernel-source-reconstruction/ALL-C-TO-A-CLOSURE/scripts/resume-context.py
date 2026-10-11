#!/usr/bin/env python3
"""Recover daef94c6 and add two verified DRM identities without editing other checkouts."""
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parents[1]
R=P.parents[2]
B=R.parent
ORIGINAL='daef94c683565afd027dc68235912bf3533f84db'
STAGED='437ebd5762afa2512fe1ba10102e6b4f4d6beba9'
AUD='reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
PREFIX='reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE/'
def git(*a,repo=R):
    return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def rows(text):
    return list(csv.DictReader(io.StringIO(text),delimiter='\t'))
def tsv(path,records):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,list(records[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(records)
original=subprocess.check_output(['git','-C',str(R),'show',ORIGINAL+':'+PREFIX+'C-CLOSURE-MANIFEST.tsv'])
orig=rows(original.decode());assert len(orig)==18
current=rows((P/'C-CLOSURE-MANIFEST.tsv').read_text());assert current[:18]==orig
(P/'C-CLOSURE-ORIGINAL-MANIFEST.tsv').write_bytes(original)
old_sha=hashlib.sha256(original).hexdigest()
(P/'C-CLOSURE-ORIGINAL-MANIFEST.sha256').write_text(old_sha+'  C-CLOSURE-ORIGINAL-MANIFEST.tsv\n')
staged=rows(git('show',STAGED+':'+AUD));staged_by={x['filename']:x for x in staged}
source=B/'android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1'
assert git('rev-parse','HEAD',repo=source)=='425ffd724462639899a71d3aa57da85b290037fe'
assert git('status','--porcelain',repo=source)==''
addition=[]
for name in ['drm_display_helper.ko','drm_dma_helper.ko']:
    row=staged_by[name];assert row['source_status']=='C' and row['source_commit']=='425ffd724462639899a71d3aa57da85b290037fe'
    operand=Path('/home/armol/kernel-work/allc/stock-ops/vendor_boot_platform')/name
    assert hashlib.sha256(operand.read_bytes()).hexdigest()==row['stock_sha256']
    assert operand.stat().st_size==int(row['stock_size'])
    addition.append(dict(module_id=row['module_id'],filename=name,group='BTF-DRM',initial_class='C (pending Codex delta; canonical D)',
        stock_sha256=row['stock_sha256'],stock_partition=row['partitions'],
        maintained_source_repo='../'+source.name,maintained_source_commit=row['source_commit'],
        compiled_source_lineage='AUDIO-DEPENDENCIES-BATCH-02:'+row['public_source_pins'],
        current_exact_residual='Split-BTF type/name references only; all non-BTF/GNU20 bytes exact in Codex B1/B2',
        already_tested_variants='Public GKI12901745 base leaves +15 types/+389 string-byte reference residual; original Codex proof retained',
        proposed_next_experiment='Compile unchanged target source using source-generated MTK ACK OEM base cafe5987; strict GNU20-only whole ELF, then fresh B1/B2',
        external_dependencies='Source-generated OEM split-BTF base; official GKI core symvers; genuine rebuilt shared provider witnesses',
        worktree_owner='AUDIO-DEPENDENCIES-BATCH-02; this task uses a separate audio_shared_infrastructure-allc clone',acceptance_state='C_OPEN'))
assert len({x['module_id'] for x in orig+addition})==20
tsv(P/'C-CLOSURE-MANIFEST-AMENDMENT.tsv',addition)
tsv(P/'C-CLOSURE-MANIFEST.tsv',orig+addition)
new_sha=hashlib.sha256((P/'C-CLOSURE-MANIFEST.tsv').read_bytes()).hexdigest()
(P/'C-CLOSURE-MANIFEST.sha256').write_text(new_sha+'  C-CLOSURE-MANIFEST.tsv\n')
state=json.loads((P/'C-CLOSURE-STATE.json').read_text());accepted=[x for x in state['modules'] if x['accepted']]
assert len(accepted)==8
recovery=[]
for m in state['modules']:
    item=dict(filename=m['filename'],module_id=m['module_id'],recovered_class=m['final_class'],source_commit=m['source_commit'],residual=m['exact_parity'],evidence=m['evidence'],next_experiment=m['next_immediate_action'])
    if m['accepted']:
        proofs=[json.loads((P/e).read_text())[m['filename'][:-3]] for e in m['evidence']]
        assert len(proofs)==2 and all(x['unresolved']==0 and x['stock_sha256']==m['stock_sha256'] for x in proofs)
        assert proofs[0]['normalized_sha256']==proofs[1]['normalized_sha256']
        item['acceptance_axes']={k:proofs[0][k] for k in ['functions','data','imports','exports','kcfi_abs_ids','relocations','bytes','allowed_range','normalized_sha256']}
    recovery.append(item)
context=dict(resumed_commit=ORIGINAL,own_head=git('rev-parse','HEAD'),own_status=git('status','--porcelain'),
    original_manifest_sha256=old_sha,amended_manifest_sha256=new_sha,original_targets=18,added_targets=2,
    recovered_A=8,recovered_remaining_C=10,extended_remaining_C_before_experiments=12,
    worktrees=git('worktree','list','--porcelain'),modules=recovery,amendment=addition,
    source_heads=[],audits={},disproven_experiments=rows((P/'EXPERIMENTS.tsv').read_text()),
    untested_source_backed_hypotheses=['DRM helpers with already source-reproduced OEM BTF base','AW883XX independently typed helper-extracted insertion-sort composition'],
    exclusions=['No other agent checkout edits','No shared stock edits','No hardware','No pushes'])
for path in sorted(B.glob('android_kernel_modules_*ulefone_gq5012bf1*')):
    context['source_heads'].append(dict(path=str(path),head=git('rev-parse','HEAD',repo=path),status=git('status','--porcelain',repo=path)))
for label,sha in [('canonical',git('rev-parse','HEAD',repo=B/'ulefone-gq5012bf1-research')),('codex57','55dab18ac0470d4145f05fba48076b75d9e75ebb'),('codex22',STAGED)]:
    audit=rows(git('show',sha+':'+AUD));index={x['module_id']:x for x in audit}
    counts=dict(collections.Counter(x['source_status'] for x in audit))
    overlap=[x['module_id'] for x in accepted if index[x['module_id']]['source_status'] in ['A','B']]
    context['audits'][label]=dict(commit=sha,counts=counts,existing_A_overlap=overlap,closure_classes={x['module_id']:index[x['module_id']]['source_status'] for x in orig+addition})
required=['C-CLOSURE-STATE.json','C-CLOSURE-MANIFEST.tsv','C-CLOSURE-SUMMARY.md','MODULE-PARITY.tsv','EXPERIMENTS.tsv','BLOCKERS.tsv','LEGACY-C-RECONSTRUCTION.md','CMDQ-CRC-TYPE-GRAPHS.md','OEM-BTF-BASE-INVESTIGATION.md','USB-SRCVERSION-PROVENANCE.md','TCPC-CLASS-FINAL-DIFFS.md','AW883XX-FINAL-DIFF.md','BUILD-REPRODUCTION.md','AUDIT-DELTA.tsv']
context['read_checkpoint_files']={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in required}
(P/'evidence/resume-context.json').write_text(json.dumps(context,indent=2)+'\n')
text='# Resume from daef94c6 — recovered evidence, additive DRM scope\n\nOriginal18 immutable rows are preserved byte-for-byte in C-CLOSURE-ORIGINAL-MANIFEST.tsv.\nC-CLOSURE-MANIFEST-AMENDMENT.tsv adds only two verified DRM identities from Codex staged\n437ebd57 at maintained source425ffd72; no other checkout or ownership record was edited.\n\n| Module | Recovered class | Actual source commit | Evidence / precise residual | Next executable experiment |\n|---|---|---|---|---|\n'
for m in recovery:
    residual='Strict B1/B2 GNU20-only acceptance; '+str(m['acceptance_axes']['functions'])+' functions' if m['recovered_class']=='A' else str(m['residual'])
    text+='| '+' | '.join([m['filename'],m['recovered_class'],m['source_commit'],residual,m['next_experiment']])+' |\n'
for m in addition:text+='| '+' | '.join([m['filename'],'C (amendment)',m['maintained_source_commit'],m['current_exact_residual'],m['proposed_next_experiment']])+' |\n'
text+='\n## Already rejected hypotheses\n\n'
for e in context['disproven_experiments']:
    text+='- '+e['id']+': '+e['measured_result']+' ('+e['result']+').\n'
text+='\n## Canonical vs staged accounting\n\n'
for label,a in context['audits'].items():text+='- '+label+' '+a['commit']+': '+str(a['counts'])+'; existing closure-A overlap='+str(len(a['existing_A_overlap']))+'.\n'
text+='\nNo projected totals are forced. Original8 A are preserved; scope is20 with12 open before new experiments.\nFull identities, source HEADs/status, worktree ownership, B1/B2 axes, checkpoint hashes\nand exact per-target next actions are in evidence/resume-context.json.\n'
(P/'RESUME-DAEF94C6.md').write_text(text)
print('Recovered8 A/10 C; separately verified2 DRM C additions; original18 frozen rows preserved; extended20 targets/12 C before new experiments')
