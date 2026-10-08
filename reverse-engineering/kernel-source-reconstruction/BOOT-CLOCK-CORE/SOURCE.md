# BOOT-CLOCK-CORE — where the source is

## Maintained source repository

**`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_boot_clock_ulefone_gq5012bf1`**

* Branch `main`, commit **`e99d919`** (full id in `source/` bundle: `git bundle list-heads`).
* No remote configured; not pushed. Intended remote:
  `git@github.com:LieppOS/android_kernel_modules_boot_clock_ulefone_gq5012bf1.git`.
* Redundant copy: `source/android_kernel_modules_boot_clock_ulefone_gq5012bf1.bundle`
  (`git clone <bundle>`); plain copies of `SOURCE-PINS.tsv` and `patches/` alongside it.

The repository is a pinned-source manifest + complete patch set + build/verify scripts. It
contains no upstream tree copy, no stock binary and no firmware.

## Exact revisions (verified by git tree id on every bootstrap)

| id | repository | commit | tree |
|---|---|---|---|
| common | https://android.googlesource.com/kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` |
| clang | https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86 | `7775eb113f960bc69a780b621d03a715914d4bca` | `clang-r487747c` = `8eb8e3afb00a52d48b29381d73daf352362231ad` |
| kdm | https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878 | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` |
| alps5e41 | same | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` |
| GKI vmlinux.symvers | ci.android.com 12901745 `kernel_aarch64` | — | sha256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548` (xz fallback in repo) |

`kdm` supplies only vendor Kconfig + `mgk_64_k61_defconfig`. All compiled clock source,
headers and the AEE provider witness source come from `alps5e41`.

## Patches (complete)

| patch | base | change | result tree |
|---|---|---|---|
| `0001-owned-module-build-scope.patch` | alps5e41 | new `drivers/clk/mediatek/Kbuild` (scope wrapper) | — |
| `0002-mt6878-gq5012bf1-disp-pwm-clocks.patch` | + 0001 | `clk-mt6878.c` (+22/−1), `clk-mt6878-peri.c` (+4), `dt-bindings/clock/mt6878-clk.h` (+5/−2) | `src/kdm` = `471af75e129b81418f195c2a8348167df33740de` |
| `0003-provider-abi-witness-scope.patch` | alps5e41 | top-level `Kbuild` + `aee/aed/Kbuild` (AEE CRC witness only) | `src/prov` = `4ffb2f3b4160f8ce295986cffd32582488ecaaa0` |

## Build

```sh
cd android_kernel_modules_boot_clock_ulefone_gq5012bf1
scripts/bootstrap.sh ~/bootclk-ws             # fetch + verify all pins
scripts/b1b2.sh ~/bootclk-ws <stock-dir>       # B1, B2, compare, full stock acceptance
```

Offline: `scripts/archive-pins.sh ~/bootclk-ws <mirror>`; then
`LIEPPOS_BOOTCLK_MIRROR=<mirror> scripts/bootstrap.sh <fresh-ws>`. The pins are identical to
the GPU recipe's, so the existing mirror `/home/armol/kernel-work/lieppos-gpu-pin-mirror`
serves this recipe unchanged (used for the clean-checkout verification).

## Limits

* Bootstrapping needs the upstream hosts or a pin mirror; mirrors are not stored in a LieppOS
  repository (third-party trees, 2.4 GB toolchain).
* Build IDs hash absolute paths; determinism holds per workspace path.
