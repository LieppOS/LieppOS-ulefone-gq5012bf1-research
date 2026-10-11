# Source-version investigation — actual pinned modpost inputs

## Verified implementation

The source is pinned GKI common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`,
`scripts/mod/sumversion.c`, called by `modpost.c:1809` and emitted by
`add_srcversion():2076`. `struct module.srcversion` has 25 bytes; the caller passes
`sizeof(srcversion)-1` (24), so `snprintf` stores **23 uppercase hexadecimal MD4
characters**, not MD5 and not a complete 32-character digest.

The diagnostic C wrapper includes the unmodified upstream implementation. It
regenerates all four metadata-blocked modules' exact existing values directly
from their actual `.mod` and `.o.cmd` files; read traces and input SHA256 are in
`evidence/srcversion/baseline-traces.json`. It never writes generated module
source, metadata, fingerprints or ELF bytes.

`CONFIG_MODULE_SRCVERSION_ALL` is **disabled**. These modules request fingerprints
through their actual `MODULE_VERSION` declarations. The parser traverses the
ordered object list in `.mod`, then `source_` and qualifying `deps_` entries in
`.o.cmd`. Despite a comment mentioning subdirectories, the implemented last-slash
comparison accepts dependencies **in exactly the object's directory**, excluding
TCPC's `inc/` headers and common generated/vendor include directories.

| Module | Exact baseline hashed input order | Stock | Baseline natural result |
|---|---|---|---|
| charger_class | charger_class.c, charger_class.h | E4A92CD3F20A3D2142F16B6 | 66ADA0AAEAEA649866AF7A8 |
| mtk_chg_type_det | mtk_chg_type_det.c, mtk_charger.h, charger_class.h, adapter_class.h, mtk_charger_algorithm_class.h, mtk_smartcharging.h | F7A2E5433A38379D631644F | F2C230777ABCBB6B44AEE0B |
| rt_pd_manager | rt_pd_manager.c only | C4301583FE25F39BA52E75D | 48B276D3F1DDD74E905394C |
| tcpc_mt6375 | tcpc_mt6375.c only | D27BCF95DDC8F09B632224B | EA7DA9D08253B7F0F495FB1 |

## Important disproven explanations

- Whitespace and `/* ... */` comments do **not** explain these fingerprints: the
  parser excludes them. Ordinary `//` comments are **not** excluded.
- Compiler-preprocessed source is **not** the hashed stream. Disabled `#if`
  branches, unused declarations, macro definitions and includes spelled in the
  source still enter the hash. A diagnostic fixture proves identical preprocessed
  translation units can have different natural srcversions.
- TCPC `inc/` header revisions cannot directly fix either single-file fingerprint
  under the measured dependency graph. They can affect code/ABI/counters and must
  still be independently checked, but their bytes are not hashed here.
- Changing the toolchain alone does not recover unknown source text. No compiler
  flag, forced srcversion, modpost alteration or ELF rewrite is a permitted fix.
- Earlier descriptions of MD5, comments/whitespace generally causing the residual,
  or ABI parity alone proving an operational drop-in are not accepted evidence.

Seven parser fixtures pass; see `parser-semantics.json`. Their role is to explain
hashing, not search for a crafted preimage or waive source provenance.

## Authentic source recovery so far

A read-only scan found 604 local instances and **21 distinct coherent source input
sets** across all four metadata modules (3 charger_class, 3 mtk_chg_type_det,
5 rt_pd_manager, 10 tcpc_mt6375). No natural stock match. Inputs are hashed with
full paths and SHA256; content existence alone is not a public/OEM lineage proof.

Separately, **19 distinct immutable Git source sets** were extracted from local
ALPS/Nothing and three actual public MiCode TCPC repositories, including the
maintained historical OEM reconstruction commits. No stock match under the
verified baseline dependency order. Each set records full commit and paths.
Candidate revisions still require their own compiler dependency/behavior checks;
a fingerprint comparison alone does not accept them.

The previous 1,376 guessed-token variants are preserved in legacy research and
are not rerun. This investigation searches existing coherent files/Git objects,
not arbitrary token placement, source garbage or digest preimages.

## Current classification and exact remaining uncertainty

For the first three modules, existing complete instruction/initialized-data,
ABI/KCFI/license, raw/semantic relocation and symbol/layout evidence localizes the
remaining non-GNU difference to generated source-version metadata. The digest
origin and current inputs are now known precisely. **The original OEM raw token
streams are not known**, so the exact differing source tokens cannot honestly be
identified from a truncated digest or code parity alone.

The observed ELF difference is source-provenance metadata, not an instruction
change. That does not establish that every unavailable OEM source line is
nonbehavioral under other configurations, and does not meet strict whole-ELF A.
The existing canonical B rule also requires actual equivalent-function proof;
metadata-only waiver is not that proof. Until natural stock fingerprints are
regenerated from authentic inputs, retain C. No acceptance criterion changed.

## Final measured inputs after source reconstruction

The maintained source corrections leave the first three fingerprints unchanged. MT6375's genuine declaration-order correction changes its natural digest, but does not recover stock. TCPC class now matches all 709 instruction bodies/positions and its 54-entry timer table; its original raw source token stream is still unknown.

| Module | Stock | Final natural result |
|---|---|---|
| charger_class | E4A92CD3F20A3D2142F16B6 | 66ADA0AAEAEA649866AF7A8 |
| mtk_chg_type_det | F7A2E5433A38379D631644F | F2C230777ABCBB6B44AEE0B |
| rt_pd_manager | C4301583FE25F39BA52E75D | 48B276D3F1DDD74E905394C |
| tcpc_mt6375 | D27BCF95DDC8F09B632224B | 86B9C4E19D9B7E5A9933F96 |
| tcpc_class | 2909B7703B5C133511935DD | 4D57E32A74284A7BDBD3C58 |

`tcpc_class.mod` lists **34 actual composite objects**. The exact parser performs **40 source/header reads**: all ordered C files plus six repeated same-directory `pd_dpm_prv.h` reads. Headers in `inc/` remain excluded. This repetition/composition cannot be replaced by hashing a deduplicated file set or preprocessed source. `evidence/metadata/final-inputs/all-five-traces.json` regenerates all five current values from real `.mod`/`.cmd` inputs and checks the unmodified generated `.mod.c` results.

For the first three, the observed difference is source-provenance metadata, not code/ABI/relocation changes. For MT6375, digest and prefix-counter lineage remain unknown against OEM inputs. For TCPC class, code/timer differences are resolved, while raw token provenance, compiler-generated source-line diagnostic strings/BUG entries and consequent string-pool metadata remain incomplete. Exact differing OEM tokens **cannot be named honestly without the original inputs**; compiler agreement does not identify disabled-source/include/declaration spelling. No metadata-only Category B waiver is asserted.

Next: acquire an authentic GQ5012BF1/OEM source release or preserved original
compiler `.cmd` and matching source/header files; compare exact ordered token
streams with the preserved MD4 probe, then rebuild with pinned Clang and complete
whole-ELF acceptance. Final source experiments/build status are recorded separately
in EXPERIMENTS.tsv and MODULE-PARITY.tsv; this is a progress record, not certification.
