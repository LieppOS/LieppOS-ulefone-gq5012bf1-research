# Phase 4 — Slot-B minimum viable source stack (GQ5012BF1)

This document answers one question:

> **What can we boot now, without finishing every obscure module?**

Three targets are defined: **Level A — first boot**, **Level B — usable phone**,
**Level C — source-complete**. Every module carries one label:
`SOURCE_NOW`, `STOCK_TRANSITION`, or `NOT_REQUIRED`.

Companion documents: `phase4-remaining-module-triage.md` (dispositions and
priorities), `phase4-remaining-module-dependency-graph.md` (build order),
`phase4-buildability-plan.md` (build environment).

---

## 0. The enabling fact

Three independently-established results make an early Slot-B boot possible:

1. **The stock boot kernel is bit-for-bit identical to Google's published
   `Image.lz4` for `ab/12901745`** (`exact-gki-binary-identity.md`). Ulefone did
   not ship a modified GKI core.
2. **All 2 946 observed stock kernel-facing `CONFIG_MODVERSIONS` requirements
   match the exact Google `vmlinux.symvers`** —
   `exact-gki-full-crc-comparison.csv` yields `Counter({'MATCH': 2946})`, i.e.
   *zero* mismatches.
3. **All 23 still-unresolved stock modules import zero unresolved and zero
   mismatched kernel symbols** (re-verified in this triage; table in
   `phase4-remaining-module-triage.md` §7).

Therefore a self-built `//common:kernel_aarch64` from the pinned CI workspace is
a **drop-in replacement** for the stock kernel while the entire stock vendor
module set is retained unchanged.

We do **not** need source purity before the first Slot-B boot.

---

## LEVEL A — FIRST BOOT

**Goal:** boot Slot B on a kernel we built ourselves, reach Android userspace,
keep adb, and keep the device recoverable. Nothing else.

**Minimum change set: exactly one artefact.**

| component | label | detail |
|---|---|---|
| GKI core (`boot.img` kernel) | **SOURCE_NOW** | `//common:kernel_aarch64` built in `/home/armol/kernel-work/gki-12901745-workspace` from `kernel/common @ 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` with the 20 pinned CI project SHAs |
| all 184 vendor_boot platform modules | **STOCK_TRANSITION** | unchanged binaries, `modules.load` order preserved verbatim |
| all 195 vendor_dlkm modules | **STOCK_TRANSITION** | unchanged, `modules.load` order preserved verbatim |
| all 60 system_dlkm modules | **STOCK_TRANSITION** | unchanged |
| `modules.load`, `modules.load.recovery`, `modules.dep`, `modules.alias`, `modules.softdep` | **STOCK_TRANSITION** | byte-identical; do not regenerate |
| `odm_dlkm` | **NOT_REQUIRED** | contains no kernel modules (only `etc/`) |
| DT / DTBO | **STOCK_TRANSITION** | unchanged — out of scope for this task |
| `uarthub_drv` | **NOT_REQUIRED** | `uarthub-disable = <1>`; OF entry resolves to `undef_plat_data` |

**Unresolved modules that must be reconstructed for Level A: ZERO.**

All 23 stay `STOCK_TRANSITION`, including the two `P0_BOOT_CRITICAL` ones:

| module | why it must stay | blob safety |
|---|---|---|
| `tkcore` | KeyMint 3.0 + Gatekeeper + Widevine + FBE unlock | `YES_SAFE_TRANSITION` (101/101 kernel CRCs, 0 intermodule imports) |
| `tkcore_drv` | TEE transport for the above | `YES_WITH_STOCK_PROVIDER_CHAIN` (`tkcore` + `ffa_v10`) |
| `panel_ky_vtdr6115_dphy_cmd` | main display | `YES_WITH_STOCK_PROVIDER_CHAIN` |
| all other 20 | see triage TSV | 7 `YES_SAFE_TRANSITION`, 16 `YES_WITH_STOCK_PROVIDER_CHAIN` |

### Level A acceptance criteria

1. `uname -r` reports the locally built vermagic, **not** `g945dff7bc1bf`.
2. `dmesg` shows zero `disagrees about version of symbol` and zero
   `Unknown symbol` lines.
3. All 184 platform + 195 vendor_dlkm modules appear in `lsmod`.
4. Display lights up (`yft-lcm-vtdr6115-drv-` sequence in dmesg).
5. `keystore2`, `vendor.keymint-3-0-trustkernel` and `vendor.gatekeeper` reach
   `running`; encrypted `/data` mounts.
6. adb is up and Slot B is marked successful.

### Level A risk register

| risk | mitigation |
|---|---|
| vermagic mismatch rejects every stock module | build with the exact `LOCALVERSION`/`SCMVERSION` handling of the CI build, or accept `modules.load` failure and fall back to Slot A |
| module signature enforcement | the CI workspace has no `signing_key.pem`; confirm `CONFIG_MODULE_SIG_FORCE` is not set before flashing |
| Kleaf prebuilt path is blocked | known: `kernel_filegroup` omits `KernelBuildExtModuleInfo.strip_modules`; use the source-backed `//common:kernel_aarch64` target (already proven to build) |

---

## LEVEL B — USABLE PHONE

**Goal:** daily-driver basics — display, touch, charging, audio, connectivity,
core power. Adds the frozen reconstructions plus the `P1`/`P2` work.

### B.1 Already frozen — promote to `SOURCE_NOW`

| module | label | status |
|---|---|---|
| `st21nfc` | SOURCE_NOW | `ST21_SOURCE_DELTA_RECONSTRUCTION_COMPLETE`, 54/54 CRCs |
| `mtk_disp_notify` | SOURCE_NOW | `DIRECT_SOURCE_VARIANT / mediatek_v2` (all 6 exports) |
| `mtk_mbox` | SOURCE_NOW | frozen |
| `mtk_tinysys_ipi` | SOURCE_NOW | frozen |
| `mtk_rpmsg_mbox` | SOURCE_NOW | frozen |
| `connfem` | SOURCE_NOW | `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION` |
| `tcpc_class` | SOURCE_NOW | frozen |
| `tcpc_mt6375` | SOURCE_NOW | frozen |
| `pd_dbg_info` | SOURCE_NOW | frozen |
| `leds_rgb_aw2013` | SOURCE_NOW | byte-identical except vermagic |
| `aw36515` | SOURCE_NOW | `SOURCE_DELTA_RECONSTRUCTION_EXACT`, 47/47 CRCs |
| `aw36518` | SOURCE_NOW | 47/47 CRCs |
| `aw36518_v2` | SOURCE_NOW | 46/46 CRCs |
| `aw883xx_driver` | SOURCE_NOW | 236/236 functions |
| `yft_tpd_gesture` | SOURCE_NOW | byte-exact code/data; 2/3 export CRCs |
| `focaltech_touch_spi_ft3680` | SOURCE_NOW | **must be relinked against the STOCK `yft_devinfo` `Module.symvers`** (see B.2) |
| `custom_ldo_wl2868` | SOURCE_NOW | `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; FROZEN FOR RE; exact function/KCFI/call and MODVERSION/export ABI sets; 50/50 verifier |
| `custom_ldo` | SOURCE_NOW | `STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`; 2/2 functions byte-identical, exact provider/consumer CRCs |
| `sc851x_charger` | SOURCE_NOW | `SOURCE_RECONSTRUCTED`; no-public-source oracle, exact-GKI build clean, all function sizes/KCFI/data/strings/MODVERSIONs and relocation target/type sequences match |
| `sc8571_charger` | SOURCE_NOW | `SOURCE_RECONSTRUCTED`; exact-GKI build clean; exact provider CRC, KCFI, `__versions`, register/ADC tables and charger callback slots; bounded ABI/behavioral static parity PASS; needs stock-compatible `charger_class` |

### B.2 The `yft_devinfo` pin — mandatory for Level B

| module | label | rule |
|---|---|---|
| `yft_devinfo` | **STOCK_TRANSITION** | keep the stock `.ko`; do **not** ship the reconstruction |

Reason: 10 of its 27 export CRCs (all `*_device_add()`) are still gapped on a
73-character vendor enum text. Those exports are imported by `sh366003_fg`,
`hynitron`, `spi_tiny_co5300_lcd`, `imgsensor`, `hf_manager` and the
reconstructed `focaltech_touch_spi_ft3680`.

Every consumer — source-built or stock — must be linked against the **stock**
provider's `Module.symvers` via `KBUILD_EXTRA_SYMBOLS`. That is linking against
the real provider, not patching a reconstruction's exports.

Shipping the reconstructed `yft_devinfo` at Level B would break the fuel gauge,
rear touch, rear display, camera sensors and motion sensors simultaneously.

### B.3 New work required for Level B

| order | module | label | disposition | why Level B |
|--:|---|---|---|---|
| 1 | `panel_ky_vtdr6115_dphy_cmd` | ABI_SOURCE | BLOCKED_WITH_EXACT_MISSING_EVIDENCE | panel logic reconstructed; exact provider type graph needed for 7 CRCs |
| 4 | `sh366003_fg` | DONE | SOURCE_RECONSTRUCTED | `3rd-gauge`; behavioral reconstruction with documented residuals; exact stock YFT ABI, exact AFI image, exact-GKI/verifier PASS |
| 5 | `conninfra` | SOURCE_NOW | FORWARD_PORT | root of all connectivity |
| 6 | `wmt_chrdev_wifi_connac2` | SOURCE_NOW | FORWARD_PORT | WLAN adaptor |
| 7 | `wlan_drv_gen4m_6878` | SOURCE_NOW | FORWARD_PORT | Wi-Fi |
| 8 | `bt_drv_6878` | SOURCE_NOW | FORWARD_PORT | Bluetooth |
| 9 | `gps_drv_dl_v051` | SOURCE_NOW | FORWARD_PORT | GNSS |
| 10 | `gps_pwr` | SOURCE_NOW | FORWARD_PORT | GNSS power (on-demand load path preserved) |
| 11 | `gps_scp` | SOURCE_NOW | FORWARD_PORT | GNSS SCP offload (on-demand load path preserved) |
| 12 | `fingerprint` | SOURCE_NOW | RE_REQUIRED | 10 export CRCs gate the sensor driver |

Plus the platform prerequisites named in the dependency graph:
`connadp`, `connscp`, `ccci_md_all`, `aee_aed`, `device-apc-common`,
`wlan_page_pool`, `mtk_panel_ext`, `mediatek_drm`, `charger_class`,
`mt6375-charger`, `spi-mt65xx`, `mtk-pwm`, `imgsensor`, `hf_manager`,
`cfg80211`, `bluetooth`, `mddp`, `pmic_lbat_service`, `ffa_v10` — all
`LIKELY_PLATFORM_MATCH` bulk forward-port work outside this triage set.

### B.4 Still `STOCK_TRANSITION` at Level B

| module | label | reason |
|---|---|---|
| `tkcore` | STOCK_TRANSITION | no source anywhere; `P0`; VERY_HIGH RE risk |
| `tkcore_drv` | STOCK_TRANSITION | same |
| `microarray_fp_tee` | STOCK_TRANSITION | TEE-mediated SPI; not observable from Linux |
| `yft_devinfo` | STOCK_TRANSITION | ABI pin, §B.2 |
| `spi_tiny_co5300_lcd` | STOCK_TRANSITION | rear display; `P3` |
| `hynitron` | STOCK_TRANSITION | rear touch; `P3` |
| `leds_ln2403` | STOCK_TRANSITION | camping light; `P3` |
| `yft_tiny2c_usb` | STOCK_TRANSITION | thermal camera; `P3` |
| `yft_gpio_keys` | STOCK_TRANSITION | `P3`; trivial to promote whenever wanted |

### Level B acceptance criteria

Display + backlight + 60/90/120 Hz mode switching · FT3680 touch · charging
including PD/PPS · both fuel gauges · audio through the AW883xx smart PA ·
Wi-Fi · Bluetooth · GNSS fix · cameras enumerate and stream · NFC · RGB
notification LED · flashlight. Fingerprint and the rear/mini display continue to
work off stock blobs.

---

## LEVEL C — SOURCE-COMPLETE TARGET

Everything we intend to replace from source. Promotes the Level-B holds:

| module | label at Level C | blocker to clear |
|---|---|---|
| `yft_gpio_keys` | SOURCE_NOW | none — `STRONG_SOURCE_MATCH` against exact-GKI `drivers/input/keyboard/gpio_keys.c`; rename + small delta |
| `leds_ln2403` | SOURCE_NOW | none technical — 0 exports, DT + sysfs ABI already fully recovered; clean-room rewrite |
| `yft_tiny2c_usb` | SOURCE_NOW | none technical — 0 exports, DT + sysfs ABI recovered; pair with the ThermoVue userspace work |
| `hynitron` | SOURCE_NOW | 65 functions incl. an embedded CST816D/CST816T firmware-update engine; must reproduce 2 export CRCs for `spi_tiny_co5300_lcd` |
| `spi_tiny_co5300_lcd` | SOURCE_NOW | 25 functions + the `TINY_LCM_IOC_*` misc-device ABI; needs `yft_devinfo` and `hynitron` settled first |
| `microarray_fp_tee` | SOURCE_NOW | requires a TEE-side oracle; only attempt after `tkcore` is understood |
| `yft_devinfo` | SOURCE_NOW | **the 73-character vendor enum type text.** 409 061 884 semantically plausible spellings and 56 495 harvested real enum definitions were already excluded by exhaustion. Only a YFT/Ulefone BSP drop containing `yft_devinfo.h` can close it. |
| `tkcore` | SOURCE_NOW *(aspirational)* | complete TEE client core RE; 25-symbol ABI; VERY_HIGH |
| `tkcore_drv` | SOURCE_NOW *(aspirational)* | SMC/FF-A transport RE; VERY_HIGH |
| `uarthub_drv` | **NOT_REQUIRED** | disabled in DT on this board |

Level C is explicitly **not** a precondition for anything. Two entries
(`tkcore`, `tkcore_drv`) may reasonably remain stock indefinitely: they are
`P0_BOOT_CRITICAL`, have no source anywhere, are ABI-safe as blobs, and a
mistake there costs the device its ability to unlock encrypted `/data`.

---

## Label summary

| level | SOURCE_NOW | STOCK_TRANSITION | NOT_REQUIRED |
|---|---:|---:|---:|
| **A — first boot** | 1 (the GKI core) | 439 stock modules | `odm_dlkm` modules, `uarthub_drv` |
| **B — usable phone** | 19 frozen + 11 new = 30, plus platform prereqs | 9 | `uarthub_drv` |
| **C — source-complete** | all except the two TEE modules if they are held | 0-2 | `uarthub_drv` |

## Answer to the driving question

> **What can we boot now without finishing every obscure module?**

**Everything.** Level A needs a single new artefact — the source-built exact GKI
core — and zero reconstructed vendor modules. The full stock vendor stack loads
against it because all 2 946 kernel-facing CRCs and all 23 unresolved modules'
imports are proven `MATCH` with zero unresolved symbols.

The correct sequencing is therefore: **boot first and validate the source
stack incrementally**. `fingerprint` is now the sole genuine RE target;
`custom_ldo_wl2868` and `custom_ldo` are both source-ready. Remaining Level-B
work is forward-port or exact-provider-ABI work, not WL2868 reverse engineering.

---

## Safety

Static/read-only analysis only. No flashing, slot switch, boot-control change,
`insmod`/`rmmod`, bind/unbind, sysfs write, GPIO change, I2C write, charging
test, panel command, light enable, or calibration/NVRAM/DT/DTBO modification was
performed in producing this plan.
