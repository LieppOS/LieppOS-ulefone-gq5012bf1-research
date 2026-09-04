# Phase 4: Android Common 6.1.115 buildability

## Baseline

Authoritative GKI core:

- Linux 6.1.115
- Android KMI generation android14-11
- Android Common commit:
  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
- Android CI build:
  12901745
- target:
  kernel_aarch64

The stock GQ5012BF1 boot kernel is bit-for-bit identical to the published
Google Image.lz4 from this build.

All 2,946 observed stock kernel-facing CONFIG_MODVERSIONS requirements match
the exact Google vmlinux.symvers.

Therefore Phase 4 does not attempt to recreate a proprietary Ulefone kernel
core.

The task is to validate and forward-port MediaTek/Nothing device-module source
onto this exact 6.1.115 GKI baseline.

## Phase 3 result

The broad source-discovery problem is complete.

Remaining hardware-specific port tracks:

- aw36515
- aw36518
- aw36518_v2
- aw883xx_driver
- focaltech_touch_spi_ft3680
- leds_rgb_aw2013

UARTHUB is excluded from the required-port set because stock GQ5012BF1 has:

  uarthub-disable = <1>

and the stock MT6878 OF entry resolves to undef_plat_data.

## Phase 4 classification

Each candidate should eventually receive:

- source origin
- source path
- build target
- Kconfig symbol
- stock placement
- module dependencies
- kernel imports
- module-to-module dependencies
- MT6878 specificity
- expected 6.1.115 compatibility
- actual compile result
- required source changes
- runtime/test priority

Compile-result states:

- NOT_TESTED
- BUILDS_CLEAN
- BUILDS_WITH_WARNINGS
- BUILD_SYSTEM_BLOCKED
- HEADER_API_BREAK
- KERNEL_API_BREAK
- CONFIG_DEPENDENCY
- MISSING_GENERATED_FILE
- MISSING_FIRMWARE_INTERFACE
- LINK_SYMBOL_FAILURE
- NEEDS_ULEFONE_PORT
- NOT_REQUIRED

## Initial strategy

Do not begin with the entire MT6878 BSP.

First validate:

1. exact Android Common build environment
2. small/simple Nothing donor modules
3. foundational MediaTek infrastructure
4. connectivity
5. charging / TCPC
6. display notifier and peripherals
7. camera/GPU/media
8. Ulefone-specific ports

Stock binaries remain valid transition fallbacks because exact GKI KMI
compatibility has already been proven.


## First-batch source/build discovery

Initial Phase 4 inspection established:

### mtk_disp_notify

Nothing contains two source copies:

- drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c
- drivers/gpu/drm/mediatek/dummy_drm/mtk_disp_notify.c

Both are wired through CONFIG_DEVICE_MODULES_DRM_MEDIATEK.

Their exact source equivalence must be checked before choosing the canonical
donor path.

### ST21 NFC

Direct target:

  CONFIG_NFC_ST21NFC -> st21nfc.o

Source:

  drivers/misc/mediatek/nfc/st21nfc/st21nfc.c

This is a strong small first compilation candidate.

### MediaTek tinysys IPI / mailbox

Direct targets:

  CONFIG_MTK_IPI  -> mtk_tinysys_ipi.o
  CONFIG_MTK_MBOX -> mtk-mbox.o

The separate:

  mtk-mbox-mailbox.o

is a different mailbox driver and must not be confused with stock mtk_mbox.

These modules should be dependency-tested together before compilation.

### Connectivity dependency hierarchy

connfem is an explicit composite module target.

conninfra is a major connectivity symbol/header provider.

WLAN, Bluetooth and GPS build definitions consume conninfra and/or connfem
headers and Module.symvers.

Therefore conninfra/WLAN are not suitable as the first proof-of-build targets.

The exact MT6878 WLAN target is:

  wlan_drv_gen4m_6878

but its implementation is shared from the generic gen4m source tree rather
than source files named after the final module.

### Initial compile candidate order

Tentative first validation order:

1. mtk_disp_notify
2. st21nfc
3. mtk_mbox
4. mtk_tinysys_ipi

Only after the exact 6.1.115 build environment is validated should the first
compilation attempt be made.


## First compile candidate refinement

### mtk_disp_notify source variant resolved

The two Nothing mtk_disp_notify implementations are not equivalent.

dummy_drm exports only:

- mtk_disp_notifier_register
- mtk_disp_notifier_unregister
- mtk_disp_notifier_call_chain

mediatek_v2 additionally exports:

- mtk_disp_sub_notifier_register
- mtk_disp_sub_notifier_unregister
- mtk_disp_sub_notifier_call_chain

The stock GQ5012BF1 mtk_disp_notify.ko exports all six symbols.

The mediatek_v2 header also contains fingerprint/UI notifier definitions that
are absent from dummy_drm.

Therefore the canonical GQ5012BF1 donor variant is:

  device_modules/drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c

Classification:

  DIRECT_SOURCE_VARIANT / mediatek_v2

The dummy_drm implementation is not contract-equivalent to stock and should
not be used.

### First compilation order

Revised validation order:

1. st21nfc
   - no stock module dependencies
   - self-contained Makefile/Kconfig
   - mostly standard Linux/I2C/NFC interfaces

2. mtk_disp_notify
   - no stock module dependencies
   - exact exported interface variant identified
   - requires local MediaTek DRM logging header

3. mtk_mbox
   - no stock module dependencies
   - requires MediaTek mtk-mbox.h and trace header overlay

4. mtk_tinysys_ipi
   - stock depends on mtk_rpmsg_mbox and mtk-mbox
   - should not be the first standalone build test

Heavy connectivity modules remain deferred.


## First-batch ABI dependency matrix

Stock ABI classification for the initial buildability batch:

| module | unique imports | kernel | intermodule | unknown |
| --- | ---: | ---: | ---: | ---: |
| mtk_disp_notify | 5 | 5 | 0 | 0 |
| st21nfc | 54 | 54 | 0 | 0 |
| tcpc_mt6375 | 63 | 41 | 22 | 0 |
| mtk_tinysys_ipi | 28 | 23 | 5 | 0 |
| mtk_mbox | 32 | 32 | 0 | 0 |
| connfem | 65 | 65 | 0 | 0 |
| conninfra | 194 | 175 | 19 | 0 |
| gps_pwr | 24 | 21 | 3 | 0 |
| gps_scp | 31 | 26 | 5 | 0 |
| wlan_drv_gen4m_6878 | 390 | 295 | 95 | 0 |

All ten have zero unclassified stock imports.

This confirms that the Phase 2 kernel-vs-module ABI split provides complete
dependency classification for the Phase 4 candidate set.

The first standalone compile candidates are therefore:

1. st21nfc
2. mtk_disp_notify
3. mtk_mbox

connfem is also kernel-only from the stock ABI perspective, but is deferred
until the basic external-module build pipeline is validated because of its
larger source/build surface.


## Exact Android CI build workspace

The standalone Android Common checkout is not by itself the complete build
environment used for GKI CI build 12901745.

The exact manifest revision is:

  c6de413eac1ce136d34190e99a34101c036fd3ad

Its default project revision is:

  main-kernel-build-2023

and the kernel/common project is explicitly on:

  android14-6.1-2024-12

However moving branch names are not used as the reproducibility authority.

Android CI BUILD_INFO supplies immutable revisions, including:

- kernel/common
  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09

- kernel/build
  c0156661aa24e62647ea34d21fbd13d2b93dd89c

- kernel/configs
  76dd129942d2d1a1ccaa3ea0effa682e9e1828ac

- kernel/prebuilts/build-tools
  e905be252a53d20c52bd9e59df3ff8fdd46b9eab

- platform/prebuilts/build-tools
  c181f690fe9b76142b3203c2ab959b6299d4d1fd

- platform/prebuilts/clang/host/linux-x86
  7775eb113f960bc69a780b621d03a715914d4bca

The manifest also proves that tools/bazel and the root WORKSPACE are linkfiles
provided by kernel/build rather than files expected inside kernel/common.

Therefore Phase 4 must reconstruct the CI workspace using:

1. exact manifest layout
2. exact CI project SHAs
3. manifest linkfiles

rather than compiling the isolated common tree with host tooling.


## BUILD_INFO pin extraction methodology

BUILD_INFO contains multiple JSON objects with generic fields named
"revision". These fields must not be globally interpreted as project names.

Exact project SHAs are extracted only from:

1. project records containing both:
   - name = project name
   - revision = 40-character SHA

2. project-name -> 40-character SHA mappings where the key itself is a
   repository/project name.

The Phase 4 extractor is:

  kernel/scripts/build_phase4_gki_pins.py

It writes output atomically so a parser failure cannot truncate a previously
valid pin table.

Output:

  kernel/phase4-gki-build-pins.tsv


## Historical kernel/common upstream ref handling

The initial exact-SHA workspace sync failed only for kernel/common.

The base CI manifest defines kernel/common with:

  revision="android14-6.1-2024-12"
  upstream="android14-6.1-2024-12"

The local CI lock correctly overrode revision to:

  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09

However Repo still used the inherited upstream hint while fetching and attempted:

  refs/heads/android14-6.1-2024-12

That historical branch is no longer advertised by the remote.

The exact stock GKI commit is associated with release tag:

  android14-6.1-2024-12_r4

Therefore the locked local manifest additionally overrides kernel/common
upstream to:

  refs/tags/android14-6.1-2024-12_r4

The authoritative revision remains the exact CI SHA; the tag is used only as a
stable fetch/ref reachability hint.


## Exact CI workspace reconstruction

The Android CI build 12901745 workspace was successfully reconstructed from:

- manifest revision:
  c6de413eac1ce136d34190e99a34101c036fd3ad

- all 20 project revisions extracted from BUILD_INFO

- manifest linkfile behavior

Initial synchronization failed only because the historical kernel/common
upstream branch:

  refs/heads/android14-6.1-2024-12

is no longer advertised remotely.

The exact release tag remains available:

  android14-6.1-2024-12_r4

Tag object:

  05364ffdd5ca7f72a7897d11c2ceb3df313ba93f

Peeled commit:

  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09

The local lock manifest therefore keeps the authoritative CI SHA as revision
and uses the release tag only as the stable upstream fetch hint.

kernel/common subsequently synchronized successfully and resolves exactly to:

  6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
  android14-6.1-2024-12_r4

A subsequent full 20-project repo sync completed successfully.


## Historical Kleaf workspace path constraint

The exact build 12901745 Kleaf wrapper failed before Bazel startup when the
workspace was located under a path containing spaces:

  .../LieppOS custom ROM/kernel-research/gki-12901745-workspace

Observed failure:

  tools/bazel: line 16: /home/armol: Is a directory

This affected even:

  tools/bazel --version
  tools/bazel query ...

Therefore this is a build-wrapper/path parsing issue, not a kernel target or
module compilation failure.

The exact pinned workspace is relocated intact to a path without spaces:

  $HOME/kernel-work/gki-12901745-workspace

No pinned source or build-tool revisions are modified.

## ST21 external-module harness

The Nothing donor Makefile gates ST21 with:

  obj-$(CONFIG_NFC_ST21NFC) += st21nfc.o

For the standalone GKI external-module compatibility test, the donor source is
left byte-identical while the test harness uses:

  obj-m += st21nfc.o

This isolates source/API compatibility from Nothing's device Kconfig.

The external Kleaf target uses:

  kernel_build = "//common:kernel_aarch64"

and expects:

  st21nfc.ko

No driver source modifications have been made.


## ST21 Kleaf target resolution

The standalone ST21 external-module harness successfully resolves under the
exact CI build 12901745 Kleaf workspace.

Target:

  //external/lieppos/st21nfc:st21nfc

Direct kernel build dependency:

  //common:kernel_aarch64

Bazel package/query analysis succeeds.

Therefore:

- historical Kleaf is operational
- the external package is valid
- kernel_module() syntax is correct
- //common:kernel_aarch64 resolves correctly
- the ST21 harness reaches the exact GKI build target

No module compilation has yet been performed.

### Historical Bazel invocation detail

The exact historical wrapper rejects:

  tools/bazel --version

as an unknown startup option.

This is not a wrapper failure: normal Bazel query operations succeed after
moving the workspace to a path without spaces.

Use:

  tools/bazel version

when version information is needed.

### Next optimization question

The exact common BUILD graph exposes targets including:

  //common:kernel_aarch64_downloaded
  //common:kernel_aarch64_download_or_build
  //common:kernel_aarch64_headers_downloaded

Before the first module compilation, Phase 4 will determine whether the
external kernel_module rule can consume exact downloaded CI kernel artifacts
instead of rebuilding the GKI kernel from source.


## Exact GKI prebuilt path for external modules

The exact build 12901745 Kleaf graph provides three distinct GKI interfaces:

  //common:kernel_aarch64
    rule type: _kernel_build

  //common:kernel_aarch64_downloaded
    rule type: filegroup

  //common:kernel_aarch64_download_or_build
    rule type: kernel_filegroup

kernel_aarch64_downloaded is only the raw downloaded artifact collection and
is not the intended kernel_build interface for an external kernel_module.

kernel_aarch64_download_or_build is the prebuilt-capable kernel interface.

Its srcs select between:

  //common:kernel_aarch64_downloaded

when use_prebuilt_gki is enabled, and:

  //common:kernel_aarch64

otherwise.

The exact historical Kleaf documentation states that:

  --use_prebuilt_gki=<build_number>

selects Android CI GKI artifacts.

For GQ5012BF1 the authoritative build number is:

  12901745

Therefore the preferred first compatibility experiment will use:

  kernel_build = "//common:kernel_aarch64_download_or_build"

with CI build:

  12901745

This avoids unnecessarily rebuilding the GKI core while preserving a second
source-GKI target for later reproducibility comparisons.

## ST21 MediaTek include-path assessment

The Nothing ST21 Makefile adds:

  -I$(DEVICE_MODULES_PATH)/drivers/misc/mediatek/include/mt-plat

However inspection of st21nfc.c and st21nfc.h found no MediaTek or mt-plat
header includes.

The source includes only standard Linux/NFC headers plus:

  st21nfc.h

MediaTek legacy I2C code is conditional on:

  KRNMTKLEGACY_I2C

Optional power-statistics code is conditional on:

  ST54J_PWRSTATS

Neither is enabled by the standalone external-module harness.

Therefore no MediaTek header overlay is presently required for the first ST21
compile compatibility test.

The donor C and header files remain byte-identical to NothingOSS source.


## Historical Kleaf prebuilt external-module incompatibility

Configured analysis of:

  //external/lieppos/st21nfc:st21nfc_ci_gki

with:

  --use_prebuilt_gki=12901745

fails inside the exact build 12901745 Kleaf implementation before any module
compilation occurs.

kernel_module requires its kernel_build target to provide:

  KernelBuildExtModuleInfo

and accesses:

  KernelBuildExtModuleInfo.strip_modules

The exact kernel_filegroup implementation does provide
KernelBuildExtModuleInfo, but its provider instance contains:

- modules_staging_archive
- modules_env_and_minimal_outputs_info
- modules_env_and_all_outputs_info
- modules_install_env_and_outputs_info
- module_hdrs
- module_scripts
- collect_unstripped_modules

and does NOT contain:

  strip_modules

Configured analysis therefore fails with:

  'KernelBuildExtModuleInfo' value has no field or method 'strip_modules'

This is a historical Kleaf provider-contract mismatch.

Classification:

  st21nfc_ci_gki: BUILD_SYSTEM_BLOCKED

This failure does NOT indicate:

- an ST21 source incompatibility
- a Linux 6.1.115 API incompatibility
- a missing Ulefone dependency
- a module symbol/KMI problem

No C compilation has occurred.

The exact source-backed target remains:

  //external/lieppos/st21nfc:st21nfc_source_gki

using:

  //common:kernel_aarch64

This target preserves the exact unmodified CI build-tool and kernel-source
environment and is therefore the preferred first actual compilation test.

The pinned historical Kleaf source will not be modified merely to optimize
the test through downloaded prebuilts.


## ST21 source-backed configured analysis

Configured analysis of:

  //external/lieppos/st21nfc:st21nfc_source_gki

completed successfully against:

  //common:kernel_aarch64

Result:

  Analyzed target successfully
  93,427 targets configured
  0 build actions executed

Therefore the source-backed ST21 target has passed:

- Bazel package resolution
- historical kernel_module rule analysis
- exact kernel_build provider validation
- exact GKI target configuration
- external-module dependency configuration

No C compilation has occurred yet.

Classification:

  st21nfc_source_gki: READY_FOR_COMPILE

The prebuilt-backed alternative remains:

  st21nfc_ci_gki: BUILD_SYSTEM_BLOCKED

because the historical kernel_filegroup implementation omits
KernelBuildExtModuleInfo.strip_modules while kernel_module requires it.

This provider mismatch is specific to the historical Kleaf build system and is
not evidence of a driver, kernel API, KMI, or Ulefone compatibility problem.

