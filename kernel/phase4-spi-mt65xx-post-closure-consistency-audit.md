# Post-`spi-mt65xx` documentation consistency audit

## Scope and result

Documentation/status synchronization only after the `spi-mt65xx`
`DIRECT_SOURCE_MATCH` closure and post-SPI MicroArray acceptance rebuild. No
reverse engineering, reconstruction source, build metadata, symvers, phone,
module, flash, boot, slot, or runtime operation was performed.

**Result: PASS — `CURRENT_STALE = 0`.**

## 1. Files audited

The entire repository was searched. The following maintained status documents
were then reviewed directly:

- `kernel/phase4-remaining-module-triage.md`
- `kernel/phase4-remaining-module-triage.tsv`
- `kernel/phase4-buildability-plan.md`
- `kernel/phase4-slot-b-minimum-source-stack.md`
- `kernel/phase4-remaining-module-dependency-graph.md`
- `kernel/module-replacement-plan.md`
- `kernel/zero-blob-queue.md`
- `kernel/phase4-microarray-fp-tee-reconstruction.md`
- `kernel/phase4-microarray-fp-tee-abi-provenance.md`
- `kernel/phase4-microarray-fp-tee-source-candidates.md`
- `kernel/phase4-spi-mt65xx-reconstruction.md`
- `kernel/phase4-spi-mt65xx-RED.md`
- `kernel/phase4-fingerprint-reconstruction.md`
- `kernel/phase4-ffa-v10-post-closure-consistency-audit.md`
- `kernel/unknown-exact-audit.md`

README/status/queue/roadmap/graph/plan/summary filenames repo-wide were also
searched. Kernel stock-oracle reports, verifier records, scripts, source/build
snapshots, and raw ABI inventories were inspected as search matches but were
not rewritten as current-status prose.

## 2. Files changed

- `kernel/phase4-remaining-module-dependency-graph.md`
- `kernel/phase4-slot-b-minimum-source-stack.md`
- `kernel/phase4-remaining-module-triage.md`
- `kernel/phase4-remaining-module-triage.tsv`
- `kernel/module-replacement-plan.md`
- `kernel/phase4-buildability-plan.md`
- `kernel/phase4-fingerprint-reconstruction.md`
- `kernel/phase4-microarray-fp-tee-source-candidates.md`
- `kernel/phase4-ffa-v10-post-closure-consistency-audit.md`
- `kernel/unknown-exact-audit.md`
- this audit

`zero-blob-queue.md`, both authoritative MicroArray reports, the authoritative
SPI report, and mandatory RED were already correct and remain unchanged.

## 3. Stale current-state claims found and corrected

| file | stale current claim | correction |
|---|---|---|
| dependency graph | TEE graph labeled MicroArray `[stock]` | labeled `RECONSTRUCTED / FROZEN`; retained only the stock-runtime tkcore edge |
| dependency graph | Tier 13 held both tkcore and MicroArray on stock | Tier 13 runtime stock dependency is tkcore only; optional staged stock deployment is explicitly separate |
| dependency graph | old fingerprint milestone called MicroArray stock-held and SPI unchanged | milestone labeled historical; current MicroArray/SPI closure appended |
| Slot-B plan | acceptance used source fingerprint with stock MicroArray/TrustKernel | source-built fingerprint + MicroArray + SPI, with stock runtime tkcore |
| Slot-B plan | source-complete summary counted “two TEE modules” | MicroArray counted source-closed; tkcore alone is the fingerprint path's unresolved runtime TEE provider |
| Slot-B plan | final summary called MicroArray stock-held | MicroArray closed/frozen; tkcore is its remaining stock runtime dependency |
| triage narrative | first-boot compatibility implied stock fingerprint/SPI/MicroArray was required | stock use labeled optional conservative deployment; source status stated separately |
| triage §16 | current recommended keep-stock list included MicroArray and TinyLCD and called TinyLCD unclosed | both labeled source-reconstructed/frozen; only optional staged stock retention remains |
| triage §18 | transition hold grouped MicroArray, tkcore_drv, and TinyLCD with tkcore | tkcore is the required runtime stock item; the other three are optional staged-stock binaries despite source closure |
| triage TSV | tkcore row used old transition-blob classification | exact current `NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL / NOT RECONSTRUCTED / STOCK RUNTIME PROVIDER` state and 14/25 split |
| triage TSV | tkcore_drv row said retain stock and keep ffa_v10 stock | current source reconstruction, 8/5 split, 43/43, real source-built ffa_v10 |
| triage TSV | fingerprint next step referred to stock/unclosed MicroArray | provider-before-consumer order retained; later MicroArray closure recorded |
| triage TSV | TinyLCD row remained a transition blob | current source-reconstructed/frozen 30/30 state; stock YFT ABI boundary retained |
| replacement plan | old 63/66 targets were not sufficiently separated from current acceptance | targets explicitly labeled historical/pre-SPI; current 65/1 acceptance stated |
| replacement plan | fingerprint milestone said MicroArray remained incomplete | milestone labeled historical; current MicroArray and SPI closures added |
| fingerprint report | “MicroArray remains untouched” read as current | scoped explicitly to the historical provider-only milestone; later closure noted without changing behavior |
| MicroArray candidates | stock SPI witness phrasing was unqualified | heading labeled historical pre-SPI and superseding 65/1 provenance added |
| old ffa consistency audit | body mentions SPI closure as still open | historical-snapshot banner points to this superseding audit |
| unknown-source audit | current-resolution note retained old tkcore/tkcore_drv/MicroArray verdicts | synchronized exact current classifications and removed MicroArray from unresolved list |
| buildability plan | original disposition counts appeared current | counts labeled a superseded historical triage snapshot |

## 4. Historical statements intentionally retained

- The four `63/66`, `63 NATURAL`, and `3/66` matches remain because every one
  is explicitly labeled historical, pre-SPI, or an historical evidence target.
- The original stock-provider witness source/build snapshots remain unchanged.
- Stock ELF, stock-consumer, stock-oracle, and stock ABI inventory references
  remain factual evidence, not source-status claims.
- The mandatory SPI RED report remains unchanged.
- The old post-ffa audit body remains an historical record under a new explicit
  supersession banner.
- Chronological buildability/triage baseline counts remain where explicitly
  labeled historical.

## 5. Source status versus deployment policy

Current source status:

- `fingerprint`: `SOURCE_RECONSTRUCTED / FROZEN FOR RE`
- `spi-mt65xx`: `DIRECT_SOURCE_MATCH / SOURCE_NOW / FROZEN FOR RE`
- `microarray_fp_tee`: `SOURCE_RECONSTRUCTED / FROZEN FOR RE`
- `tkcore`: `NOT RECONSTRUCTED / STOCK RUNTIME PROVIDER`

A conservative first Slot-B boot may still deploy stock binaries for any of the
first three. Such wording is now labeled **optional conservative integration
strategy** or **staged stock deployment**. It is never used as reconstruction
status. The full fingerprint runtime stack is not source-pure because tkcore
remains stock.

## 6. Final fingerprint stack graph

```text
fingerprint [SOURCE_RECONSTRUCTED / FROZEN]
    | 4 natural provider edges
    v
microarray_fp_tee [SOURCE_RECONSTRUCTED / FROZEN]
    ^                                      ^
    | 2 NATURAL_SPI_PROVIDER edges         | tee_spi_transfer
    |                                      | STOCK_PROVIDER_WITNESS
spi-mt65xx [DIRECT_SOURCE_MATCH / FROZEN]   tkcore [STOCK RUNTIME / NOT RECONSTRUCTED]
```

## 7. Final MicroArray ABI provenance

- 66/66 stock MODVERSION edges exact.
- 65/66 natural: 59 exact-GKI + 4 source-built fingerprint + 2 source-built
  SPI provider edges.
- `mt_spi_enable_master_clk` (`0x1cc49782`) and
  `mt_spi_disable_master_clk` (`0xccc1e350`) are
  `NATURAL_SPI_PROVIDER`.
- The only remaining stock-runtime witness is `tee_spi_transfer`
  (`0x184ce7da`) from tkcore.
- `depends=fingerprint,spi-mt65xx,tkcore` and the 27/27 defined function set
  remain exact. Behavior was not reopened.

## 8. Final tkcore and adjacent provider status

- `tkcore`: `NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL / NOT
  RECONSTRUCTED / STOCK RUNTIME PROVIDER`; 122 functions, 25 exports, 101
  MODVERSIONs, 14/25 export CRCs natural, 11/25 blocked. Natural reproduction
  of the `tee_spi_transfer` type/CRC is ABI evidence only.
- `tkcore_drv`: `SOURCE_RECONSTRUCTED /
  SOURCE_NOW_WITH_PROVIDER_WITNESSES / PROVIDER_ABI_PARTIAL / FROZEN FOR RE`;
  8 natural, 5 stock-provider witnesses, 43/43 verifier.
- `ffa_v10`: `DIRECT_SOURCE_MATCH / FROZEN FOR RE`; 34/34 function bytes,
  5/5 natural exports, 49/49 verifier.

## 9. Remaining required-grep matches and classifications

All required searches were executed after the prose/status corrections. Each
individual result was classified by path and line. Counts below are the
post-correction, pre-audit-file results; any self-match introduced by this
file is a quoted classification record or command term, never current status.

| search group | matches | classification |
|---|---:|---|
| historical `63/66` / `63 NATURAL` / `3/66` forms | 4 | `HISTORICAL_VALID` — all explicitly labeled |
| MicroArray + transition status | 0 | no remaining match |
| MicroArray + held-on-stock status | 0 | no remaining match |
| SPI + witness wording | 1 | `CURRENT_VALID` false-positive: line says source-built SPI plus the one tkcore witness |
| each SPI clock export + old witness label | 1 each | `HISTORICAL_VALID` before→after provenance rows |
| “two TEE modules” | 1 | `HISTORICAL_VALID`/command literal in superseded ffa audit |
| MicroArray + stock wording | 121 | `RAW_EVIDENCE_DO_NOT_EDIT`, `HISTORICAL_VALID`, `CURRENT_VALID`, or `FALSE_POSITIVE`; zero stale |
| SPI + stock wording | 104 | same four valid classes; stock oracle/ELF/path comparisons dominate; zero stale |
| fingerprint + stock MicroArray wording | 5 | stock-behavior classification, stock-oracle evidence, or historical audit quotation; zero stale |
| tkcore_drv + stock wording | 109 | raw ABI data/build target names, current stock-tkcore dependency, optional deployment, or historical audit; zero stale |
| TinyLCD + stock wording | 72 | raw ABI/oracle data, current stock-YFT provider boundary, or optional staged deployment; zero stale |

Path-level classification rules applied to every match:

- `kernel/kmi-symbol-map.csv`, `stock-intermodule-abi.csv`,
  `stock-kmi-requirements.csv`, frozen oracle/verifier JSON/TXT, scripts,
  witness C, and saved BUILD/Makefile snapshots:
  `RAW_EVIDENCE_DO_NOT_EDIT`.
- Stock-oracle comparisons such as “stock exact”, stock file paths,
  `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`, and `stock-ABI` target names:
  `FALSE_POSITIVE` where they do not claim deployment/source status.
- Explicit `before`, `historical`, `pre-spi`, original-milestone, and
  superseded-audit text: `HISTORICAL_VALID`.
- Current references to stock runtime tkcore, stock YFT provider ABI, or
  optional conservative stock deployment: `CURRENT_VALID`.

No match remains in `CURRENT_STALE`.

## 10. Consistency invariants

| # | invariant | result |
|---:|---|---|
| 1 | SPI is `DIRECT_SOURCE_MATCH` | PASS |
| 2 | SPI is frozen | PASS |
| 3 | SPI function bytes 31/31 | PASS |
| 4 | SPI natural exports 3/3 | PASS |
| 5 | SPI verifier 82/82 | PASS |
| 6 | MicroArray source-reconstructed | PASS |
| 7 | MicroArray frozen | PASS |
| 8 | MicroArray behavior not reopened | PASS |
| 9 | MicroArray acceptance 66/66 exact | PASS |
| 10 | MicroArray provenance 65/66 natural | PASS |
| 11 | SPI enable edge natural | PASS |
| 12 | SPI disable edge natural | PASS |
| 13 | only MicroArray stock witness is `tee_spi_transfer` | PASS |
| 14 | tkcore not reconstructed | PASS |
| 15 | tkcore remains stock runtime | PASS |
| 16 | natural tkcore ABI evidence is not runtime source purity | PASS |
| 17 | fingerprint source-reconstructed/frozen | PASS |
| 18 | tkcore_drv remains 8 natural / 5 witnesses | PASS |
| 19 | ffa_v10 remains direct-source/frozen | PASS |
| 20 | full fingerprint stack not called source-pure | PASS |
| 21 | source status separated from first-boot stock policy | PASS |
| 22 | no current list calls MicroArray unresolved | PASS |
| 23 | no current list calls SPI unresolved | PASS |
| 24 | no current list calls TinyLCD unresolved | PASS |
| 25 | tkcore alone is unresolved runtime TEE provider in fingerprint path | PASS |

## 11. Final verdict

`CURRENT_STALE = 0`

**POST-SPI DOCUMENTATION CONSISTENCY: PASS**
