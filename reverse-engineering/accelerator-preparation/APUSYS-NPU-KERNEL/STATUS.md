# APUSYS-NPU-KERNEL status — 2026-10-08

**DONE — scoped normal-world kernel reconstruction.**

| Target | Source | Fresh B1/B2 | Static stock parity | Unresolved |
|---|---|---|---|---:|
| `apu_top.ko` | public ALPS `5e415e059253` | byte-deterministic | all bytes except 20-byte build ID | 0 |
| `apusys.ko` | public ALPS `5e415e059253` + explicit stock MDLA object order | byte-deterministic | all bytes except 20-byte build ID | 0 |

Maintained local source: `android_kernel_modules_apusys_ulefone_gq5012bf1` commit `924f66b779a64ae0b05f89e233ff2317866050ba`; no remote and no push. A complete Git bundle and plain pin/patch/reference copies are under `source/`.

Acceptance covers 2,308 defined function occurrences, 1,643 data objects, 555 imports, 32 exports, 171 KCFI absolute IDs and 56,399 relocations. All are exact. Thirteen external provider CRCs are naturally regenerated from public source on every build. Clean checkout B1/B2 includes all target object intermediates and symvers.

Runtime inference remains **UNTESTED**, not a static reconstruction blocker. Required future tests are enumerated in `source-to-userspace-contract.md`. Proprietary signed firmware/algorithms remain explicitly excluded.
