> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Two variant axes are now proven: the **dual-source main camera slot** (`camera-main-identity.md`) and the **unpopulated Ilitek/ChipOne touch alternates** (`ilitek-population.md`).

# Hardware variants and population uncertainty

This device has unusually strong signs of a shared board/firmware family. “Supported in software” is not the same as “fitted on this unit.”

## Variant axes

| Area | Evidence | Current conclusion |
|---|---|---|
| Product identity | `GQ5012BF1_EEA`, custom version `DZ_M170_Ulefone_EEA_Armor29Pro_20251022_V35` | this is the Thermal EEA family build |
| RF FEM | 10-entry ConnFem catalog; 3 HWID GPIOs ⇒ 8 selections; Qorvo/Skyworks/no-FEM/bypass candidates | selected FEM pair UNKNOWN |
| Primary touch | FT3680 embedded firmware; 3 module records, only record 0 populated | FT3680 is fitted; two alternate records are latent |
| Auxiliary touch/display | Hynitron `hyn_ts`, Ilitek and ChipOne-TDDI bindings | Hynitron rear touch proven; Ilitek/ChipOne population UNKNOWN |
| Cameras | four sensor driver names: IMX989, front JN1, rear JN1MAIN2, OV64B | four camera paths proven; OEM “IMX989 GN1” label conflicts with geometry |
| Camera OIS | DW9781C `camera-ois-main@e` at `4-000e`, HAL OIS=[0] | controller fitted, stock disabled; exact lens association UNKNOWN |
| Power | SC8571 master/slave + SC851x companion, two RT6160 rails, two gauges | high-power charging topology proven; exact populated silicon revisions partly UNKNOWN |
| Thermal | M170/M170L2 name, FM78100/tiny2c_usb binding, 640×512/25-Hz claim | thermal module present; exact core/NETD/radiometry UNKNOWN |
| Memory | 512 GB and 12/16 GB product claims | exact physical SKU and package IDs UNKNOWN |

## Important contradictions

1. Official text says “50MP Sony IMX989 GN1”. **RESOLVED 2026-09-08 (`../verification/findings/camera-main-identity.md`):** not a contradiction but a **dual-source slot** — `sensor0` declares `imx989`, `s5kgm2sp` and `s5kgn1sp` and binds by sensor-ID probe; this unit probed **IMX989** (Sony-specific 4096×3072 RAW), and Ulefone documents the Samsung population. Retail lots differ.
2. Official camera marketing says 108 MP periscope; live driver says `S5KJN1MAIN2_MIPI_RAW` (50-MP-class JN1 family). **RESOLVED 2026-09-08 (`../verification/findings/camera-stream-configurations.md`):** the third rear camera is a **50 MP ultrawide** (16 mm, f/2.2, 117.3°, autofocus per the OEM). **No periscope exists** in the device tree, the HAL or Ulefone's current specification — the periscope reading is withdrawn.
3. Marketing 10600 mAh and gauge design capacity 8594000 µAh do not reconcile without pack/gauge unit interpretation. Pack topology is now **resolved as 2S / 7.74 V** (see `../verification/findings/battery-pack.md`); the numeric capacity gap remains open.
4. 1000-lumen/570-LED auxiliary-light claim conflicts with local emitter count/measurement; retain as claim, not BOM fact.

## ROM implications

* Preserve all compatible DT overlays and hardware-ID selection logic until runtime HWID is decoded.
* Do not delete “unused” drivers: ConnFem, alternate touch modules, SC8571/SC851x, thermal Miko nodes and alternate camera tables may be needed by another production lot.
* A capability matrix must label each cell as chip ceiling, board-configured, stock-used, or uncertain.

## Verification

Read HWID GPIO values, decode EEPROM calibration/module IDs, inspect package markings, compare multiple GQ5012BF1 retail lots, and record exact submodel/build before merging a custom ROM.

Sources: S01–S05, S10/S15/S20/S21; findings L02/L04/L10/L11/L13/L15.
