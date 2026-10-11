# USB/Type-C Batch04 closure investigation — partial source improvement

**All five targets processed. Newly certified: 0. All five remain Category C.**

The task did not manufacture fingerprints/counters or relax acceptance to claim closure. It resolved all eight TCPC class instruction mismatches and the complete runtime timer table, isolated the remaining exact metadata differences, and established genuinely independent deterministic source builds. Authentic original OEM token/include/diagnostic lineage is still unavailable offline.

## Five-module matrix

| Module | Original → final | Source correction | Exact instructions | Exact data objects | Remaining blocker |
|---|---|---|---:|---:|---|
| charger_class | C → C | No behavior/source token change; actual MD4/dependencies traced | 90/90 | 20/21 | Original OEM raw source/header token stream; generated srcversion |
| mtk_chg_type_det | C → C | No behavior/source token change; actual six-file MD4 stream traced | 8/8 | 20/21 | Original OEM raw source/header token stream; generated srcversion |
| rt_pd_manager | C → C | No C change; only its C file enters actual fingerprint | 11/11 | 19/20 | Original OEM C tokens; generated srcversion |
| tcpc_mt6375 | C → C | Real ALPS/stock license-before-version declaration order | 66/66 | 21/28 | Natural srcversion and unexplained +1 source/header counter prefix; raw symbol/string metadata |
| tcpc_class | C → C | Eight complete stock instruction reconstructions; all54 timer values recovered | **709/709** | **113/114** | Natural srcversion, six source-line diagnostic strings,37 BUG line records and consequent string-pool/mapping metadata |

Data counts deliberately include generated metadata objects; they are not percentages used to waive complete acceptance. All five retain matching imported/exported CRCs, export license buckets and KCFI. Both BTF sections are absent in these operands. TCPC class's final code/data positions and section layout match; metadata relocations still fail exact raw/semantic comparison. Diagnostic target resolution accounts for all 1,778 relocation residues without modifying an operand.

## Evidence and reproducibility

- [SRCVERSION-INVESTIGATION](SRCVERSION-INVESTIGATION.md): exact pinned **MD4**, real `.mod`/`.cmd` input order, actual same-directory header rule, authentic local source/history scans, all five natural results. No MD5 substitution, guessed-token/preimage search or generated fingerprint assignment.
- [TCPC-METADATA-INVESTIGATION](TCPC-METADATA-INVESTIGATION.md): actual macro/counter origin, public declaration-order precedent and explicitly unresolved stock prefix.
- [TCPC-CLASS-FUNCTION-DIFFS](TCPC-CLASS-FUNCTION-DIFFS.md): all eight original sizes/addresses, complete disassemblies/relocations, source correction and stage-by-stage result; real timer data was not dismissed as metadata.
- [SOURCE-LINEAGE](SOURCE-LINEAGE.md): authentic bases, old/new commits, retained historical/failed experiments, identical shared source patch and recoverable verified bundles.
- [BUILD-REPRODUCTION](BUILD-REPRODUCTION.md): **four fresh source-clone builds**, all30 raw/stripped outputs and157 objects byte-identical,437 exact ABI producer records,25 prior stock acceptances preserved/five strict rejections retained, **23 mutation tests PASS**. Initial DWARF failure and path-bearing manifest-checker failure are retained and explained.

Maintained source commits:

- Type-C **`758f9edc78c7a50d07b8629126438a3674845911`**.
- Charging/shared engine **`b2a343a9d8664b77a63dc16835b5af0fd0e55cf1`**.

These are isolated `codex/usb-typec-closure` branches, not changes to canonical checkouts. Exact source changes restore measured selected-stock behavior, not an assertion that distinct public PD/safety algorithms are equivalent. No runtime/board safety claim or hardware operation is inferred from compile agreement.

## Audit and integration

Canonical base remains `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263`. No canonical audit/queue/ownership/runtime state was edited. [AUDIT-DELTA.tsv](AUDIT-DELTA.tsv) contains **22 compare-and-swap field changes** for these five identities only; source classes stay C. It updates preserved evidence/source references and TCPC class's honest instruction count (701→709, eight instruction mismatches→zero), **not whole-module acceptance**.

Counts before and after any proposed delta: **245 certified / 213 remaining / 458 identities**; zero new certifications; all453 unselected rows preserved. Actual canonical head/counts/drift are recorded in `evidence/audit-delta.json`. Integrate only after concurrent work has finished, source changes/evidence are reconciled, field preconditions still match, and validators pass. The delta has not been applied.

### Live canonical validation is blocked

A separate read-only canonical validator run **FAILs** on60 unrelated missing stock SHA identities,60 unexpected identities and frozen-inventory/ownership-set drift. Live audit mutation baseline likewise rejects that drift. All five selected stock SHAs still match the frozen inputs, and the canonical audit TSV is byte-unchanged. The existing14 audit mutation tests PASS against the explicitly labeled frozen-inventory fixture; **this is not a live canonical PASS**. Failure logs are retained under `evidence/audit-validation/`. Reconcile concurrent/frozen-stock drift before any integration; no unrelated stock identity or audit was repaired by this task.

## Safety and residual task

No phone access, adb/fastboot, module loading, PD negotiation, role/mux switching, charger reset/disable, protection-threshold modification, register/I2C poking, firmware change, hardware test or Git push. No selected compiled body/stock data was transplanted into build inputs.

[REMAINING-BLOCKERS](REMAINING-BLOCKERS.md) and [NEXT-TASK](NEXT-TASK.md) identify the precise missing OEM inputs. Without them, a complete A/B claim would be unjustified; deterministic compilation and 709 exact bodies alone are not closure.
