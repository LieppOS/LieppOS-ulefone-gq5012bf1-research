# DRAFT: source code request to Ulefone (NOT SENT — requires user approval)

> Status: draft for the user to review. Nothing has been sent, filed or published. Adapt the tone, sender
> identity and contact channel before use.

**Subject:** Request for the corresponding kernel source code for the Ulefone Armor 29 Pro Thermal (GQ5012BF1),
firmware GQ5012BF1_EEA_V15

Dear Ulefone open-source / compliance team,

I own an Ulefone Armor 29 Pro Thermal. I would like to obtain the complete corresponding source code for the Linux
kernel and the GPL-licensed kernel modules distributed with its firmware.

## 1. Exact device and firmware identification

| | |
|---|---|
| Model | Ulefone Armor 29 Pro Thermal, project/board **GQ5012BF1**, SoC MediaTek **MT6878T** |
| Firmware | `ro.build.display.id=GQ5012BF1_EEA_V15` |
| Build fingerprint | `Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/1761131274:user/release-keys` |
| Vendor build | `ro.vendor.build.version.incremental=mp1rck6989v164P8` |
| Kernel | `6.1.115-android14-11-g945dff7bc1bf` (Android GKI build 12901745) |
| Module partitions | vendor_boot (196 module files), vendor_dlkm (215), system_dlkm (60) |

## 2. What is requested

The complete source, as used to build this firmware, of:

1. the **vendor kernel module tree** (MediaTek `kernel_device_modules-6.1` and `kernel_modules` as modified for
   GQ5012BF1), including every Kconfig, Makefile/Kbuild and defconfig fragment, and the build scripts used to
   produce the shipped `.ko` files;
2. in particular, the modules listed below, which declare a GPL licence in their own `.modinfo` but whose exact
   source is not in any public MediaTek, vendor or ODM release we could find.

Hashes are the SHA-256 of the files as shipped. They are given only as precise technical identifiers.

### 2.1 GPL modules whose exact source is missing

| Module | Class | License (modinfo) | Stock sha256 | Missing |
|---|---|---|---|---|
| `aw883xx_driver.ko` | C | GPL v2 | `3bc4722c6550abb9cfd75d06602c2a1bff8d0b6af58708324479ef6a0d22c9b4` | exact Awinic AW883XX v1.7.1 scene/bin parser text (inlined insertion-sort loop shape) |
| `charger_class.ko` | C | GPL | `0c5bd394088d109c569cf5803a82edd0f182bad53714c284f99a797c76cf4e94` | raw source text (srcversion = MD4 over source tokens/deps) of Richtek charger_class 1.0.0_G as shipped |
| `custom-ldo-wl2868.ko` | G | GPL v2 | `dab36e3d2593546d72b4fa7257b4a303c65c0ad4c507bbd1fbb50e1578111d48` | original WL2864/WL2868 camera LDO misc driver (will_ldo_vout/en) source as shipped |
| `custom-ldo.ko` | G | GPL | `9d3d4a3786dd71af4fdee07e4bc332526816b62143925f4e5923f286c9d91556` | original custom LDO (2 functions) source as shipped |
| `flashlight.ko` | D | GPL | `87b18cde1f47c857689602c3232f14874e84fb65b445e4308e80f04728bdefae` | OEM flashlight-core.c with flashlight_drvctrl, flashlight_sw_ctrl_show/_store, "ignore pt" path, no battery-OC callback |
| `focaltech_touch_spi_ft3680.ko` | C | GPL v2 | `6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162` | FocalTech FT3680 SPI driver revision used by the ODM |
| `fpsgo.ko` | D | Proprietary | `e5ec5051d4431f3816e3900c9da52358eae5e62238fad3d71247fe1e08a8a635` | source of xgf_v3_ko_quark (XGF/FSTB/FBT/RL: xgf_est_runtime, fbt_cal_target_time, fstb_get_target_fps, rl_closed_loop_ko_init ...) |
| `hynitron.ko` | G | GPL v2 | `860f28409fdd59458640cd067fec6eb83f3e5ec00ca12782c0e152323a351fb6` | original Hynitron CST rear touch driver incl. firmware header source as shipped |
| `leds-ln2403.ko` | G | GPL | `211bda35ee3476c107d7e495a0463c27bbef114a031a6b81b8bb718bbe54ee94` | original LN2403 PWM camera light source as shipped |
| `msync2_frd.ko` | D | Proprietary | `75405b2f0b7b61981f060ad7852b57e58a95b494bb251e8e49e0ac7c4de601f1` | source of mtk_disp_msync (fpsgo2msync_hint_frameinfo, mtk_drm_get_target_fps, mtk_sync_slow_descent, mtk_sync_te_level_decision) |
| `mtk_chg_type_det.ko` | C | GPL | `8b8922f5bd6a2aea2f512e9b38bae19475f62ae27492bd9ea74c19cb1d4e4a5d` | raw source text for 1.0.2_MTK |
| `panel-ky-vtdr6115-dphy-cmd.ko` | G | GPL v2 | `1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07` | original VTDR6115 AMOLED panel driver (MTK DRM panel) source as shipped |
| `rt_pd_manager.ko` | C | GPL | `b82517127d6360f600e60d2b39d4970c61eab4263e7da67ee28fc5c94cb6715a` | raw source text for rt_pd_manager 1.0.11 |
| `sc851x_charger.ko` | G | GPL v2 | `b5e5f08bcfe37ac8c81525b0d4fe514902b552cc45b7f99fbeda8b80f6c2aa0c` | original SouthChip SC851x driver source as shipped |
| `sc8571_charger.ko` | G | GPL v2 | `790065853b875213ee7906bb4c41a5f272106b24a537034a886f12f0153d1d0b` | original SouthChip SC8571 MTK driver source as shipped |
| `sh366003_fg.ko` | G | GPL v2 | `527bddb4ddb11e94ed85e6969a10f807178cbb3f0fd326c8509824800a3d61a7` | original Sinowealth SH366003 fuel gauge source as shipped |
| `spi_tiny_co5300_lcd.ko` | G | GPL v2 | `39eecad8254c2fc69f9c8d52902b443b3adc64c79c4c6a529af19b4b1f2a9742` | original CO5300 tiny SPI rear LCD source as shipped |
| `st21nfc.ko` | C | GPL | `5c5945457f8e3f37744c95a98075278134a328590d27e00d38dd8de8261078e8` | clean preserved recipe + 2 residual functions; ST public driver 2.2.0.19 lineage |
| `tcpc_class.ko` | C | GPL | `2426edb571f5f8c2c1317b618fe6c10a095a59cf17acdd4d17ef583f63b5b5c5` | exact line layout of tcpc core 2.0.31_MTK (six __LINE__ diagnostic strings, 37 BUG line numbers) + srcversion |
| `tcpc_mt6375.ko` | C | GPL v2 | `30abac643ebc7428a5ff350741d22b0f4bdcf65a5a071f55ec7ba78d862ca750` | source text producing +1 __COUNTER__/unique-ID prefix and srcversion |
| `tkcore.ko` | C | GPL | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | TrustKernel 6:1.1-k6.6 normal-world core: plat.c (CPU affinity: plat_cpu_is_big 68B, plat_tee_init 176B), tee_procfs.c logger (logd, tee_init_procfs,  |
| `yft_devinfo.ko` | C | GPL | `0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe` | YFT private enum/type headers behind 10 exported device_add CRCs and 11 KCFI IDs; probe/sysfs code |
| `yft_tiny2c_usb.ko` | G | GPL | `77baeee8fa7c01d9b6ad9b3a9743caa69aa61b840c3d565d5263d3e965d63eed` | original YFT tiny2c USB companion source as shipped |
| `yft_tpd_gesture.ko` | G | GPL | `e7d4e7cfe4defdd69ff0e1be50c7a3de173b5c717e47e969cf0f9dec13baf9bc` | original YFT touch gesture wake source as shipped |

### 2.2 Why public sources do not suffice

Each module was rebuilt from the closest public MediaTek ALPS, NothingOSS, upstream Linux or vendor release, using
the exact GKI kernel and compiler. Most of the device's 458 kernel modules then match the shipped binaries byte for
byte. The modules above do not, for these reasons:

- **flashlight.ko:** the shipped `flashlight-core.c` has three extra functions (`flashlight_drvctrl`,
  `flashlight_sw_ctrl_show`, `flashlight_sw_ctrl_store`), an "ignore pt" path and strict power throttling.
  None of these exist in any public revision.
- **charger_class, mtk_chg_type_det, rt_pd_manager, tcpc_class, tcpc_mt6375:** the code is already identical; only
  the source-derived metadata differs (`srcversion`, `__LINE__` strings, counter prefixes). The exact source
  files as built are needed.
- **focaltech_touch_spi_ft3680, aw883xx_driver, st21nfc, yft_devinfo:** these are vendor driver revisions that
  differ from the public releases.
- **Board-specific drivers:** panel-ky-vtdr6115-dphy-cmd, spi_tiny_co5300_lcd, hynitron, leds-ln2403,
  custom-ldo/-wl2868, sc851x/sc8571 chargers, sh366003_fg, yft_tiny2c_usb and yft_tpd_gesture have no public source
  at all.
- **tkcore.ko:** see the separate TrustKernel note. Version `6:1.1-k6.6` of the TrustKernel normal-world driver
  (GPL) is not public.

### 2.3 Not requested

- `fpsgo.ko` and `msync2_frd.ko` declare `license=Proprietary`. Their source is **not** claimed under the GPL;
  any request for them is a separate courtesy request.
- Firmware blobs, trusted applications, secure-world code, userspace HALs and calibration data are not requested.

## 3. Licensing basis (verified, not assumed)

- Every module in §2.1 carries `license=GPL` or `GPL v2` in its own `.modinfo` (see SOURCE-RELEASE-EVIDENCE.md).
- These modules are distributed with the device's Linux kernel.
- We ask for the source that corresponds to the binaries as distributed.

We would be grateful for a download link or archive. Thank you.

Kind regards,
[name / contact]
