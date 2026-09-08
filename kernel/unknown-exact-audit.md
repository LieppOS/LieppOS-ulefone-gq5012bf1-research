# UNKNOWN exact-source reconnaissance

- stock UNKNOWN binaries: 22
- method: exact module/chip/alias/compatible/export searches only
- no fuzzy candidate ranking is used

> ## CURRENT-RESOLUTION NOTE (Phase 4 remaining-module triage)
>
> The per-module sections below are the **original** exact-evidence scan and are
> preserved verbatim as historical evidence. Several of their verdicts are now
> stale. The authoritative current status for every still-unresolved module is:
>
> * `kernel/phase4-remaining-module-triage.md` (narrative + summary tables)
> * `kernel/phase4-remaining-module-triage.tsv` (machine-readable, 37 columns)
> * `kernel/phase4-remaining-module-dependency-graph.md`
> * `kernel/phase4-slot-b-minimum-source-stack.md`
>
> Stale-verdict corrections established by that triage:
>
> | module | this file says | current status |
> |---|---|---|
> | `conninfra` | `STRONG_API_HIT` | **EXACT_SOURCE / FORWARD_PORT** — bazel target `//…/connectivity/conninfra:conninfra` with an explicit MT6878 object set (`Kbuild:424-436`) |
> | `wmt_chrdev_wifi_connac2` | `STRONG_API_HIT` | **EXACT_SOURCE / FORWARD_PORT** — `//…/wlan/adaptor/build/connac2x:wmt_chrdev_wifi_connac2` |
> | `wlan_drv_gen4m_6878` | `RELATED_SOURCE_HIT` | **EXACT_SOURCE / FORWARD_PORT** — `//…/wlan/core/gen4m/build/connac2x/6878:wlan_drv_gen4m_6878`; `Kbuild:26-27` selects `Kbuild.6878` |
> | `bt_drv_6878` | `STRONG_API_HIT` | **EXACT_SOURCE / FORWARD_PORT** — `//…/bt/mt66xx:btif` emits `bt_drv_6878.ko`; `btif/Kbuild:142 MODULE_NAME := bt_drv_$(BT_PLATFORM)` |
> | `gps_drv_dl_v051` | `RELATED_SOURCE_HIT` (1 hit) | **EXACT_SOURCE / FORWARD_PORT** — `//…/gps/data_link/plat/v051:gps_drv_dl_v051`, Kbuild comment `# For MT6878 SoC + MT6686 A-die` |
> | `gps_pwr` / `gps_scp` | `RELATED_SOURCE_HIT` | **EXACT_SOURCE / FORWARD_PORT** — `define_mgk_ko(name = "gps_pwr" / "gps_scp")` |
> | `fingerprint` | `RELATED_SOURCE_HIT`, 97 hits | **NO_USEFUL_SOURCE / RE_REQUIRED** — the 97 hits are netfilter-OSF / x509 / unrelated-DTS noise and are rejected. Real identifier is `mediatek,yft_finger`; the module is 16 functions of YFT pinctrl/GPIO glue. |
> | `tkcore` | `STRONG_API_HIT`, 60 hits | **NO_USEFUL_SOURCE / STOCK_TRANSITION_BLOB** — the 60 hits are GlobalPlatform `TEEC_*` API-name collisions with MicroTrust TEEI (`drivers/tee/teei/510/…`). `grep -rl 'trustkernel\|tkcore'` over the Nothing MT6878 trees and the MiCode vendor-reference BSPs returns **zero** files. |
> | `panel_ky_vtdr6115_dphy_cmd` | `NO_EXACT_HIT` | **STRUCTURAL_DONOR_ONLY / RE_REQUIRED** — donor located: `MotorolaMobilityLLC/kernel-mtk@0087a407394abd3ab073e1a2df164f1187959a3f` `dsi-panel-mot-csot-vtdr6115-655-fhdp-dphy-vdo-144hz.c` (CSOT 144 Hz VDO vs Ulefone KY 120 Hz cmd) |
> | `custom_ldo_wl2868` | `NO_EXACT_HIT` | **STRUCTURAL_DONOR_ONLY / RE_REQUIRED** — donor located: `sonyxperiadev/kernel@7e42db1690b55e374fd6a6af536684a746bac614` `drivers/regulator/wl2868c-regulator.{c,h}` (regulator-framework model; stock is a chardev+export model). Nothing ships only `cust_wl2864c.dtsi`; the `wl2864c.ko` target in `mgk_64_k61.bzl` has **no** source in the published tree. |
> | `custom_ldo` | `NO_EXACT_HIT` | no donor found, but **STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION** completed from stock ELF: 2/2 functions byte-identical, exact CRC/KCFI/relocations, exact-GKI build clean |
> | `sc851x_charger`, `sh366003_fg`, `leds_ln2403`, `tkcore_drv` | `NO_EXACT_HIT` | unchanged — **NO_USEFUL_SOURCE** re-confirmed against the Nothing trees, the MiCode vendor-reference BSPs and public source indexes |
>
> Modules resolved since this scan and therefore no longer unresolved:
> `aw883xx_driver`, `aw36515`, `aw36518`, `aw36518_v2`, `leds_rgb_aw2013`,
> `connfem`, `custom_ldo`.
>
> Modules **missing** from this 22-entry scan that the triage proved are also
> still unresolved: `sc8571_charger`, `microarray_fp_tee`, `spi_tiny_co5300_lcd`,
> `hynitron`, `yft_gpio_keys`, `yft_tiny2c_usb`, `yft_devinfo`.
>
> Transition-blob result applying to **all** of them: every one imports 0
> unresolved and 0 CRC-mismatched kernel symbols against the exact Google GKI
> `vmlinux.symvers` for `ab/12901745`.

## tkcore

- locations: `vendor_boot_platform`
- result: **STRONG_API_HIT**
- evidence kinds: `EXPORT`
- exact hit records: 60
- description: `TrustKernel TKCore TEEC v1.0`
- aliases: ``

- `EXPORT` `TEEC_InitializeContext` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:22
- `EXPORT` `TEEC_FinalizeContext` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:32
- `EXPORT` `TEEC_OpenSession` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:49
- `EXPORT` `TEEC_RegisterSharedMemory` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:60
- `EXPORT` `TEEC_InvokeCommand` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:73
- `EXPORT` `TEEC_ReleaseSharedMemory` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:80
- `EXPORT` `TEEC_CloseSession` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:82
- `EXPORT` `TEEC_OpenSession` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:102
- `EXPORT` `TEEC_AllocateSharedMemory` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:111
- `EXPORT` `TEEC_InvokeCommand` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:130
- `EXPORT` `TEEC_ReleaseSharedMemory` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:140
- `EXPORT` `TEEC_CloseSession` → `device_modules:drivers/tee/teei/510/tz_driver/teei_client_transfer_data.c:142
- `EXPORT` `TEEC_OpenSession` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:238
- `EXPORT` `TEEC_InvokeCommand` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:261
- `EXPORT` `TEEC_InitializeContext` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:293
- `EXPORT` `TEEC_CloseSession` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:346
- `EXPORT` `TEEC_CloseSession` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:439
- `EXPORT` `TEEC_FinalizeContext` → `device_modules:drivers/tee/teei/510/tz_driver/sysfs.c:647
- `EXPORT` `TEEC_InvokeCommand` → `device_modules:drivers/tee/teei/510/tz_dcih/tz_dcih.c:51
- `EXPORT` `TEEC_InvokeCommand` → `device_modules:drivers/tee/teei/510/tz_dcih/tz_dcih.c:81
- ... 40 more exact-hit records in CSV

## panel_ky_vtdr6115_dphy_cmd

- locations: `vendor_boot_platform`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `vtdr6115 VDO 120HZ AMOLED Panel Driver`
- aliases: `of:N*T*Chx,vtdr6115,cmd,120hz,ky;of:N*T*Chx,vtdr6115,cmd,120hz,kyC*`

- No exact source hit found.

## leds_ln2403

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `Module For PWM LN2403`
- aliases: `of:N*T*Cmediatek,yft_camplight;of:N*T*Cmediatek,yft_camplightC*`

- No exact source hit found.

## aw883xx_driver

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `ASoC AW883XX Smart PA Driver`
- aliases: ``

- No exact source hit found.

## bt_drv_6878

- locations: `vendor_dlkm`
- result: **STRONG_API_HIT**
- evidence kinds: `EXPORT`
- exact hit records: 8
- description: `Mediatek Bluetooth Driver`
- aliases: ``

- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/wlan/core/gen4m/mgmt/rlm_domain.c:2804
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/wlan/core/gen4-mt79xx/mgmt/rlm_domain.c:2181
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/mt66xx/include/btmtk_main.h:689
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/linux_v2/include/btmtk_main.h:971
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/linux_v2/btmtk_main.c:4191
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/linux_v2/btmtk_main.c:4217
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/mt66xx/btmtk_main.c:3241
- `EXPORT` `btmtk_set_country_code_from_wifi` → `kernel_modules:connectivity/bt/mt66xx/btmtk_main.c:3265

## sh366003_fg

- locations: `vendor_boot_platform`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `SH SH366003 Gauge Driver`
- aliases: `of:N*T*Csh,sh366003;of:N*T*Csh,sh366003C*;i2c:sh366003`

- No exact source hit found.

## connfem

- locations: `vendor_dlkm`
- result: **STRONG_API_HIT**
- evidence kinds: `EXPORT;MODULE_NAME`
- exact hit records: 135
- description: `Connsys FEM (Front-End-Module) Driver`
- aliases: ``

- `MODULE_NAME` `connfem` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:21
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6897_connfem.dtsi:6
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6878_connfem.dtsi:6
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/tb8796p1_64_sp.dts:302
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/tb8796p1_64_sp.dts:546
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_k6989_connfem.dtsi:5
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/tb8792p1_64_sp.dts:34
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/tb8792p1_64_sp.dts:359
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_k6985_connfem.dtsi:5
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_k6897_connfem.dtsi:5
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_k6886_connfem.dtsi:5
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_k6878_connfem.dtsi:5
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6989_connfem.dtsi:6
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/mt6989.dts:2072
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/mt6989.dts:2073
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/mt6989.dts:18425
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_connfem.dtsi:6
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/k6989v1_64.dts:341
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/k6989v1_64.dts:619
- `MODULE_NAME` `connfem` → `device_modules:arch/arm64/boot/dts/mediatek/mt6985.dts:13142
- ... 115 more exact-hit records in CSV

## aw36518

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `Awinic AW36518 LED flash driver`
- aliases: `i2c:aw36518;of:N*T*Cmediatek,aw36518;of:N*T*Cmediatek,aw36518C*`

- No exact source hit found.
- **Resolved by reconstruction** (Phase 4): the MediaTek V4L2 `aw36518.c` in the
  Motorola `kernel-mtk` tree is the structural donor; the LieppOS
  reconstruction is ABI-exact against the stock oracle. See
  `kernel/phase4-aw36518-reconstruction.md`.

## gps_scp

- locations: `vendor_dlkm`
- result: **RELATED_SOURCE_HIT**
- evidence kinds: `MODULE_NAME`
- exact hit records: 9
- description: `GPS2SCP stp dev`
- aliases: ``

- `MODULE_NAME` `gps_scp` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:31
- `MODULE_NAME` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/Kbuild:43
- `MODULE_NAME` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/Kbuild:50
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/init.gps_scp.rc
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/gps2scp.c
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/Makefile
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/Kbuild
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/BUILD.bazel
- `MODULE_NAME;PATH` `gps_scp` → `kernel_modules:connectivity/gps/gps_scp/Android.mk

## aw36515

- **Resolved by reconstruction** (Phase 4): reverse-engineered with its own
  mandatory RED against the public MediaTek donor
  `MotorolaMobilityLLC/kernel-mtk@ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de`
  `drivers/misc/mediatek/flashlight/v4l2/aw36515.c`, then rebuilt against exact
  GKI `ab/12901745`.  Result `SOURCE_DELTA_RECONSTRUCTION_EXACT`: 23/23
  functions, 23/23 size-identical, 22/23 byte-identical, 46/46 imports, 47/47
  identical MODVERSION CRCs.  See `kernel/phase4-aw36515-reconstruction.md`,
  `kernel/phase4-aw36515-RED.md` and `kernel/phase4-aw36515-delta-ledger.tsv`.
  The `cust_mt6985_alpha_camera_v4l2.dtsi` hits below are the original
  Phase-2/3 classifier evidence and are kept for the record; the GQ5012BF1 DT
  contract actually in force is `kernel/phase4-aw36515-dt-contract.md`.

- locations: `vendor_dlkm`
- result: **STRONG_HARDWARE_HIT**
- evidence kinds: `ALIAS;CHIP_TOKEN;COMPATIBLE;MODULE_NAME`
- exact hit records: 9
- description: `Awinic AW36515 LED flash driver`
- aliases: `i2c:aw36515;of:N*T*Cmediatek,aw36515;of:N*T*Cmediatek,aw36515C*`

- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:7
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:10
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:18
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:504
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:505
- `COMPATIBLE` `mediatek,aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:505
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:509
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:510
- `ALIAS;CHIP_TOKEN;MODULE_NAME` `aw36515` → `device_modules:arch/arm64/boot/dts/mediatek/cust_mt6985_alpha_camera_v4l2.dtsi:511

## leds_rgb_aw2013

- locations: `vendor_boot_platform`
- result: **RESOLVED — DIRECT_SOURCE_VARIANT / SOURCE_DELTA_RECONSTRUCTION_EXACT**
  (superseding the original `RELATED_SOURCE_HIT`)
- evidence kinds: `CHIP_TOKEN` (original scan) + `MODULE_AUTHOR`, `STRING_SET`,
  `STRUCT_LAYOUT`, `KCFI_TYPEID` (Phase 4)
- exact hit records: 47
- description: `AW2013 LED driver`
- aliases: `of:N*T*Cawinic,rgb,aw2013;of:N*T*Cawinic,rgb,aw2013C*`

### Phase 4 resolution

The original scan flagged this only as a chip-token hit. The decisive evidence
is the module author: `Nikita Travkin <nikitos.tr@gmail.com>` with
`license=GPL v2` — i.e. the **upstream mainline Linux** driver
`drivers/leds/leds-aw2013.c`, *not* an Awinic vendor driver (contrast the
Awinic parts on the same board, which carry `Alec <like@awinic.com>`).

Donor: `common/drivers/leds/leds-aw2013.c` at exact GKI
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`,
sha256 `8458f2aac83ccb6d996f88895b5e9ce953d3475019405ad869bde06a3c361b17`.
Every upstream diagnostic string is present verbatim in the stock binary; the
regmap config and the whole `struct i2c_driver` are byte-identical to an
untouched donor build; `aw2013_blink_set` is size-identical (492 B).

Ulefone/YFT delta (19 items, fully enumerated in
`phase4-leds-rgb-aw2013-delta-ledger.tsv`): identity rename
(`leds-rgb-aw2013`, `awinic,rgb,aw2013`), the `vcc` regulator replaced by the
`aw2013-pwd-gpio` chip-enable GPIO, a `led-fixed-brightness` per-channel
brightness clamp, and two new functions `led_aw2103_get_boot_mode()` /
`led_aw2103_control()` implementing a MediaTek power-off-charging battery
indicator.

Reconstruction is byte-identical to stock in every content-bearing section
(8/8 functions, 170/170 relocations, 27/27 MODVERSION CRCs, 0 exports); only
the `.modinfo` vermagic SCM stamp differs.

See `phase4-leds-rgb-aw2013-reconstruction.md` (authoritative),
`phase4-leds-rgb-aw2013-RED.md`, `-stock-oracle.txt`, `-hardware-contract.md`,
`-dt-contract.md`, `-userspace-contract.md`, `-register-map.tsv`.

- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:54
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:56
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:57
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:63
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:67
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:73
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:100
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:119
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:134
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:136
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:141
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:152
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:155
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:160
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:161
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:186
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:187
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:195
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:198
- `CHIP_TOKEN` `aw2013` → `kernel:drivers/leds/leds-aw2013.c:210
- ... 27 more exact-hit records in CSV

## custom_ldo

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `Custom Ldo Driver`
- aliases: ``

- No exact source hit found.

### Phase 4 reconstruction follow-up (2026-09-08)

The source-search result remains historically correct: no donor was found.
Nevertheless, binary-led reconstruction is now complete at
`STOCK_CONSUMER_ABI_EXACT_RECONSTRUCTION`. Both stock functions were recovered
byte-identically (28 bytes each); prototypes, KCFI, all three import CRCs, both
export CRCs, and all 10 relocations match. Exact-GKI `BUILD_RC=0`, unresolved
symbols 0. Authoritative report: `phase4-custom-ldo-reconstruction.md`.

## gps_drv_dl_v051

- locations: `vendor_dlkm`
- result: **RELATED_SOURCE_HIT**
- evidence kinds: `MODULE_NAME`
- exact hit records: 1
- description: `GPS FW log driver`
- aliases: ``

- `MODULE_NAME` `gps_drv_dl_v051` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:27

## gps_pwr

- locations: `vendor_dlkm`
- result: **RELATED_SOURCE_HIT**
- evidence kinds: `MODULE_NAME`
- exact hit records: 67
- description: `GPS_PWR dev`
- aliases: ``

- `MODULE_NAME` `gps_pwr` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:30
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:36
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:41
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:53
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:57
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:59
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:64
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:65
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:74
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:81
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:83
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:88
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:92
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:103
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:107
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:113
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:117
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:123
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:135
- `MODULE_NAME` `gps_pwr` → `kernel_modules:connectivity/gps/gps_pwr/gpspwr.c:142
- ... 47 more exact-hit records in CSV

## wmt_chrdev_wifi_connac2

- locations: `vendor_dlkm`
- result: **STRONG_API_HIT**
- evidence kinds: `CHIP_TOKEN;EXPORT;MODULE_NAME`
- exact hit records: 150
- description: ``
- aliases: ``

- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/usb.c:105
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/usb.c:131
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c:32
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c:78
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c:29
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c:44
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/pci_mac.c:44
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:23
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:34
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:66
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:174
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:188
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:208
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:231
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:242
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:251
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:253
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:287
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:292
- `CHIP_TOKEN` `connac2` → `kernel:drivers/net/wireless/mediatek/mt76/mt7921/mcu.c:366
- ... 130 more exact-hit records in CSV

## sc851x_charger

- locations: `vendor_boot_platform`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `SC SC851X Driver`
- aliases: ``

- No exact source hit found.

## tkcore_drv

- locations: `vendor_boot_platform`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `TrustKernel TKCore TZ driver`
- aliases: ``

- No exact source hit found.

## aw36518_v2

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `Awinic AW36518_V2 LED flash driver`
- aliases: `i2c:aw36518_v2;of:N*T*Cmediatek,aw36518_v2;of:N*T*Cmediatek,aw36518_v2C*`
- **Resolved by reconstruction** (Phase 4): proved to be the same vendor source
  as `aw36518` with the name token changed and the `is_yft_cts_board()` CTS skip
  compiled out (19/23 functions byte-identical between the two stock modules,
  identical string multiset after normalisation, one import less).  The LieppOS
  reconstruction is ABI-exact against the V2 oracle; see
  `kernel/phase4-aw36518-v2-reconstruction.md` and
  `kernel/phase4-aw36518-v2-delta-ledger.tsv`.

- No exact source hit found.

## custom_ldo_wl2868

- locations: `vendor_dlkm`
- result: **NO_EXACT_HIT**
- evidence kinds: ``
- exact hit records: 0
- description: `WL2864 & WL2868 Power IC Driver`
- aliases: ``

- No exact source hit found.

## conninfra

- locations: `vendor_dlkm`
- result: **STRONG_API_HIT**
- evidence kinds: `EXPORT;MODULE_NAME`
- exact hit records: 392
- description: ``
- aliases: ``

- `MODULE_NAME` `conninfra` → `kernel:drivers/net/wireless/mediatek/mt76/mt7915/soc.c:287
- `MODULE_NAME` `conninfra` → `kernel:drivers/net/wireless/mediatek/mt76/mt7915/soc.c:301
- `MODULE_NAME` `conninfra` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:22
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6989.dts:9174
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6989.dts:9175
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6985.dts:7559
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6985.dts:7560
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:15693
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:15694
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:15695
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:15696
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:16152
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:16154
- `MODULE_NAME` `conninfra` → `device_modules:arch/arm64/boot/dts/mediatek/mt6897.dts:16159
- `MODULE_NAME` `conninfra` → `device_modules:drivers/misc/mediatek/connectivity/power_throttling/conn_power_throttling.h:134
- `MODULE_NAME` `conninfra` → `device_modules:drivers/misc/mediatek/connectivity/common/wmt_build_in_adapter.h:20
- `EXPORT` `conninfra_reg_readable` → `device_modules:drivers/misc/mediatek/connectivity/common/wmt_build_in_adapter.h:20
- `MODULE_NAME` `conninfra` → `device_modules:drivers/misc/mediatek/connectivity/common/wmt_build_in_adapter.h:21
- `MODULE_NAME` `conninfra` → `device_modules:drivers/misc/mediatek/connectivity/common/wmt_build_in_adapter.h:33
- `EXPORT` `conninfra_reg_readable` → `device_modules:drivers/misc/mediatek/connectivity/common/wmt_build_in_adapter.h:33
- ... 372 more exact-hit records in CSV

## fingerprint

- locations: `vendor_boot_platform`
- result: **RELATED_SOURCE_HIT**
- evidence kinds: `MODULE_NAME`
- exact hit records: 97
- description: `for yft fingerprint driver`
- aliases: `of:N*T*Cmediatek,yft_finger;of:N*T*Cmediatek,yft_fingerC*`

- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:15
- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:16
- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:19
- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:21
- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:24
- `MODULE_NAME` `fingerprint` → `kernel:include/uapi/linux/netfilter/nfnetlink_osf.h:112
- `MODULE_NAME` `fingerprint` → `kernel:net/netfilter/xt_osf.c:53
- `MODULE_NAME` `fingerprint` → `kernel:net/netfilter/xt_osf.c:71
- `MODULE_NAME` `fingerprint` → `kernel:net/netfilter/nft_osf.c:194
- `MODULE_NAME` `fingerprint` → `kernel:net/netfilter/nfnetlink_osf.c:26
- `MODULE_NAME` `fingerprint` → `kernel:net/netfilter/nfnetlink_osf.c:136
- `MODULE_NAME` `fingerprint` → `kernel:include/linux/platform_data/cros_ec_commands.h:6083
- `MODULE_NAME` `fingerprint` → `kernel:include/linux/netfilter/nfnetlink_osf.h:8
- `MODULE_NAME` `fingerprint` → `kernel:include/linux/netfilter/nfnetlink_osf.h:10
- `MODULE_NAME` `fingerprint` → `kernel:include/linux/netfilter/nfnetlink_osf.h:12
- `MODULE_NAME` `fingerprint` → `kernel:arch/arm64/boot/dts/qcom/sdm632-fairphone-fp3.dts:168
- `MODULE_NAME` `fingerprint` → `kernel:arch/arm64/boot/dts/qcom/sc7280-herobrine.dtsi:128
- `MODULE_NAME` `fingerprint` → `kernel:arch/arm64/boot/dts/qcom/sc7280-herobrine.dtsi:243
- `MODULE_NAME` `fingerprint` → `kernel:arch/arm64/boot/dts/qcom/msm8994-sony-xperia-kitakami.dtsi:97
- `MODULE_NAME` `fingerprint` → `kernel:crypto/asymmetric_keys/x509_cert_parser.c:564
- ... 77 more exact-hit records in CSV

## wlan_drv_gen4m_6878

- locations: `vendor_dlkm`
- result: **RELATED_SOURCE_HIT**
- evidence kinds: `CHIP_TOKEN;MODULE_NAME`
- exact hit records: 941
- description: `NIC_DESC`
- aliases: ``

- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:37
- `MODULE_NAME` `wlan_drv_gen4m_6878` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:37
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:38
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:39
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:40
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:41
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:42
- `CHIP_TOKEN` `gen4m` → `device_modules:kernel/kleaf/mgk_64_k61.bzl:43
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/connectivity/Makefile:50
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/connectivity/Makefile:73
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/connectivity/Makefile:77
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/connectivity/Makefile:79
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/connectivity/Makefile:90
- `CHIP_TOKEN` `gen4m` → `device_modules:drivers/misc/mediatek/include/mt-plat/mtk_ccci_common.h:588
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/osal/include/sys_adaption.h:56
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/osal/include/net_adaption.h:1298
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/hal/include/operation.h:17
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/hal/include/operation.h:347
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/hal/gen4m/operation_gen4m.c:103
- `CHIP_TOKEN` `gen4m` → `kernel_modules:connectivity/wlan/core/gen4m/wlan_service/glue/hal/gen4m/operation_gen4m.c:2526
- ... 921 more exact-hit records in CSV

