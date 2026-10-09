# Source ownership and immutable inputs

Maintained local repository:
`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_pinctrl_ulefone_gq5012bf1`.
Commit recorded in `source/COMMIT`; recoverable `source/android_kernel_modules_pinctrl_ulefone_gq5012bf1.bundle`.
No remote configured; no push performed. The recipe contains source pins, complete patches,
configuration/KMI identities, build/acceptance scripts and licences—not stock binaries.

| Input | Immutable commit | Tree |
|---|---|---|
| android.googlesource.com/kernel/common | 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09 | 710eb859513863cda0204995a411d5795ad3fe92 |
| platform/prebuilts/clang/host/linux-x86 | 7775eb113f960bc69a780b621d03a715914d4bca | clang-r487747c: 8eb8e3afb00a52d48b29381d73daf352362231ad |
| NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878 (configuration) | 957dac185efe46cbf6336b0fff9516d84c8cd78f | 05f9c65d40ef9e4bdbe17397a90edd303a5da6dd |
| same (compiled C) | 5e415e059253ce0d2e61c97108e5f5785d71f06f | 9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c |

GKI build 12901745 `kernel_aarch64/vmlinux.symvers`: SHA256
`61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548`.
Hash-verified public fallback `.xz` included. No external vendor symvers/header overlay,
provider reconstruction, private header or companion module is required.

| Output | Compiled implementation |
|---|---|
| pinctrl-mtk-v2 | mtk-eint.c + pinctrl-mtk-common-v2.c + pinctrl-paris.c, in that order |
| pinctrl-mtk-common-v2_debug | pinctrl-mtk-common-v2_debug.c |
| pinctrl-mt6878 | pinctrl-mt6878.c + pinctrl-mtk-mt6878.h descriptor arrays |
| pinctrl-mt6363 | pinctrl-mt6363.c |

The only patch is `0001-owned-pinctrl-build-scope.patch`: top-level Kbuild retains vendor
include ordering and flags, selects only `drivers/pinctrl/mediatek/`; directory Kbuild
includes the original vendor Makefile, then limits obj-m to the exact four names. Source
ordering/conditionals remain unmodified. Patched full source tree:
`251e316f6560f4653356ff2980ccc4544c9dc7cd`. Per-input blob/byte hashes in
`evidence/source/source-blobs.tsv`.

Kernel/module sources and local recipe: GPL-2.0, upstream notices preserved. Clang is the
Apache-2.0 WITH LLVM-exception build tool. See maintained `LICENSE.md` and pins for URLs.

```sh
cd '/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_pinctrl_ulefone_gq5012bf1'
LIEPPOS_PINCTRL_MIRROR=/home/armol/kernel-work/lieppos-gpu-pin-mirror scripts/bootstrap.sh ~/pinctrl-ws
scripts/b1b2.sh ~/pinctrl-ws /path/to/stock/lib/modules
```

Unset the mirror variable for immutable public retrieval. `archive-pins.sh` preserves a
complete offline input mirror with toolchain/core-symvers hashes. The source bundle preserves
the recipe, not all fetched public/toolchain blobs; both recovery mechanisms are documented.
