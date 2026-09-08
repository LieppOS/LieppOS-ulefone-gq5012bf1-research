# custom_ldo_wl2868 source candidates

## Classification

No byte-identical or source-identical public candidate was found. The reconstruction is **SOURCE_RECONSTRUCTION_STRUCTURAL_AND_BEHAVIORAL_APPROXIMATION**, not a proven source recovery.

## Local/public candidates

| Candidate | Evidence | Classification |
|---|---|---|
| Sony `wl2868c-regulator.c`, commit `7e42db1690b5…` | WL2868C register/voltage/enable family; regulator-framework implementation; compatible `willsemi,wl2868c`; no misc chardev or `will_ldo_*` exports | `STRUCTURAL_DONOR_ONLY` |
| OnePlus `oplus_camera_wl2868c.c`, commit `e01f963b0f71…` | Camera-oriented raw-I2C family; exported enable/set-voltage helpers; supports WL2868C/WL28681C/FAN53870; different platform DT and no stock misc ABI | `STRUCTURAL_DONOR_ONLY` |
| MiCode `wl2868c.c` / `wl28681c.c`, commits `b9d51e845272…`, `9c6256406e2a…`, `2d6f27aa19d5…` | Closest custom-driver architecture: raw WL2868C register map, global client, enable/vset operations, camera-facing ABI; still regulator/sysfs/cdev based and not stock source | `STRUCTURAL_DONOR_ONLY` |
| Motorola Lineage `wl2864c-regulator.c`, commit `1b1263a43c34…` | Same WL2864C seven-LDO register family and enable register 0x0e; regulator framework and different DT/GPIO contract | `STRUCTURAL_DONOR_ONLY` |
| Nothing `cust_wl2864c.dtsi`, commit `957dac185efe…` | Confirms common address 0x29, seven outputs, camera rail names; no matching stock compatible or driver source | `DT/HARDWARE REFERENCE ONLY` |
| Local vendor trees | `device_modules`, `kernel_modules`, and `kernel` contain no matching custom source; a `wl2864c.ko` build target exists without source | `NO_EXACT_SOURCE` |

## Stock-vs-donor discriminators

The frozen stock ELF has 15 functions, a `wl2864c` misc device, raw `i2c_transfer`, `memdup_user`, GPIO consumers named `reset` and `vin1_en`, DT compatible `will,wl2864c_pmu`, and exactly two exported symbols `will_ldo_vout`/`will_ldo_en`. None of the donor candidates has this combined contract.

Raw donor snapshots and hashes are retained under `workspace/phase4-custom-ldo-wl2868/donors/`.
