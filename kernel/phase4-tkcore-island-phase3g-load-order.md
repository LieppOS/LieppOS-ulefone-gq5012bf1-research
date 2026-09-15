# TrustKernel Phase 3G — load-order preservation

Result: **PASS — no `modules.load` redesign or edit is required**.

The index is one-based among non-empty entries in each authoritative stock file.

## Normal boot

| Stock filename | Stock location | Stock load index | Replacement filename | Replacement location | Relative order preserved? |
|---|---|---:|---|---|---|
| `tkcore.ko` | vendor boot platform ramdisk `/lib/modules/tkcore.ko` | 100 | `tkcore.ko` | same exact path | **YES** |
| `tkcore_drv.ko` | vendor boot platform ramdisk `/lib/modules/tkcore_drv.ko` | 101 | stock `tkcore_drv.ko` retained | same exact file/path | **YES** |
| `tmem_ffa.ko` | vendor_dlkm `/lib/modules/tmem_ffa.ko` | 152 | source `tmem_ffa.ko` | same exact path | **YES** |

Critical stock-retained providers/order:

| Partition/load file | Index | Module | Phase-3G action |
|---|---:|---|---|
| vendor boot platform | 98 | `ffa_v10.ko` | retain stock |
| vendor boot platform | 99 | `teeperf.ko` | retain stock |
| vendor boot platform | 100 | `tkcore.ko` | replace in place |
| vendor boot platform | 101 | `tkcore_drv.ko` | retain stock |
| vendor_dlkm | 149 | `gz_tz_system.ko` | retain stock |
| vendor_dlkm | 150 | `gz_main_mod.ko` | retain stock |
| vendor_dlkm | 151 | `gz_log_mod.ko` | retain stock |
| vendor_dlkm | 152 | `tmem_ffa.ko` | replace in place |

The required `ffa_v10 → teeperf → tkcore → tkcore_drv` sequence remains contiguous. `gz_tz_system` remains before `tmem_ffa`; `tkcore` and `ffa_v10` are already loaded from the ramdisk before vendor_dlkm processing.

Stock fingerprint order is also untouched: `spi-mt65xx` 120, `fingerprint` 182, `microarray_fp_tee` 183.

## Recovery list

The extracted platform ramdisk also carries `modules.load.recovery`: `ffa_v10` 96, `teeperf` 97, `tkcore` 98, `tkcore_drv` 99, `spi-mt65xx` 118, `fingerprint` 186, `microarray_fp_tee` 187. The source `tkcore` replacement is by the same filename and path, while stock `tkcore_drv` is retained; this file likewise needs no edit.

## Dependency metadata

The broader static acceptance population was successfully checked with source `tkcore_drv` as well, but the minimized first runtime image deliberately reverts that member to stock. No `modules.dep`, `modules.alias`, `modules.load` or `modules.load.recovery` file is edited: all loader-visible filenames remain identical, stock `tkcore_drv` consumes the source provider's stock-identical exported CRC surface, and source `tmem_ffa` retains its accepted dependency names `gz_tz_system,tkcore,ffa_v10`.
