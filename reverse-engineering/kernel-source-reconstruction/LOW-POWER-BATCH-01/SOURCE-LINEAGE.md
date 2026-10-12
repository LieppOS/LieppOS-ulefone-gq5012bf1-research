# Source lineage

Maintained repository: `android_kernel_modules_low_power_ulefone_gq5012bf1` @ `185621496e49c59b162e815e6f84f97bc7b1768c`
(new). It is a history-preserving fork of `android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` 8e7a66e1,
keeping that engine's GPL-2.0-only scripts and authorship history. It owns only the 12 frozen identities. The
inherited display patches and the unused inherited scope-documentation patch were removed, so the assembled
tree is pure pinned ALPS plus Kbuild route changes (`source-scope.patch`, recorded per build).

| Input | Commit | Tree | Role |
|---|---|---|---|
| MediaTek ALPS device modules (NothingOSS mirror) | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | complete C/H/Kbuild for all 12 targets and 14 provider witness units |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` | Kconfig + `mgk_64_k61_defconfig` (`CONFIG_MTK_LOW_POWER_MODULE=m`, `MTK_LPM_MT6878=m`, `MTK_CPU_IDLE_GOV=m` / `"MHSP"`, `MTK_SWPM_MODULE=m`, `MTK_SSC_MODULE=m`, `MTK_SSC_DBG_V2=m`, `MTK_MBRAINK=m`) |
| Android GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` | headers, Kbuild/modpost |
| clang r487747c | `7775eb113f960bc69a780b621d03a715914d4bca` | `8eb8e3afb00a52d48b29381d73daf352362231ad` | compiler |
| GKI 12901745 vmlinux.symvers | sha256 `61933b61…` | — | core CRC input |

The OEM split-BTF base is not used: none of the 12 stock modules has a `.BTF` section.

## Per target (all PUBLIC_EXACT, no OEM delta)

| Module | Kbuild unit (ALPS) | Distinct KDM inputs (.c / total) |
|---|---|---|
| mtk-lpm | `drivers/misc/mediatek/lpm` `mtk-lpm.o` | 15 / 36 |
| mtk-lpm-plat-v1 | `lpm/modules/platform/v1` `${BUILD_MTK_LPM_PLAT_MODUDLE_NAME}` = mtk-lpm-plat-v1 (uses `../suspend_v1`) | 3 / 16 |
| lpm-gov-MHSP | `lpm/governors/MHSP` `lpm-gov-$(CONFIG_MTK_CPU_IDLE_GOV_VERSION)` = lpm-gov-MHSP | 1 / 6 |
| mtk-lpm-dbg-common-v2 | `lpm/modules/debug/v2` | 21 / 53 |
| mtk-lpm-dbg-mt6878 | `lpm/modules/debug/mt6878` | 3 / 32 |
| mtk-swpm | `drivers/misc/mediatek/swpm` `mtk-swpm.o` | 4 / 13 |
| mtk-swpm-dbg-common-v1 | `swpm/modules/debug/v1` | 1 / 8 |
| mtk-swpm-dbg-v6878 | `swpm/modules/debug/v6878` | 4 / 21 |
| mtk-swpm-cpu-dbg-v6878 | `swpm/modules/debug/v6878` | 2 / 12 |
| mtk-ssc | `drivers/misc/mediatek/ssc` | 1 / 7 |
| mtk-ssc-dbg-v2 | `ssc/debug/v2` | 1 / 5 |
| mtk_mbraink | `drivers/misc/mediatek/mbraink` | 10 / 33 |

Every compiled input (34 608 records: KDM/COMMON git blob IDs, GENERATED sha256) is listed in
`evidence/source-inputs/SOURCE-INPUTS.tsv`, generated from the B1 Kbuild `.cmd` records.

The `swpm/modules/debug/v6878` Makefile can also build `mtk-swpm-mem-dbg-v6878` and `mtk-swpm-core-dbg-v6878`.
GQ5012BF1 ships neither (absent from vendor_dlkm and modules.load), so they are not built or claimed.

Historical search (EXPERIMENTS L03) found no earlier LieppOS reconstruction of these modules. All sources are
GPL-2.0 MediaTek/Linux, retrieved unmodified with their SPDX and copyright headers intact.
