# LOW-POWER-BATCH-01 — summary

**Result: all 12 frozen LPM / SWPM / SSC / mbraink Category D targets were reconstructed from unmodified pinned
MediaTek ALPS source and independently certified as Category A.** Each passed B1/B2 whole-stock ELF acceptance
under the unchanged strict verifier, with only the GNU20 build ID differing. No OEM patch, placeholder, waiver
or BTF base was needed. Canonical is not edited; the identity-keyed CAS delta validates in both integration orders:

- **with the staged BOOT-DEPENDENCY-BATCH-01:** A361 / B1 / C10 / D32 / E0 / F0 / G54 = **362 certified, 96
  uncertified**;
- **alone on canonical:** A345 / B1 / C10 / D48 / G54.

In both cases the validator passes with 0 errors and the 14 audit mutation tests pass.

- **Start:** canonical `21ec8901` (A333 B1 C10 D60 G54). Staged overlay `codex/boot-dependency-batch-01` @ `a4de67d5`
  (16 D→A, not merged; its rows are not re-counted).
- **Manifest:** `BATCH-MANIFEST.tsv`, SHA256 `aebcb768591206d1e671c49f9add0d693c62960c4e1a5f8f51c8732b12528fb5`,
  committed at `cab171fd` before any source work.
- **Source:** `android_kernel_modules_low_power_ulefone_gq5012bf1` @ `185621496e49…`, bundle
  `bundles/low-power.bundle` (verified; cloned fresh twice).

| Module | Family | Functions | Data | Imports/Exports | KCFI IDs | Relocs | Residual |
|---|---|---|---|---|---|---|---|
| mtk-lpm | LPM | 89/89 | 62/62 | 81/48 | 3 | 1152 | none |
| mtk-lpm-plat-v1 | LPM | 29/29 | 25/25 | 43/0 | 0 | 324 | none |
| lpm-gov-MHSP | LPM | 19/19 | 26/26 | 53/0 | 2 | 363 | none |
| mtk-lpm-dbg-common-v2 | LPM | 154/154 | 135/135 | 111/50 | 0 | 2818 | none |
| mtk-lpm-dbg-mt6878 | LPM | 27/27 | 35/35 | 34/0 | 0 | 1141 | none |
| mtk-swpm | SWPM | 47/47 | 29/29 | 33/34 | 1 | 434 | none |
| mtk-swpm-dbg-common-v1 | SWPM | 8/8 | 15/15 | 21/4 | 0 | 157 | none |
| mtk-swpm-dbg-v6878 | SWPM | 47/47 | 78/78 | 63/0 | 2 | 867 | none |
| mtk-swpm-cpu-dbg-v6878 | SWPM | 9/9 | 16/16 | 12/0 | 0 | 70 | none |
| mtk-ssc | SSC | 11/11 | 25/25 | 26/6 | 0 | 258 | none |
| mtk-ssc-dbg-v2 | SSC | 6/6 | 15/15 | 12/0 | 0 | 110 | none |
| mtk_mbraink | MBRAINK | 80/80 | 74/74 | 135/1 | 0 | 3588 | none |

Byte-identical against stock in every module: all CRCs, licences, namespaces, KCFI type IDs, raw and semantic
relocations, section headers, symbol and string tables, and `.modinfo` (vermagic, srcversion, depends). Nothing
was forced, transplanted or patched.

## Dependencies

- **Edge census:** 624 import edges, CRC-consistent 624/624. 496 resolve to GKI, 87 are intra-batch, and 41 go to
  14 external providers.
- **Witnesses:** all 39 external slots were compiled naturally from provider source with exact CRC, licence, KCFI
  and namespace.
- **Provider classes:** 12 of the 14 providers are canonical Category A. `mtk-swpm-perf-arm-pmu` (10 slots) is A only
  in the staged boot overlay, and its source in this repository is the same ALPS `swpm` directory. `mtk_fpsgo`
  (4 slots, used by mbraink) stays **Category D**, because a witness is not certification.
- **Exporter derivation:** the symvers exporter column now comes from Kbuild's own `.mod` composite membership.
- **Load order:** every provider loads before its consumer.

## Findings

- **SSC is configured off by the stock DT (static inference).** The stock DT has no `mediatek,ssc` node, so by source
  `ssc_init()` returns `[SSC] disabled` before any vcore/GPU vlogic voting.
- **Stock DT parameters.** The stock DT fixes the LPM contract (suspend method, logger states, 16 irq-remain
  entries, 8 resource-ctrl entries, PSCI idle states) and the SWPM DSU-PMU features
  (`pmu-dsu-support=1`, `pmu-dsu-type=0xa`).
- **Firmware boundaries.** LPM goes through `MTK_SIP_MTK_LPM_CONTROL` SMCs to SPM/ATF, SWPM through SSPM reserved
  memory, sbuf and SCMI, and SSC through tinysys SCMI. mbraink exposes genetlink `MBRAINK_LINK` and ioctls. The
  firmware and userspace sides are not reconstructed and not claimed. Details are in HARDWARE-CONTRACT.md.

## Reproducibility and safety

- **Builds:** B1 and B2 used fresh bundle clones and fresh offline workspaces with the development directory
  quarantined, at 4 CPUs and nice 10.
- **Identity:** the 24 `.ko` and stripped outputs, 221 intermediates, configs, natural symvers and source trees
  are identical across builds and equal to development D1/D3.
- **Mutations:** 162 + 162 ELF mutation controls behave correctly.
- **Canonical:** master is untouched (`21ec8901`, clean). All 471 stock `.ko` are unchanged, and the live
  inventory passes (458/471, 60/60 signed); the validator and its 14 tests pass.
- **Isolation:** no existing repository or worktree was modified. Only this task's two scratch worktrees were
  removed, after their evidence was copied here. No build workspace was deleted.
- **Offline:** no ADB, phone, flash or push.

Reports: HARDWARE-CONTRACT.md, SOURCE-LINEAGE.md, LOW-POWER-DEPENDENCY-GRAPH.tsv, ABI-PROVIDERS.tsv, BATCH-PARITY.tsv,
EXPERIMENTS.tsv, BLOCKERS.tsv, BUILD-REPRODUCTION.md, SOURCE-REPOSITORIES.tsv, AUDIT-DELTA.tsv,
PROPOSED-AUDIT-{COMBINED,STANDALONE}.patch, MERGE-INSTRUCTIONS.md, NEXT-BATCH.md, BATCH-STATE.json.
