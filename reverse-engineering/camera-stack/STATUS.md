# GQ5012BF1 normal camera stack — status matrix (2026-10-02)

Authoritative detail: `README.md` (this directory). Workspace copy: `../../../CAMERA-STACK-STATUS.md`.
Component folders: `Reverse Engineer - DONE/{CAMERA-IMX989,CAMERA-OV64B,CAMERA-S5KJN1MAIN2,DW9781C-OIS}`,
`Reverse Engineer - PARTIAL/{CAMERA-HAL-ISP,CAMERA-S5KJN1}`.
ThermoVue excluded. EEPROM/VCM internals belong to other tracks.

## Cameras

| ID | role | sensor (evidence) | kernel subdrv | bus / 7-bit addr | seninf / PHY | MCLK | rails (WL2864C ch / fixed) | AF | OIS | PDAF | stock modes | kernel source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | rear main | IMX989 — **PROVEN** (chip-ID 0x0989 bind) | imx989_mipi_raw | i2c-7 / 0x1A | port 3 / C-PHY 3-trio | CAMTG3 19.2 MHz | a3 d2 io7 af5 + GPIO184 | main_vcm 7-0x0a | none in stock path | CAMSV_QPD | 33 | **source, byte-exact** (NothingOSS donor + stock data/ODM edits) |
| 1 | front | S5KJN1 — PROVEN (0x38E1) | s5kjn1_mipi_raw | i2c-4 / 0x3D | port 2 / D-PHY 4L | CAMTG2 24 MHz | d1(1.2V) a4 io7 + GPIO76 | none | – | none | 5 | **source, byte-exact** (generated from stock) |
| 2 | rear | S5KJN1 die, driver pseudo-ID 0x38E2 — PROVEN | s5kjn1main2_mipi_raw | i2c-2 / 0x2D | port 1 / D-PHY 4L | CAMTG4 24 MHz | d1 a4 io7 af6 + GPIO76 | main4_vcm 2-000d (wire 0x0C) | – | CAMSV (QSC dead) | 5 | **source, byte-exact vs the SHIPPED module: 32/32 TU symbols; B1==B2 — DONE** (`s5kjn1main2/`) |
| 3 | rear | OV64B — PROVEN (0x566442) | ov64b_mipi_raw | i2c-4 / 0x10 (+0x22) | port 0 / D-PHY 4L | CAMTG2 24 MHz | a4 af5 d1(1.1V) io7 | main2_vcm 4-0x0b | – | type CAMSV, unused | 5 (max 4624×3472) | **source, byte-exact vs the SHIPPED module: 27/27 TU symbols; B1==B2 — DONE** (`ov64b/`) |
| – | OIS | DW9781C — DT client bound; physical presence not evidenced (no stock I2C access) | dw9781c.ko | i2c-4 / **0x0A** (DT @0e) | – | – | rst = camera-common-dovdd (fixed, no GPIO); no vdd | – | – | – | – | **EXACT NothingOSS source; stock file identical except build-id — DONE** (`dw9781c-ois/`) |

## Layers

| layer | status | reconstructable? |
|---|---|---|
| sensor sub-driver data (IDs, modes, tables, pw_seq, VC) | **complete** for all 9 compiled sub-drivers (`stock-imgsensor-oracle/`) | yes |
| **imgsensor.ko (framework + 9 sub-drivers)** | **reconstructed to source** (`reconstruction/imgsensor/`): 618/619 functions and 394/394 data objects byte-identical; modversions, KCFI, modinfo, symtab identical; whole stripped file differs in 70 bytes (one function, explained in `binary-analysis/README.md`) | **yes — done (parity build)** |
| custom-LDO / WL2864C, AW365xx flash | reconstructed earlier (DONE/PARTIAL tracks) | yes |
| DW9781C OIS | **DONE**: byte-identical except build-id, B1==B2; no stock path reaches the chip (`dw9781c-ois/`) | yes |
| **camsys/ISP kernel modules** — `mtk-cam-isp7sp` (1220/1220 fn, 579/579 data), `mtk_imgsys_v4l2` (185/185, 139/139), `mtk_imgsys_isp7sp` (85/85, 119/119), `mtk_imgsys_cmdq` (165/165, 171/171), `mtk_hcp` (169/169, 53/53), `mtk_ccuv` (45/45, 22/22), `ccd_rpmsg` (29/29, 13/13), `mtk_ccd_remoteproc` (25/25, 13/13), `mtk_aie` (135/135, 116/116) + `mtk_aie_debug_7sp_2`, `camera_dpe_isp7sp` (96/96, 118/118), `mtk-ipesys-me` (14/14, 8/8), `mtk_c2ps` (106/106, 144/144), `c2ps_perf_ioctl`, `imgsensor-glue` | **reconstructed to source, every function and data object byte-identical** (`kernel-isp-imgsys/binary-analysis/per-module/*.tsv`; tree: `gki-12901745-workspace/vendor/mediatek/kernel_modules/mtkcam`) | **yes — done (parity build)** |
| **`camera_eeprom_v4l2.ko`** (cam_cal / OTP) | **126/126 functions, 127/127 data byte-identical**: stock `cam_cal_format.h` ABI (24-byte part number, `sensorID` @0x20, no `FuseId`), all 37 layout tables/config records decoded from relocations, ODM 2A/LSC/PDAF parsers for imx989(cts)/ov64b/s5kjn1*/hi847/s5khp2sp/s5khp3sp*/imx616/ova0b40* restored, `camera_otp` sysfs class probe path | **yes — done (parity build)** |
| CCU firmware `ccu.img` | proprietary binary | no |
| CameraProvider AIDL + mtkcam pipeline/feature/3A/ISP userspace (774 ELFs) | proprietary blobs only | no (reuse blobs) |
| tuning (`*_tuning.so`, `*_IdxMgr.so`, `ISP_param.db`, `ISP_mapping.db`, NVRAM libs) | proprietary data | no (reuse) |
| HAL lens/OIS tables | OIS deliberately Dummy in `libcameracustom.lens.so` | – |

## Status changes

> **Correction 2026-10-07 (`ov64b/stale-claims.md` #2):** the "reproducibility"
> relabel below is wrong. The comparison operand behind the module-wide numbers
> is the shipped `vendor_dlkm/lib/modules/imgsensor.ko` (sha256 `9243061c…`):
> `cmp` against the rebuild (`imgsensor.parity.stripped.ko`, sha256
> `a4364973…`, B1==B2) gives 70 bytes, which are 20 build-id bytes and 50 bytes
> in `yft_ctrl_nightled_by_idx`. That function is mechanically proven
> equivalent for both of its constant call sites. Every sub-driver TU is
> therefore byte-identical to the shipped module. Per-component closure
> still needs its own TU proof and integration review: done for `CAMERA-OV64B`
> (`ov64b/README.md`).

Two different claims were previously merged into one sentence here; they are now
separated.

* **Reproducibility** holds module-wide: all 9 compiled sub-drivers and the
  imgsensor framework exist as source that rebuilds bit-for-bit from the tree —
  618/619 functions, 394/394 data objects, one explained residual
  (`yft_ctrl_nightled_by_idx`). That compares our own stock-data build with our
  rebuild, so it certifies the tree, not agreement with MTK.
* **Stock parity** (comparison against the shipped `imgsensor.ko`) is now proven
  for `CAMERA-IMX989`: `imx989` `0x989` and `imx989cts` `0x988` equal on all 39
  mode fields, 174/174 `static_ctx`, 66/66 register tables and 14 263/14 263
  register write pairs — zero deltas. `CAMERA-IMX989` is therefore **DONE**.

All 9 compiled sub-drivers exist as C with their stock payload generated, so what
is missing for the other seven is not source but the **comparison against the
shipped module**: `ov64b`, `s5kjn1`, `s5kjn1cts`, `s5kjn1main2`, `ov32b40`,
`s5kgm2sp`, `s5kgn1sp` are unreconciled on that axis (OV64B's donor best-match
crossmatch is 50/54 IDENTICAL + 4 NEAREST, i.e. the donor path alone does not
close it). On the framework axis, stock vs recon reports 532 shared functions with
25 byte-differing and 36 stock-only (see
`donor-comparisons/imgsensor-stock-vs-recon-parity.txt`). Per-sensor tuning
`.so`/DB stay blobs (`CAMERA-HAL-ISP`); DW9781C-OIS is DONE (`dw9781c-ois/README.md`). Its physical population and
lens are a hardware-only boundary that no stock software observes.

## Known stock defects found

Checked against the output size each mode's register table programs
(`reconstruction/imgsensor/corrected/*.tsv`; CORRECTED headers are separate from
the parity build):

* IMX989 modes 3/4/5/13 and IMX989CTS 3/4/5, OV64B 3/4: frame-descriptor RAW VC
  size wrong (ODM kept donor descriptors); TG window right.
* S5KGM2SP modes 0/1/2/4: VC wrong, preview VC height typo 300 (for 3000).
* S5KJN1 / JN1CTS / JN1MAIN2 hs/slim: VC right, **TG window wrong** (full
  4080×3072 instead of 1920×1080 / 640×480).
* OV32B40: every mode's VC ≠ TG and the per-mode tables never program an output
  size (10-pair PLL stubs; slim holds a Samsung table) — undeterminable, placeholder
  driver.
* JN1 hs/slim modes carry pasted IMX989 timings (placeholders; not exposed).
* Earlier notes' `camreg`/`ois-en-gpios` DT claims for DW9781C/WL2864C are
  not in the live DT (corrected in research repo).

## Next highest-value camera task

Offline work that still *exists* on the parity axis: close the remaining 7 of the
9 compiled sub-drivers against the shipped module exactly as IMX989 was closed
(`imgsensor_oracle.py` → `compare_oracles.py`): their C and generated payload
already exist, so this is measurement, not writing. Then the framework axis —
25 byte-differing and 36 stock-only functions as C (custom-LDO hooks, YFT
CTS/devinfo calls, HV charger toggle, night-LED, reg8 I2C). Source behind a
semantic oracle is the only form of this claim the shipped binary can support.

Already closed offline: the module-wide reproducibility result above (residual:
the documented `yft_ctrl_nightled_by_idx`). Remaining work for the closed part is
on-device — boot the rebuilt modules and confirm they enumerate; optionally
on-device A/B of the CORRECTED build for modes HAL can select (IMX989 3/4/5/13,
IMX989CTS 3/4/5, JN1 hs/slim).
