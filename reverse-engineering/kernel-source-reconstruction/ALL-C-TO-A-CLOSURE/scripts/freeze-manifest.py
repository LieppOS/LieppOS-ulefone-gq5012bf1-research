#!/usr/bin/env python3
"""Freeze the authoritative Category-C closure manifest (read-only inputs, writes C-CLOSURE-MANIFEST.tsv).

Inputs: canonical audit at f61ebf03 (this branch base) + the two pending Codex deltas
(codex/audio-batch-01, codex/scp-connectivity-batch-01) read with `git show`.
"""
import csv, hashlib, io, subprocess
from pathlib import Path

P = Path(__file__).resolve().parents[1]; R = P.parents[2]
BASE = 'f61ebf03275ba2d3f6aa4f9d5aebe18e12922263'
git = lambda *a: subprocess.check_output(['git', *a], cwd=R, text=True)
rows = {r['module_id']: r for r in csv.DictReader(io.StringIO(git('show', f'{BASE}:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')), delimiter='\t')}
pend = {}
for br, d in [('codex/audio-batch-01', 'AUDIO-BATCH-01'), ('codex/scp-connectivity-batch-01', 'SCP-CONNECTIVITY-BATCH-01')]:
    head = git('rev-parse', br).strip()
    for r in csv.DictReader(io.StringIO(git('show', f'{head}:reverse-engineering/kernel-source-reconstruction/{d}/AUDIT-DELTA.tsv')), delimiter='\t'):
        if r['new_source_status'] == 'C':
            pend[r['module_id']] = (br, head, d)

USB_TC = ('../android_kernel_modules_usb_typec_ulefone_gq5012bf1-usb-typec-closure', '758f9edc78c7a50d07b8629126438a3674845911')
USB_CH = ('../android_kernel_modules_charging_battery_ulefone_gq5012bf1-usb-typec-closure', 'b2a343a9d8664b77a63dc16835b5af0fd0e55cf1')
CLOSURE = 'codex/usb-typec-closure@7e196c32 USB-TYPEC-CLOSURE'
CMDQ_TV = 'CMDQ-MAILBOX-ABI recursive symtypes preserved; default ALPS 5e41 declarations (canonical evidence)'
CMDQ_NX = 'Diff exported-symbol genksyms expansions against authentic alternative MTK cmdq/mailbox header revisions (NothingOSS KDM branches, MT6878 OEM releases); locate first divergent type node'
BTF_TV = 'public GKI 12901745 base (130351 types) -> constant +15/+389 shift residual; ALL-C: kleaf MTK ACK c364c39ae8d gki_defconfig = 130348 types'
BTF_NX = 'Build split-BTF base vmlinux from MTK ACK c364c39ae8d (exact merge of GKI 6b18f0b5) with vendor (mgk) config under kleaf-equivalent flags; require 130366 types / 2300745 string bytes'
SRCV_TV = 'USB-TYPEC-CLOSURE srcversion/sumversion traces; four metadata candidates revisited; MD4 input files enumerated'
SRCV_NX = 'Compute modpost sumversion over authentic alternative revisions of the same-directory source/header set (ALPS/NothingOSS KDM branches, other MT6878 OEM releases); accept only an exact srcversion match'
spec = {
    'cmdq-platform-mt6878.ko': ('CMDQ', 'cmdq', '1 import CRC mismatch + counter-symbol residue; all function bytes exact', CMDQ_TV, CMDQ_NX, 'mtk-cmdq-drv-ext exports'),
    'cmdq-sec-drv.ko': ('CMDQ', 'cmdq', '16 export CRC mismatches + counter-symbol residue; all function bytes exact', CMDQ_TV, CMDQ_NX, 'mtk-cmdq-drv-ext, TEE/secure-world boundary (not reconstructed)'),
    'cmdq-test.ko': ('CMDQ', 'cmdq', '3 import CRC mismatches + counter-symbol residue; all function bytes exact', CMDQ_TV, CMDQ_NX, 'mtk-cmdq-drv-ext, cmdq-sec-drv exports'),
    'mtk-cmdq-drv-ext.ko': ('CMDQ', 'cmdq', '7 export CRC mismatches + counter-symbol residue; all function bytes exact', CMDQ_TV, CMDQ_NX, 'mailbox core; 4 downstream consumers'),
    'thermal-generic-adc.ko': ('BTF', 'thermal_cooling', '.BTF type/string references only (GNU20 + 21 BTF bytes)', BTF_TV, BTF_NX, 'OEM split-BTF base vmlinux'),
    'cfg80211.ko': ('BTF', 'connectivity', '.BTF only: 25249/398337 bytes, type-ID/name-offset references', BTF_TV, BTF_NX, 'OEM split-BTF base vmlinux'),
    'mac80211.ko': ('BTF', 'connectivity', '.BTF only: 26027/363011 bytes, type-ID/name-offset references', BTF_TV, BTF_NX, 'OEM split-BTF base vmlinux; cfg80211'),
    'bluetooth.ko': ('BTF', 'connectivity', '.BTF only: 14551/215660 bytes, type-ID/name-offset references', BTF_TV, BTF_NX, 'OEM split-BTF base vmlinux'),
    'charger_class.ko': ('USB', USB_CH, 'srcversion only (90/90 functions, data 20/21: __UNIQUE_ID_srcversion)', SRCV_TV, SRCV_NX, 'none beyond Batch04 providers'),
    'mtk_chg_type_det.ko': ('USB', USB_CH, 'srcversion only (8/8 functions, data 20/21)', SRCV_TV, SRCV_NX, 'none beyond Batch04 providers'),
    'rt_pd_manager.ko': ('USB', USB_TC, 'srcversion only (11/11 functions, data 19/20)', SRCV_TV, SRCV_NX, 'tcpc_class'),
    'tcpc_mt6375.ko': ('USB', USB_TC, 'srcversion + __COUNTER__-numbered .modinfo/addressable objects (66/66 functions, data 21/28)', SRCV_TV + '; license/version ordering restored', 'Recover OEM translation-unit composition that shifts __COUNTER__ by +1 (extra counter user before module macros) and the same-directory token set', 'tcpc_class'),
    'tcpc_class.ko': ('USB', USB_TC, 'srcversion only after closure (709/709 functions, 113/114 data, 54 timers exact)', SRCV_TV + '; 701->709 functional closure done', SRCV_NX, 'none beyond Batch04 providers'),
    'aw883xx_driver.ko': ('AUDIO', 'audio', 'aw883xx_dev_cfg_load: 3560 B stock vs 3496 B build, 248/892 normalized instructions (inlined scene parser)', '18 falsified scene-parser variants (AUDIO-BATCH-01 evidence/aw883xx-scene-parser)', 'Recover pass-1 block order: helper extraction of insertion sort + int8/uint16 profile index types (per AUDIO-BATCH-01 BLOCKERS)', 'none (CRC/KCFI exact)'),
    'focaltech_touch_spi_ft3680.ko': ('LEGACY', 'research workspace', '40 functions size-different; opcode/call-boundary differences; recipe incomplete', 'historical display-input/ft3680 reconstruction', 'Recover authentic FocalTech FT3680 SPI driver revision; re-run function-level diff against it', 'yft_devinfo exports'),
    'yft_devinfo.ko': ('LEGACY', 'research workspace', '10 exported device_add CRCs + 11 KCFI IDs differ; provider enum/type graph; probe/sysfs codegen', 'historical YFT-DEVINFO reconstruction; enum-tag search (~1.4e13 spellings excluded, SCP-CONNECTIVITY-BATCH-01)', 'Recover ODM yft_devinfo header (enum/type graph) from consumer debug strings and CRC inversion constraints', 'consumers: hf_manager, touch, camera, charging'),
    'st21nfc.ko': ('LEGACY', 'research workspace', '22/24 raw function matches; relocation/semantic acceptance not demonstrated; recipe incomplete', 'historical ST21NFC reconstruction', 'Re-diff the 2 mismatching functions against ST public st21nfc revisions; complete clean recipe', 'none known'),
    'tkcore.ko': ('LEGACY', 'research workspace', 'only 5/19 consumer CRC edges reproduced; 14 private-type CRC edges', 'historical TRUSTKERNEL source island', 'Recover TrustKernel private type declarations from consumer modules symtypes constraints', 'TEE boundary (trusted world not reconstructed)'),
}
out = []
for mid in [m for m, r in rows.items() if r['source_status'] == 'C'] + sorted(pend):
    r = rows[mid]; name = r['filename']
    grp, repo, residual, tried, nxt, deps = spec[name]
    if isinstance(repo, tuple):
        src_repo, src_commit, lineage, owner = repo[0], repo[1], 'USB-TYPEC-CLOSURE committed source (supersedes canonical ' + r['source_commit'][:10] + ')', CLOSURE
    elif mid in pend:
        br, head, d = pend[mid]
        src_repo, src_commit = r['source_repo'], 'see ' + d
        lineage, owner = f'{br}@{head[:8]} {d}', f'{br} (pending, not integrated)'
    else:
        src_repo, src_commit, lineage, owner = r['source_repo'], r['source_commit'], r['source_group'], 'canonical master (f61ebf03)'
    out.append(dict(module_id=mid, filename=name, group=grp,
                    initial_class='C' if r['source_status'] == 'C' else f"C (pending delta; canonical {r['source_status']})",
                    stock_sha256=r['stock_sha256'], stock_partition=r['partitions'], maintained_source_repo=src_repo,
                    maintained_source_commit=src_commit, compiled_source_lineage=lineage, current_exact_residual=residual,
                    already_tested_variants=tried, proposed_next_experiment=nxt, external_dependencies=deps,
                    worktree_owner=owner, acceptance_state='C_OPEN'))
assert len(out) == 18 and len({o['module_id'] for o in out}) == 18
with (P / 'C-CLOSURE-MANIFEST.tsv').open('w', newline='') as f:
    w = csv.DictWriter(f, list(out[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(out)
(P / 'C-CLOSURE-MANIFEST.sha256').write_text(hashlib.sha256((P / 'C-CLOSURE-MANIFEST.tsv').read_bytes()).hexdigest() + '  C-CLOSURE-MANIFEST.tsv\n')
print(len(out), 'rows;', sum(o['initial_class'] == 'C' for o in out), 'canonical C +', len(pend), 'pending C')
