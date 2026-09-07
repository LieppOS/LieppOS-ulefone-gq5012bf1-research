# Phase 2 Local MT6878 / GQ5012BF1 Findings

## Stock DLKM inventory

Canonical local stock extraction:

`workspace/gq5012bf1/stock/partitions/`

Exact module counts:

| Partition | Modules |
|---|---:|
| vendor_dlkm | 215 |
| system_dlkm | 60 |
| odm_dlkm | 0 |
| Total | 275 |

### vermagic

All 215 `vendor_dlkm` modules report:

`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`

All 60 `system_dlkm` modules report:

`6.1.115-android14-11-g6b18f0b574ab-ab12901745 SMP preempt mod_unload modversions aarch64`

Therefore the stock system uses two module sets built with different kernel
build/git identifiers while sharing Linux 6.1.115, Android14-11, AArch64 and
CONFIG_MODVERSIONS characteristics.

This does not by itself prove ABI incompatibility. Symbol CRC / KMI comparison
is still required.

## Ulefone-specific / notable stock modules found

- focaltech_touch_spi_ft3680.ko
- hynitron.ko
- spi_tiny_co5300_lcd.ko
- yft_devinfo.ko
- yft_tiny2c_usb.ko
- touch_boost.ko
- mtk_ioctl_touch_boost.ko

Other relevant stock modules include:

- charger_cooling.ko
- mtk_battery_oc_throttling.ko
- mtk_low_battery_throttling.ko
- thermal-generic-adc.ko
- thermal_interface.ko
- thermal_trace.ko
- nfc.ko

`yft_tpd_gesture.ko` and `yft_gpio_keys.ko` were not found under the canonical
stock partition extraction by exact filename during this pass.

## NothingOSS source reconnaissance

### MT6375

Strong source coverage exists in `android_kernel_device_modules_6.1_nothing_mt6878`.

Observed source includes:

- drivers/mfd/mt6375.c
- drivers/power/supply/mt6375-charger.c
- drivers/power/supply/mt6375-gauge.c
- drivers/misc/mediatek/typec/tcpc/tcpc_mt6375.c
- MT6375 ADC/AUXADC support
- DT bindings
- Kconfig / Makefile integration
- MT6878 DTS references

This is a strong MediaTek platform-source donor candidate.

### ST21 NFC

Nothing source contains MediaTek ST21 NFC support:

- drivers/misc/mediatek/nfc/st21nfc/st21nfc.c
- drivers/misc/mediatek/nfc/st21nfc/st21nfc.h
- drivers/misc/mediatek/nfc/st54spi.c

This is a strong NFC platform/source donor candidate, pending comparison with
the Ulefone DT and actual vendor NFC implementation.

### FocalTech

Nothing contains a MediaTek FocalTech FT3519 driver tree and the
`focaltech_config.h` file contains an FT3680 reference.

This is evidence of a closely related FocalTech driver family, but is NOT yet
a direct source match for Ulefone's `focaltech_touch_spi_ft3680.ko`.

Requires module symbol, compatible, transport and driver-source comparison.

### No meaningful source match yet

Current searches found no convincing Ulefone-specific source for:

- Hynitron
- CO5300 secondary display
- YFT infrastructure
- ThermoVue
- AC020 thermal subsystem
- Microarray fingerprint / madev
- SC8571

Some raw substring hits for AC020, Microarray, madev and YFT were unrelated and
must not be treated as source matches.


## Exact stock module inventory

`kernel/stock-module-inventory.csv` was generated from the canonical ignored
stock extraction.

Validated:

- vendor_dlkm: 215 modules
- system_dlkm: 60 modules
- odm_dlkm: 0 modules
- total: 275 modules
- ELF architecture: 275/275 AArch64
- `__versions`: present in 275/275 modules

This confirms CONFIG_MODVERSIONS-style symbol CRC compatibility is relevant
for every module in the examined DLKM sets.

### Kernel build identities

vendor_dlkm (215/215):

`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`

system_dlkm (60/60):

`6.1.115-android14-11-g6b18f0b574ab-ab12901745 SMP preempt mod_unload modversions aarch64`

The system_dlkm build ID matches the observed stock runtime kernel identity,
while vendor_dlkm has a different git/build suffix. The fact that the stock
firmware ships both sets means vermagic string identity is not sufficient for
compatibility conclusions. Exact imported-symbol CRC comparison is required.

## Ulefone/YFT dependency findings

### FT3680

`focaltech_touch_spi_ft3680.ko`

- depends: `yft_tpd_gesture,mtk_disp_notify,yft_devinfo`
- OF compatible: `focaltech,fts`
- 104 imported symbols
- 0 exported symbols

`yft_tpd_gesture` is therefore a real dependency of the FT3680 stack even
though no `yft_tpd_gesture.ko` was found in the vendor_dlkm/system_dlkm module
inventory. It must be searched for in vendor_boot/platform modules, another
module location, or investigated as a metadata/build-layout discrepancy.

### Hynitron

`hynitron.ko`

- depends: `yft_devinfo`
- I2C alias: `hyn_ts`
- OF compatible: `hynitron,hyn_ts`
- 53 imports
- 2 exports

### CO5300 rear display

`spi_tiny_co5300_lcd.ko`

- depends: `yft_devinfo,hynitron`
- SPI alias: `SSD1317`
- OF compatible: `hxytech,_spi_tiny_lcd`
- srcversion: `3058614C4D8DB62181261D9`
- 57 imports

This establishes a direct dependency between the rear-display driver and the
Hynitron touch driver.

### YFT infrastructure

`yft_devinfo.ko`

- 39 imports
- 27 exports

The unusually large exported-symbol set suggests this is shared Ulefone/YFT
kernel infrastructure rather than a standalone informational driver.

`yft_tiny2c_usb.ko`

- OF compatible: `mediatek,yft_tiny2c_usb`
- I2C alias: `tiny2c_usb-sensor`
- depends: `mt6375-charger`

This directly couples YFT-specific hardware logic to the MT6375 charging/USB
stack.


## FT3680 gesture dependency resolution

Further stock analysis found no `yft_tpd_gesture.ko` or `yft_gpio_keys.ko`
anywhere in the currently extracted stock partition tree.

No references to those module filenames/names were found in the extracted
module metadata.

There is an important difference between the FT3680 module's embedded
build-time dependency metadata and the shipped depmod tree:

`modinfo focaltech_touch_spi_ft3680.ko` reports:

`depends: yft_tpd_gesture,mtk_disp_notify,yft_devinfo`

but stock `vendor_dlkm/lib/modules/modules.dep` resolves FT3680 only to:

`yft_devinfo.ko`

Therefore `yft_tpd_gesture` must NOT currently be assumed to be a separately
shipped vendor_dlkm module. Possible explanations include built-in kernel
code, vendor_boot/platform module placement, another module location, or
build-time dependency metadata that no longer corresponds exactly to the
shipping module layout.

### Confirmed FT3680 gesture symbol CRCs

`modprobe --dump-modversions focaltech_touch_spi_ft3680.ko` confirms imports:

- `tpgesture_value` — CRC `0x02f3ea4c`
- `tpgesture_status` — CRC `0x30ac810a`

These symbols provide concrete identifiers for locating the actual runtime
gesture provider and for later KMI compatibility analysis.


## FT3680 provider-map refinement

The complete 275-module DLKM set was searched for exports of
`tpgesture_value` and `tpgesture_status`.

Neither symbol has a provider in vendor_dlkm or system_dlkm.

This rules out the currently extracted DLKM sets as the runtime provider of
the FT3680 gesture ABI.

`yft_devinfo.ko` exports the following FT3680 imports:

- `touch_fw_version`
- `yft_spitouchpanel_device_add`
- `yft_set_touch_device_used`

Therefore `yft_devinfo.ko` is confirmed as shared Ulefone/YFT kernel
infrastructure used directly by the FT3680 touchscreen driver.

The unresolved FT3680 vendor-specific imports currently include:

- `tpgesture_value` CRC `0x02f3ea4c`
- `tpgesture_status` CRC `0x30ac810a`
- `tpgesture_hander` CRC `0x8386526d`
- `mtk_disp_notifier_register` CRC `0x4c353ac0`
- `mtk_disp_notifier_unregister` CRC `0xa11ab00a`

The misspelling `tpgesture_hander` is the actual imported symbol name and must
be preserved when searching source/binaries.

Likely remaining provider locations are stock built-in kernel code and/or
vendor_boot/early-boot modules.


## FT3680 vs Nothing source boundary

Exact-symbol comparison refined the FT3680 source-port boundary.

NothingOSS provides the MediaTek display notifier API imported by the stock
Ulefone FT3680 module:

- `mtk_disp_notifier_register`
- `mtk_disp_notifier_unregister`

Nothing source contains implementations in the MediaTek DRM display-notifier
code, and Nothing's own FocalTech FT3519 touchscreen driver uses the same API.

This portion of the FT3680 dependency stack is therefore a strong
LIKELY_PLATFORM_MATCH/source-donor candidate.

NothingOSS does not contain the Ulefone/YFT-specific FT3680 imports:

- `tpgesture_value`
- `tpgesture_status`
- `tpgesture_hander`
- `touch_fw_version`
- `yft_spitouchpanel_device_add`
- `yft_set_touch_device_used`

The final three symbols are confirmed exports of stock `yft_devinfo.ko`.

The first three gesture symbols have no provider in the complete 275-module
vendor_dlkm/system_dlkm inventory. Their provider must therefore be sought in
vendor_boot/early modules or built-in stock kernel code.

This means the likely FT3680 porting model is:

1. reuse/forward-port MediaTek/FocalTech platform infrastructure;
2. reproduce or port Ulefone's YFT device-registration API;
3. locate/reconstruct Ulefone's gesture ABI;
4. adapt the FT3680-specific controller differences from the available
   FocalTech family source.


## Stock vendor_boot layout

Stock `vendor_boot.img` was parsed successfully as Android vendor_boot header
version 4.

SHA256:

`c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756`

Contents:

- vendor_ramdisk00
  - size: 28,759,822 bytes
  - type: 0x1 / PLATFORM
  - LZ4 compressed
- vendor_ramdisk01
  - size: 4,714,551 bytes
  - type: 0x2 / RECOVERY
  - name: recovery
  - LZ4 compressed
- DTB: 342,395 bytes
- bootconfig: empty

Searching the still-compressed vendor ramdisk fragments for FT3680/YFT symbol
strings produced no hits and is not conclusive. The ramdisks must be
decompressed before determining whether early-boot modules provide the
unresolved gesture symbols.


## vendor_boot PLATFORM module discovery

Decompression of the stock vendor_boot v4 ramdisks established:

- PLATFORM ramdisk: 196 kernel module files
- RECOVERY ramdisk: 0 kernel module files

Therefore the previous 275-module count represents the DLKM partitions only,
not the complete stock kernel-module universe.

There are currently 471 observed module placements:

- 215 vendor_dlkm
- 60 system_dlkm
- 196 vendor_boot PLATFORM

This is NOT yet a unique-module count because vendor_boot and DLKM contain
overlapping module names.

The PLATFORM ramdisk explicitly contains important modules absent from the
previous DLKM-only analysis, including:

- `yft_gpio_keys.ko`
- `mtk_disp_notify.ko`
- `microarray_fp_tee.ko`
- `sc8571_charger.ko`
- `st21nfc.ko`
- `mt6375.ko`
- `mt6375-adc.ko`
- `mt6375-auxadc.ko`
- `mt6375-battery.ko`
- `mt6375-charger.ko`
- `tcpc_mt6375.ko`
- another `yft_devinfo.ko`

The decompressed PLATFORM CPIO also contains the strings:

- `tpgesture_value`
- `tpgesture_status`
- `tpgesture_hander`
- `yft_tpd_gesture`
- `yft_gpio_keys`

This strongly places the previously unresolved FT3680 gesture ABI in the
vendor_boot PLATFORM module set rather than in the GKI kernel itself.

Exact module/provider identification remains required.


## FT3680 stock dependency chain resolved

Extraction and symbol indexing of the vendor_boot PLATFORM ramdisk fully
resolved the previously missing FT3680 providers.

Stock FT3680 imports resolve as follows:

| Symbol | Provider | Placement |
|---|---|---|
| tpgesture_value | yft_tpd_gesture | vendor_boot PLATFORM |
| tpgesture_status | yft_tpd_gesture | vendor_boot PLATFORM |
| tpgesture_hander | yft_tpd_gesture | vendor_boot PLATFORM |
| mtk_disp_notifier_register | mtk_disp_notify | vendor_boot PLATFORM |
| mtk_disp_notifier_unregister | mtk_disp_notify | vendor_boot PLATFORM |
| touch_fw_version | yft_devinfo | vendor_boot PLATFORM + vendor_dlkm |
| yft_spitouchpanel_device_add | yft_devinfo | vendor_boot PLATFORM + vendor_dlkm |
| yft_set_touch_device_used | yft_devinfo | vendor_boot PLATFORM + vendor_dlkm |

`yft_tpd_gesture.ko` metadata:

- name: `yft_tpd_gesture`
- description: `YFT touch gesturewake driver`
- license: GPL
- no module dependencies
- exports:
  - `tpgesture_hander`
  - `tpgesture_status`
  - `tpgesture_value`

`mtk_disp_notify.ko` exports:

- `mtk_disp_notifier_call_chain`
- `mtk_disp_notifier_register`
- `mtk_disp_notifier_unregister`
- `mtk_disp_sub_notifier_call_chain`
- `mtk_disp_sub_notifier_register`
- `mtk_disp_sub_notifier_unregister`

The Nothing MT6878 source tree contains source implementations for the same
MediaTek display-notifier API, making this portion of the touchscreen stack a
strong platform-source match.

`yft_devinfo.ko` exists in both vendor_boot PLATFORM and vendor_dlkm. The two
files are byte-identical:

SHA256:
`0d5e547e3e6c313c88695b2c8f9aae04398e3c8822f16d57dff6aea011f821fe`

Both use:

`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`

The FT3680 stack therefore consists of:

1. MediaTek display-notifier infrastructure, for which Nothing source exists.
2. Ulefone/YFT gesture infrastructure in `yft_tpd_gesture`.
3. Ulefone/YFT board/device-registration infrastructure in `yft_devinfo`.
4. The Ulefone FT3680 FocalTech controller driver itself.

This strongly supports classifying the FT3680 driver as NEEDS_ULEFONE_PORT
rather than DIRECT_SOURCE_MATCH, while the MediaTek display notifier is a
LIKELY_PLATFORM_MATCH pending exact source/build comparison.


## Stock module placement deduplication

Across the currently examined stock module locations:

- vendor_dlkm: 215 placements
- system_dlkm: 60 placements
- vendor_boot PLATFORM: 196 placements
- vendor_boot RECOVERY: 0 placements

Total observed module placements: 471.

SHA256/filename deduplication established:

- unique SHA256 module binaries: 458
- unique module filenames: 457
- exact duplicated binary groups: 13
- same filename with different binary contents: 1

The only same-filename/different-binary collision found is `bluetooth.ko`.

system_dlkm copy SHA256:

`d2659fb37cd1d08469eac25bff927efb54390fdaf598532c0a9ddfa219b22555`

vendor_dlkm copy SHA256:

`2df021ea9d5b0563ad21029a8cab1ba43d392b12af460ff3f0f7c36372b282fa`

Therefore 471 must not be used as a unique module count. The current exact
distinct-binary count across the examined DLKM + vendor_boot PLATFORM
locations is 458.

This is still termed the current observed stock module universe until boot
and init_boot are explicitly checked for any additional module payloads.


## vendor_boot / vendor_dlkm duplication pattern

Exact SHA256 comparison found 13 duplicated binary groups.

Every exact duplicate is a vendor_boot PLATFORM + vendor_dlkm pair:

- yft_devinfo.ko
- mtk_dynamic_loading_throttling.ko
- reboot-mode.ko
- spmi-mtk-mpu.ko
- mtk_low_battery_throttling.ko
- mtk_pbm.ko
- mtk-mbox.ko
- mtk_mdpm.ko
- syscon-reboot-mode.ko
- mtk-mmdvfs-v3-start.ko
- mtk_tinysys_ipi.ko
- mtk_battery_oc_throttling.ko
- mtk_rpmsg_mbox.ko

This establishes a deliberate stock layout where selected boot-critical
modules are duplicated byte-for-byte between vendor_boot PLATFORM and
vendor_dlkm.

## bluetooth.ko dual-build finding

`bluetooth.ko` is the only currently observed same-filename/different-binary
collision.

Both copies report:

- name: bluetooth
- description: Bluetooth Core ver 2.22
- license: GPL
- dependency: rfkill
- srcversion: `9E17CAE916EF8C636C6E105`

system_dlkm SHA256:

`d2659fb37cd1d08469eac25bff927efb54390fdaf598532c0a9ddfa219b22555`

system_dlkm vermagic:

`6.1.115-android14-11-g6b18f0b574ab-ab12901745 SMP preempt mod_unload modversions aarch64`

vendor_dlkm SHA256:

`2df021ea9d5b0563ad21029a8cab1ba43d392b12af460ff3f0f7c36372b282fa`

vendor_dlkm vermagic:

`6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`

The identical srcversion and module metadata strongly indicate the same
Bluetooth source revision was built separately against the system/GKI and
vendor kernel build environments.

Exact __versions CRC comparison is required to determine whether the two
builds expose the same KMI requirements despite their different vermagic
identities.


## Stock proof of GKI/KMI compatibility across build identities

The two stock `bluetooth.ko` binaries were compared using their complete
`__versions` tables.

Results:

- system_dlkm entries: 219
- vendor_dlkm entries: 219
- common symbols: 219
- same CRC: 219
- different CRC: 0
- system-only symbols: 0
- vendor-only symbols: 0

The binaries nevertheless have different SHA256 hashes, sizes and vermagic
kernel-release/build identifiers.

system_dlkm:

`6.1.115-android14-11-g6b18f0b574ab-ab12901745`

vendor_dlkm:

`6.1.115-android14-11-g945dff7bc1bf`

Both have the same srcversion:

`9E17CAE916EF8C636C6E105`

Android common 6.1 module-loader behavior explains this arrangement:
when CONFIG_MODVERSIONS data/CRCs are present, `same_magic()` ignores the
first vermagic component (the kernel release string) and compares the
remaining vermagic characteristics. Symbol compatibility is then checked
using module-version CRCs.

Therefore the differing Ulefone kernel build suffixes do not by themselves
represent a module ABI incompatibility.

For this Bluetooth module, the stock GKI-side and vendor-side builds expose
an identical 219-symbol versioned dependency contract.

This is direct stock evidence supporting a KMI-focused compatibility strategy
rather than requiring exact kernel git/build identity.

## Normal-boot yft_devinfo loading

Normal vendor_boot `modules.load` does not explicitly list `yft_devinfo.ko`.

However:

- `sh366003_fg.ko` is explicitly listed for normal boot.
- `modules.dep` states that `sh366003_fg.ko` depends on `yft_devinfo.ko`.

Android first-stage init uses libmodprobe to process `modules.load`.
libmodprobe resolves hard dependencies from `modules.dep` before loading the
requested target module.

Therefore normal boot can load `yft_devinfo.ko` transitively before
`sh366003_fg.ko`; it does not need a separate explicit entry in modules.load.

Recovery additionally lists `yft_devinfo.ko` explicitly.


## Correct symbol-introspection method for stripped stock modules

The stock kernel modules are sufficiently stripped that `llvm-nm` is not a
reliable source for imported/exported-symbol counts.

For example, `bluetooth.ko` appeared to have zero imports via `llvm-nm`, while
its `__versions` data contains 219 versioned symbol requirements.

Verified usable interfaces are:

- versioned symbol requirements / CRCs:
  `modprobe --dump-modversions <module>`
- exported symbol names:
  ELF section `__ksymtab_strings`, readable with:
  `readelf -p __ksymtab_strings <module>`

Both system_dlkm and vendor_dlkm Bluetooth modules retain
`__ksymtab_strings`.

The existing `stock-module-inventory.csv` import/export counts generated via
`llvm-nm` must therefore not be used for KMI conclusions and should be
regenerated with the corrected extraction method.


## bluetooth.ko complete ABI/API equivalence

Full exported-symbol comparison of the two stock Bluetooth Core builds found:

- system_dlkm exports: 72
- vendor_dlkm exports: 72
- export-set differences: 0

Combined with the previous `__versions` comparison:

- required/versioned symbols: 219 vs 219
- identical required symbols: 219
- identical CRCs: 219
- differing CRCs: 0
- exported symbols: 72 vs 72
- exported-symbol differences: 0

Therefore the two different `bluetooth.ko` binaries have an identical observed
module ABI/API contract despite differing SHA256 hashes, sizes, and kernel
build/vermagic suffixes.

This is strong stock-device evidence that KMI/symbol-version compatibility,
rather than exact kernel build identity, is the relevant compatibility
criterion for these Android GKI/vendor module builds.


## boot and init_boot module check

`boot.img` is Android boot header v4 and contains:

- kernel: 16,498,955 bytes
- ramdisk: 0 bytes

Therefore boot.img contains no separate ramdisk kernel-module payload.

`init_boot.img` is Android boot header v4 and contains an LZ4-compressed
ramdisk. The ramdisk decompresses successfully to an SVR4/newc CPIO archive.

No `.ko` files were found in init_boot.

Therefore the currently identified stock module-bearing locations are:

- system_dlkm
- vendor_dlkm
- vendor_boot PLATFORM

Current exact accounting:

- module placements: 471
- distinct SHA256 module binaries: 458
- unique module filenames: 457
- exact duplicated binary groups: 13
- same-name/different-binary cases: 1 (`bluetooth.ko`)


## Phase 2 automated stock/Nothing indexing

The generated Phase 2 index completed successfully with all stock placement
invariants satisfied.

Stock module universe:

- module placements: 471
- distinct SHA256 module binaries: 458
- unique module filenames: 457

Generated symbol/index data:

- versioned import records: 26,111
- exported symbol records: 4,875
- Nothing source module targets indexed: 16,116

Initial classifier output:

- DIRECT_SOURCE_MATCH: 257
- LIKELY_PLATFORM_MATCH: 170
- NEEDS_ULEFONE_PORT: 1
- ULEFONE_ONLY: 8
- ALTERNATE_BOM: 0
- UNKNOWN: 22

These classification counts are provisional.

The current classifier allows an exact module-name match plus an overlapping
exported symbol to promote a module to DIRECT_SOURCE_MATCH. Some Nothing
source-index records may also use directory-level fallback source evidence.

Therefore DIRECT_SOURCE_MATCH entries require an evidence-quality audit before
the classifications are considered final.


## UNKNOWN fuzzy-candidate audit rejected

The first fuzzy UNKNOWN-module candidate audit did not produce evidence strong
enough for classification.

It generated obvious false-positive associations, including unrelated GPS,
fingerprint, connectivity, power-throttling and generic kernel targets.

No UNKNOWN module produced a rank-1 candidate score >= 100.

Therefore none of the fuzzy candidates are used to modify module-map.csv.

UNKNOWN resolution now uses exact-source reconnaissance only:

- exact module identifiers
- exact component/chip identifiers
- exact OF compatible strings
- exact bus/platform aliases
- exact stock exported API symbols

Fuzzy token/name similarity is not accepted as classification evidence.


## UNKNOWN exact-source audit resolution

The 22 UNKNOWN modules were re-audited using exact evidence rather than fuzzy
name matching.

Strong Nothing MT6878 source donors were identified for:

- connfem
- conninfra
- gps_pwr
- gps_scp
- gps_drv_dl_v051
- wmt_chrdev_wifi_connac2
- wlan_drv_gen4m_6878

These are backed by exact stock module/build/API evidence and published
MediaTek connectivity/GPS/WLAN source in the Nothing MT6878 trees.

`bt_drv_6878` is retained as LIKELY_PLATFORM_MATCH because Nothing publishes
and builds the MediaTek BT linux_v2 stack and contains matching BT APIs, but
the exact Ulefone `bt_drv_6878` output target has not yet been proven.

`leds_rgb_aw2013` is retained as LIKELY_PLATFORM_MATCH because the same AW2013
chip driver exists in the available kernel source, while Ulefone uses a custom
`awinic,rgb,aw2013` integration.

External source/vendor-resource reconnaissance also changed the porting plan:

- aw883xx_driver:
  Awinic publishes GPL-2.0 AW883xx Smart PA driver source.
  Phase 2 classification was: NEEDS_ULEFONE_PORT, not binary-only reconstruction.

  RESOLVED in Phase 4 -> SOURCE_DELTA_RECONSTRUCTION_EXACT.
  See kernel/phase4-aw883xx-reconstruction.md (authoritative).
  The public donor (awinic-driver/aw883xx @ 4f52a10) is v1.6.0 while stock is
  v1.7.1, and no public v1.7.1 drop exists; the 11 deltas were recovered from
  the stock binary. Result: 236/236 functions, 235/236 byte-identical,
  0/236 differing relocation multisets, exact stock ABI parity.

- aw36515:
  Awinic provides AW36515 Android driver/sample/porting resources.
  Classification: NEEDS_ULEFONE_PORT.

- aw36518 / aw36518_v2:
  Awinic provides AW36518/AW3651X Android driver/sample/porting resources.
  Classification: NEEDS_ULEFONE_PORT.

The following currently have no usable source donor in the Nothing tree or
the external-source audit and remain ULEFONE_ONLY in the donor-map sense:

- panel_ky_vtdr6115_dphy_cmd
- leds_ln2403
- sh366003_fg
- sc851x_charger
- custom_ldo
- custom_ldo_wl2868
- tkcore
- tkcore_drv
- fingerprint

ULEFONE_ONLY here means absent from the current usable donor-source set, not
that the underlying silicon was designed by Ulefone.

TrustKernel TKCore uses the standard GlobalPlatform TEE Client API. Therefore
the TEEC_* symbol overlap seen in Nothing's different TEE implementation is
API compatibility and is not evidence that TKCore source exists in Nothing.

LN2403 hardware documentation is publicly available, so a future replacement
driver can be implemented from hardware documentation plus stock behavioral
evidence rather than purely from binary disassembly.

VTDR6115 is identified as a Viewtrix AMOLED display-driver IC, but no usable
kernel panel source has yet been located.


## Stock KMI requirement split

The complete 5,207-symbol stock import ABI was split by provider.

Results:

- raw versioned import records: 26,111
- unique imported symbol/CRC requirements: 5,207
- conflicting CRC requirements: 0
- symbols provided by another stock module: 2,261
- symbols requiring a kernel/builtin provider: 2,946

Therefore the actual kernel-facing compatibility target for retaining the
complete stock module population is 2,946 unique symbol/CRC requirements.
The remaining 2,261 symbols form the stock module-to-module ABI.

Nothing published KMI symbol-name coverage of the 2,946 kernel requirements:

- covered by device MTK symbol-list union: 2,139
- missing from device MTK symbol-list union: 807
- covered by kernel base + MTK + Nothing union: 2,913
- missing from kernel base + MTK + Nothing union: 33
- covered by any inspected Nothing published symbol list: 2,913
- missing from all inspected published Nothing lists: 33

Thus Nothing's published KMI lists cover 98.88% of the Ulefone stock
kernel-facing imported symbol names.

This is symbol-name coverage only. CRC equality is not yet proven.

The Android Common arm64 base abi_gki_aarch64 list intentionally contains
only module_layout and __put_task_struct. Large vendor KMI surfaces are carried
by additional symbol lists such as abi_gki_aarch64_mtk and
abi_gki_aarch64_nothing.

The remaining 33 names must not automatically be treated as incompatible ABI
gaps. A symbol may be exported by the Nothing kernel source while being absent
from the inspected published symbol lists. Each of the 33 must therefore be
mapped to its stock consumer modules and checked for actual source/export
presence.


## Resolution of the 33 published-KMI-list gaps

The 33 kernel-facing stock symbols absent from the inspected Nothing published
KMI symbol lists were checked directly against Nothing kernel source exports.

Results:

- published-list gaps: 33
- explicit Nothing source exports found: 32
- no explicit Nothing source export found: 1

The sole no-export result is:

- cpu_busy_with_softirqs
  - stock required CRC: 0x3c5aab9e
  - stock consumer: scheduler.ko
  - module classification: LIKELY_PLATFORM_MATCH

All published-list gaps consumed by ULEFONE_ONLY modules are explicitly
exported in the Nothing kernel source.

All published-list gaps consumed by NEEDS_ULEFONE_PORT modules are explicitly
exported in the Nothing kernel source.

Both published-list gaps consumed by DIRECT_SOURCE_MATCH modules are explicitly
exported in the Nothing kernel source.

Therefore no kernel symbol-name/export blocker has yet been demonstrated for
the ULEFONE_ONLY proprietary-module population.

The 33-symbol discrepancy is primarily a published KMI-list coverage issue,
not evidence that the corresponding kernel APIs are absent from Nothing source.

Android Common later explicitly exported cpu_busy_with_softirqs for vendor
scheduler users. This is consistent with the Ulefone scheduler module importing
that symbol and with Nothing's older Linux 6.1.68 source base lacking the
explicit export.

Exact compatibility is still not proven because CONFIG_MODVERSIONS requires
matching CRC values, not merely matching symbol names and exports.


## Minimal proprietary-module KMI contract

The kernel-facing ABI was reduced to the subset required by modules that
cannot yet be replaced directly from the current donor-source set.

Results:

- complete stock kernel-facing KMI: 2,946 symbols
- ULEFONE_ONLY kernel requirements: 304 symbols
- NEEDS_ULEFONE_PORT kernel requirements: 157 symbols
- combined ULEFONE_ONLY + NEEDS_ULEFONE_PORT requirements: 354 symbols
- overlap between those two groups: 107 symbols

Therefore, if all DIRECT_SOURCE_MATCH and LIKELY_PLATFORM_MATCH modules are
rebuilt from source, only 304 stock kernel symbol/CRC contracts currently need
to be preserved for the remaining ULEFONE_ONLY binary modules.

During transition, before the five NEEDS_ULEFONE_PORT modules are rebuilt, the
binary-compatible kernel target is 354 unique symbol/CRC requirements.

The target can shrink below 304 as additional Ulefone-specific modules are
reimplemented or source donors are found.

Nothing's Linux 6.1.68 source contains cpu_busy_with_softirqs, but it is static
and is not exported. No export commit was found in that Nothing repository
history. Ulefone stock scheduler.ko imports the symbol.

Therefore stock scheduler.ko is not directly compatible with the older Nothing
source implementation of this API. This is a kernel-version/source-delta issue,
not a ULEFONE_ONLY blocker, because scheduler is classified as a platform-source
module that can be rebuilt/forward-ported.


## Hard Ulefone binary KMI name/export coverage

The ULEFONE_ONLY kernel-facing contract contains 304 unique symbol/CRC
requirements.

Published Nothing KMI-name coverage:

- in inspected Nothing published KMI lists: 289
- outside inspected published KMI lists: 15

All 15 unlisted symbols were independently verified as explicit exports in the
Nothing kernel source.

Therefore:

- hard ULEFONE_ONLY kernel requirements: 304
- symbol names with a Nothing source-level provider/export path: 304
- demonstrated source-level name/export blockers: 0

The remaining unresolved compatibility problem is CRC equivalence under
CONFIG_MODVERSIONS.

This is important because absence from a published KMI list did not imply
absence from the Nothing kernel source. The 15 Ulefone-only list gaps are
exported APIs and therefore remain viable candidates for preservation in a
forward-ported/custom kernel.

cpu_busy_with_softirqs is not part of the 304-symbol ULEFONE_ONLY hard
contract. It is consumed by scheduler.ko, which is classified as
LIKELY_PLATFORM_MATCH and can be rebuilt or forward-ported rather than retained
as an irreplaceable proprietary binary.


## Ulefone-only KMI reduction potential

The 304-symbol hard proprietary kernel ABI was analyzed by individual
ULEFONE_ONLY consumer.

Of the 304 required kernel symbol/CRC contracts:

- 172 are currently exclusive to exactly one ULEFONE_ONLY module
- 132 are shared by two or more ULEFONE_ONLY modules

Largest immediate single-module KMI reductions:

- tkcore: 44 exclusive requirements (101 total)
- yft_gpio_keys: 36 exclusive requirements (65 total)
- panel_ky_vtdr6115_dphy_cmd: 19 exclusive requirements (38 total)
- tkcore_drv: 16 exclusive requirements (54 total)
- microarray_fp_tee: 13 exclusive requirements (59 total)
- spi_tiny_co5300_lcd: 9 exclusive requirements (54 total)
- yft_devinfo: 9 exclusive requirements (40 total)
- hynitron: 7 exclusive requirements (51 total)
- sc8571_charger: 5 exclusive requirements (41 total)
- sh366003_fg: 5 exclusive requirements (33 total)

Exclusive requirements are those that would immediately cease to constrain
the kernel ABI if the corresponding binary module were replaced by a
source-built implementation.

These counts are not reverse-engineering difficulty scores. In particular,
tkcore has the largest KMI impact but belongs to the TEE/security stack and is
likely substantially harder to replace than yft_gpio_keys.

yft_gpio_keys is therefore a strong early reconstruction candidate: it removes
36 currently exclusive stock CRC requirements while using conventional
GPIO/input/IRQ kernel interfaces.

yft_devinfo has lower direct KMI reduction but remains strategically important
because multiple Ulefone-specific drivers depend on its exported module ABI.


## Ulefone module-to-module ABI dependency graph

ULEFONE_ONLY modules were analyzed as providers of symbols imported by other
stock modules.

Provider summary:

- yft_devinfo:
  - consumed exported symbols: 23
  - consumer modules: 7
  - binary-class consumers: 5

- tkcore:
  - consumed exported symbols: 19
  - consumer modules: 3
  - binary-class consumers: 2

- fingerprint:
  - consumed exported symbols: 4
  - consumer modules: 1
  - binary-class consumers: 1

- yft_tpd_gesture:
  - consumed exported symbols: 3
  - consumer modules: 1
  - binary-class consumers: 1

- custom_ldo_wl2868:
  - consumed exported symbols: 2
  - consumer modules: 1
  - binary-class consumers: 1

- hynitron:
  - consumed exported symbols: 2
  - consumer modules: 1
  - binary-class consumers: 1

- custom_ldo:
  - consumed exported symbols: 2
  - consumer modules: 1
  - binary-class consumers: 0

No multiply-exported imported symbols were found. The inferred stock
module-to-module provider graph therefore has unambiguous symbol providers.

This materially affects reconstruction order.

yft_gpio_keys is the strongest early reconstruction candidate because it:

- removes 36 currently exclusive kernel CRC requirements
- does not appear as an inter-module ABI provider
- uses conventional GPIO/input/IRQ interfaces

yft_devinfo is instead a dependency hub. Replacing it independently requires
preserving the module exports required by its remaining stock consumers, or
migrating those consumers at the same time.

Ulefone-specific reconstruction should therefore be planned by subsystem and
dependency graph rather than only by kernel-KMI reduction count.

TrustKernel/fingerprint modules should remain late-stage targets because of
TEE/security complexity despite their relatively large KMI impact.


## Exact stock GKI provenance

The stock runtime kernel reports:

6.1.115-android14-11-g6b18f0b574ab-ab12901745
#1 Fri Jan 10 22:12:05 UTC 2025

This was matched exactly to Android Common:

- release tag: android14-6.1-2024-12_r4
- common commit:
  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
- Android CI kernel_aarch64 build: 12901745
- common commit timestamp:
  2025-01-10 22:12:05 UTC

The git abbreviation, Android build number and timestamp all match the stock
runtime kernel string.

Therefore the GQ5012BF1 stock GKI base is pinned to Android Common commit
6b18f0b574ab3267615ae6ce642d5a7c3c21ac09 / build 12901745.

This is substantially stronger than identifying only Linux 6.1.115 or the
android14-6.1 branch.

Bit-for-bit identity between the Ulefone boot kernel and the published Google
GKI artifact still requires a binary hash comparison, but the source/build
provenance is effectively identified.

This exact GKI revision should be used as the baseline for CONFIG_MODVERSIONS
CRC reconstruction instead of the older Nothing Linux 6.1.68 common tree.


## Exact Android Common 6.1.115 comparison

The exact Android Common GKI source was checked out successfully:

- tag: android14-6.1-2024-12_r4
- commit: 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
- Linux version: 6.1.115
- Android CI kernel_aarch64 build: 12901745

Comparison against the older Nothing 6.1.68 GKI defconfig produced a 196-line
diff, mostly consisting of platform enablement and normal Android Common
evolution.

The inspected KMI-sensitive arm64 GKI configuration remains aligned on:

- CONFIG_CFI_CLANG=y
- CONFIG_MODULE_UNLOAD=y
- CONFIG_MODVERSIONS=y
- CONFIG_MODULE_SCMVERSION=y
- CONFIG_MODULE_SIG=y
- CONFIG_DEBUG_INFO_DWARF4=y
- CONFIG_DEBUG_INFO_BTF=y
- CONFIG_MODULE_ALLOW_BTF_MISMATCH=y

The exact 6.1.115 GKI additionally has:

- CONFIG_MODULE_SIG_PROTECT=y

The previous cpu_busy_with_softirqs discrepancy is now fully explained.

Nothing Linux 6.1.68 contains cpu_busy_with_softirqs as a static scheduler
helper and does not export it.

Exact Android Common Linux 6.1.115 contains the same helper as a global
function and exports it with:

EXPORT_SYMBOL_GPL(cpu_busy_with_softirqs);

Therefore the stock scheduler.ko dependency on cpu_busy_with_softirqs is
explained by Android Common version evolution rather than a Ulefone-specific
kernel export.

The exact Android Common source also contains the MediaTek KMI list
android/abi_gki_aarch64_mtk, with 3581 file lines in this revision.

The next compatibility step is direct CRC comparison against Android CI build
12901745 vmlinux.symvers.


## Exact Google GKI CRC proof

Android CI build 12901745 `kernel_aarch64` was downloaded directly from the
official Android CI artifact service.

BUILD_INFO independently confirms:

- build: 12901745
- target: kernel_aarch64
- branch: aosp_kernel-common-android14-6.1-2024-12
- kernel/common:
  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
- Linux version: 6.1.115

The downloaded `vmlinux.symvers` contains 7,993 exported symbols and contains
no duplicate symbol names with differing CRCs.

Direct comparison against the stock GQ5012BF1 module requirements produced:

- complete stock kernel-facing ABI:
  2,946 / 2,946 exact CRC matches
- CRC mismatches: 0
- missing symbols: 0

Transitional ULEFONE_ONLY + NEEDS_ULEFONE_PORT ABI:

- 354 / 354 exact CRC matches
- mismatches: 0
- missing: 0

Hard ULEFONE_ONLY ABI:

- 304 / 304 exact CRC matches
- mismatches: 0
- missing: 0

Therefore every kernel-facing CONFIG_MODVERSIONS requirement observed in the
entire stock module population is satisfied exactly by Google's official
kernel_aarch64 GKI build 12901745.

This proves that the stock Ulefone module population uses the exact Google GKI
ABI represented by that build.

It does not by itself prove that the kernel binary contained in Ulefone boot.img
is byte-identical to Google's published Image. Binary identity requires a
separate kernel Image hash comparison.

The previous cpu_busy_with_softirqs investigation was also closed directly:

Google GKI build 12901745 exports:

0x3c5aab9e cpu_busy_with_softirqs vmlinux EXPORT_SYMBOL_GPL

which exactly matches the CRC imported by the Ulefone stock scheduler module.

Implication for custom-kernel development:

Google GKI build 12901745 / Android Common commit
6b18f0b574ab3267615ae6ce642d5a7c3c21ac09 is the authoritative kernel ABI
baseline for GQ5012BF1.

The Nothing MT6878 trees should primarily be treated as MediaTek BSP/vendor
driver source donors and forward-ported onto this exact Android Common baseline,
rather than using Nothing's older Linux 6.1.68 kernel core as the final kernel.


## Exact stock kernel binary identity

The kernel payload extracted from the stock GQ5012BF1 boot.img was compared
directly against the official Android CI Image.lz4 artifact from build
12901745.

Stock boot kernel:

- size: 16,498,955 bytes
- format: LZ4 compressed ARM64 kernel Image
- SHA256:
  1f2a9e9b1c1d2533ca649a472c29df42b029b63dac677c5d439a358ede67e722

Google Android CI build 12901745 Image.lz4:

- size: 16,498,955 bytes
- format: LZ4 compressed ARM64 kernel Image
- SHA256:
  1f2a9e9b1c1d2533ca649a472c29df42b029b63dac677c5d439a358ede67e722

A direct cmp comparison reports the files as bit-for-bit identical.

Therefore the kernel payload shipped by Ulefone in the stock GQ5012BF1
boot.img is exactly Google's published Image.lz4 artifact from Android CI
kernel_aarch64 build 12901745.

Combined with the previously proven CONFIG_MODVERSIONS results:

- complete stock kernel-facing ABI: 2,946 / 2,946 CRC matches
- transition binary ABI: 354 / 354 CRC matches
- hard ULEFONE_ONLY ABI: 304 / 304 CRC matches
- CRC mismatches: 0
- missing symbols: 0

the GQ5012BF1 kernel baseline is now identified at both binary and ABI level.

Authoritative kernel baseline:

- Android Common tag: android14-6.1-2024-12_r4
- commit:
  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
- Android CI build: 12901745
- target: kernel_aarch64
- Linux: 6.1.115

This means Ulefone did not ship a privately modified GKI kernel binary for
this stock build. Device-specific functionality is supplied through vendor
modules, device tree, vendor_boot and associated MediaTek/Ulefone components.

For LieppOS custom-kernel development, Google's exact Android Common GKI
revision should be treated as the kernel core baseline. Nothing MT6878 sources
should be treated primarily as BSP/vendor-module source donors to be
forward-ported onto that baseline.

