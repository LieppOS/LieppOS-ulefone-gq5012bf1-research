# Source lineage — APUSYS-NPU-KERNEL

The accepted source is public NothingOSS/MediaTek ALPS commit `5e415e059253ce0d2e61c97108e5f5785d71f06f` from `android_kernel_device_modules_6.1_nothing_mt6878`. Its complete Git tree is `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c`. The candidate `957dac185efe46cbf6336b0fff9516d84c8cd78f` was tested first and rejected as the module source: `apu_top` had 272/276 name-keyed bodies identical and `apusys` 1,739/1,773; ALPS 5e41 closed those source changes. The 957dac tree remains the exact vendor config/Kconfig pin.

Unmodified 5e41 initially produced complete `apu_top` code and apparent `apusys` MDLA differences. Mapping each output `.text` function occurrence back to all 164 constituent objects proved 1,963/1,963 sequences were present; only 35 MDLA objects had moved. Root cause was the Makefile expression `$(shell ... find mdla -name "*.c")`, whose output follows filesystem enumeration. The stock order was recovered from the ELF function sequence and made explicit. After that build-only correction, both modules became whole-file identical except build ID.

No C or header file differs from 5e41. The final source tree after scope/order patch is `4e308365cd59051c937f8fb76c221a80496e31b7`; base tree is recorded in `source/reference/source-trees.txt`. The exact patch is preserved both in the maintained repository and `source/patches/`.

Build baseline:

* GKI common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, Android CI 12901745;
* official GKI `vmlinux.symvers` SHA-256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548`;
* Android Clang 17.0.2 `r487747c`, prebuilts commit `7775eb113f960bc69a780b621d03a715914d4bca`;
* vendor config from 957dac, SHA-256 `8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`;
* release `6.1.115-android14-11-g945dff7bc1bf`, `-D__ANDROID_COMMON_KERNEL__`, `-faddrsig`, and path-only prefix mapping.

The earlier local archive commit `2ae742f...` and patched mixed-tree commit `ca8b550...` were preparation conveniences, not authoritative source pins. The maintained recipe reconstructs directly from public commits and needs no prior `/home/armol/kernel-work` tree.
