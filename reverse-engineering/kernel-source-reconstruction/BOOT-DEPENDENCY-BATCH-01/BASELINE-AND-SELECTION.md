# Baseline and frozen selection

Canonical start: master `21ec8901524f65075a1e09a017b96de55c2566e6` (clean). Audit: A333 B1 C10 D60 E0 F0 G54.

Selection rule (exact, from `kernel-source-parity-audit/ALL-457-MODULES.tsv`):
`source_status == D` and `priority == P0_BOOT`. Exactly 16 rows match; no padding or substitution.

Meaning of `P0_BOOT` (from `scripts/generate.py` lines 91-100): a non-A/B, non-optional row whose
`reverse-engineering/boot/module-loading/module-classification.tsv` `resolved_phase` is `first-stage`,
i.e. the module ships in vendor_boot and is in the first-stage `modules.load` (or is pulled in as a
dependency of one: kfifo_buf ← industrialio-triggered-buffer), and the saved capture recorded it
loaded. `necessity = REQUIRED_BY_RETAINED_FIRST_STAGE_LOAD_CONTRACT` describes the stock load
contract, **not** proof that the platform cannot boot without the module. arm_dsu_pmu and
mtk-swpm-perf-arm-pmu are absent from the recovery load list. Per-module necessity is analysed in
BOOT-DEPENDENCY-ANALYSIS.md.

Every stock file's SHA256/size was re-hashed read-only from the canonical analysis tree and matches
its audit row. Manifest SHA256 is recorded in `BATCH-MANIFEST.sha256`.
No existing maintained repository or research package owns any of the 16 (repository-wide grep;
earlier packages only queued timer-mediatek / 8250_mtk / i2c-mt65xx as future candidates).
