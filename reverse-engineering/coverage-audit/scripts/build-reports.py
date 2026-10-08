#!/usr/bin/env python3
"""Measured coverage reports, synchronized with authorized accelerator registration.
No reconstruction, stock rediscovery or hardware operations. Replay from committed tables.
"""
from __future__ import annotations
import csv
import json
import os
from collections import Counter
from pathlib import Path
from urllib.parse import quote
from audit_policy import CANDIDATES, INTEGRATION, PROPOSALS

HERE=Path(__file__).resolve().parent;CA=HERE.parent;RE=CA.parent
PARTIAL_MEANING={'A':'Actionable static RE; runtime acceptance separate','B':'Closed kernel/source boundary; proprietary integration remains','C':'Proprietary boundary','D':'Hardware/runtime/teardown gated','E':'Stale/duplicate/wrong scope','F':'Umbrella/tracking scope'}

def read(name):
 with (CA/name).open() as f:return list(csv.DictReader(f,delimiter='\t'))
def save(path,text):path.write_text(text.rstrip()+'\n');print(path.relative_to(RE.parent))
def esc(s):return (s or '-').replace('|','\\|').replace('\n',' ')
def link_from(path,base=None):return quote(os.path.relpath(RE.parent/path,base or CA),safe='/-_.')
def metrics():
 names={'components':'components.tsv','km':'kernel-modules.tsv','dt':'device-tree.tsv','hw':'hardware.tsv','hs':'hals-services.tsv','vs':'vendor-services.tsv','fw':'firmware.tsv','sw':'secure-world.tsv','bs':'boot-storage.tsv','ai':'android-integration.tsv','ul':'userspace-libraries.tsv','art':'artifact-map.tsv'}
 m={k:read(v) for k,v in names.items()};m['status']=Counter(x['status'] for x in m['components']);m['partial']=Counter(x['partial_class'] for x in m['components'] if x['status']=='PARTIAL')
 m['snapshot']=json.loads((CA/'audit-evidence/final-snapshot.json').read_text());m['manifest']=json.loads((CA/'audit-evidence/manifest-audit-2026-10-07.json').read_text());return m
def stamp(m):return f"Snapshot: **{m['snapshot']['date']}**, source HEAD `{m['snapshot']['source_head']}`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction."
def next_targets(m):
 by={x['component']:x for x in m['components']};out=[]
 for c in CANDIDATES:
  if c['component'] not in by:raise ValueError('unregistered target '+c['component'])
  r=by[c['component']]
  if r['status']=='PARTIAL' and r['partial_class']=='A':out.append({'rank':len(out)+1,'status':'PARTIAL',**c})
 return out
def compact_ranking(m,base=None):return [f"{r['rank']}. **{r['component']}** — {r['kind']}; [handoff/evidence]({link_from(r['research_path'],base)})." for r in next_targets(m)]

def build_next(m):
 targets=next_targets(m)
 with (CA/'next-re.tsv').open('w',newline='') as f:
  fields=list(targets[0]) if targets else ['rank','status','component'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(targets)
 out=['# Next-RE handoff priorities','',stamp(m),'','Accelerator priority follows the authorized dependency-aware roadmap, not unsupported closure-probability or hour estimates. Remaining general static targets follow it. DONE and non-A targets are automatically omitted. No reconstruction is performed here.','']
 for r in targets:
  out += [f"## {r['rank']}. {r['component']} — {r['status']}",'']+[f'- **{k}:** {r[k]}' for k in ('kind','scope','difficulty','probability','evidence','missing','closure','effort','dependency','phone')]+[f"- [Canonical handoff/evidence]({link_from(r['research_path'])}).",'']
 out += ['## Separate ROM integration queue','','| Component | Status | Remaining action |','|---|---|---|'];by={x['component']:x for x in m['components']}
 for n,a in INTEGRATION.items():
  if n in by:out.append(f"| {n} | {by[n]['status']} | {esc(a)} |")
 out += ['','[Accelerator roadmap](../accelerator-re-roadmap.md): six prepared scopes, precise reconstruction order and proprietary exclusions. Runtime/HAL/SELinux, proprietary and inventory tracking are not module-parity shortcuts.'];save(CA/'NEXT-RE.md','\n'.join(out))

def build_partial(m):
 rs=[x for x in m['components'] if x['status']=='PARTIAL'];out=['# PARTIAL triage','',stamp(m),'',f'All **{len(rs)}** current PARTIAL directories have one A–F class. Camera kernel child is A; HAL/3A/firmware algorithms remain C. Existing static DONE scopes stay DONE.','','| Component | Class | Remaining boundary | Next action | Difficulty | Dependencies |','|---|---|---|---|---|---|']
 for r in rs:out.append('| '+' | '.join(esc(r[k]) for k in ('component','partial_class','blocker','recommended_action','difficulty','dependencies'))+' |')
 out += ['','## Classification totals','','| Classification | Count |','|---|---:|']+[f"| {k} — {v} | {m['partial'][k]} |" for k,v in PARTIAL_MEANING.items()]+[f'| **Total PARTIAL** | **{len(rs)}** |','','## Ranked static targets','']+compact_ranking(m);save(CA/'PARTIAL-TRIAGE.md','\n'.join(out))

def build_missing(m):
 e=[r for r in m['art'] if r['coverage']=='E'];out=['# Current missing-coverage verdict','',stamp(m),'',f'**{len(e)} unmapped normalized rows.** The prior Mali ownership hole is filled by the authorized MALI-GPU-KERNEL PARTIAL registration. Ownership is not source/parity closure.','','## Six prepared normal-world kernel owners','']
 for n in ('MALI-GPU-KERNEL','APUSYS-NPU-KERNEL','CAMERA-ISP-KERNEL','MTK-VCODEC-KERNEL','MTK-MDP-KERNEL','GPU-AI-AUX-KERNEL-INTERFACES'):
  r=next(x for x in m['components'] if x['component']==n);out.append(f"- **{n} ({r['status']})**: {r['modules']}. [Handoff](../accelerator-preparation/{n}/CLAUDE-HANDOFF.md).")
 out += ['','APUSYS/MDLA/RPMsg is accelerator-kernel ownership, not camera-consumer ownership. Camera child preserves existing function/data proofs; HAL parent stays PARTIAL. MDP is not DRM DONE, and GPUEB/VCP clients are not TinySys IPI DONE. Shared generic infrastructure and proprietary firmware remain explicit boundaries.','','RT5133 still denotes an unbound reference client; its supported static DONE scope and rejected rename are unchanged. [Capture correction](notes/RT5133-CORRECTION.md). No new hardware binding/execution or parity is claimed.']
 if e:out += ['','## Remaining exact unmapped records']+[f"- {r['artifact_type']}: `{r['artifact']}`" for r in e]
 save(CA/'MISSING-COVERAGE.md','\n'.join(out))

def build_changes(m):
 count=len(m['components']);delta=sum(p[4] for p in PROPOSALS if p[3]=='ACCEPT RECOMMENDATION');out=['# Taxonomy decisions after accelerator preparation','',stamp(m),'',f'**Current registered total: {count}.** Six authorized PARTIAL registrations (including the camera child) are applied. No unrelated merge, removal, rename or DONE promotion was performed.','','| Proposal | Operation | Decision | Remaining conditional change |','|---|---|---|---:|']
 out += [f'| {p[0]} | {p[1]} | {p[3]} | {p[4]:+d} |' for p in PROPOSALS]
 for cid,op,n,decision,d,why,preserve in PROPOSALS:out += ['',f'## {cid}: {op} — {decision}','',f'- **Components:** {n}',f'- **Rationale:** {why}',f'- **Preservation/remaining consequences:** {preserve}',f'- **Remaining conditional change:** {d:+d}']
 out += ['','## Conditional count, not current reality','',f'Only still-unapplied accepted recommendations would yield {count} {delta:+d} = **{count+delta} canonical components**. This is not current reality; applied additions are not counted twice. All unrelated migrations need separate approval and evidence-preserving redirects/manifest/index changes. RT5133 rename remains rejected.'];save(CA/'PROPOSED-CHANGES.md','\n'.join(out))

def build_readiness(m):
 out=['# LieppOS development readiness','',stamp(m),'','| Target | Assessment | Remaining work |','|---|---|---|',
 '| Custom GKI/kernel | Static baseline strong; custom boot unproved | Preserve SYSTEM-DLKM 60/60 baseline, exact containers and KMI; close accelerator/source/DT ABI and validate actual boot later. |',
 '| Full custom ROM | Integration incomplete | Preserve external 24afa6b vendor.prop and bluetooth_audio.xml fixes; verify emitted properties, VINTF, init, enforcing SELinux and real HAL registration. |',
 '| Daily driver | NOT PROVEN | Actual boot, radio/IMS, camera/audio, connectivity, sensors, fingerprint/NFC, suspend, charging/thermal, OTA/recovery acceptance remains. |',
 '| Hardware parity | Proprietary/physical/runtime gated | Retain CSF/APU/VCP/CCU/SCP/DSP/modem images, 3A/PQ/tuning, RIL/IMS, TAs and calibration; static preparation proves no accelerator execution. |',
 '| Google-free LieppOS | Product integration work | Remove/replace Google services while retaining vendor contracts; decide DRM/attestation/app compatibility. |',
 '| Stock-integrity secondary slot | Stock B anchor verified | Preserve B and shared userdata/FBE/metadata/rollback/snapshot state; never overwrite anchor for experimental tests. |',
 '| Future Linux slot | Source-actionable baseline, feature parity uncertain | Accelerator source/ABI, remote firmware, Linux userspace replacements, audio/sensors/modem/display and power policy remain. |',
 '','## Existing closures preserved','']
 by={r['component']:r for r in m['components']}
 for n in ('SYSTEM-DLKM','BOOT-IMAGES','VENDOR-PROPERTIES','VINTF-HAL-MANIFEST','PARTITION-OWNERSHIP','USB-CHARGER-INTEGRATION','INTERNAL-THERMAL-USB'):
  r=by[n];out.append(f"- **{n} ({r['status']})**: {r['notes']}. [Research]({link_from(r['research_path'])}).")
 out += ['','Do not force RT5133 binding; the observed failure releases GPIO1 for the working WL2864C camera rails. [Correction](notes/RT5133-CORRECTION.md). Property installation, build success and component DONE never replace runtime acceptance.'];save(CA/'PORT-READINESS.md','\n'.join(out))

def build_summary(m):
 s=m['status'];active=[r for r in m['dt'] if int(r['nodes_enabled'])>0];e=sum(r['coverage']=='E' for r in m['art']);out=['# Coverage verdict: ACCOUNTED — kernel RE pending','',stamp(m),'','Authorized accelerator preparation fills ownership, not source or runtime parity. All six scopes are accessible; no proprietary firmware payload copied.','',f"- Components **{len(m['components'])}**: DONE **{s['DONE']}**, PARTIAL **{s['PARTIAL']}**, BLOCKED **{s['BLOCKED']}**, TODO **{s['TODO']}**.",f"- Modules **{len(m['km'])}**; DT **{len(m['dt'])}** / **{sum(int(r['nodes']) for r in m['dt'])}** node instances; active mapped **{sum(r['coverage']!='E' for r in active)}/{len(active)}**.",f"- HAL/services **{len(m['hs'])+len(m['vs'])}**; firmware **{len(m['fw'])}**; secure-world **{len(m['sw'])}**; partitions **{len(m['bs'])}**.",f"- Integration **{len(m['ai'])}**; significant libraries **{len(m['ul'])}**; normalized records **{len(m['art'])}**; unmapped E **{e}**.",'','## PARTIAL A–F','']+[f"- {k}={m['partial'][k]} — {v}" for k,v in PARTIAL_MEANING.items()]
 out += ['','## Accelerator ownership applied','','Six registrations own 41 exact stock targets. Preserve 16 camera function/data proof pairs, SCP/ADSP/TinySys and named camera DONE scopes. No new module parity, hardware execution or unrelated taxonomy migration is claimed. [Roadmap](../accelerator-re-roadmap.md).','','## Next work','']+compact_ranking(m)+['','## Validation/hygiene','','Historical audit/manifest records remain historical; the accelerator preparation validation records current scoped registration, exact input checks, manifest drift and reproducibility. [Preparation](../accelerator-preparation/README.md). [RT5133 retraction](notes/RT5133-CORRECTION.md) remains valid. See [PARTIAL triage](PARTIAL-TRIAGE.md), [taxonomy](PROPOSED-CHANGES.md) and [readiness](PORT-READINESS.md). Stop global inventory work; proceed only with component reconstruction and later authorized integration/runtime validation.'];save(CA/'SUMMARY.md','\n'.join(out))

def build_index(m):
 out=['# GQ5012BF1 reverse-engineering index','',stamp(m),'','Phone: Ulefone Armor 29 Pro Thermal / GQ5012BF1 / MT6878T. DONE is named static/source/inventory closure, not proprietary openness or runtime readiness. `component` is singleton primary ownership; co-mentions/umbrellas are references only. Accelerator registrations were authorized preparation, not reconstruction.','','## Current totals','','| Status | Count |','|---|---:|']+[f"| {s} | {m['status'][s]} |" for s in ('DONE','PARTIAL','BLOCKED','TODO')]+[f"| **TOTAL** | **{len(m['components'])}** |",'','## PARTIAL classification','','| Classification | Count |','|---|---:|']+[f"| {k} — {v} | {m['partial'][k]} |" for k,v in PARTIAL_MEANING.items()]
 out += ['','## Master component table','','| Component | Status | Subsystem | Scope | Class | Kernel | Userspace | Firmware | Hardware | Remaining/DONE limits | Research | Workspace |','|---|---|---|---|---|---|---|---|---|---|---|']
 for r in m['components']:
  ws=RE.parent.parent/r['workspace_path']/'README.md';fields=[r[k] for k in ('component','status','subsystem','scope','partial_class','kernel_state','userspace_state','firmware_state','hardware_state')]+[r['blocker'] or r['notes']]
  out.append('| '+' | '.join(esc(x) for x in fields)+f" | [report]({link_from(r['research_path'],RE)}) | [scope]({quote(os.path.relpath(ws,RE),safe='/-_.')}) |")
 out += ['','## Accelerator preparation','','[Six-scope roadmap](accelerator-re-roadmap.md), [precise module/DT/source metadata and Claude handoffs](accelerator-preparation/README.md). Six new PARTIALs, no unrelated merges/removals/renames. Camera HAL stays proprietary PARTIAL; sensor TUs/EEPROM/VCM/OIS/rails and existing transports remain DONE. APUSYS is not camera kernel ownership; MDP is not DRM closure; GPUEB/VCP clients are not transport closure.','','## Current artifact axes','']
 for n,k in (('kernel-modules','km'),('device-tree','dt'),('hardware','hw'),('hals-services','hs'),('vendor-services','vs'),('firmware','fw'),('secure-world','sw'),('boot-storage','bs'),('android-integration','ai'),('userspace-libraries','ul'),('artifact-map','art')):out.append(f"- [{n}.tsv](coverage-audit/{n}.tsv): {len(m[k])} rows, coverage {dict(sorted(Counter(r['coverage'] for r in m[k]).items()))}.")
 out += ['','## Ranked static work','']+compact_ranking(m,RE)+['','[Summary](coverage-audit/SUMMARY.md), [triage](coverage-audit/PARTIAL-TRIAGE.md), [ownership gaps](coverage-audit/MISSING-COVERAGE.md), [taxonomy](coverage-audit/PROPOSED-CHANGES.md), [readiness](coverage-audit/PORT-READINESS.md). [RT5133 correction](coverage-audit/notes/RT5133-CORRECTION.md) remains valid. Preserve external property/VINTF fixes and stock B; actual boot/SELinux/HAL/OTA and proprietary algorithms remain separate. No further global discovery is required for this captured stock build.'];save(RE/'index.md','\n'.join(out))

def build_manifest_note(m):
 a=m['manifest'];out=['# Manifest hygiene — historical baseline','','Frozen 2026-10-07 audit; not current directory totals and not an accelerator registration run. Unrelated drift is not silently repaired.','','| Measure | Historical result |','|---|---:|']
 for label,key in (('Manifest rows','rows_total'),('Resolved','rows_resolved'),('Missing','rows_missing_file'),('Malformed','rows_wrong_field_count'),('Hash mismatches','rows_hash_mismatch'),('Size mismatches','rows_size_mismatch'),('Unregistered files','unregistered_files_total')):out.append(f'| {label} | {a[key]} |')
 out += [f"| Duplicate paths | {len(a['duplicate_paths'])} |",'','[Historical machine result](../audit-evidence/manifest-audit-2026-10-07.json). Current scoped registration/drift is recorded separately in accelerator-preparation validation.'];save(CA/'notes/MANIFEST-HYGIENE.md','\n'.join(out))

def build_readme(m):
 out=['# GQ5012BF1 coverage database — accelerator ownership synchronized','',stamp(m),'',f"[PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md): all {m['status']['PARTIAL']} current PARTIAL components. Six authorized PARTIAL additions and singleton module/DT ownership are applied; no source parity is fabricated. [Accelerator roadmap](../accelerator-re-roadmap.md).",'','## Reports','']+[f'- [{n}]({n})' for n in ('SUMMARY.md','PARTIAL-TRIAGE.md','NEXT-RE.md','MISSING-COVERAGE.md','PROPOSED-CHANGES.md','PORT-READINESS.md')]+['','## Reproduce committed metadata','','```sh']
 out += [f'python3 reverse-engineering/coverage-audit/scripts/{s}.py' for s in ('build-kernel-modules','build-devicetree','build-hardware','build-services','build-integration','build-components','build-reports','check-audit','test-final-audit')]+['```','','No fresh full module investigation or payload harvest. Changed pack identity/claims were refreshed with existing harvesters. [Current snapshot](audit-evidence/final-snapshot.json). [Historical final-audit validation](notes/FINAL-VALIDATION.md) is not the new accelerator snapshot; current preparation has its own validation record. No proprietary payload enters Git.'];save(CA/'README.md','\n'.join(out))

def build_axis_notes(m):
 out=['# HAL, init, firmware, secure-world and boot/storage coverage','',stamp(m),'','Built from committed metadata-only raw TSVs and current curated ownership; no payload copied. Source availability, DT enablement and interface declaration are not runtime or parity proof.','','## Measured inventory','','| Axis | Rows | A | B | C | D | E |','|---|---:|---:|---:|---:|---:|---:|']
 for label,k in [('VINTF families + legacy HAL libraries','hs'),('Init services + trigger executables','vs'),('Firmware/calibration payloads','fw'),('Secure-world surfaces','sw'),('Scatter/ABOTA partition families','bs')]:
  c=Counter(r['coverage'] for r in m[k]);out.append(f'| {label} | {len(m[k])} | '+' | '.join(str(c[a]) for a in 'ABCDE')+' |')
 out += ['','GPU interface/service ownership is now MALI-GPU-KERNEL PARTIAL, not an E gap. CSF/APU/GPUEB/VCP binary algorithms are excluded; CCU algorithms remain camera HAL, with a separate ISP host owner. Firmware owner denotes the interface/retention boundary, never reconstructed remote internals. Loading claims are per-payload evidence to reconcile, not proof of a universal Linux loader.','','Matrix declarations are framework requirements, not implementation proof. Twenty-two missing-executable non-trigger service groups remain reference baggage; virtual camera, face example and alternative fingerprint templates are not additional fitted hardware. DOOGEE-named EIS calibration remains reference tuning. A/B partition pairs are grouped, not new components. Secure-world/boot ownership is separate from accelerator host ABI.','','Reproduce: `python3 scripts/build-services.py` then `python3 scripts/build-reports.py` from the coverage-audit directory. Raw stock harvests are preserved; no repeated hardware discovery required.'];save(CA/'notes/SERVICES-FIRMWARE.md','\n'.join(out))

 def_update=CA/'notes/ANDROID-USERSPACE.md';text=def_update.read_text()
 text=text.replace('missing GPU kernel/service implementation ownership remains E on the service/KMD/DT axes','GPU kernel/service implementation now has registered PARTIAL ownership on the service/KMD/DT axes')
 text=text.replace('Mali/GPU userspace libraries are represented by `VENDOR-BLOB-HAL-INVENTORY`; that does not close the separate missing active Mali kernel/DT ownership scope.','Mali/GPU consumers are assigned to the registered `MALI-GPU-KERNEL` kernel-facing boundary where applicable; proprietary payloads are retained, not reconstructed.')
 text=text.split('## Unified artifact map')[0]+'## Unified artifact map\n\n'+f"`artifact-map.tsv` has {len(m['art']):,} normalized records; {sum(r['coverage']=='E' for r in m['art'])} current E ownership gaps after the authorized accelerator registrations. The historical ten Mali E rows are now assigned, not source/runtime-closed.\n"
 save(def_update,text)

def main():
 m=metrics()
 for fn in (build_next,build_partial,build_missing,build_changes,build_readiness,build_summary,build_index,build_manifest_note,build_readme,build_axis_notes):fn(m)
if __name__=='__main__':main()
