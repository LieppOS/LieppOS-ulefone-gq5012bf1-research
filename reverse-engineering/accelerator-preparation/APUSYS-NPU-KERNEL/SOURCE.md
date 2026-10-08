# APUSYS-NPU-KERNEL source

## Maintained repository

`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_apusys_ulefone_gq5012bf1`

* branch `master`, verified commit `924f66b779a64ae0b05f89e233ff2317866050ba`;
* intended remote: `LieppOS/android_kernel_modules_apusys_ulefone_gq5012bf1`;
* no remote is configured and nothing was pushed;
* complete local backup: `source/android_kernel_modules_apusys_ulefone_gq5012bf1.bundle`.

The repository is a pinned-source recipe, complete patch, build/verification scripts, public GKI metadata, and hash oracles. It contains no stock module, proprietary firmware, model, key, or calibration.

## Immutable inputs

| input | repository | commit / identity |
|---|---|---|
| GKI common | `https://android.googlesource.com/kernel/common` | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` |
| Android Clang | `https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86` | `7775eb113f960bc69a780b621d03a715914d4bca`, subtree `clang-r487747c` |
| vendor config | `https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878` | `957dac185efe46cbf6336b0fff9516d84c8cd78f` |
| APUSYS + provider source | same | `5e415e059253ce0d2e61c97108e5f5785d71f06f` |
| GKI `vmlinux.symvers` | Android CI build 12901745 | SHA-256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548` |

All Git inputs are verified by tree ID (`SOURCE-PINS.tsv`). The mixed-build config hashes to `8f9d1d2901dfbc77062764b4f9e21bc1000097392a36f8ba1eebd9c47d35f50e`.

## Reconstruction

The public ALPS 5e41 APUSYS C and headers are the stock source. There is no behavioral source patch. `patches/0001-owned-pair-and-stock-mdla-order.patch` only:

1. restricts top-level Kbuild to the owned APUSYS directory;
2. omits separately owned `sapu.ko` and unshipped `apu_aov.ko`;
3. replaces upstream `find mdla -name '*.c'` filesystem enumeration with the exact stock object order.

The last point explains the initial false MDLA residue: all 1,963 `.text` function occurrences mapped to donor objects, but a different filesystem order moved duplicate-name static functions. Explicit stock order makes every code/data/relocation byte match.

Thirteen imports from `aee_aed`, `mtk_slbc`, `mtk_qos`, `mtk_peak_power_budget`, `mrdump`, and `iommu_debug` receive CRCs generated naturally from public provider source on every build. The checked reference is an oracle only; build fails if any generated CRC differs.

## Reproduce

```sh
cd '/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_apusys_ulefone_gq5012bf1'
WS=/path/without/spaces/apusys-work
scripts/bootstrap.sh "$WS"
scripts/b1b2.sh "$WS" /path/to/stock/vendor_dlkm/lib/modules
```

Without stock blobs, `scripts/b1b2.sh "$WS"` still checks whole normalized module hashes. `scripts/archive-pins.sh` creates an offline mirror; `LIEPPOS_APUSYS_MIRROR=/mirror` consumes one.

## Independent result

A fresh clone at `/home/armol/kernel-work/apusys-npu-cleancheck/repo`, using only the saved public-input mirror, rebuilt B1 and B2. Raw/stripped modules, all target `.o`, target/provider `Module.symvers`, CRC witnesses, and source-tree IDs were identical. Both installed modules equal stock after zeroing only the 20-byte GNU build-ID descriptor. No `srcversion` exception exists.
