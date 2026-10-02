# GQ5012BF1 normal camera stack — status matrix (2026-10-02)

Authoritative detail: `README.md` (this directory). Workspace copy: `../../../CAMERA-STACK-STATUS.md`.
Component folders: `Reverse Engineer - PARTIAL/{CAMERA-HAL-ISP,CAMERA-IMX989,CAMERA-OV64B,CAMERA-S5KJN1,CAMERA-S5KJN1MAIN2,DW9781C-OIS}`.
ThermoVue excluded. EEPROM/VCM internals belong to other tracks.

## Cameras

| ID | role | sensor (evidence) | kernel subdrv | bus / 7-bit addr | seninf / PHY | MCLK | rails (WL2864C ch / fixed) | AF | OIS | PDAF | stock modes | kernel source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | rear main | IMX989 — **PROVEN** (chip-ID 0x0989 bind) | imx989_mipi_raw | i2c-7 / 0x1A | port 3 / C-PHY 3-trio | CAMTG3 19.2 MHz | a3 d2 io7 af5 + GPIO184 | main_vcm 7-0x0a | none in stock path | CAMSV_QPD | 33 | **50/54 tables = NothingOSS MT6878 donor**; 4 recovered from stock |
| 1 | front | S5KJN1 — PROVEN (0x38E1) | s5kjn1_mipi_raw | i2c-4 / 0x3D | port 2 / D-PHY 4L | CAMTG2 24 MHz | d1(1.2V) a4 io7 + GPIO76 | none | – | none | 5 | no exact source; data recovered; JN1 public donors near |
| 2 | rear | S5KJN1 die, driver pseudo-ID 0x38E2 — PROVEN | s5kjn1main2_mipi_raw | i2c-2 / 0x2D | port 1 / D-PHY 4L | CAMTG4 24 MHz | d1 a4 io7 af6 + GPIO76 | main4_vcm 2-0x0d | – | CAMSV | 5 | as cam 1 |
| 3 | rear | OV64B — PROVEN (0x566442) | ov64b_mipi_raw | i2c-4 / 0x10 (+0x22) | port 0 / D-PHY 4L | CAMTG2 24 MHz | a4 af5 d1(1.1V) io7 | main2_vcm 4-0x0b | – | type CAMSV, unused | 5 (max 4624×3472) | older NothingOSS donor revision; stock data recovered |
| – | OIS | DW9781C — PROVEN | dw9781c.ko | i2c-4 / **0x0A** (DT @0e) | – | – | rst = camera-common-dovdd | – | – | – | – | **EXACT NothingOSS source** |

## Layers

| layer | status | reconstructable? |
|---|---|---|
| sensor sub-driver data (IDs, modes, tables, pw_seq, VC) | **complete** for all 9 compiled sub-drivers (`stock-imgsensor-oracle/`) | yes |
| imgsensor framework (adaptor, frame-sync, ioctl, virt-sensor) | 507/532 shared fns byte-identical after 1 proven struct delta; 36 stock-only fns (YFT, custom-LDO, HV-charger, 7 sensor TUs) | yes, near-exact |
| custom-LDO / WL2864C, AW365xx flash | reconstructed earlier (DONE/PARTIAL tracks) | yes |
| DW9781C OIS | exact | yes |
| camsys/seninf, imgsys P2, HCP, CCU rproc, AIE, DPE, PDA | 97–100% identifier coverage in NothingOSS MT6878 mtkcam; not parity-built | likely (STRONG) |
| CCU firmware `ccu.img` | proprietary binary | no |
| CameraProvider AIDL + mtkcam pipeline/feature/3A/ISP userspace (774 ELFs) | proprietary blobs only | no (reuse blobs) |
| tuning (`*_tuning.so`, `*_IdxMgr.so`, `ISP_param.db`, `ISP_mapping.db`, NVRAM libs) | proprietary data | no (reuse) |
| HAL lens/OIS tables | OIS deliberately Dummy in `libcameracustom.lens.so` | – |

## Status changes

None moved to DONE. All six components stay **PARTIAL**:
CAMERA-HAL-ISP (proprietary userspace/tuning), CAMERA-IMX989 / OV64B /
S5KJN1 / S5KJN1MAIN2 (no exact C for stock TUs or ODM edits; tuning),
DW9781C-OIS (driver exact, physical lens association still UNKNOWN).

## Known stock defects found

* IMX989 modes 3/4/5/13, OV64B 3/4, JN1 hs/slim: frame descriptors do not
  match the mode window (ODM kept donor descriptors).
* JN1 hs/slim modes carry pasted IMX989 timings (placeholders; not exposed).
* Earlier notes' `camreg`/`ois-en-gpios` DT claims for DW9781C/WL2864C are
  not in the live DT (corrected in research repo).

## Next highest-value camera task

Build an `imgsensor.ko` reconstruction that reaches full stock parity:
recover the 25 remaining ODM-edited framework functions + the 36
stock-only functions as C (custom-LDO hooks, YFT CTS/devinfo calls, HV
charger toggle, night-LED, reg8 I2C) and regenerate the 7 missing sensor
TUs from `stock-imgsensor-oracle/` data, verified function-by-function with
`imgsensor_framework_parity.py`. That turns the whole sensor kernel layer
into source; the ISP kernel modules (mtk-cam-isp7sp, imgsys) are the next
parity-build targets.
