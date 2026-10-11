# Remaining blockers — all five strict C, no scope expansion

## Authentic source-token inputs

| Target | Measured ordered hash input | Missing evidence |
|---|---|---|
| charger_class | C plus same-directory `charger_class.h` | Original OEM C/header tokens, including disabled code/declarations |
| mtk_chg_type_det | C, `mtk_charger.h`, `charger_class.h`, `adapter_class.h`, `mtk_charger_algorithm_class.h`, `mtk_smartcharging.h` | Original coherent OEM six-file revision and dependency order |
| rt_pd_manager | C only | Original OEM C tokens; TCPC `inc/` bytes do not directly enter this digest |
| tcpc_mt6375 | C only | Original OEM C tokens plus real included-header counter consumption |
| tcpc_class |34 composite objects;40 C/header reads including six repeated `pd_dpm_prv.h` reads | Original complete raw OEM token stream and compiler/source-line lineage |

The pinned sumversion wrapper regenerates every final `.mod.c` value exactly. The mismatch is not caused by using the wrong digest algorithm (actual MD4), hashing preprocessed/unique files, overlooked `inc/` bytes, source filename paths, bytecode patching or compiler ABI differences. Actual differing OEM tokens cannot be recovered honestly from a truncated fingerprint alone. Existing authentic cached candidates/history scans did not reproduce the required values; their negative results are retained.

## MT6375 prefix

Stock init/cleanup/author/description/license/version counters are454–459. Corrected normal source expansion produces455–460. The license/version order is genuinely resolved; the extra prefix increment cannot be assigned to a specific OEM include/declaration without the original translation-unit inputs. Do not remove an arbitrary unused declaration, add fillers, redefine a counter or rename materialized symbols to force454.

## TCPC class diagnostics

All709 instruction bodies/positions, all54 runtime timer values and113 non-srcversion data objects/positions match. Remaining exact differences are generated srcversion; six FORTIFY source-line strings;37 BUG source-line records;1,778 string-pool relocation/addend records and18 mapping-symbol positions. All1,778 relocation residues are classified by target resolution, but raw operands remain different. Do not rewrite diagnostic strings, BUG entries, symbol tables or source fingerprints, and do not call a metadata-only equivalence waiver A/B.

## Canonical integration gate

The current live validator rejects60 unrelated missing/60 unexpected stock identities plus frozen inventory/ownership drift. The five scoped identities are unchanged. Do not integrate the delta or adjust unrelated stock SHA rows to make the validator pass. Resolve concurrent/frozen-stock input drift separately; then rerun the unchanged live validator and mutation tests. Frozen-inventory fixture mutation PASS is not live acceptance.

## Required next evidence

Obtain an authentic original GQ5012BF1 vendor C/header release, original Kbuild `.mod`/`.cmd`/dependency/include trace, or a preserved coherent OEM source snapshot with provenance. Rebuild naturally using the existing pinned engines, trace raw source order and counter expansion, and run unchanged complete acceptance plus fresh independent builds. No further large batch or hardware probing is required to state these limits.
