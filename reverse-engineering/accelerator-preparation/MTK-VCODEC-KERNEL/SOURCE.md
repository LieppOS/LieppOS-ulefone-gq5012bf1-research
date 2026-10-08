# Maintained source — MTK-VCODEC-KERNEL

**Repository:** `LieppOS custom ROM/android_kernel_modules_vcodec_ulefone_gq5012bf1`
(local, branch `main`; **never pushed**).

It is a *recipe*, not a vendored copy: all source is fetched by immutable commit id and
verified by git tree id before use.

## Pinned inputs (`SOURCE-PINS.tsv`)

| id | commit | role |
|---|---|---|
| `common` | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | GKI `kernel/common`, build 12901745: headers, kbuild, modpost |
| `clang` | `7775eb113f960bc69a780b621d03a715914d4bca` (`clang-r487747c`) | Android clang 17.0.2, build 10087095, lld, LLVM tools |
| `kdm` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | vendor Kconfig + `mgk_64_k61_defconfig` **only** |
| `alps5e41` | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | **all** VCodec/VCU/clock driver source and provider source |

GKI `vmlinux.symvers` for build 12901745, sha256
`61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548`, supplies core-kernel
export CRCs. Kernel release is stamped to the stock vermagic
`6.1.115-android14-11-g945dff7bc1bf`; the vendor kernel output `.config` is pinned by sha256
`8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`.

## Source trees (`reference/source-trees.txt`)

| unit | base tree | patched tree | purpose |
|---|---|---|---|
| `src/kdm` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | `a6f90e6578809df579b2e6445f05811a8962ed3f` | the five owned modules |
| `src/prov` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | `9303b1bb3ff64aa7f9086ecb637c5d83deff6f7c` | external provider ABI witnesses |

`assemble.sh` aborts if either the base or the patched tree id differs, so a silent source
edit cannot survive.

## Patches (2, build-scope only)

* `patches/0001-owned-module-build-scope.patch` — adds `Kbuild` to
  `drivers/media/platform/mtk-vcodec`, `drivers/media/platform/mtk-vcu` and
  `drivers/clk/mediatek`. Each includes the unchanged vendor `Makefile` and sets `obj-m` to
  the owned modules only (`mtk-vcodec-common`, `mtk-vcodec-dec-v1`, `mtk-vcodec-enc-v1`;
  `mtk-vcu`; `clk-mt6878-vcodec`), so that unrelated vendor modules in the same directories
  are not built.
* `patches/0002-provider-abi-witness-scope.patch` — adds a root `Kbuild` listing the eleven
  directories that define the external exports, plus three directory wrappers
  (`mtk-interconnect`, `slbc`, `sched`) needed because their vendor `Makefile`s rely on
  include paths a full-tree build would otherwise provide. Used only to regenerate provider
  CRCs; no provider binary is produced or shipped.

**Zero C or header modifications.** Both patches add files only.

## Build identity

`clang-r487747c`, `LLVM=1 LLVM_IAS=1`, `ARCH=arm64`,
`KCFLAGS=-D__ANDROID_COMMON_KERNEL__ -faddrsig -fmacro-prefix-map=<tree>/=../kernel_device_modules-6.1/`,
`module_scmversion=` empty, `DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1`.
`-faddrsig` is required because the stock modules carry `.llvm_addrsig`; the prefix map only
rewrites `__FILE__` text to MediaTek's in-tree spelling.

Build order matters: `mtk-vcodec` first, then `mtk-vcu` (which links against the exports
`mtk-vcodec-common` just produced), then `drivers/clk/mediatek`.

## Entry points

```sh
scripts/bootstrap.sh <workspace>                 # fetch + verify pins (LIEPPOS_VCODEC_MIRROR for offline)
scripts/b1b2.sh      <workspace> [<stock-dir>]   # two clean builds, determinism, full stock parity
```

Stock `.ko` operands stay outside the repository; they are passed by path.
No proprietary firmware, stock binary or Android payload is committed.
