
## Initial stock-vs-NothingOSS evidence

Stock module SHA256:

`30abac643ebc7428a5ff350741d22b0f4bdcf65a5a071f55ec7ba78d862ca750`

Stock metadata:

- module: `tcpc_mt6375`
- version: `1.0.3`
- author: Gene Chen <gene_chen@richtek.com>
- description: MT6375 USB Type-C Port Controller Interface Driver
- DT compatible: `mediatek,mt6375-tcpc`
- dependencies: `tcpc_class,pd_dbg_info`
- srcversion: `D27BCF95DDC8F09B632224B`

Primary NothingOSS source candidate:

`device_modules/drivers/misc/mediatek/typec/tcpc/tcpc_mt6375.c`

NothingOSS MT6878 DTS contains:

`compatible = "mediatek,mt6375-tcpc"`

The stock binary contains the same major MT6375 feature set visible in the
NothingOSS source, including:

- Type-C CC handling
- USB PD transmit/receive
- VCONN
- VBUS short-to-CC detection
- water detection
- FOD
- cable-type detection
- Type-C OTP
- hidden/CC-high detection
- low-power mode
- vendor-defined alert handling

### Dependency classification

The non-GKI imports are dominated by the MediaTek TCPC framework.

`tcpc_class` supplies the `tcpc_*`, `tcpci_*`, and `tcpm_*` APIs.

`pd_dbg_info` supplies:

- `pd_dbg_info`

Therefore `tcpc_mt6375` should not yet be reverse engineered or built against
fake symbol contracts.

Current classification:

`LIKELY_DIRECT_SOURCE_MATCH`

Next step:

1. validate/rebuild `tcpc_class`
2. validate/rebuild `pd_dbg_info`
3. build unchanged `tcpc_mt6375.c` against those exact dependency contracts

## Dependency stack resolved

The Type-C stack dependency order is:

`pd_dbg_info -> tcpc_class -> tcpc_mt6375`

with `tcpc_mt6375` also importing `pd_dbg_info` directly.

`tcpc_class.ko` imports `pd_dbg_info` with MODVERSION CRC:

`0x48fb7437`

`tcpc_mt6375.ko` imports the same symbol with the same CRC:

`0x48fb7437`

The remaining non-GKI imports of `tcpc_mt6375` are 21 APIs provided by
`tcpc_class`, including the required `tcpc_*`, `tcpci_*`, and `tcpm_*`
interfaces.

This confirms a coherent stock Type-C framework ABI and establishes the
correct source-validation order:

1. pd_dbg_info
2. tcpc_class
3. tcpc_mt6375

## tcpc_class composition resolved

Stock `tcpc_class.ko` corresponds to the NothingOSS MediaTek TCPC framework.

The NothingOSS Kbuild composition contains 34 objects:

Base framework:

- tcpci_core.o
- tcpci_typec.o
- tcpci_timer.o
- tcpm.o
- tcpci.o
- tcpci_alert.o
- rt-regmap.o

USB Power Delivery layer:

- tcpci_event.o
- pd_core.o
- pd_policy_engine.o
- pd_process_evt.o
- pd_dpm_core.o
- pd_dpm_alt_mode_dp.o
- pd_dpm_pdo_select.o
- pd_dpm_reaction.o
- pd_process_evt_snk.o
- pd_process_evt_src.o
- pd_process_evt_vdm.o
- pd_process_evt_drs.o
- pd_process_evt_prs.o
- pd_process_evt_vcs.o
- pd_process_evt_dbg.o
- pd_process_evt_tcp.o
- pd_process_evt_com.o
- pd_policy_engine_src.o
- pd_policy_engine_snk.o
- pd_policy_engine_ufp.o
- pd_policy_engine_vcs.o
- pd_policy_engine_dfp.o
- pd_policy_engine_dr.o
- pd_policy_engine_drs.o
- pd_policy_engine_prs.o
- pd_policy_engine_dbg.o
- pd_policy_engine_com.o

Stock clearly contains the USB-PD portion.

Stock `tcpc_class.ko` depends only on:

`pd_dbg_info`

Expected CRC:

`0x48fb7437`

The reconstructed exact-match `pd_dbg_info.ko` exports exactly:

`0x48fb7437`

Therefore the Type-C framework can now be rebuilt against the real reconstructed
dependency rather than a fake symbol contract.

Current classification:

`tcpc_class.ko`: LIKELY_DIRECT_SOURCE_MATCH

No reverse engineering is justified before an unchanged-source build using the
correct MediaTek config/include environment.

## First tcpc_class standalone build blocker

The complete public NothingOSS TCPC object composition was staged and compiled
against exact GKI 12901745 with the reconstructed exact-match `pd_dbg_info`
dependency.

Compilation reached the individual TCPC/PD sources but failed because numerous
Richtek/MediaTek private compile-time feature macros were undefined, including:

- CONFIG_USB_PD_REV30
- CONFIG_USB_PD_REV30_CHUNKING_BY_PE
- CONFIG_USB_PD_VCONN_STABLE_DELAY
- CONFIG_USB_PD_VCONN_SAFE5V_ONLY
- CONFIG_USB_PD_SAFE0V_DELAY
- CONFIG_USB_PD_SAFE0V_TIMEOUT
- CONFIG_USB_PD_SAFE5V_DELAY
- CONFIG_USB_PD_RETRY_CRC_DISCARD
- CONFIG_USB_PD_VBUS_STABLE_TOUT
- CONFIG_USB_PD_WAIT_BC12
- CONFIG_USB_PD_CUSTOM_VDM
- CONFIG_USB_PD_DFP_READY_DISCOVER_ID
- CONFIG_TYPEC_CAP_NORP_SRC

The build also reports `PD_CABLE_CURR_UNKNOWN` as undeclared; this is currently
treated as a downstream consequence of the missing PD feature-definition state.

This failure pattern affects many translation units simultaneously and is
therefore classified as a missing vendor TCPC configuration layer, not evidence
of source divergence.

No donor C source has been modified.

Next step:

Map each undefined CONFIG macro to the NothingOSS TCPC configuration headers or
Kconfig definitions and reproduce the original vendor feature matrix before any
source changes or reverse engineering.

## tcpc_class compilation reached modpost

After adding the root-level private header `pd_dpm_prv.h` to the Kleaf `srcs`,
the complete `tcpc_class` source set compiled successfully and linked into:

`tcpc_class.ko`

The only remaining failure occurred during modpost:

`"pd_dbg_info" [tcpc_class.ko] undefined`

This is not a source, header, or configuration failure.

The Kleaf target already declares:

`//lieppos/pd-dbg-info-recon:pd_dbg_info_gki`

as a `kernel_module` dependency.

For legacy `kernel_module` rules, Kleaf restores the dependency
`Module.symvers`, but Kbuild/modpost must also receive that file through:

`KBUILD_EXTRA_SYMBOLS`

Therefore the next change is limited to the standalone Makefile wrapper,
passing the restored reconstructed `pd_dbg_info` `Module.symvers` into the
recursive kernel build.

At this point the following have been proven sufficient to compile all
`tcpc_class` translation units:

- exact Google GKI 12901745
- complete NothingOSS TCPC source composition
- MediaTek `CONFIG_TCPC_CLASS=m` semantics
- MediaTek `CONFIG_USB_POWER_DELIVERY=m` semantics
- private TCPC/PD feature headers
- root-level `pd_dpm_prv.h`
- reconstructed exact-match `pd_dbg_info`

No `tcpc_class` donor C source has been modified.

Current classification remains:

`LIKELY_DIRECT_SOURCE_MATCH`

## First successful tcpc_class rebuild — source/config mismatch confirmed

The complete NothingOSS `tcpc_class` framework now builds successfully against
exact Google GKI 12901745.

The reconstructed exact-match `pd_dbg_info` dependency resolves correctly:

`0x48fb7437`

The build-system work is therefore solved.

However, the rebuilt NothingOSS framework is not stock-equivalent.

Stock:

`version: 2.0.31_MTK`

Current NothingOSS donor:

`version: 2.0.27_MTK`

Stock `tcpc_mt6375` requires 21 `tcpc_class` exports.

Current donor result:

- 17 required symbols are exported but all have CRCs different from stock
- 4 required symbols are missing:
  - `tcpc_typec_handle_wd`
  - `tcpm_check_suspend_pending`
  - `tcpm_resume`
  - `tcpm_suspend`

The import sets also differ materially.

Stock-only examples:

- `___ratelimit`
- `mutex_trylock`
- `mutex_is_locked`
- `class_create_file_ns`

Current donor-only examples:

- `__pm_relax`
- `pm_wakeup_ws_event`
- `wakeup_source_register`
- `wakeup_source_unregister`
- `devm_power_supply_get_by_phandle`
- `__const_udelay`

This proves that remaining differences are no longer GKI/Kleaf/build-wrapper
issues.

Current classification:

`SOURCE_REVISION_MISMATCH + CONFIG_MISMATCH`

Before binary reconstruction:

1. search all local/public donor history for `2.0.31_MTK`;
2. recover Ulefone's TCPC feature configuration from stock;
3. especially investigate water-detection and TCPC suspend/resume guards;
4. rebuild with evidence-backed stock config;
5. only then determine the residual source delta.

No tcpc_class donor C source has been modified.

## tcpc_class config/source split confirmed

Further analysis separated configuration drift from source revision drift.

### Ulefone stock water detection

Stock `tcpc_class.ko` exports:

- `tcpc_typec_handle_wd`
- `tcpci_notify_wd_status`
- `tcpci_set_water_protection`

Stock `tcpc_mt6375.ko` imports:

- `tcpc_typec_handle_wd`

The public NothingOSS source already contains the full
`tcpc_typec_handle_wd()` implementation, guarded by:

`CONFIG_WATER_DETECTION`

which is derived from:

`CONFIG_MTK_TYPEC_WATER_DETECT`

NothingOSS `mgk_64_k61_defconfig` disables that option, while Ulefone stock
clearly had the feature enabled.

Therefore `CONFIG_MTK_TYPEC_WATER_DETECT` is a proven Ulefone stock build
configuration difference and must be enabled in the stock-target validation
build.

### Genuine source revision additions

The following stock-exported APIs do not exist anywhere in the public
NothingOSS 2.0.27_MTK donor tree:

- `tcpm_suspend`
- `tcpm_resume`
- `tcpm_check_suspend_pending`

NothingOSS local files and complete git history contain no `2.0.31_MTK`
revision.

Stock identifies the framework as:

`2.0.31_MTK`

Public donor identifies itself as:

`2.0.27_MTK`

Therefore the remaining delta includes genuine post-2.0.27 source changes in
addition to Ulefone-specific configuration.

Next sequence:

1. rebuild 2.0.27 donor with proven stock water-detection config;
2. re-evaluate ABI/export CRC differences;
3. freeze that result as the reconstruction baseline;
4. reconstruct only the residual 2.0.27 -> 2.0.31 delta against stock.

Do not reverse engineer config-driven differences.

## Water-enabled reconstruction baseline

Ulefone's proven stock water-detection configuration was enabled in the
NothingOSS 2.0.27 exact-GKI baseline.

The build exports the previously missing water APIs, confirming that the
missing `tcpc_typec_handle_wd` symbol was configuration-driven.

Water-enabled baseline exports include:

- `tcpc_typec_handle_wd`: `0xe5432845`
- `tcpci_set_water_protection`: `0xc1e3e3d6`
- `tcpci_notify_wd_status`: `0xa3df0685`

Stock `tcpc_mt6375.ko` requires:

- `tcpc_typec_handle_wd`: `0x117b6a26`

Therefore enabling the correct feature restores the symbol but not the stock
ABI. A genuine source/header/structure revision delta remains.

Stock-only PM API evidence:

- `tcpm_check_suspend_pending`
  - size: 84 bytes
  - CRC required by mt6375: `0x446dd691`

- `tcpm_suspend`
  - size: 148 bytes
  - CRC required by mt6375: `0x1ccba3ae`

- `tcpm_resume`
  - size: 56 bytes
  - CRC required by mt6375: `0xf7af27dd`

Stock PM disassembly shows a suspend-admission protocol based on two activity
states, `tcpc_get_timer_tick()`, a suspend flag, and a resume waitqueue.

The NothingOSS 2.0.27 donor already contains `atomic_t suspend_pending` and
increments/decrements it in `tcpci_event.c`, but lacks the three exported PM
APIs and does not expose the stock `resume_wait_que` mechanism.

The remaining work is now classified as targeted reconstruction of the
2.0.27_MTK -> 2.0.31_MTK framework delta.

## tcpc_class reconstruction strategic result

A public MediaTek TCPC `2.0.31_MTK` source revision was located during
reconstruction:

- repository: `MiCode/MTK_kernel_device_modules`
- branch: `bsp-chagall-w-oss`
- commit: `2d6f27aa19d521409f443c8d821e2d475bdc72b6`

Additional public 2.0.31 branches were also identified.

After removing vendor-only Xiaomi additions and reconstructing Ulefone-specific
behavior, the resulting `tcpc_class` has:

- exact 707-function defined set
- 696/707 exact function sizes
- 632/707 byte-identical functions
- exact import set
- exact imported MODVERSION CRCs
- exact `struct tcpc_device` allocation size (`0x35a8`)
- exact 31-slot `struct tcpc_ops` layout (`0xf8`)
- byte-exact recovered suspend/resume APIs
- recovered Ulefone `yft_tcpc_polarity` class attribute
- stock version `2.0.31_MTK`

Remaining differences:

- all 21 `tcpc_mt6375`-required export CRCs differ from stock
- 11 functions retain genuine source-level differences
- final `.text` is +600 bytes versus stock

The export CRC mismatch appears to originate from unrecoverable name-level
vendor header metadata despite matching measurable layout.

For a fully rebuilt LieppOS Type-C stack, matching stock export CRC values is
not intrinsically required: dependent modules rebuilt against the reconstructed
headers will naturally consume the reconstructed CRC contract.

However, any remaining proprietary stock consumer of `tcpc_class` would still
require stock-compatible CRCs. Therefore the complete stock consumer boundary
must be enumerated before permanently adopting the reconstructed ABI.

Current classification:

`STRUCTURALLY_MATCHED_RECONSTRUCTION / COHERENT_SOURCE_ABI_CANDIDATE`

It should not yet be called behaviorally exact because 11 function-level
source differences remain.

Next:

1. enumerate all stock `tcpc_class` consumers;
2. rebuild `tcpc_mt6375` from the public 2.0.31 source against reconstructed
   `tcpc_class`;
3. validate its ABI, function sizes and behavior against stock;
4. decide whether remaining TCPC consumers will also be rebuilt or whether
   exact stock genksyms compatibility must be pursued.

## tcpc_class consumer boundary

The complete stock module boundary consuming `tcpc_class` has been enumerated.

Seven stock modules import TCPC framework APIs:

| Module | TCPC APIs imported |
|---|---:|
| `tcpc_mt6375.ko` | 21 |
| `rt_pd_manager.ko` | 15 |
| `mtk_pd_adapter.ko` | 15 |
| `mtk_chg_type_det.ko` | 6 |
| `extcon-mtk-usb.ko` | 3 |
| `tcpci_late_sync.ko` | 2 |
| `mt6375-charger.ko` | 2 |

Therefore a LieppOS-specific reconstructed `tcpc_class` ABI is viable only if
the complete consumer boundary that remains enabled is rebuilt against that
same reconstructed header/API contract.

Do not mix these stock consumers with the reconstructed `tcpc_class` unless
their imported MODVERSION CRCs are individually proven compatible.

## Public 2.0.31 tcpc_mt6375 donor evidence

The public MediaTek 2.0.31 source at:

`MiCode/MTK_kernel_device_modules`
`bsp-chagall-w-oss`
`2d6f27aa19d521409f443c8d821e2d475bdc72b6`

contains:

- suspend-aware `mt6375_read_helper`
- suspend-aware `mt6375_write_helper`
- `tcpm_suspend`
- `tcpm_check_suspend_pending`
- `tcpm_resume`
- `vbus_to_cc_dwork`
- water-detection integration
- FOD integration
- Type-C OTP integration
- `set_vbus_short_cc`
- revised TCPC ops compatible with the recovered 2.0.31 framework

Ulefone stock `tcpc_mt6375.ko` contains matching function/string fingerprints,
including:

- `mt6375_read_helper`
- `mt6375_write_helper`
- `mt6375_vbus_to_cc_dwork_handler`
- `mt6375_tcpc_suspend`
- `mt6375_tcpc_suspend_late`
- `mt6375_tcpc_resume`
- FOD / OTP / water paths
- `tcpm_suspend`
- `tcpm_check_suspend_pending`
- `tcpm_resume`

Current classification:

`tcpc_mt6375.ko = LIKELY_DIRECT_SOURCE_MATCH_2.0.31`

Build and binary validation are required before accepting that classification.

## Xiaomi `enable_io_boost` removal confirmed

The MiCode 2.0.31 MT6375 donor contained:

- static function `mt6375_enable_io_boost`
- `.enable_io_boost = mt6375_enable_io_boost` in `mt6375_tcpc_ops`

Stock Ulefone `tcpc_mt6375.ko` contains no
`mt6375_enable_io_boost` symbol.

After removing the initializer, the function became unused and the compiler
failed with `-Wunused-function`, proving that the callback is completely
isolated from the rest of the driver.

Therefore both the callback entry and its static implementation are confirmed
Xiaomi-only source and should be removed from the Ulefone stock-target donor.

This matches the previously reconstructed Ulefone `struct tcpc_ops` layout:

- 31 slots
- size `0xf8`
- no `enable_io_boost`
- no `set_watchdog`

No reverse engineering is required for this difference.

## MiCode 2.0.31 MT6375 Xiaomi-only ops trim

The first build of the public MiCode 2.0.31 `tcpc_mt6375.c` against the
reconstructed Ulefone `tcpc_class` failed on:

`struct tcpc_ops.enable_io_boost`

This is expected and confirms a previously recovered framework difference.

Stock Ulefone `mt6375_tcpc_ops` is exactly 31 slots / 0xf8 bytes and does not
contain the Xiaomi-only callbacks:

- `enable_io_boost`
- `set_watchdog`

The reconstructed Ulefone `tcpc_class` intentionally removed those fields.

Therefore the MiCode MT6375 donor must also have those Xiaomi-only initializer
entries removed before it can be evaluated as a Ulefone 2.0.31 source donor.

This remains a source-fork trimming issue, not reverse engineering.

## Standalone Kleaf modules_install wrapper fix

After removing the confirmed Xiaomi-only `enable_io_boost` callback and static
implementation, `tcpc_mt6375.c` passed source compilation.

The next failure was:

`make: *** No rule to make target 'modules_install'. Stop.`

This is a standalone wrapper issue only.

Kleaf invokes the external module's `modules_install` target after building the
module, so the wrapper must expose both:

- `modules`
- `modules_install`

and pass the reconstructed `tcpc_class` and exact reconstructed `pd_dbg_info`
`Module.symvers` through `KBUILD_EXTRA_SYMBOLS` for both targets.

No additional MT6375 source divergence was indicated by this failure.

## First successful 2.0.31 MT6375 rebuild

The public MediaTek 2.0.31 `tcpc_mt6375.c`, after removing the previously
proven Xiaomi-only `enable_io_boost` callback/function, builds successfully
against:

- exact Google GKI 12901745
- reconstructed Ulefone `tcpc_class` 2.0.31
- exact reconstructed `pd_dbg_info`

Driver identity matches stock:

- name: `tcpc_mt6375`
- version: `1.0.3`
- dependencies: `tcpc_class,pd_dbg_info`

Stock license metadata is `GPL v2`; current public donor reports `GPL`.

Import comparison is extremely close:

- every stock import is present except `tcpc_typec_handle_fod`
- no unrelated extra import was observed

Only five functions currently differ in size:

- `mt6375_fod_irq_handler`
  - stock `0x114`
  - rebuilt `0x0c0`
  - delta `-0x54` / -84 bytes

- `mt6375_pd_evt_handler`
  - stock `0x54`
  - rebuilt `0x60`
  - +12 bytes

- `mt6375_set_low_power_mode`
  - stock `0x1b4`
  - rebuilt `0x1f0`
  - +60 bytes

- `mt6375_tcpc_init`
  - stock `0x4e8`
  - rebuilt `0x4f4`
  - +12 bytes

- `mt6375_tcpc_probe`
  - stock `0x954`
  - rebuilt `0x95c`
  - +8 bytes

The FOD difference is especially constrained. Public 2.0.31 source contains a
commented `tcpc_typec_handle_fod()` framework handoff while Ulefone stock
imports `tcpc_typec_handle_fod`, and the stock FOD IRQ handler is 84 bytes
larger.

Current classification:

`NEAR_DIRECT_2.0.31_SOURCE_MATCH / SMALL_ULEFONE_VARIANT_DELTA`

Next:

1. prove the stock FOD call by relocation/disassembly;
2. check sibling public 2.0.31 branches for the active FOD implementation;
3. restore the source-backed FOD path;
4. revalidate imports/function sizes;
5. compare only the four remaining residual functions.

No Codex reconstruction is justified yet because the remaining differences may
still be recoverable directly from public 2.0.31 variants.

## Type-C core reconstruction milestone

`tcpc_mt6375.ko` reconstruction is complete.

Final result:

- 66/66 functions byte-identical
- `.text` byte-identical to stock
- `.init.text` / `.exit.text` identical
- `.rodata`, `.rodata.str1.1`, `.data` identical
- all resolved relocations identical
- imports identical
- all import MODVERSION CRCs identical
- reconstructed `tcpc_class` / `pd_dbg_info` provider coherence exact

Classification:

`BYTE_EXACT_CODE_RECONSTRUCTION / FROZEN`

`tcpc_class.ko` was also upgraded during the MT6375 reconstruction.

Consumer-side struct-offset evidence identified MiCode-only fields in
`struct tcpc_device` and `struct pd_port`. Removing those fields caused the
reconstructed TCPC framework to naturally reproduce all 21 stock CRCs consumed
by `tcpc_mt6375`.

Final tcpc_class state:

- 21/21 MT6375-required stock export CRCs exact
- no CRC tables edited
- 707/707 functions present
- 699/707 functions byte-identical
- exact import set
- exact import MODVERSION CRCs
- exact `struct tcpc_device` allocation size
- exact 31-slot `struct tcpc_ops`

Classification:

`ABI_EXACT_RECONSTRUCTION`

The previous plan to automatically rebuild every stock TCPC consumer against a
new LieppOS CRC namespace is no longer assumed necessary.

Next step:

Audit the remaining six stock `tcpc_class` consumers against the reconstructed
provider's natural Module.symvers.

If their imported TCPC CRCs already match, they may remain stock during early
custom-kernel integration and do not need immediate reconstruction.

## Complete stock TCPC consumer ABI audit

The remaining six stock consumers were audited against the natural
`Module.symvers` generated by the reconstructed `tcpc_class`.

Results:

| Consumer | TCPC imports | Exact | Mismatch |
|---|---:|---:|---:|
| `rt_pd_manager.ko` | 15 | 15 | 0 |
| `mtk_pd_adapter.ko` | 15 | 15 | 0 |
| `mtk_chg_type_det.ko` | 6 | 6 | 0 |
| `extcon-mtk-usb.ko` | 3 | 3 | 0 |
| `tcpci_late_sync.ko` | 2 | 2 | 0 |
| `mt6375-charger.ko` | 2 | 2 | 0 |

Total:

`43 / 43 exact, 0 mismatches`

Together with the 21 TCPC imports of the byte-exact reconstructed
`tcpc_mt6375.ko`, the complete seven-module TCPC consumer boundary is:

`64 / 64 exact`

Therefore the reconstructed `tcpc_class` preserves the stock ABI namespace for
the complete known TCPC consumer stack.

The six consumers above can remain stock during initial LieppOS custom-kernel
integration. Rebuilding them is deferred source-completeness work rather than
a bring-up requirement.

Type-C core status:

- `pd_dbg_info`: exact reconstruction / frozen
- `tcpc_class`: stock-ABI-exact reconstruction / ABI frozen
- `tcpc_mt6375`: byte-exact reconstruction / frozen
- six remaining consumers: stock ABI-compatible

Phase status:

`TYPE-C CORE COMPLETE FOR INITIAL CUSTOM-KERNEL INTEGRATION`

## Superseded by final reconstruction report

This file records the historical dependency-resolution, build-environment and
source-comparison work for the MT6375 TCPC driver.

Authoritative final report:

    kernel/phase4-tcpc-mt6375-reconstruction.md

Final classification:

    BYTE_EXACT_CODE_RECONSTRUCTION

The final reconstruction has 66/66 byte-identical functions, byte-identical
code/data-bearing sections, resolved relocations matching stock, and exact
import MODVERSION CRCs.

Keep this file as historical provenance for the dependency-stack and build
investigation only.
