# BOOT-CLOCK-CORE — six MT6878 first-stage clock modules

Source-reconstruction package (not a workspace component; see `RECONSTRUCTION-REPORT.md` →
registration decision). **Static result: 6/6 byte-exact except GNU build ID.**

| file | content |
|---|---|
| [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) | result table, method, classification |
| [SOURCE.md](SOURCE.md) | maintained repo, pins, patches, build commands |
| [source-lineage.md](source-lineage.md) | per-module source files and public history examined |
| [build-reproduction.md](build-reproduction.md) | inputs, clean-checkout B1/B2 run, build-ID offsets |
| [module-parity.tsv](module-parity.tsv) | per-module hashes and every parity axis |
| [function-parity.tsv](function-parity.tsv) / [data-parity.tsv](data-parity.tsv) | 256 functions / 324 data objects |
| [abi-parity.md](abi-parity.md) | imports/exports/CRC/KCFI/modinfo and provider verification |
| [clock-tree.md](clock-tree.md) | per-module clock inventory, display-PWM path |
| [dt-provider-contract.md](dt-provider-contract.md) | 14 DT providers, 67 consumers / 387 refs |
| [boot-dependencies.md](boot-dependencies.md) | first-stage order, dependencies, Slot B conditions |
| [runtime-validation.md](runtime-validation.md) | what remains to test on hardware |
| [stale-claims.md](stale-claims.md) | corrected earlier statements |
| `evidence/` | acceptance ledgers, B1/B2 hashes, clean-checkout log, DT consumer ledger, `SHA256SUMS` |
| `source/` | git bundle of the maintained repo, pins, patches |

Registration: this is the parity-audit source group `BOOT-CLOCK-CORE`, not a registered
DONE/PARTIAL component. Canonical ownership of the six modules is unchanged
(`COVERED-GENERIC` in `coverage-audit/kernel-modules.tsv`); only their source class in
`kernel-source-parity-audit/` moved D → A.
