# Phase 3 local findings — source/build mapping

## Candidate population

The source-port investigation starts from:

- 441 classified module-map rows
- 440 distinct module names
- duplicate classified name: bluetooth
- DIRECT_SOURCE_MATCH names: 100
- LIKELY_PLATFORM_MATCH names: 335
- NEEDS_ULEFONE_PORT names: 5

The duplicate bluetooth name corresponds to the previously identified
same-filename/different-binary stock Bluetooth modules.

## Exact Google GKI module separation

Android CI kernel_aarch64 build 12901745 publishes 60 .ko artifacts.

After normalizing hyphens and underscores, all 60 artifact names map into the
candidate module set.

Therefore these 60 modules are not MediaTek/Nothing forward-port targets.
They are supplied directly by the exact Google GKI build used by the phone.

The initial exact-name comparison found only 55 because five Google artifact
names use hyphens while the stock module names use underscores:

- can-bcm -> can_bcm
- can-dev -> can_dev
- can-gw -> can_gw
- can-raw -> can_raw
- cdc-acm -> cdc_acm

Normalization recovers all 60.

## Normalized Nothing source/build mapping

The normalized mapping pass produced:

- GOOGLE_GKI_ARTIFACT: 60
- NOTHING_BUILD_TARGET: 334
- NOTHING_SOURCE_BASENAME: 2
- UNRESOLVED: 44

Thus 396 / 440 candidate names, or 90.0%, already have a structural source
resolution before compilation.

By classification:

DIRECT_SOURCE_MATCH:
- Google GKI: 2
- Nothing build target: 88
- Nothing source basename: 1
- unresolved: 9

LIKELY_PLATFORM_MATCH:
- Google GKI: 58
- Nothing build target: 246
- Nothing source basename: 1
- unresolved: 30

NEEDS_ULEFONE_PORT:
- unresolved: 5

All five NEEDS_ULEFONE_PORT modules remain unresolved under exact/normalized
module-name matching:

- aw36515
- aw36518
- aw36518_v2
- aw883xx_driver
- focaltech_touch_spi_ft3680

This is expected: this classification represents modules requiring adaptation
from related donor source rather than exact same-name donor modules.

## Explicit MT6878 build/source context

Thirty candidate modules currently have direct MT6878-context build or source
evidence in the normalized Nothing tree, including:

- MT6878 clock drivers
- CMDQ platform
- Device APC
- MDP
- MMQoS
- DCM
- MT6369 audio glue
- CM manager
- GPU frequency
- MML
- SCPSYS
- power-domain checking
- PDA
- pinctrl
- MT6878 AFE

This provides strong evidence that the Nothing tree contains a substantial
MT6878 BSP implementation, not merely generic MediaTek code.

## Parser limitation

The normalized parser currently recognizes Makefile/Kbuild obj-* targets but
does not fully capture Android.bp / BUILD.bazel/custom macro targets.

The earlier exact-target parser did identify strong build evidence for several
modules the normalized parser currently calls unresolved, including:

- connfem
- gps_drv_dl_v051
- gps_pwr
- gps_scp
- wlan_drv_gen4m_6878
- wmt_chrdev_wifi_connac2

Therefore the exact and normalized maps must be merged before declaring any
module genuinely unresolved.

Mention-only evidence is not considered sufficient source proof.


## Merged structural source map

The exact-target and normalized source/build maps were merged.

Final structural result:

- candidate module names: 440
- GOOGLE_GKI_ARTIFACT: 60
- NOTHING_BUILD_TARGET: 341
- NOTHING_SOURCE: 1
- UNRESOLVED: 38

Therefore 402 / 440 candidate module names, or 91.4%, have already been
structurally resolved before attempting compilation.

DIRECT_SOURCE_MATCH:

- total: 100
- Google GKI artifact: 2
- Nothing build target: 95
- unresolved: 3

The only remaining unresolved DIRECT_SOURCE_MATCH names are:

- arm_dsu_pmu
- syscon_reboot_mode
- thermal_generic_adc

LIKELY_PLATFORM_MATCH:

- total: 335
- Google GKI artifact: 58
- Nothing build target: 246
- Nothing source: 1
- unresolved: 30

NEEDS_ULEFONE_PORT:

- total: 5
- unresolved: 5

The five expected Ulefone-port targets remain:

- aw36515
- aw36518
- aw36518_v2
- aw883xx_driver
- focaltech_touch_spi_ft3680

The remaining unresolved population must not be interpreted as missing source.
Several names appear to belong to Android Common/GKI source, while others are
likely MediaTek aggregate or renamed build targets.

The next resolution pass therefore checks the exact Android Common 6.1.115
source tree before performing semantic MediaTek donor matching.


## Android Common resolution pass

The remaining 38 structurally unresolved candidate names were checked against
the exact Android Common Linux 6.1.115 source tree at:

6b18f0b574ab3267615ae6ce642d5a7c3c21ac09

Nine additional modules were resolved as Android Common build targets:

- arm_dsu_pmu
- drm_display_helper
- drm_dma_helper
- industrialio_triggered_buffer
- kfifo_buf
- mac80211
- reboot_mode
- syscon_reboot_mode
- thermal_generic_adc

This resolves all remaining DIRECT_SOURCE_MATCH names.

Current structural resolution:

- candidate module names: 440
- exact Google GKI artifacts: 60
- Nothing build targets: 341
- Nothing source-only matches: 1
- additional Android Common targets: 9
- still unresolved: 29

Thus 411 / 440 candidate module names, or 93.4%, are structurally resolved.

DIRECT_SOURCE_MATCH is now:

- total: 100
- resolved: 100
- unresolved: 0

The remaining 29 consist of:

- 24 LIKELY_PLATFORM_MATCH modules requiring semantic/aggregate-target mapping
- 5 NEEDS_ULEFONE_PORT modules requiring Ulefone-specific adaptation

The remaining filename-mapping problem is therefore no longer evidence of a
missing MT6878 BSP. Most remaining platform modules belong to recognizable
subsystems such as connectivity, camera/AI, Mali GPU, LPM/SWPM and video.


## Semantic resolution pass

Semantic subsystem searching resolved several cases that same-filename mapping
missed.

Strong exact Nothing build evidence:

- connscp
  - device_modules/drivers/misc/mediatek/conn_scp/Makefile explicitly sets:
    MODULE_NAME := connscp

- fmradio_drv_connac2x
  - kernel_modules/connectivity/fmradio/BUILD.bazel explicitly publishes:
    Build/connac2x/fmradio_drv_connac2x.ko

- mali_dmabuf_test_mt6878_r44
- mali_kbase_mt6878_r44
- mali_mgm_mt6878_r44
- mali_prot_alloc_mt6878_r44
  - all four exact module names are explicitly published by
    kernel_modules/gpu/BUILD.bazel
  - kernel_modules/gpu/mt6878/Makefile wires the MT6878 Mali r44p1
    driver, memory-group-manager, protected-memory-allocator and
    dma-buf-test directories.

Strong semantic MT6878 source evidence:

- lpm_gov_MHSP
  - MediaTek MHSP governor implementation exists at:
    device_modules/drivers/misc/mediatek/lpm/governors/MHSP/lpm-mhsp.c
  - its Makefile includes lpm-mhsp.o in the LPM governor object set.

- ISP7SP camera stack
  - Nothing mtkcam contains explicit MT6878 ISP7SP data.
  - mtk_imgsys-isp7sp.c contains compatible:
    mediatek,imgsys-isp7sp-mt6878
  - MT6878-specific clocks, DMA port data and platform configuration are
    present.

- CCD camera remoteproc/RPMsg
  - mtkcam contains camsys/remoteproc/mtk_ccd.c
  - mtkcam contains camsys/rpmsg/mtk_ccd_rpmsg.c
  - therefore the stock CCD remoteproc/RPMsg modules have concrete
    semantic donor source even though output-name mapping was missed.

- uarthub
  - MediaTek UARTHUB source is present and is directly integrated with
    the Nothing 8250_mtk UART driver through CONFIG_MTK_UARTHUB.

Other donor evidence:

- leds_rgb_aw2013
  - Nothing's kernel source contains the generic Awinic AW2013
    3-channel LED driver.
  - exact compatibility with the stock Ulefone vendor module remains
    to be tested through aliases, DT compatible strings and symbol contract.

- focaltech_touch_spi_ft3680
  - Nothing's FocalTech touchscreen family does not contain the exact
    Ulefone module but focaltech_config.h explicitly defines FT3680 chip ID:
    _FT3680 0x3680008A
  - this strengthens its status as a related source-family donor.

No local Nothing semantic hits were found for:

- aw36515
- aw36518
- aw36518_v2
- aw883xx_driver

These require external donor research or Ulefone reconstruction.


## Targeted build-definition resolution

Further targeted build-definition inspection resolved additional platform
modules that generic filename indexing missed.

Connectivity:

- connadp
  - exact MediaTek module target:
    MODULE_NAME := connadp
  - built through CONFIG_MTK_COMBO

- connscp
  - exact module target:
    MODULE_NAME := connscp
  - built through CONFIG_MTK_CONN_SCP

- fmradio_drv_connac2x
  - exact module artifact explicitly listed by Nothing:
    Build/connac2x/fmradio_drv_connac2x.ko

- bt_drv_6878
  - Nothing Bluetooth Kbuild defines:
    MODULE_NAME := bt_drv_$(BT_PLATFORM)
  - this is a parameterized exact module family.
  - BT_PLATFORM=6878 still needs to be located in the MT6878 build invocation
    before marking the exact output name proven.

- uarthub_drv
  - exact module target:
    MODULE_NAME := uarthub_drv
  - built through CONFIG_MTK_UARTHUB
  - however the inspected platform-selection section currently visibly wires
    MT6985 and MT6989 platform implementations.
  - MT6878-specific UARTHUB compatibility remains unproven and must be checked
    separately rather than assuming the generic target is sufficient.

Camera:

Nothing explicitly publishes/builds:

- camera_dpe_isp7sp.ko
- ccd_rpmsg.ko
- mtk_ccd_remoteproc.ko
- mtk_aie.ko

These are therefore direct source/build donors rather than semantic-only
matches.

Video:

The Nothing MediaTek codec Makefile contains the concrete module target:

- mtk-vcodec-enc-v1.o

This corresponds to stock mtk_vcodec_enc_v1 after standard hyphen/underscore
module-name normalization.

Low-power / SWPM:

The Nothing device-module tree contains dedicated:

- LPM MT6878 debug build directory
- SWPM v6878 debug build directory
- SSC v2 build path

The exact final output names are variable-generated and need one additional
variable-definition pass before being marked exact.


## Parameterized build-target closure

Additional variable expansion resolved more of the previously unresolved
platform modules.

Bluetooth:

- kernel_modules/connectivity/bt/mt66xx/6878/Kbuild contains:
  BT_PLATFORM := 6878

Combined with:

  MODULE_NAME := bt_drv_$(BT_PLATFORM)

this proves the Nothing source tree directly builds:

  bt_drv_6878.ko

for MT6878.

Low-power modules:

The following stock names have exact normalized Nothing build targets:

- mtk_lpm_dbg_common_v2
  <- mtk-lpm-dbg-common-v2

- mtk_lpm_dbg_mt6878
  <- mtk-lpm-dbg-mt6878

The platform module:

- mtk_lpm_plat_v1

still requires resolving MTK_LPM_MODULE_PLATFORM_PLAT_NAME before its exact
output name is considered proven.

SWPM:

Exact normalized Nothing targets now proven:

- mtk_swpm_dbg_v6878
  <- mtk-swpm-dbg-v6878

- mtk_swpm_cpu_dbg_v6878
  <- mtk-swpm-cpu-dbg-v6878

- mtk_swpm_dbg_common_v1
  <- mtk-swpm-dbg-common-v1

SSC:

Exact normalized Nothing target:

- mtk_ssc_dbg_v2
  <- mtk-ssc-dbg-v2

UARTHUB:

The Nothing tree builds an exact uarthub_drv module and its OF table explicitly
contains:

  mediatek,mt6878-uarthub

However the MT6878 compatible currently maps to:

  &undef_plat_data

while concrete platform implementations are visibly supplied for MT6985 and
MT6989.

Therefore uarthub_drv is classified as:

  EXACT_GENERIC_TARGET / MT6878_PLATFORM_IMPLEMENTATION_UNPROVEN

It must not yet be treated as a complete MT6878 donor.


## Phase 3 special-handling boundary

Subsequent parameter and build-variable inspection closes additional modules.

Exact or normalized build resolution now includes:

- bt_drv_6878
- camera_dpe_isp7sp
- ccd_rpmsg
- connadp
- connscp
- fmradio_drv_connac2x
- mali_dmabuf_test_mt6878_r44
- mali_kbase_mt6878_r44
- mali_mgm_mt6878_r44
- mali_prot_alloc_mt6878_r44
- mtk_aie
- mtk_cam_isp7sp
- mtk_ccd_remoteproc
- mtk_lpm_dbg_common_v2
- mtk_lpm_dbg_mt6878
- mtk_lpm_plat_v1
- mtk_ssc_dbg_v2
- mtk_swpm_cpu_dbg_v6878
- mtk_swpm_dbg_common_v1
- mtk_swpm_dbg_v6878
- mtk_vcodec_enc_v1

mtk_cam_isp7sp is built from:

  CAM_MODULE := mtk-cam-isp7sp

and the MT6878 build specifically includes:

  mtk_cam-plat-mt6878.o

mtk_lpm_plat_v1 is generated from:

  MTK_LPM_MODULE_PLATFORM_PLAT_NAME=v1
  BUILD_MTK_LPM_PLAT_MODUDLE_NAME=mtk-lpm-plat-${MTK_LPM_MODULE_PLATFORM_PLAT_NAME}

which produces mtk-lpm-plat-v1.ko, corresponding to stock
mtk_lpm_plat_v1.ko after module-name normalization.

### Remaining special-handling set

The remaining source-port/reconstruction questions are now:

- aw36515
- aw36518
- aw36518_v2
- aw883xx_driver
- focaltech_touch_spi_ft3680
- leds_rgb_aw2013
- lpm_gov_MHSP
- uarthub_drv

This is the practical Phase 3 boundary.

UARTHUB deserves special treatment:

Nothing builds an exact uarthub_drv target and recognizes
"mediatek,mt6878-uarthub", but that compatible maps to an empty
undef_plat_data operations structure.

Concrete UARTHUB platform implementations in this donor tree are present only
for MT6985 and MT6989.

Therefore Nothing supplies the generic UARTHUB framework but does not currently
provide a proven MT6878 platform backend.


## MHSP governor closure

The final MHSP build wiring is now resolved.

Kconfig defines:

  CONFIG_MTK_CPU_IDLE_GOV_VERSION default "MHSP"

The MHSP Makefile defines:

  LPM_CPUIDLE_GOV_NAME=lpm-gov-${CONFIG_MTK_CPU_IDLE_GOV_VERSION}
  obj-$(CONFIG_MTK_CPU_IDLE_GOV) += ${LPM_CPUIDLE_GOV_NAME}.o

Therefore the Nothing tree builds:

  lpm-gov-MHSP.ko

which corresponds directly to stock:

  lpm_gov_MHSP.ko

after hyphen/underscore module-name normalization.

lpm_gov_MHSP is therefore removed from the special-handling set.

## UARTHUB MT6985 reuse hypothesis

The stock GQ5012BF1 uarthub_drv.ko exports the expected full UARTHUB public API
and depends on mtk_disp_notify.

Nothing's published UARTHUB framework recognizes the MT6878 compatible but maps
it to an empty undef_plat_data structure, while concrete platform
implementations exist for MT6985 and MT6989.

Unexpectedly, the stock GQ5012BF1 binary contains MT6985-specific identifiers,
including:

  uarthub_get_hwccf_univpll_on_info_mt6985
  g_enable_apuart_debug_info_mt6985

This raises a strong but currently unproven hypothesis that the Ulefone MT6878
build reuses the MT6985 UARTHUB backend.

The next test is exact comparison of MT6985 source function/register
identifiers against the stock binary.


## AW2013 stock filename and vendor-fork evidence

The stock module's ELF/module name is normalized as:

  leds_rgb_aw2013

but its actual vendor_boot filename is:

  leds-rgb-aw2013.ko

Location:

  vendor_boot PLATFORM / lib/modules/leds-rgb-aw2013.ko

Stock SHA256:

  97c86e3b3dd038c4fc90b73315aac966087a852d604f103fc166076bd28f7549

The earlier direct filesystem lookup failed because it searched for
leds_rgb_aw2013.ko rather than the actual hyphenated filename.

The stock module uses DT compatible:

  awinic,rgb,aw2013

whereas the common/Nothing AW2013 driver uses:

  awinic,aw2013

The stock ABI inventory also shows additional power-supply, GPIO and DT APIs
that warrant explicit source comparison.

AW2013 should therefore be treated as a probable vendor fork of the common
AW2013 driver until contract equivalence is tested.


## AW2013 vendor fork confirmed

Direct stock-to-Nothing comparison confirms that leds_rgb_aw2013 is not a
drop-in instance of the common leds-aw2013 driver.

Stock:

- actual filename: leds-rgb-aw2013.ko
- module name: leds_rgb_aw2013
- author: Nikita Travkin <nikitos.tr@gmail.com>
- description: AW2013 LED driver
- compatible: awinic,rgb,aw2013
- imports: 27 kernel symbols

Stock-specific behavior/identifiers include:

- yft_aw2013_parse_dts
- aw2013-pwd-gpio
- led-fixed-brightness
- led_aw2103_boot_mode
- power_supply_get_by_name
- power_supply_get_property
- raw GPIO request/read/output handling

The following stock-used APIs are all absent from Nothing's common
leds-aw2013.c:

- power_supply_get_by_name
- power_supply_get_property
- of_find_node_opts_by_path
- of_get_named_gpio
- gpio_request
- gpio_to_desc
- gpiod_direction_output_raw
- gpiod_get_raw_value

Nothing/common uses compatible:

  awinic,aw2013

while stock uses:

  awinic,rgb,aw2013

Classification:

  RELATED_DIRECT_SOURCE_FAMILY / NEEDS_ULEFONE_PORT

The common AW2013 driver supplies the chip/register/LED implementation.
The remaining work is reconstruction of Ulefone/YFT DT, GPIO, power-supply and
boot-mode glue rather than reconstruction of the whole driver.

## UARTHUB donor identity

Further comparison shows the stock uarthub_drv.ko contains both MT6985 and
MT6989 platform implementations.

Nothing's Makefile likewise builds both platform implementations whenever
their source files are present.

Stock string counts:

- MT6835: 1
- MT6878: 1
- MT6886: 1
- MT6897: 1
- MT6983: 1
- MT6985: 141
- MT6989: 146

The single hits for the unsupported SoCs correspond to OF compatible strings,
whereas MT6985 and MT6989 have substantial implementation-specific content.

Of 74 MT6985-specific identifiers extracted from the Nothing donor source,
70 occur exactly in the stock binary.

ELF symbol inspection additionally proves the stock binary contains concrete:

- mt6985_plat_data
- mt6989_plat_data
- extensive *_mt6985 implementation functions
- extensive *_mt6989 implementation functions
- undef_plat_data
- apuarthub_of_ids

Therefore the Nothing UARTHUB tree is a very-high-confidence direct source
family for the stock binary.

The stock ELF relocation table resolves the OF platform-data mapping
definitively.

apuarthub_of_ids relocation offsets show:

- MT6835 -> undef_plat_data
- MT6878 -> undef_plat_data
- MT6886 -> undef_plat_data
- MT6897 -> undef_plat_data
- MT6983 -> undef_plat_data
- MT6985 -> mt6985_plat_data
- MT6989 -> mt6989_plat_data

Therefore stock GQ5012BF1 does not reuse the MT6985 or MT6989 UARTHUB backend
for MT6878.

The live stock device tree also contains:

- compatible = mediatek,mt6878-uarthub
- uarthub-disable property

The property was subsequently decoded as big-endian u32 value 1, proving
that UARTHUB is intentionally disabled in the stock GQ5012BF1 configuration.


## UARTHUB closed: intentionally disabled on GQ5012BF1

The stock live device tree property was decoded directly:

  /uarthub/uarthub-disable

Raw bytes:

  00 00 00 01

Big-endian value:

  uarthub-disable = 1

The stock module ELF relocation table also proves:

- MT6835 -> undef_plat_data
- MT6878 -> undef_plat_data
- MT6886 -> undef_plat_data
- MT6897 -> undef_plat_data
- MT6983 -> undef_plat_data
- MT6985 -> mt6985_plat_data
- MT6989 -> mt6989_plat_data

Therefore GQ5012BF1 does not select either the MT6985 or MT6989 UARTHUB
platform backend.

The published MediaTek/Nothing driver logic reads either:

  uarthub_disable
  uarthub-disable

and sets:

  g_uarthub_disable = ((uarthub_disable == 0) ? 0 : 1)

During initialization:

  uarthub_core_check_disable_from_dts(g_uarthub_pdev);

  if (g_uarthub_disable == 1)
      return 0;

Thus the stock configuration intentionally disables UARTHUB before platform
operations are required.

Most exported UARTHUB operational APIs similarly return 0 immediately when
g_uarthub_disable == 1.

Final classification:

  EXACT_SOURCE_FAMILY / INTENTIONALLY_DISABLED_ON_GQ5012BF1

UARTHUB requires no MT6878 backend reconstruction for stock-equivalent
LieppOS operation and is removed from the special-handling set.

