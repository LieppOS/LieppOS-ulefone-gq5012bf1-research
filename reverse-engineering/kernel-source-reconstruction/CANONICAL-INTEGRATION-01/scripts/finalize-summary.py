#!/usr/bin/env python3
"""Deterministically refresh the human-readable audit narrative after apply-canonical.py.

Every number is computed from the current identity-keyed ALL-457-MODULES.tsv; each textual
replacement must match exactly once or the script aborts (no silent drift).  Historical
"Then: N certified" entries are preserved verbatim; one new entry is appended.  Re-running
on an already-finalized tree is a no-op (idempotent).  Runs the unchanged validator after.
"""
import collections, csv, os, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
A = R / 'reverse-engineering/kernel-source-parity-audit'
rows = list(csv.DictReader((A / 'ALL-457-MODULES.tsv').open(), delimiter='\t'))
c = collections.Counter(r['source_status'] for r in rows)
cert = c['A'] + c['B']; unc = 458 - cert - c['F']
first = sum(r['necessity'] == 'REQUIRED_BY_RETAINED_FIRST_STAGE_LOAD_CONTRACT' and r['source_status'] not in 'ABF' for r in rows)
unknown = sum(r['necessity'] == 'UNKNOWN' for r in rows)
assert (c['A'], c['B'], c['C'], c['D'], c['E'], c['F'], c['G']) == (333, 1, 10, 60, 0, 0, 54), dict(c)
S = A / 'SUMMARY.md'; t = S.read_text()
MARK = '**CANONICAL-INTEGRATION-01 processed:**'


def once(old, new):
    global t
    assert t.count(old) == 1, ('anchor not unique', old[:80], t.count(old))
    t = t.replace(old, new)


if MARK not in t:
    once("> `../kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-SUMMARY.md`.\n",
         "> `../kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-SUMMARY.md`.\n\n"
         f"> {MARK} completed packages integrated by identity-keyed CAS on f61ebf03:\n"
         "> AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01, AUDIO-DEPENDENCIES-BATCH-02 (via\n"
         "> COMPLETED-BATCHES-INTEGRATION-01, 57A/6C), NEXT-DG-BATCH-01 (22 D→A) and\n"
         "> ALL-C-TO-A-CLOSURE (10 C→A after canonical combined-environment strict reverification;\n"
         "> 32 already-A rows moved to the superseding verified recipe tips), plus the USB-TYPEC-CLOSURE\n"
         "> 22-field C-evidence update (no class change). STOCK-INVENTORY-INTEGRITY history merged.\n"
         f"> Current: **{cert} certified /{unc} remaining of458**. Ten C retained with explicit blockers.\n"
         "> See `../kernel-source-reconstruction/CANONICAL-INTEGRATION-01/INTEGRATION-SUMMARY.md`.\n")
    once("| A — VERIFIED_BYTE_EXACT | 244 | 60 system_dlkm ELF bodies;40 accelerator;6 boot-clock;10 storage;4 pinctrl;4 regulator;3 interconnect/EMI;1 IOMMU;31 batch01;27 batch02;33 batch03;25 batch04; declared nonbehavioral metadata differences |",
         f"| A — VERIFIED_BYTE_EXACT | {c['A']} | 60 system_dlkm ELF bodies;40 accelerator;6 boot-clock;10 storage;4 pinctrl;4 regulator;3 interconnect/EMI;1 IOMMU;31 batch01;27 batch02;33 batch03;25 batch04;20 audio;17 SCP/connectivity;20 audio-dependencies;22 diagnostics/MET;10 all-C closure (4 CMDQ,4 OEM-BTF-base,2 DRM); declared nonbehavioral metadata differences |")
    once("| C — REPRODUCIBLE_SOURCE_UNVERIFIED | 14 | FT3680,YFT devinfo,ST21NFC,tkcore;four CMDQ;native ADC BTF;five independently built Batch04 source-token/counter/TCPC residuals; full acceptance incomplete |",
         f"| C — REPRODUCIBLE_SOURCE_UNVERIFIED | {c['C']} | FT3680,YFT devinfo,ST21NFC,tkcore;AW883XX scene-parser codegen;five USB/Type-C source-token/counter residuals; full acceptance incomplete |")
    once("| D — SOURCE_CANDIDATE_ONLY | 91 |", f"| D — SOURCE_CANDIDATE_ONLY | {c['D']} |")
    once("| G — UNRESOLVED | 108 |", f"| G — UNRESOLVED | {c['G']} |")
    once("**245 A/B identities are certified.213 identities are not certified or legitimately\nexcluded.** Of those,**105** are candidate/incomplete-acceptance cases (91D+14C),\nand **108 remain unresolved for independent reproducibility**. Do not describe this as\n213 new reverse-engineering projects:the108 G cases",
         f"**{cert} A/B identities are certified.{unc} identities are not certified or legitimately\nexcluded.** Of those,**{c['D'] + c['C']}** are candidate/incomplete-acceptance cases ({c['D']}D+{c['C']}C),\nand **{c['G']} remain unresolved for independent reproducibility**. Do not describe this as\n{unc} new reverse-engineering projects:the{c['G']} G cases")
    once("There are **74 uncertified identities required by", f"There are **{first} uncertified identities required by")
    once("**271 identities, production/runtime necessity remains unknown**", f"**{unknown} identities, production/runtime necessity remains unknown**")
    once("Source is located in some form for all213 remaining identities:91 public candidates and\n122 reconstructed/built cases (108G+14C). **Fourteen have class C's specific",
         f"Source is located in some form for all{unc} remaining identities:{c['D']} public candidates and\n{c['G'] + c['C']} reconstructed/built cases ({c['G']}G+{c['C']}C). **Ten have class C's specific")
    S.write_text(t)
Q = A / 'RECONSTRUCTION-QUEUE.md'; q = Q.read_text()
old = 'Completed integration: AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01 and AUDIO-DEPENDENCIES-BATCH-02.'
new = ('Completed integration (CANONICAL-INTEGRATION-01): AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01, '
       'AUDIO-DEPENDENCIES-BATCH-02, NEXT-DG-BATCH-01, ALL-C-TO-A-CLOSURE and the USB-TYPEC-CLOSURE C-evidence update.')
if old in q:
    assert q.count(old) == 1; Q.write_text(q.replace(old, new))
p = subprocess.run([sys.executable, str(A / 'scripts/validate.py')], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
assert p.returncode == 0, p.stdout[-2000:]
print(f'SUMMARY/queue refreshed: A{c["A"]} B{c["B"]} C{c["C"]} D{c["D"]} G{c["G"]}; {cert} certified/{unc}; first-stage uncertified {first}; validator PASS')
