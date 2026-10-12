# Baseline and frozen selection

- Canonical master `21ec8901524f65075a1e09a017b96de55c2566e6` (clean): A333 B1 C10 D60 E0 F0 G54.
- Staged overlay (not merged): `codex/boot-dependency-batch-01` @ `a4de67d5`, source
  `android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` @ `8e7a66e1`, 16 D→A proposed (A349 … D44).
  Its 16 identities, including `mtk-swpm-perf-arm-pmu.ko`, are excluded here and never re-counted.
- Selection: the family proposed in BOOT-DEPENDENCY-BATCH-01/NEXT-BATCH.md, confirmed against the canonical
  audit as unowned Category D rows (`CANDIDATE:device_modules:drivers/misc/mediatek/{lpm,swpm,ssc,mbraink}…`):
  LPM 5, SWPM 4, SSC 2, MBRAINK 1 = **12**. `cpuqos_v3.ko` (cache-auditor, imports only mtk_slbc) was named
  in NEXT-BATCH as a neighbour, but it is not in these source families and is left for a later batch.
- All 12 are vendor_dlkm second-stage `insmod_sh:vendor` modules (seq 280–434) listed in modules.load and
  recorded loaded in the saved capture. Stock SHA256/size re-hashed read-only from canonical and equal to the audit.
- Ownership check: no maintained repository or research package claims any of the 12 (see EXPERIMENTS L01).
