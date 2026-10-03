# GQ5012BF1 normal camera stack — offline reverse engineering (2026-10-02)

Scope: the four "normal" cameras (IMX989, S5KJN1 front, S5KJN1MAIN2, OV64B),
the DW9781C OIS, the MT6878 ISP kernel stack and the MTK camera HAL.
ThermoVue/AC020 is out of scope. EEPROM/VCM internals belong to the
CAMERA-EEPROMS / CAMERA-VCMS tracks and are touched only as dependencies.

All work is static: stock images (`workspace/gq5012bf1/stock/…`), the frozen
2026-08-31 read-only capture (`snapshots/live-stock-adb-20260831-115649`),
the merged stock DT, and local/public donor source. Nothing was sent to the
phone.

Evidence classes: **PROVEN** (read directly from stock binary/DT/runtime
capture, or byte-level parity), **STRONG** (several independent stock
signals), **INFERRED** (one signal or naming), **UNKNOWN**.

## 0. Headline results

0. **(update) `imgsensor.ko` rebuilt from source to stock parity.**
   `reconstruction/imgsensor/` holds the framework + all 9 sub-drivers;
   618/619 functions and 394/394 data objects byte-identical, modversions /
   KCFI / modinfo identical, stripped module differs in 70 bytes (one
   explained function). Reports: `binary-analysis/`. Stock geometry defects
   are kept in the parity build and fixed only in a separate CORRECTED
   build (`-DGQ5012BF1_CAM_CORRECTED`).
1. **Stock `imgsensor.ko` fully decoded.** A dependency-free ELF/RELA walker
   (`scripts/imgsensor_oracle.py`) using struct layouts recovered by DWARF
   from the Nothing MT6878 headers (sizes verified against the stock objects:
   `subdrv_mode_struct`=440, `subdrv_static_ctx`=800, `subdrv_entry`=40,
   `pw_seq`=12) extracts, for all **9 compiled sub-drivers**, every
   static_ctx field, every mode (pclk/linelength/framelength/fps/MIPI
   rate/windows/PDAF/HDR/CSI params), every VC frame descriptor, every power
   sequence and **all 105 register tables** → `stock-imgsensor-oracle/`.
   The stock sensor data is therefore recoverable verbatim even where no
   donor source exists.
2. **IMX989: exact public donor family exists** (NothingOSS MT6878
   `mtkcam/imgsensor/src-v4l2/common/imx989_mipi_raw` + `imx989lite_mipi_raw`).
   Of 54 stock IMX989 register tables, **50 are byte-identical** to a donor
   table (init, 23/24 seamless tables, 26 mode tables); **4 mode tables
   (custom7/8/12/20) are a stock-only register revision**; 83/87 static_ctx
   fields identical. Ulefone changes are a mode re-mapping, a PDAF type
   change, removed OIS rail, CTS-board gating and an AWB-gain hook.
   **Closed 2026-10-03** as `Reverse Engineer - DONE/CAMERA-IMX989/`: re-verified
   from scratch against the shipped module — 41/41 modes (33 + 8), 174/174
   `static_ctx` fields and **14 263/14 263 register write pairs identical**, zero
   deltas; see `notes/imx989.md`.
3. **Shared imgsensor framework is near-exact donor source.** Building the
   Nothing `src-v4l2` framework against exact GKI 12901745 and adding **one
   proven struct delta** (a 14-int `custom_ldo` channel array in
   `struct adaptor_ctx`, `reconstruction/…patch`) raises byte-identical shared
   functions from **244/532 → 507/532**; frame-sync (179 fns), ioctl (64),
   command, trace, i2c, util and virt-sensor are 100% byte-identical.
   Remaining: 25 functions with ODM edits + 36 stock-only functions (YFT
   hooks, custom-LDO, HV-charger toggle, and 7 sensor TUs with no public
   v4l2-common source).
4. **`dw9781c.ko` is an EXACT match** of Nothing
   `device_modules/drivers/misc/mediatek/lens/ois/dw9781c/dw9781c.c`:
   19/19 functions byte-identical, 19/19 KCFI, 38/38 MODVERSION CRCs,
   52/52 strings, every code/data section identical (only vermagic tag,
   build-id and relocation-table order differ).
5. **Userspace OIS is not wired.** `libcameracustom.lens.so` lens tables
   (PROVEN): `vcm_list_0` maps 0x989/0x988/0x8e1→`main_vcm`,
   0x38e2→`main4_vcm`, 0x566442→`main2_vcm`, and **every `ois_list_N`
   contains only the `Dummy` entry** — the HAL's `OISDrv` can never open the
   DW9781C, which is the root cause of `availableOpticalStabilization=[0]`.
6. **Camera→bus→port→rail map is closed** from DT + stock code (table §2).
7. Proprietary boundary is now precise (§6): the whole userspace HAL (774
   ELFs), 3A, per-sensor tuning (`*_tuning.so`, `*_IdxMgr.so`,
   `ISP_param.db`/`ISP_mapping.db`), CCU firmware, plus the 7 sensor
   sub-drivers without public src-v4l2 source.

## 1. End-to-end path (PROVEN unless marked)

```
Android Camera2 API
 → cameraserver (system, media.camera)                         [live svc list]
 → android.hardware.camera.provider.ICameraProvider/internal/0 (AIDL v2)
     /vendor/bin/hw/camerahalserver (u:r:mtk_hal_camera, user cameraserver)
     + IISPModule/internal/1, IATMs/default, IBGService/default (same process)
 → libmtkcam_hal_aidl_provider → _device → libmtkcam_pipeline / pipelinemodel /
   featurepipe (capture, streaming, p2g, depthmap) / featurepolicy
 → sensor layer: libcam.halsensor(.hwintegration) + libcameracustom.imgsensor.core
     (+ libmtkcam_metastore / libmtkcam.logicalmodule = per-DRVNAME static metadata,
      libcameracustom.lens = sensor-id→VCM/OIS driver tables)
 → 3A: libcam.hal3a* + lib3a.* (ae/af/awb/flash/flicker/pd) + oisdrv/lensdrv
 → ISP: libcam.halisp.* (v4l2), libimgsys_* (DIP/WPE/PQDIP/GCE), libcam.isptuning.v4l2
 → tuning: <sensor>_mipi_raw_tuning.so + <sensor>_mipi_raw_IdxMgr.so (dlopen by name
     from libcameracustom.so) + /vendor/bin/crossbuild/DataSet/SQLiteModule/db/
     tuning_DB/<sensor>_mipi_raw/mt6878/ISP_param.db + ISP_mapping.db
 → V4L2/media: /dev/media*, /dev/v4l-subdev* (OISDrv/lensdrv open subdevs by name)
 → kernel: mtk-cam-isp7sp (camsys RAW/YUV/MRAW + seninf) ← imgsensor (subdev per sensor)
           mtk_imgsys_* (P2), mtk_hcp, mtk_ccuv (CCU rproc, ccu.img fw), ccd_rpmsg/
           mtk_ccd_remoteproc, mtk_aie (FD), camera_dpe, pda_drv_mt6878, ipesys-me
 → imgsensor sub-driver → custom-ldo → custom-ldo-wl2868 (WL2864C @ i2c-11 0x29)
                         + regulator-fixed GPIO rails + pinctrl (PDN/RST/MCLK)
 → seninf-top (csi-port-0..3, mtk-csi-phy-3-1) ← physical sensor
```

## 2. Camera identity matrix

I2C addresses below are the 7-bit addresses the stock driver actually
talks to (`i2c_addr_table` write-IDs >>1; the DT `reg` only names the node).

| | Cam 0 rear main | Cam 1 front | Cam 2 rear (2nd) | Cam 3 rear (3rd) |
|---|---|---|---|---|
| HAL DRVNAME (runtime, PROVEN) | IMX989 | S5KJN1 | S5KJN1MAIN2 | OV64B |
| facing/orientation | BACK 90 | FRONT 270 | BACK (270/90) | BACK (270/90) |
| DT node | `i2c@11e02000/sensor0` | `i2c@11c23000/sensor1` | `i2c@11c22000/sensor2` | `i2c@11c23000/sensor4` |
| Linux bus | i2c-7 | i2c-4 | i2c-2 | i2c-4 |
| DT `sensor-names` | imx989, s5kgm2sp, imx989cts, s5kgn1sp | s5kjn1, ov32b40, s5kjn1cts | s5kjn1main2 | ov64b |
| chip-ID regs → value | 0x0016/17 → 0x0989 | 0x0000/01 → 0x38E1 | 0x0000/01 → 0x38E1 (+1 ⇒ pseudo 0x38E2) | 0x300A-C → 0x566442 |
| sensor I2C (7-bit) | 0x1A | 0x3D | 0x2D | 0x10, then 0x22 |
| seninf CSI port (DT graph) | csi-port-3 | csi-port-2 | csi-port-1 | csi-port-0 |
| PHY / lanes | **C-PHY, 3 trios** | D-PHY 4-lane | D-PHY 4-lane | D-PHY (CSI2) 4-lane |
| MCLK (DT clk "mclk") | CAMTG3_SEL, 19.2 MHz | CAMTG2_SEL, 24 MHz | CAMTG4_SEL, 24 MHz | CAMTG2_SEL (shared w/ cam1), 24 MHz |
| power (stock pw_seq, µV) | AVDD 2.8 (LDO3), AVDD2 1.8 (GPIO184 fixed), AFVDD 2.8 (LDO5), DOVDD 1.8 (LDO7), DVDD 1.1 (LDO2) | DOVDD 1.8 (LDO7), DVDD 1.2 (LDO1), AVDD 2.8 (LDO4), AVDD1 1.8 (GPIO76 fixed) | DOVDD 1.8 (LDO7), DVDD 1.2 (LDO1), AVDD 2.8 (LDO4), AVDD1 1.8 (`camera2-common-avdd1`, also GPIO76), AFVDD 2.8 (LDO6) | AVDD 2.8 (LDO4), AFVDD 2.8 (LDO5), DVDD 1.1 (LDO1), DOVDD 1.8 (LDO7) |
| AF actuator (userspace lens table) | `main_vcm` i2c-7 0x0a | none (fixed focus) | `main4_vcm` i2c-2 0x0d | `main2_vcm` i2c-4 0x0b |
| EEPROM node (DT) | eeprom0 i2c-7 0x51 | eeprom1 i2c-4 0x50 | eeprom2 i2c-2 0x50 | eeprom4 i2c-4 0x51 |
| kernel QSC/cali hook | `set_sensor_cali` (eeprom_info, 1) | none | `set_sensor_cali` (eeprom_info, 1) | none (donor had one; removed) |
| flash | AW36515/18 group (hasFlashUnit 1) | none | hasFlashUnit 1 | hasFlashUnit 1 |
| PDAF (static_ctx) | CAMSV_QPD | NA | CAMSV (pd_info on preview) | CAMSV type, no mode has pdaf_cap |
| kernel modes | 33 (incl. 8192×6144 remosaic @15/24, 7680×4320@30, 1080p@480, 720p@480, stagger/DCG/LBMF HDR) | 5 | 5 | **5, max output 4624×3472** (no full-array mode) |
| temperature read | yes | no | no | yes |
| seamless switch | yes | no | no | no (donor function dropped) |
| OIS | no OIS rail in stock pw_seq | – | – | DT pinctrl `oisen_*` only |

Rail note (PROVEN, `phase4-custom-ldo-imgsensor-consumer-analysis.md` +
oracle): custom-LDO channel 1 is DVDD for cams 1, 2 **and** 3 but is
programmed 1.2 V by the JN1 drivers and 1.1 V by OV64B; channel 4 is AVDD
for cams 1-3; channel 5 is AFVDD for IMX989 **and** OV64B. The value is
re-programmed on every power-on.

Board-variant logic (PROVEN from disassembly): every sub-driver's
`get_imgsensor_id` calls `yft_devinfo:is_yft_cts_board()` (DT GPIO
`urxdo_gpio_select`). `imx989`, `s5kjn1`, `s5kjn1main2`, `ov64b` only bind
when it returns 0; the `*cts` variants (expected IDs 0x988 / 0x38E0, reduced
mode sets) bind on CTS boards. This handset bound the non-CTS drivers, so
`is_yft_cts_board()==0` here. `s5kgn1sp`/`s5kgm2sp` do not consult the flag.

## 3. Kernel side

`kernel-camera-modules.tsv` lists every camera-related module with load
order, hash, `depends`, donor and status. Dependency graph (PROVEN from
modinfo):

```
custom-ldo-wl2868 ← custom-ldo ← imgsensor → imgsensor-glue, flashlight,
      yft_devinfo, mtk_charger_framework (yft_cam_open_flag), mtk_ccu_mssv, aee_aed
mtk-cam-isp7sp → ccd_rpmsg ← mtk_ccd_remoteproc ; mtk_ccu_mssv/mtk_ccuv ;
      mtk-mmdvfs-v3, mtk-smi(+dbg), mmqos, iommu_debug, cmdq, slbc, gz_tz_system
mtk_imgsys_isp7sp → mtk_imgsys_v4l2 → mtk_hcp, mtk_imgsys_cmdq, mtk-ipesys-me
dw9781c → hf_manager (sensorhub framework) ; main*_vcm/sub_vcm → camera_af_media
vendor_boot: clk-mt6878-cam/img/ccu, i2c-mt65xx, mtk-smi, mtk_iommu, mmdvfs, pinctrl-mt6878,
      mt6363/rt5133 regulators
```

Source status (`kernel-module-source-coverage.tsv`, identifier-level
triage against NothingOSS MT6878; parity builds only where stated):

| module | result |
|---|---|
| `dw9781c` | **EXACT** (§0.4) |
| `imgsensor` | framework near-exact (507/532 shared fns byte-identical with 1-line struct delta); sensor TUs: imx989 donor exact family, ov64b donor older revision, 7 TUs without public v4l2-common source |
| `custom-ldo`, `custom-ldo-wl2868`, `aw365xx` | reconstructed in earlier phase-4 work |
| `mtk-cam-isp7sp` | **EXACT** — 1220/1220 functions, 579/579 data objects (mtkcam commit 41c1a96) |
| `mtk_imgsys_*`, `mtk_hcp`, `mtk_aie*`, `camera_dpe_isp7sp`, `pda_drv_mt6878`, `mtk_ccuv`, `ccd_rpmsg`, `mtk_ccd_remoteproc`, `mtk-ipesys-me`, vmm | 97–100% name coverage in Nothing mtkcam / device_modules (STRONG; not parity-built) |
| `camera_eeprom_v4l2` | **EXACT** — 126/126 functions, 127/127 data objects (mtkcam commit 133c6c1; stock `cam_cal_format.h` ABI: 24-byte part number, `sensorID` @0x20, no `FuseId`; all 37 layout tables + ODM 2A/LSC/PDAF parsers restored) |

`imgsensor.ko` stock-only functions (36) and what they prove:

* `set_custom_ldo`/`unset_custom_ldo` + the `adaptor_ctx` slot — WL2864C rails.
* `imgsensor_high_voltage_supply` — imports `power_supply_get_by_name/
  set_property/changed`, strings `chg_psy`, `usb_psy`, `enable_hv`,
  `yft_cam_open_flag`: **camera open toggles charger high-voltage input**
  and publishes a camera-open flag consumed by `charger_cooling.ko`.
* `yft_ctrl_nightled_by_idx` → `flashlight_drvctrl` — night-LED control.
* `adaptor_i2c_reg8_rd_u8/wr_u8` — 8-bit register addressing helper.
* `imx989_awb_gain`, `s5kgn1sp_awb_gain` — sensor-side AWB gain writes.
* CTS-aware `get_imgsensor_id`, `open` (inline init + `write_sensor_Cali`).
* full TUs for s5kgm2sp, s5kgn1sp, ov32b40, s5kjn1, s5kjn1cts, s5kjn1main2,
  imx989cts (seamless/test-pattern/sensor_init/read_4cell_from_eeprom).

ODM template artefacts found by the oracle (PROVEN, data-level):
`s5kjn1*` hs_video/slim_video mode_structs carry **IMX989 timings**
(pclk 4.3904/4.352 GHz, linelength 11168/7168) and the four JN1-family
drivers plus `ov32b40` share the same 74-pair hs/slim register tables
(Samsung `0x6028/0x602A/0x6F12` indirect writes even in the OmniVision
`ov32b40` driver) — copy-paste placeholders; HAL never exposes 1200/2400 fps
for these cameras.

## 4. Userspace

* `userspace/camera-services.tsv` — provider/ISP/ATMS/BG services, process,
  SELinux domain, instances (PROVEN from vintf + live service list).
* `userspace/camera-userspace-dependencies.tsv` — 774 reachable vendor ELFs
  (DT_NEEDED + embedded `lib*.so` string edges), class, hash.
  `userspace/camera-userspace-edges.tsv` — 10 830 edges.
  `/vendor/lib64/mt6878/*` are byte-identical duplicates of `/vendor/lib64/*`.
* `userspace/camera-sensor-specific-files.tsv` — sensor-named blobs.
* `userspace/tuning-db-inventory.tsv` — 88 mt6878 tuning SQLite DBs.
  Focus sensors: `ISP_param.db` 2.4–6.5 MB, single-row `isp_all_Param`
  blob, version 15227; TreeBuildStamps imx989 20250418, imx989cts
  20250102, ov64b 20250224, s5kjn1 20250427, s5kjn1main2 20250418,
  s5kjn1cts 20250102, s5kgn1sp 20251015, ov32b40 20230522 (= MTK default
  template; its ISP_mapping.db is byte-identical to imx350/376/586/616).
* Sensor list compiled into `libcameracustom.imgsensor.core.so`:
  imx989, imx989cts, ov64b, s5kjn1, s5kjn1cts, s5kjn1main2, s5kgm2sp,
  s5kgn1sp (+ mtk000 dummy); IdxMgr list in `libcameracustom.so` adds
  ov32b40. **No `s5kgm2sp_mipi_raw_tuning.so` and no s5kgm2sp tuning DB**
  exist → a GM2-populated unit would run without sensor tuning (INFERRED:
  GM2 is a dead option).
* Static metadata per DRVNAME: `libmtkcam_metastore.so`
  (`constructCustStaticMetadata_PLATFORM_*`), `libmtkcam.logicalmodule.so`
  / `libcam.halsensor.so` (`COMMON_SENSOR_*`, `PLATFORM_LENS_*`).
* `libcam.hal3a.oisdrv.so` (`ois_drv.cpp`, `OISDrv::EnableOis`,
  `GetV4l2SubDevName`) looks the OIS subdev up via
  `GetOisDriverName()` in `libcameracustom.lens.so`, whose `ois_list_*`
  are all `Dummy` (§0.5).

## 5. DW9781C OIS (see `notes/dw9781c-ois.md`)

PROVEN: driver = Nothing source verbatim; real I2C address **0x0A on i2c-4**
(`client->addr = 0x14>>1` overrides DT `reg = 0x0e`); regulators `vdd`
(absent in DT → dummy) and `rst` (`camera-common-dovdd`, fixed 1.8 V, no
GPIO); no firmware download (`FW_UPDATE` undefined; only FW_VER/FW_DATE
read at 0x7001/0x7002); gyro source `IMU_SELECT(0x7012)=ICM42631_AUX2`;
init may **write OIS NVM** (`0x7015=2, 0xFD00=0x5252, 0x7011=0x00AA,
0x7010=0x8000`) when `GYRO_INIT(0x7018)!=1` — must never be triggered
casually. Kernel consumers: v4l2 subdev ioctl `VIDIOC_MTK_S_OIS_MODE` and
sensorhub `hf_manager` sensor type `OIS1`. Userspace consumer list empty.
Physical module: UNKNOWN (INFERRED leaning OV64B: same i2c-4 segment,
`sensor4` `oisen_*` pinctrl, DT alias `main_ois_cam1` next to
`main_af_cam1`; against: node name `camera-ois-main`, `sensor0`
`oisvdd_*` pinctrl).

## 6. Exact proprietary boundary

Reconstructable from source now (open):
`dw9781c` (exact), imgsensor framework (near-exact), imx989 sub-driver
(donor + 4 stock tables extracted), custom-ldo stack, flash drivers, and
STRONG-donor ISP kernel modules (camsys/imgsys/hcp/ccu-rproc/aie/dpe/pda).

Reconstructable only from the stock binary (no public source, but complete
data recovered by the oracle): s5kjn1 / s5kjn1main2 / s5kjn1cts /
ov32b40 / s5kgn1sp / s5kgm2sp / imx989cts sub-drivers (tables, modes,
pw_seq, IDs) — logic is generic `common_*` framework plus small inline init
(`open()` inline writes recovered by `scripts/inline_writes.py`; the 37-write
JN1 init contains all 30 pairs of the public NothingOSS-mt6886 JN1 init).

Proprietary, no source anywhere local: entire camera HAL & pipeline,
3A (`lib3a.*`, `libcam.hal3a*`), ISP userspace (`libcam.halisp*`,
`libimgsys_*`), AI/feature algos (`libcamalgo.*`, `libfeature*`,
neuron/APU), tuning (`*_tuning.so`, `*_IdxMgr.so`, `ISP_param.db`,
`ISP_mapping.db`, ParameterDB/top_control DBs, NVRAM defaults
`libcam.hal3a.v3.nvram.v4l2.so`, `libcustom_nvram.so`), CCU firmware
(`ccu.img`), per-module EEPROM calibration content.

## 7. Reproduce

```
scripts/build_donor_camera_modules.sh          # exact-GKI donor builds (host only)
python3 scripts/imgsensor_oracle.py <stock imgsensor.ko> stock-imgsensor-oracle
python3 scripts/compare_oracles.py stock-imgsensor-oracle imx989_mipi_raw <donor-oracle> imx989_mipi_raw
python3 scripts/crossmatch_tables.py stock-imgsensor-oracle sensor:s5kjn1_mipi_raw <donor-oracle>...
python3 scripts/c_tables_to_tsv.py <out> <legacy donor .c>       # legacy donors -> TSV
python3 scripts/inline_writes.py <ko> <start> <end>               # inline init writes
python3 scripts/imgsensor_framework_parity.py <stock> <rebuilt> <builddir> <out.tsv>
python3 scripts/camera_userspace_deps.py <vendor> <system> userspace
python3 scripts/tuning_db_inventory.py <vendor> userspace/tuning-db-inventory.tsv
python3 scripts/module_source_coverage.py <mods> <nothing-root> out.tsv <ko>...
```

## Methodology guard (2026-10-03): two oracles, do not conflate them

`imgsensor_parity.py` **cannot** run against the shipped module: it aborts with
`cannot attribute rebuilt function set_custom_ldo`, because MTK's binary carries
cross-module symbols that our object set does not contain. Every
"618/619 byte-identical" style number from that harness therefore compares **two
builds of our own tree**. Byte-identity in that comparison is expected by
construction, so it measures how well the tree is pinned — never whether we match
stock. Real stock parity requires `imgsensor_oracle.py` + `compare_oracles.py`
against `vendor_dlkm/lib/modules/imgsensor.ko`.

This matters because the reproducibility numbers look far more decisive than the
semantic ones (618/619 byte-exact vs "fields identical"), and it is the weaker
claim of the two. Any future camera closure must state which axis each number
came from; `DONE/CAMERA-IMX989/` is written to that standard.

Donor provenance: `donor-comparisons/nothing-mt6878-donor-file-hashes.txt`
(NothingOSS MT6878 trees under `kernel-research/nothing-mt6878`, Tetris
U2.6 release notes up to 241204) and `public-donor-file-hashes.txt`
(NothingOSS `android_kernel_5.15_nothing_mt6886@mt6886/Pacman/t`
commit b690b79a for s5kjn1; AdarshGrewal `android_kernel_xiaomi_zircon@
zircon-t-oss` commit 22f96af3 for bailus5kjn1).
