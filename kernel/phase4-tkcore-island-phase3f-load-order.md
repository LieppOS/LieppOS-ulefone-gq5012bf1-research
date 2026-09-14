# Phase 3F — load-order audit

Phase 3F **does not modify** `modules.load`, boot images, or vendor_boot. This is a read-only audit confirming the stock ordering already satisfies the accepted dependency graph.

## vendor-ramdisk `lib/modules/modules.load` (184 entries)

| Index | Module |
|---:|---|
| 98 | `ffa_v10.ko` |
| 99 | `teeperf.ko` |
| 100 | `tkcore.ko` |
| 101 | `tkcore_drv.ko` |
| 120 | `spi-mt65xx.ko` |
| 182 | `fingerprint.ko` |
| 183 | `microarray_fp_tee.ko` |

The mandated sequence `ffa_v10 → teeperf → tkcore → tkcore_drv` is present and contiguous, and `fingerprint → microarray_fp_tee` is adjacent. Preserved.

## vendor-ramdisk `modules.load.recovery` (189 entries)

`ffa_v10` 96, `teeperf` 97, `tkcore` 98, `tkcore_drv` 99, `spi-mt65xx` 118, `fingerprint` 186, `microarray_fp_tee` 187 — same relative order. Preserved.

## vendor_dlkm `lib/modules/modules.load` (195 entries)

`gz_tz_system.ko` 149, `tmem_ffa.ko` 152 — `tmem_ffa` loads after its GenieZone provider, in its stock vendor_dlkm position. Preserved.

## Cross-check against measured `depends`

| Module | Measured `depends` | Providers load earlier? |
|---|---|---|
| `tkcore.ko` | *(empty)* | n/a |
| `tkcore_drv.ko` | `ffa_v10,tkcore` | yes — 98 and 100 precede 101 |
| `tmem_ffa.ko` | `gz_tz_system,tkcore,ffa_v10` | yes — `gz_tz_system` 149 precedes 152; `tkcore`/`ffa_v10` load from the ramdisk earlier in boot |
| `microarray_fp_tee.ko` | `fingerprint,spi-mt65xx,tkcore` | yes — 120, 182 precede 183; `tkcore` at 100 |

No ordering change is required by Phase 3F, because the rebuilt modules declare exactly the same `depends` sets as the stock/frozen baselines.
