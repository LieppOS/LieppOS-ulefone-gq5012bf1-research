# custom_ldo_wl2868 source candidates

## Final bounded-pass classification

`NO_PUBLIC_SOURCE_FOUND`. No byte-identical, source-identical, or strong source match was found. This absence does not prevent stock-oracle behavioral reconstruction.

The closure pass searched the exact description, exported names, compatible, probe/open/seek typo strings, misc name, and both variant helper names through general web indexes, GitHub-indexed results, Gitee-indexed results, grep.app (service returned an HTML block page), and the available local Ulefone/reference trees. It covered NothingOSS, Sony, Motorola, OnePlus/OPPO/realme-style camera-LDO sources, MiCode, Transsion/MediaTek BSP mirrors, GitHub, and Gitee. Results contained only the already-known family datasheets and donor classes below. GitHub CLI/code API was unavailable without authentication; independent web-index searches for the same exact strings returned no matching source. This was the final bounded pass and is now frozen.

## Local/public candidates

| Candidate | Evidence | Classification |
|---|---|---|
| Sony `wl2868c-regulator.c`, commit `7e42db1690b5…` | WL2868C register/voltage/enable family; regulator-framework implementation; compatible `willsemi,wl2868c`; no misc chardev or `will_ldo_*` exports | `STRUCTURAL_DONOR_ONLY` |
| OnePlus `oplus_camera_wl2868c.c`, commit `e01f963b0f71…` | Camera-oriented raw-I2C family; exported enable/set-voltage helpers; supports WL2868C/WL28681C/FAN53870; different platform DT and no stock misc ABI | `STRUCTURAL_DONOR_ONLY` |
| MiCode `wl2868c.c` / `wl28681c.c`, commits `b9d51e845272…`, `9c6256406e2a…`, `2d6f27aa19d5…` | Closest custom-driver architecture: raw WL2868C register map, global client, enable/vset operations, camera-facing ABI; still regulator/sysfs/cdev based and not stock source | `STRUCTURAL_DONOR_ONLY` |
| Motorola Lineage `wl2864c-regulator.c`, commit `1b1263a43c34…` | Same WL2864C seven-LDO register family and enable register 0x0e; regulator framework and different DT/GPIO contract | `STRUCTURAL_DONOR_ONLY` |
| Nothing `cust_wl2864c.dtsi`, commit `957dac185efe…` | Confirms common address 0x29, seven outputs, camera rail names; no matching stock compatible or driver source | `DT/HARDWARE REFERENCE ONLY` |
| Local vendor trees | `device_modules`, `kernel_modules`, Ulefone source material, and `kernel` contain no matching custom source; a `wl2864c.ko` build target exists without source | `NO_PUBLIC_SOURCE_FOUND` |

## Stock-vs-donor discriminators

The frozen stock ELF has 15 functions, a `wl2864c` misc device, raw `i2c_transfer`, `memdup_user`, GPIO consumers named `reset` and `vin1` (the log calls the latter `vin1_en`), DT compatible `will,wl2864c_pmu`, and exactly two exported symbols `will_ldo_vout`/`will_ldo_en`. None of the donor candidates has this combined contract.

Raw donor snapshots and hashes are retained under `workspace/phase4-custom-ldo-wl2868/donors/`.
