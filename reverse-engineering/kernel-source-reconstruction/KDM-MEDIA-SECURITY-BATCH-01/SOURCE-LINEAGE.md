# Source lineage

The maintained repository is `android_kernel_modules_kdm_media_security_ulefone_gq5012bf1` @
`973eb04ac0d02be7dbb3fe8275ca35b7a5c4522b` (new). It is a history-preserving fork of
`android_kernel_modules_performance_ulefone_gq5012bf1` 7a1a1e29 and owns 10 of the 11 frozen identities;
`flashlight.ko` is blocked and not owned.

| Input | Commit | Tree | Role |
|---|---|---|---|
| MediaTek ALPS device modules (NothingOSS mirror) | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | complete C/H/Kbuild for all targets and provider witnesses |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` | Kconfig + `mgk_64_k61_defconfig`. All target options are `=m`, and the prepared `.config` b826d842 is unchanged from earlier batches |
| Android GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` | headers, Kbuild/modpost |
| clang r487747c | `7775eb113f960bc69a780b621d03a715914d4bca` | `8eb8e3afb00a52d48b29381d73daf352362231ad` | compiler |
| Historical LieppOS OEM delta | `3b995377e08cbd9ccd53fb7407fd8a88b6afb5c7` (`gki-12901745-workspace/kernel_device_modules-6.1`, 2026-10-04) | — | irtx `dma-mask-bit` (9 lines), applied unchanged as `patches/source/0001-…patch` |

No OEM split-BTF base is needed, because no target has `.BTF`.

## Per target

| Module | Kbuild unit | Distinct KDM inputs (.c / total) | Provenance |
|---|---|---|---|
| mtk-composite | `drivers/misc/mediatek/flashlight` `obj-$(CONFIG_MTK_V4L2_FLASHLIGHT)` | 1 / 2 | PUBLIC_EXACT |
| mtk_jpeg | `drivers/media/platform/mtk-jpeg` (core, dec_hw, dec_parse, enc_hw) | 4 / 17 | PUBLIC_EXACT |
| mtk-mmdvfs-v3-start | `drivers/misc/mediatek/mmdvfs` | 1 / 4 | PUBLIC_EXACT |
| mtk_sec_heap | `drivers/dma-buf/heaps` | 1 / 10 | PUBLIC_EXACT |
| mtk_heap_debug | `drivers/dma-buf/heaps` | 1 / 9 | PUBLIC_EXACT |
| widevine_driver | `drivers/misc/mediatek/widevine_drm` | 1 / 3 | PUBLIC_EXACT |
| tui-common | `drivers/input/touchscreen` (unconditional `obj-m`) | 1 / 1 | PUBLIC_EXACT |
| sapu | `drivers/misc/mediatek/apusys/sapu` (+ platform/sapu_cb power v1/v2) | 6 / 23 | PUBLIC_EXACT |
| mtk_irtx_pwm | `drivers/misc/mediatek/irtx` | 1 / 3 | PUBLIC + RECONSTRUCTED_OEM_DELTA |
| nvmem-mt635x-efuse | `drivers/nvmem` (`mt635x-efuse.c`) | 1 / 2 | PUBLIC_EXACT |
| flashlight | `drivers/misc/mediatek/flashlight` (core + device) | not built | PUBLIC_CANDIDATE_ONLY; retained D (BLOCKERS) |

The table covers 11,450 input records (git blob IDs and generated sha256 values) from the B1 `.cmd` files, listed
in `evidence/source-inputs/SOURCE-INPUTS.tsv`. The compiled `mtk_irtx_pwm.c` is blob `8bcd3571…`, the exact
post-image of historical commit 3b995377.

## irtx OEM delta: evidence chain

1. **Public revisions.** No public revision has the delta: ALPS 5e415e05 blob `fc4144e0`, the 8 MiCode/public-mtk
   revisions, and the 293 on-disk public copies all lack `dma-mask-bit`.
2. **Stock module.** It contains everything the delta adds: the `.bss` object `dma_mask_bit`, the strings
   `dma-mask-bit` and `rc=%d,dma_mask_bit=%d\n`, and an import of `dma_set_coherent_mask`. The pure-ALPS build lacks
   all of these (`evidence/development/X1-flashlight-pt-experiment/X1-irtx-pair.txt`).
3. **Stock DT.** The `irtx-pwm` node carries `dma-mask-bit = <0x23>`.
4. **Result.** With the 9-line delta the output is byte-identical to stock except the GNU build ID, in D3, B1 and B2.

This is a reconstruction proven by byte-identical output. It is **not** recovered OEM file text, although it
reproduces every emitted byte. It is the same historical change previously used for the LieppOS glue build of
this module, applied here unchanged.
