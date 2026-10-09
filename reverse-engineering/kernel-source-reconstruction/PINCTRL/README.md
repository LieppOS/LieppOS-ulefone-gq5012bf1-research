# PINCTRL — four GQ5012BF1 modules

**Four D → A: maintained pinned source, clean-checkout B1 == B2 and complete stock ELF
acceptance except GNU build ID.** Static/offline only; no phone interaction or runtime claim.

* [Result](RECONSTRUCTION-REPORT.md), [source](SOURCE.md), [lineage](SOURCE-LINEAGE.md),
  [reproduction](BUILD-REPRODUCTION.md).
* [Module parity](MODULE-PARITY.tsv), [117 functions](FUNCTION-PARITY.tsv),
  [312 data objects](DATA-PARITY.tsv), [ABI](ABI-PARITY.md).
* [Pinmux/board mapping](PINMUX-MAPPING.md), [GPIO/EINT](GPIO-EINT-CONTRACT.md),
  [DT contract](DEVICE-TREE-CONTRACT.md), [boot/deferred tests](EARLY-BOOT-DEPENDENCIES.md),
  [corrections](STALE-CLAIMS.md).
* `evidence/`: original four audit rows/identities/dependencies; source blob comparison;
  independent B1/B2 logs/hashes; all acceptance ledgers; generated full hardware indexes;
  hash manifest.
* `scripts/map-contract.py`: reproducible source + static/live DT mapping generator.
* `source/`: committed maintained recipe bundle, source pins, full scope patch and commit ID.

Scope is exactly pinctrl-mt6363, pinctrl-mt6878, pinctrl-mtk-common-v2_debug and pinctrl-mtk-v2.
Three retain COVERED-GENERIC ownership; debug retains MICROSD-KERNEL. This is an audit
reconstruction group, **not a new registered component**. No status-tree promotion,
completed clock/storage changes, unrelated identity reclassification or push occurred.
