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
| `tkcore` | KeyMint 3.0 + Gatekeeper + Widevine + FBE unlock | `YES_SAFE_TRANSITION`; source island static-complete through Phase 3E (122/122, 25/25), but **stock runtime retained pending Phase 3F and runtime validation** |
| `tkcore_drv` | TEE transport for the above | `SOURCE_NOW_WITH_PROVIDER_WITNESSES` — **SOURCE_RECONSTRUCTED / FROZEN FOR RE**; still needs stock `tkcore` at runtime; `ffa_v10` is now source-closed too (`DIRECT_SOURCE_MATCH`) |
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
| `fingerprint` | SOURCE_NOW | `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; FROZEN FOR RE; 16/16 function bytes/sizes/KCFI, 18/18 MODVERSIONs, 10/10 export CRCs, four exact MicroArray consumer edges, 39/39 verifier |
| `yft_gpio_keys` | SOURCE_NOW | `SOURCE_DELTA_RECONSTRUCTION_EXACT`; FROZEN FOR RE; exact GPIO13/F1 and GPIO8/F2 contracts, 23/23 function bytes, 65/65 CRCs, 40/40 verifier |

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
| 2 | `leds_ln2403` | DONE | SOURCE_RECONSTRUCTED | full stock hardware/sysfs state machines; exact source-built MTK PWM provider edges; 32/32 CRCs and 50/50 verifier; FROZEN FOR RE |
| 4 | `sh366003_fg` | DONE | SOURCE_RECONSTRUCTED | `3rd-gauge`; behavioral reconstruction with documented residuals; exact stock YFT ABI, exact AFI image, exact-GKI/verifier PASS |
| 5 | `conninfra` | SOURCE_NOW | FORWARD_PORT | root of all connectivity |
| 6 | `wmt_chrdev_wifi_connac2` | SOURCE_NOW | FORWARD_PORT | WLAN adaptor |
| 7 | `wlan_drv_gen4m_6878` | SOURCE_NOW | FORWARD_PORT | Wi-Fi |
| 8 | `bt_drv_6878` | SOURCE_NOW | FORWARD_PORT | Bluetooth |
| 9 | `gps_drv_dl_v051` | SOURCE_NOW | FORWARD_PORT | GNSS |
| 10 | `gps_pwr` | SOURCE_NOW | FORWARD_PORT | GNSS power (on-demand load path preserved) |
| 11 | `gps_scp` | SOURCE_NOW | FORWARD_PORT | GNSS SCP offload (on-demand load path preserved) |

Plus the platform prerequisites named in the dependency graph:
`connadp`, `connscp`, `ccci_md_all`, `aee_aed`, `device-apc-common`,
`wlan_page_pool`, `mtk_panel_ext`, `mediatek_drm`, `charger_class`,
`mt6375-charger`, `mtk-pwm`, `imgsensor`, `hf_manager`,
`cfg80211`, `bluetooth`, `mddp`, `pmic_lbat_service` — all
`LIKELY_PLATFORM_MATCH` bulk forward-port work outside this triage set.
`ffa_v10` is no longer in that bucket: it closed as `DIRECT_SOURCE_MATCH /
FROZEN FOR RE` (kernel/phase4-ffa-v10-reconstruction.md), all 5 export CRCs
natural, 34/34 functions byte-identical to stock. `spi-mt65xx` likewise closed
as `DIRECT_SOURCE_MATCH / FROZEN FOR RE`: 31/31 function bytes, all 3 exports
natural, 82/82 verifier, and its MicroArray consumer accepted.

### B.4 Level-B retained binaries and source status

This table separates source status from deployment policy. `tkcore` and
`yft_devinfo` remain genuine stock-provider dependencies. Every row explicitly
marked reconstructed/frozen is source-closed; retaining its stock binary for a
conservative staged Level-B boot is optional integration policy, not an
unresolved reconstruction.

| module | label | reason |
|---|---|---|
| `tkcore` | STOCK_TRANSITION | `P0`; source island **static-complete through Phase 3E** (122/122 function set, 0 missing, 54 byte-identical, **25/25 exports** retained, 0 island-only). **NOT RUNTIME VALIDATED; final three-consumer acceptance pending; stock runtime provider retained; replacement not claimed.** Private-type genksyms CRC provenance remains separate from behavioral completeness |
| `tkcore_drv` | **SOURCE_RECONSTRUCTED / FROZEN FOR RE** | closed 2026-09-13 with `SOURCE_NOW_WITH_PROVIDER_WITNESSES` (now 8 NATURAL/5 STOCK_PROVIDER_WITNESS after the `ffa_v10` closure); still runs against stock `tkcore` |
| `ffa_v10` | **DIRECT_SOURCE_MATCH / FROZEN FOR RE** | closed 2026-09-13; exact MediaTek vendor source, 34/34 byte-identical, 5/5 export CRCs natural, 49/49 verifier |
| `tmem_ffa` | **DIRECT_SOURCE_MATCH / FROZEN FOR RE** | closed 2026-09-13; same pinned vendor revision/directory as `ffa_v10`; 141/141 byte-identical, 15/15 export CRCs natural, 76/76 verifier; its 9 `KREE_*` edges are now **source-built natural** against the closed `gz_tz_system`; only the 7 `TEEC_*` (stock `tkcore`) edges remain stock-runtime |
| `gz_tz_system` | **SOURCE_DELTA_RECONSTRUCTION_EXACT / FROZEN FOR RE** | closed 2026-09-13; same pinned vendor revision (`device_modules@957dac18`, `geniezone/`); 61/61 byte-identical, 27/27 export CRCs natural, 35/35 consumer edges natural, 120/120 verifier; witness-free acceptance against source-built IPC/Trusty is 7/7 natural and behavior-identical |
| `gz_ipc_mod` | **DIRECT_SOURCE_MATCH / FROZEN FOR RE** | closed 2026-09-13 from exact pinned `trusty-ipc.c`; 43/43 byte/KCFI, 15/15 natural exports, 6/6 consumer edges, 269/269 verifier; uses 3 natural `gz_trusty_mod` edges |
| `gz_trusty_mod` | **DIRECT_SOURCE_MATCH / FROZEN FOR RE** | closed 2026-09-13 from exact pinned `trusty.c + smcnr-table.c`; 33/33 byte/KCFI, 14/14 natural exports, 34/34 consumer edges, 239/239 verifier; lowest GenieZone transport provider |
| `gz_main_mod` | SOURCE/FROZEN | GenieZone main driver, owns the higher-level **KREE userspace** ABI (`/dev/gz_kree`, `/dev/gz_ffa_dev`); largest `gz_tz_system` consumer (15 symbols); separate from `gz_ipc_mod`'s lower TIPC transport cdev. **DIRECT_SOURCE_MATCH / FROZEN FOR RE**: 42/42 byte-identical, zero source delta, 0 exports and 0 kernel consumers, 75/76 provider edges natural (the one exception is a declared stock `mtk_sec_heap` edge) |
| `microarray_fp_tee` | **SOURCE_RECONSTRUCTED / FROZEN FOR RE** | behavior frozen; 65 natural ABI edges after real source-built SPI provider; still uses stock runtime tkcore |
| `yft_devinfo` | STOCK_TRANSITION | ABI pin, §B.2 |
| `spi_tiny_co5300_lcd` | **SOURCE_RECONSTRUCTED / FROZEN FOR RE** | rear display; exact rebuilt-Hynitron plus stock-YFT provider ABI; 30/30 verifier; `P3` |
| `hynitron` | **SOURCE_RECONSTRUCTED / FROZEN FOR RE** | rear touch; stock `yft_devinfo` provider ABI pinned; `P3` |

### Level B acceptance criteria

Display + backlight + 60/90/120 Hz mode switching · FT3680 touch · charging
including PD/PPS · both fuel gauges · audio through the AW883xx smart PA ·
Wi-Fi · Bluetooth · GNSS fix · cameras enumerate and stream · NFC · RGB
notification LED · flashlight. Fingerprint uses source-built `fingerprint` +
source-built `microarray_fp_tee` + source-built `spi-mt65xx`, with stock runtime
`tkcore` retained. This is not a source-pure full stack because `tkcore` is not
reconstructed. The rear/mini display and rear touch are source-reconstructed;
stock `yft_devinfo` remains their pinned registry ABI provider.

---

## LEVEL C — SOURCE-COMPLETE TARGET

Everything we intend to replace from source. Promotes the Level-B holds:

| module | label at Level C | blocker to clear |
|---|---|---|
| `yft_gpio_keys` | SOURCE_NOW | **closed** — `SOURCE_DELTA_RECONSTRUCTION_EXACT`, FROZEN FOR RE; pinned donor plus proven identity/default-debounce/IRQ/logging delta |
| `leds_ln2403` | SOURCE_NOW | **closed** — `NO_PUBLIC_SOURCE_FOUND / STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; exact hardware/sysfs/timer behavior, exact provider edges, clean exact-GKI build, 50/50 verifier, FROZEN FOR RE |
| `yft_tiny2c_usb` | SOURCE_NOW | **closed** — `NO_PUBLIC_DONOR_FOUND / STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; exact 22-symbol/23-MODVERSION ABI, exact MT6375 flag edge, full thermal/USB/uSmart/DT/GPIO/sysfs/lifecycle contracts, clean exact-GKI build, 68/68 verifier, FROZEN FOR RE |
| `hynitron` | SOURCE_NOW | **closed** — `STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; fitted CST820, exact 65-function/54-import set, exact two export CRCs accepted by stock `spi_tiny_co5300_lcd`, exact images/negative programmer proof, clean build, 34/34 verifier, FROZEN FOR RE |
| `spi_tiny_co5300_lcd` | SOURCE_NOW | **closed** — `NO_PUBLIC_SOURCE_FOUND / STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE`; exact 25-function/58-MODVERSION sets, exact CO5300 table/image/ABI/state machine, clean exact-GKI build, 30/30 verifier, FROZEN FOR RE |
| `microarray_fp_tee` | **SOURCE_NOW / FROZEN FOR RE** | **closed** — behavioral reconstruction complete; 27/27 functions, 66/66 MODVERSIONs; two SPI edges natural. Phase 3F: its single `tee_spi_transfer` edge is now satisfied by the final source provider with the exact historical CRC `0x184ce7da` (`NATURAL_HISTORICAL_STOCK_CRC`), so the former stock-runtime tkcore witness is gone; the stock binary also remains ABI-compatible |
| `yft_devinfo` | SOURCE_NOW | **the 73-character vendor enum type text.** 409 061 884 semantically plausible spellings and 56 495 harvested real enum definitions were already excluded by exhaustion. Only a YFT/Ulefone BSP drop containing `yft_devinfo.h` can close it. |
| `tkcore` | **SOURCE ISLAND STATICALLY COMPLETE / NOT YET DEPLOYABLE** | Phase 3E proves 122/122 functions, 25/25 exports and exact internal callgraph; **Phase 3F final three-consumer static acceptance complete** (19/19 edges, 5 natural-historical + 14 island-natural, 0 blocked, 0 stock-tkcore witnesses). Stock no longer statically required by the source island; runtime deployment pending separately authorized validation. Historical 14/25-vs-11/25 private-type CRC provenance is not a behavioral coverage gap |
| `tkcore_drv` | **DONE — SOURCE_RECONSTRUCTED / FROZEN FOR RE** | SMC/FF-A transport RE completed 2026-09-13; 8 NATURAL/5 STOCK_PROVIDER_WITNESS, 43/43 verifier; `phase4-tkcore-drv-reconstruction.md` |
| `ffa_v10` | **DONE — DIRECT_SOURCE_MATCH / FROZEN FOR RE** | FF-A transport RE completed 2026-09-13; exact vendor source, 34/34 byte-identical, 5/5 export CRCs natural, 49/49 verifier; `phase4-ffa-v10-reconstruction.md` |
| `uarthub_drv` | **NOT_REQUIRED** | disabled in DT on this board |

Level C is explicitly **not** a precondition for anything. `tkcore` no longer
has an open static function-reconstruction gap: Phase 3E reaches 122/122 with
25/25 exports. It remains the one unresolved **deployment/runtime acceptance**
question because it is `P0_BOOT_CRITICAL`; a mistake there costs the device its
ability to unlock encrypted `/data`, so stock remains appropriate until Phase
3F consumer acceptance and separately authorized runtime validation. `tkcore_drv` and `ffa_v10` are **no longer** in that
category: both are source-reconstructed and `FROZEN FOR RE` (2026-09-13).

Do not conflate this with the Level-A **boot strategy** above, which
intentionally keeps every vendor_boot/vendor_dlkm/system_dlkm module
(including the now-source-closed `tkcore_drv` and `ffa_v10`) on their stock
binaries for the *first* boot regardless of reconstruction status — that is a
minimal-change-set decision for bring-up risk, not a claim about what has or
has not been source-reconstructed. Level C tracks the latter.

---

## Label summary

| level | source status | runtime/deployment stock policy | NOT_REQUIRED |
|---|---|---|---|
| **A — first boot** | 1 (the GKI core) | all 439 stock modules deliberately retained for minimum risk | `odm_dlkm` modules, `uarthub_drv` |
| **B — usable phone** | frozen/source-closed modules may be introduced incrementally | `tkcore` remains a stock runtime provider pending Phase 3F/runtime validation; `yft_devinfo` remains ABI-pinned; other stock retention is optional staging | `uarthub_drv` |
| **C — source-complete** | every currently source-closed module, including statically complete `tkcore` and `microarray_fp_tee` | `tkcore` deployment awaits consumer/runtime acceptance; `yft_devinfo` remains a separate ABI-pinned provider | `uarthub_drv` |

## Answer to the driving question

> **What can we boot now without finishing every obscure module?**

**Everything.** Level A needs a single new artefact — the source-built exact GKI
core — and zero reconstructed vendor modules. The full stock vendor stack loads
against it because all 2 946 kernel-facing CRCs and all 23 unresolved modules'
imports are proven `MATCH` with zero unresolved symbols.

The correct sequencing is therefore: **boot first and validate the source
stack incrementally**. `fingerprint`, `spi-mt65xx`, `microarray_fp_tee`,
`custom_ldo_wl2868`, and `custom_ldo` are source-ready and frozen for RE.
MicroArray behavior is closed; `tkcore` alone remains its stock TEE runtime
dependency. Other Level-B work is forward-port or exact-provider-ABI work.

---

## Safety

Static/read-only analysis only. No flashing, slot switch, boot-control change,
`insmod`/`rmmod`, bind/unbind, sysfs write, GPIO change, I2C write, charging
test, panel command, light enable, or calibration/NVRAM/DT/DTBO modification was
performed in producing this plan.

## extcon-mtk-usb (Phase 4 closure)

`extcon-mtk-usb` is source-closed and shippable: SOURCE_DELTA_RECONSTRUCTION_EXACT,
FROZEN FOR RE, 22/22 functions, 63/63 imports, 64/64 MODVERSION CRCs, 4/4 kCFI,
85/85 verifier. It is the owner of the uSmart accessory path (GPIO 28 detect,
GPIO 55 UVC/USB switch, GPIO 152 accessory VBUS, GPIO 37 Type-C OTG companion)
and of the `yft_usb_flag` read gate. Replacement is drop-in: ship the module as
`extcon-mtk-usb.ko` (hyphen filename, as `modules.dep` expects) while `.modinfo`
keeps `name=extcon_mtk_usb`, exactly as stock. Providers stay stock-compatible —
the reconstruction carries stock `tcpc_class` and `mt6375-charger` CRCs.
Detail: `kernel/phase4-extcon-mtk-usb-reconstruction.md`.

---

## CURRENT — TrustKernel Phase 3G-R (2026-09-15)

- **PHASE 3F:** STATIC PASS.
- **PHASE 3G:** FAILED BEFORE G1.
- **RUNTIME TRUSTKERNEL:** NOT YET TESTED.
- **PREVIOUS PHASE-3G CANDIDATE:** RETIRED — INVALID STATIC DEPLOYMENT UNIT.
- **PHASE 3G-R C0:** LOCAL TOP-LEVEL VBMETA BOOT CONTROL FAILED with stock payloads; C1 was not attempted.
- **DEVICE:** stock `vbmeta_b` restored exact; A active/bootable/successful; B bootable/not-successful.

The Phase-3G failure must not be attributed to source `tkcore` runtime. Current blocker: `kernel/phase4-tkcore-island-phase3g-r-c0-blocker.md`.
