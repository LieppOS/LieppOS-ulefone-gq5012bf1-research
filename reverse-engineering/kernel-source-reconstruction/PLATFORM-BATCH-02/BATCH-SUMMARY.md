# PLATFORM-BATCH-02 —27/27 source-certified

**Selected27; newly A27; newly B0; remaining batch C/D/G0.**
21 D and6 G moved to A only after full independent acceptance. No code/ABI residuals.
Totals: **187 certified /271 remaining /458 identities**; A186/B1/C8/D126/E0/F0/G137.
All431 unselected rows—including four Batch01 CMDQ C rows—are field-identical to baseline.
All owners/component statuses/runtime statuses/hashes/sizes/partition paths remain unchanged.
No firmware/runtime or production exclusion inferred.111 retained first-stage gaps remain.

Exact handoff frozen before implementation at2972afa. Manifest SHA256:
6b4245dadf20a2ca0cb10058313101ab5d37d53694b0d28cacef661b27301b6f.
Four coherent families:memory/interconnect7,PMIF/SPMI4,mailbox/TinySys6,power policy10.

## Every selected module

Exact counts/stock totals include initialized data and BSS layout. Every import/export CRC,
licence,namespace,KCFI ID,raw+semantic relocation,section/order/header/string/symbol table,
modinfo/vermagic/srcversion/signature byte outside the parsed GNU20-byte descriptor matches.
The shorthand source key identifies an exact compiled repository/commit below. Full machine
ledger:[BATCH-PARITY.tsv](BATCH-PARITY.tsv); per-module all-axis reports under family/evidence.

| Module | Initial class | Final class | Functions exact | Data exact | CRC/KCFI | Relocations | Maintained source | Residual |
|---|---|---|---|---|---|---|---|---|
| mtk-icc-core.ko | D | A | 35/35 | 47/47 | exact | 539 exact | IM | GNU ID only |
| emi.ko | D | A | 21/21 | 31/31 | exact | 500 exact | IM | GNU ID only |
| emi-mpu.ko | D | A | 11/11 | 19/19 | exact | 232 exact | IM | GNU ID only |
| emi-fake-eng.ko | D | A | 8/8 | 16/16 | exact | 239 exact | IM | GNU ID only |
| smpu.ko | D | A | 11/11 | 23/23 | exact | 400 exact | IM | GNU ID only |
| smpu-hook-v1.ko | D | A | 4/4 | 11/11 | exact | 72 exact | IM | GNU ID only |
| mtk_dramc.ko | D | A | 16/16 | 22/22 | exact | 358 exact | IM | GNU ID only |
| fhctl.ko | D | A | 39/39 | 210/210 | exact | 1471 exact | PP | GNU ID only |
| pd-chk-mt6878.ko | D | A | 18/18 | 48/48 | exact | 471 exact | PP | GNU ID only |
| spmi-mtk-mpu.ko | D | A | 7/7 | 31/31 | exact | 123 exact | PS | GNU ID only |
| spmi-mtk-pmif.ko | D | A | 62/62 | 76/76 | exact | 1424 exact | PS | GNU ID only |
| mtk-mbox.ko | G | A | 46/46 | 40/40 | exact | 542 exact | MT | GNU ID only |
| mtk-mbox-mailbox.ko | G | A | 10/10 | 14/14 | exact | 115 exact | MT | GNU ID only |
| mtk_rpmsg_mbox.ko | G | A | 8/8 | 12/12 | exact | 57 exact | MT | GNU ID only |
| mtk_tinysys_ipi.ko | G | A | 12/12 | 12/12 | exact | 279 exact | MT | GNU ID only |
| mcupm.ko | D | A | 42/42 | 51/51 | exact | 718 exact | MT | GNU ID only |
| sspm_v3.ko | D | A | 38/38 | 46/46 | exact | 563 exact | MT | GNU ID only |
| mtk_battery_oc_throttling.ko | D | A | 22/22 | 34/34 | exact | 381 exact | PP | GNU ID only |
| mtk_bp_thl.ko | D | A | 17/17 | 30/30 | exact | 449 exact | PP | GNU ID only |
| mtk_cpu_power_throttling.ko | D | A | 27/27 | 60/60 | exact | 314 exact | PP | GNU ID only |
| mtk_dynamic_loading_throttling.ko | D | A | 10/10 | 28/28 | exact | 424 exact | PP | GNU ID only |
| mtk_gpu_power_throttling.ko | D | A | 27/27 | 59/59 | exact | 266 exact | PP | GNU ID only |
| mtk_low_battery_throttling.ko | G | A | 52/52 | 74/74 | exact | 1168 exact | PP | GNU ID only |
| pmic_lbat_service.ko | G | A | 28/28 | 40/40 | exact | 745 exact | PP | GNU ID only |
| pmic_lvsys_notify.ko | D | A | 9/9 | 20/20 | exact | 195 exact | PP | GNU ID only |
| mtk-pmic-keys.ko | D | A | 8/8 | 30/30 | exact | 141 exact | PS | GNU ID only |
| mtk-pmic-oc-debug.ko | D | A | 7/7 | 35/35 | exact | 263 exact | PS | GNU ID only |

## Maintained source commits

Four local sibling repositories, each owning only its frozen family. Shared27/provider
build scope does not transfer ownership or certify whole external producers. Each contains
pins,complete Kbuild patch,config hash/ABI inputs,bootstrap/build/verification tools,licensing,
owned and joint golden hashes and independent checkout instructions. Recovery bundles and
COMMIT files are preserved under family/source. Final recipes contain no tracked .pyc/.o/.ko.

| Key | Repository | Exact compiled commit |
|---|---|---|
| IM | android_kernel_modules_memory_platform_ulefone_gq5012bf1 | 78cd676ac42af772a96ed8cd2e9490beb4ad1c10 |
| PS | android_kernel_modules_pmif_spmi_ulefone_gq5012bf1 | c35098cc7d0cd9603fa0d958001b893dcdd392c5 |
| MT | android_kernel_modules_mailbox_tinysys_ulefone_gq5012bf1 | ac71f3456201d68061f147a51ca3b4d5b1c94dda |
| PP | android_kernel_modules_power_policy_ulefone_gq5012bf1 | 6c8039bfbdb65d8ec92d5eb999e57a8bbc9279fc |

Public immutable inputs remain exactly:
- ALPS NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878:
  5e415e059253ce0d2e61c97108e5f5785d71f06f (C/headers;tree9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c).
- Same repository957dac185efe46cbf6336b0fff9516d84c8cd78f (Kconfig/defconfig only).
- Android common6b18f0b574ab3267615ae6ce642d5a7c3c21ac09 (GKI12901745).
- Android Clang7775eb113f960bc69a780b621d03a715914d4bca (clang-r487747c).
URLs/subtree/tree hashes in each SOURCE-PINS.tsv. Shared offline mirror only. Base config
8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e;
LLVM IAS/-faddrsig/exact macro-prefix-map/release string reproduce stock.

## Reconstruction and historical input closure

All27 are direct public C/H matches. Only0001-joint-kbuild-scope.patch:preserve original
flags/composites,Kbuild27 targets+8 genuine producer units,absolute-src wildcard/include
repair,ICC trace -I$(src),authentic power trace include resolution and original CCCI producer
include flags when configuration is modular. No board C/table/algorithm rewrite or stock
instruction/data/CRC/symbol-table transplantation.6617 C/H hashes equal immutable ALPS blobs.

Initial compilation exposed trace/include-path failures, not missing implementations.
Those failures and the successful corrected build are preserved under evidence/attempt-01/02.
No repeated blind donor retry or difficult member omission.

Six G modules recovered historical source,not rewritten.24 preserved source/header files
match explicit immutable public revisions, including common rpmsg_internal.h and a historical
mtk_sip_svc.h from957dac. Final compiled C/H is5e41 throughout. Thermal historical C matches
5e41; old recipe/source-map provenance is retained. Hidden /tmp/ispenv.sh,/tmp/connenv.sh,
mutable TinySys sb.sh/workspaces,prepared connectivity kout and camera stock-ext.symvers
are eliminated as required build inputs. No historical script was executed or overwritten.

## Independent compilation / B1-B2 / complete stock acceptance

Four source commits freshly cloned. All original recipe paths AND Batch02 development tree
unavailable during proof. Each clone actually runs complete27 B1/B2: **eight fresh builds**.
One compatible public base/header environment is reverified/reused; every target/provider
object rebuilt from a newly assembled source tree each time. No target/output cache input.

Each run:27 raw/27 stripped modules and105 intermediates deterministic within families AND
across four engines;config/source/GKI ABI/module symvers/producer CRC/licence/namespace/
KCFI-prefix witnesses agree. Compiler and modpost exits0;no warnings/errors. The entire27
passes independent full stock acceptance every run.595 functions,1119 data objects,898
imports,113 exports,23 absolute KCFI IDs and12449 raw+semantic relocations fully accounted.
Only parsed GNU20-byte build-ID differences permitted;no other metadata exceptions.

An initial successful eight-build proof was repeated after source-recipe bytecode cleanup;
final committed recipes are artifact-free. No C/H/build behavior changed. Both logs retained.
16 real ELF mutation cases pass, including function/data/relocation/import and export CRC/
metadata/header/owner/section corruption,truncation and appended signature rejection.

## Authentic provider graph and external boundary limits

[PROVIDER-GRAPH.tsv](evidence/PROVIDER-GRAPH.tsv) covers all898 imports and113 owned exports.
44/44 noncore source boundaries match CRC,licence,namespace and required provider KCFI prefix;
19 external slots regenerate naturally from genuine source. Core imports use the verified
official GKI symbol table; core provider prefix words explicitly UNKNOWN,not invented or
misrepresented as a fresh full kernel build. Exact consumer code/type IDs/imports still match.

AEE,clock-common/clkchk,mrdump,CCCI port,GPUEB,GPUFreq and SCMI producer units are fresh
source witnesses only. Already certified dependencies are referenced/reused; Batch01 modules
not reconstructed again. Uncertified whole producers are not silently promoted. No temporary
provider table or copied stock CRC substitutes for a mismatching declaration.

## Genuine GQ5012BF1 hardware findings

Saved DT SHA c30d118138ea8df045a245b21afc888408b89ea090f6781f97c8b815211c595d.
15 binary-alias matches,89 independently configured nodes,404 configured properties,
3 typed alias-match resources,48 selected load-list occurrences preserved. Alias absence does
not erase configured controllers:several static tables have no module aliases. No selected
member has canonical saved driver/module-symlink PROVEN_RUNTIME;runtime traffic remains UNKNOWN.

- EMI central window10219000 advertises legacy mediatek,mt6877-emicen;EMI MPU at10226000,
  NSMPU at10351000 and PMIF MPU at1cc04900. DRAMC exposes multiple channel/top/MD32 windows
  and two reserved rank regions. Protection,DRAM control and bandwidth voting are separate.
- PMIF/SPMI controller1cc04000 names pmif/spmimst windows and rcs_irq/pmif_irq/spmi_nack_irq.
  interrupts-extended cells and inherited parent relationships are preserved,not guessed.
  DT children include MT6363 address4,MT6369 address5,MT6319 address6 and MT6685 MFD;
  source capability does not prove physical bus transactions.
- MT6363 dynamic-loading child references ADC channels named pmic_ptim/pmic_imix_r/pmic_batadc.
  PMIC keys/LVSYS/overcurrent policy and regulator/pinctrl/interrupt services remain distinct.
- MCUPM base0c540000,mailbox0 base0c56fb00;DT labels eight mailbox IRQs and base/set/clear/
  send/receive register resources. SPI numbers24–31 are configuration,not tested IRQ delivery.
- SSPM base1c300000 uses sspm_base/cfgreg/mbox_share labels;reserved sspm_ap-shared region
  starts7f970000,size110000. Shared-memory layout and startup/command handling source is
  recovered;successful coprocessor boot or communication is not claimed.
- ICC/MMQoS/EMI-vote and already certified IOMMU/SMI/MMDVFS/DVFSRC source owners stay separate.
  Stock imports do not invent dependencies not actually present in selected binary graphs.
- Evidence labels distinguish PROVEN_RUNTIME,ENABLED_IN_STOCK_DT,STOCK_BINARY_IMPLEMENTATION,
  PUBLIC_REFERENCE_ONLY and UNKNOWN. Current saved binding evidence is not reinterpreted.

Host source does not open-source SCP/SSPM/MCUPM/VCP/GPUEB/APUSYS firmware. Secure-monitor
calls,memory-protection secure services,firmware/calibration and actual MMIO/IRQ/PMIC/mailbox
operations remain separate unvalidated boundaries. No proprietary-firmware blame for ABI gaps.

## Blockers / audit / commits / next

Batch02 implementation/ABI blockers: **zero**;BLOCKERS.tsv is a header-only zero-row ledger.
Batch01 four CMDQ C blockers and all other271 source gaps remain explicitly unchanged.
Canonical validator PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES,zero errors;14 audit
mutation tests and16 actual ELF mutation cases pass. Exactly458 identities/471 occurrences,
no omitted path,duplicate,unsupported A/B claim,broken source ref or ownership/status drift.
[final-validation.json](evidence/final-validation.json) proves all431 unselected rows unchanged.

Research checkpoints:2972afa(freeze),5bc73b9(all27 development/source recovery),
f85ff4e(memory),b0534fe(PMIF),46aa419(mailbox/TinySys),e3d58b6(power policy).
Shared independent proof:2e87a85. Final audit commit follows;exact pointers in
BATCH-STATE.json/Git history.
All source/research repositories local and clean;no push.

Exact next dependency-aware recommendation:**34 remaining identities**,current queue head
sec-rng then diagnostics/watchdog,PMIF MFD/ADC/common clock supply,thermal/CPU/power policy.
Every filename in [NEXT-BATCH.md](NEXT-BATCH.md);machine IDs/classes/owners/hashes preserved.
Revalidate/freeze before execution;no Batch02 amendment. Historical G source preserved,not
rewritten; no radio/audio algorithm reconstruction or secure firmware commands implied.

Strictly offline. No ADB,phone,flash,reboot,slot switch,module loading,register write,
TinySys/CMDQ/DMA test,secure-world command,firmware/calibration modification or push.
