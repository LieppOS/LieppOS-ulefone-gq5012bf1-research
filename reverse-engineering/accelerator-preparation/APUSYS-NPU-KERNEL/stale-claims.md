# Corrected preparation claims

| # | Earlier claim | Correction/evidence |
|---:|---|---|
| 1 | No target rebuild or parity was available. | Fresh independent B1/B2 now closes both modules on every static axis; see `parity-report.md`. |
| 2 | The 957dac Nothing donor was the leading source candidate. | It is the correct config pin but not stock module source. Public ALPS `5e415e059253` is the exact C/header lineage. |
| 3 | Apparent MDLA function differences implied code reconstruction. | They were a name-keyed comparison artifact plus filesystem-dependent object link order. All 164 objects mapped; explicit stock order yields exact code/data/relocations without behavioral edits. |
| 4 | External CRC provenance remained unknown. | All 13 non-GKI provider CRCs are generated from public source each build and equal stock. |
| 5 | IOCTL/native/compat/buffer contract still had to be recovered. | Exact source plus whole-ELF parity identifies `/dev/apusys`, commands 32–35, fixed layouts and lifetime; documented in `source-to-userspace-contract.md`. |
| 6 | DT enablement, module loading and Android libraries could support a runtime inference claim. | They establish reachability only. Probe, firmware handshake, real NPU execution, recovery, power and performance remain explicit future tests. |
| 7 | Local archive commit `2ae742f...` was needed as donor identity. | It was only a pristine local archival commit. The reproducible source pin is upstream `5e415e059253ce0d2e61c97108e5f5785d71f06f`. |

Original preparation tables are retained where useful; accepted closure documents supersede their `UNKNOWN/PARTIAL` conclusions.
