# Hynitron source candidates

## Method

Bounded static search covered the required identifiers (`hynitron`, `hyn_ts`,
`hynitron,hyn_ts`, CST816/D/T/S/CST8xx, both stock `tiny_tp_*_contorl`
exports, all three YFT symbols), all 65 stock function names, the module author
and version strings, both embedded firmware names, and distinctive error text.
Local NothingOSS/source mirrors and the exact-GKI tree were searched first;
GitHub/Lineage review and general web indexes were then searched across the
named OEM/BSP families (Nothing, MediaTek, Motorola/MiCode, OnePlus,
OPPO/realme, Transsion, Sony, Ulefone/YFT, GitHub and Gitee).

## Results

| Candidate | Frozen provenance | Evidence | Classification |
|---|---|---|---|
| AYN QCS8550 Hynitron vendor driver | `workspace/phase4-hynitron/source-search/ayn-a552fac-hynitron/`; LineageOS `android_kernel_ayn_qcs8550-modules`, commit `a552fac8fae2c65b7e2e1f3a42e4580732659a6c` | 60/65 stock ELF names appear as parsed C definitions (63/65 as identifiers when module wrappers are excluded), 141 exact stock printable strings, same core/I2C/gesture/update architecture. But it is a 2023 Spreadtrum-labelled V3.1 tree configured for CST148/QCOM, has 194 parsed functions and large ESD/tool/proximity/update families absent from stock, lacks both Ulefone exports and both stock firmware images, and uses different platform/PM APIs. | **STRUCTURAL_DONOR_ONLY** |
| Mainline `drivers/input/touchscreen/hynitron_cstxxx.c` | Linux upstream, including the searched `torvalds/linux` tree | Small generic CST3xx/CST8xx input driver. It lacks YFT registration, firmware engine, gestures, GPIO policy, sysfs factory ABI, and tiny-LCD exports. | SAME_CHIP_DIFFERENT_FRAMEWORK |
| `koendv/cst816t` and other MCU CST816T drivers | GitHub public CST816T repositories | Useful only as protocol corroboration; not Linux/Android vendor framework and not stock source. | SAME_CHIP_DIFFERENT_FRAMEWORK |
| `lupyuen/hynitron_i2c_cst0xxse` | GitHub | Different CST0xxSE family and framework; no GQ5012BF1/YFT delta. | NO_USEFUL_SOURCE |
| NothingOSS and named OEM/BSP searches | local Nothing index plus bounded web/code search | No exact `tiny_tp_*_contorl`, firmware filename, Ulefone/YFT delta, or exact source hit. | NO_USEFUL_SOURCE |

## Exact-source verdict

No exact GQ5012BF1 source was found. The previous project classification is
therefore **not upgraded**: `STRUCTURAL_DONOR_ONLY`. The AYN tree is frozen for
lineage and algorithm comparison, not accepted as completion evidence. Stock
ELF, live/extracted DT and stock userspace remain authoritative.
