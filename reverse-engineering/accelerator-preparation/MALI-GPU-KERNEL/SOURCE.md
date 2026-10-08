# MALI-GPU-KERNEL — where the source is

## Maintained source repository

**`/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_gpu_ulefone_gq5012bf1`**

* Branch `main`, verified commit **`9d05ae8`** (scripts and patches unchanged since `ac1c57a`).
* Intended remote: `git@github.com:LieppOS/android_kernel_modules_gpu_ulefone_gq5012bf1.git`.
  No remote is configured, and it has not been pushed.
* A redundant copy lives in this research tree: `source/android_kernel_modules_gpu_ulefone_gq5012bf1.bundle`
  (`git clone <bundle>`). Its plain-file copies are `source/SOURCE-PINS.tsv`, `source/patches/`
  and `source/reference/`.

The repository is a **pinned-source manifest + complete patch set + build scripts**. It
contains no copy of upstream trees: they are fetched by immutable commit id and verified by
git tree id.

## Exact revisions

| id | repository | commit | branch / ref |
|---|---|---|---|
| common | https://android.googlesource.com/kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | android14-6.1-2024-12 (now `deprecated/`), GKI build 12901745 |
| clang | https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86 | `7775eb113f960bc69a780b621d03a715914d4bca` (`clang-r487747c/`) | GKI 12901745 manifest |
| kdm | https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878 | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | mt6878/Tetris/u |
| alps5e41 | same | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | mt6878/{Galaga,Galaxian,Tetris}/16b |
| nkm | https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878 | `580d08eac018657a993e56b1806407e41a3b9545` | mt6878/Galaga/v |
| nkm_v1124 | same | `c3d070e6155c9f373224fa2b17027d07583c37bc` | mt6878/Galaga/16b, mt6878/Tetris/16b |
| GKI vmlinux.symvers | ci.android.com 12901745 `kernel_aarch64` | sha256 `61933b61252e3311bd8c3bf2c179270ba21ae5bf99a4ece3b88d2e9d9dc1c548` | (compressed fallback copy in the repo) |

## Patches (complete)

| patch | base | kind |
|---|---|---|
| `kdm/0001-build-restrict-the-top-level-Kbuild-to-drivers-gpu-m.patch` | 957dac | build plumbing |
| `kdm/0002-gpu-mediatek-do-not-build-gpueb-and-gpu_iommu.patch` | 957dac + 0001 | build plumbing |
| `kdm/0003-gpu-mediatek-take-ged-and-gpufreq-from-ALPS-5e415e05.patch` | 957dac + 0001..0002 | verbatim import from 5e415e059253 (checked by script) |
| `gpu/0001-mali-r44p1-take-page-migration-and-pm_driver-files-f.patch` | 580d08e `gpu/` subset | verbatim import of 4 files from c3d070e6155c (checked by script) |

Resulting trees: `src/kdm` = `39d806ce72d69b83d614e324fa73104db093f635`,
`src/gpu` = `9bd1368f96a922ab2b08a8d98dc582633b0180dd`.

## Build

```sh
cd android_kernel_modules_gpu_ulefone_gq5012bf1
scripts/bootstrap.sh ~/lieppos-gpu-ws                    # fetch + verify all pins
scripts/b1b2.sh ~/lieppos-gpu-ws [<stock vendor_dlkm/lib/modules>]
#   -> ~/lieppos-gpu-ws/out/B1/*.ko, *.stripped; B1==B2 check; stock verification
```

To build offline or for long-term storage, use `scripts/archive-pins.sh <ws> <mirror>`,
then `LIEPPOS_GPU_MIRROR=<mirror> scripts/bootstrap.sh <ws>`.

## Verified (2026-10-08)

Evidence: `evidence/source-preservation/`.

| test | result |
|---|---|
| clean clone `ac1c57a`, empty workspace, all pins fetched from upstream, old work dir `build/` hidden | bootstrap 3m17s, every pin tree id matched; B1 == B2; 30/30 provider CRCs re-derived = stock; **8/8 stock-identical** after normalization (raw diffs: 20/20/20/20/20/19/20 bytes build-id; kbase 43 = build-id + srcversion) |
| full research acceptance tool on that B1 | function, data, section, relocation and ABI ledgers identical to the closure ledgers |
| offline mirror, network blocked, fresh workspace | 8/8 stock-identical |
| fresh clone of final commit `9d05ae8` from the mirror, fresh workspace | B1 == B2; 8/8 stock-identical |

## If `/home/armol/kernel-work/accelerator-mali-gpu-kernel/build/` is deleted

Nothing is lost:
* that directory held two local git repositories (no remotes);
* their content equals the pins + patches above. `gpu` is tree-identical; `kdm` differs only
  by two touchscreen `*.i` files its import silently dropped through `.gitignore`, which no
  GPU object reads;
* the clean-checkout test ran with it moved away.

## Limits

* Rebuilding needs the upstream hosts (GitHub NothingOSS, AOSP gitiles, ci.android.com), or
  a mirror made with `archive-pins.sh`.
* Mirrors are not stored in any LieppOS repository, because they hold third-party trees and
  a 2.4 GB toolchain. A mirror was written to
  `/home/armol/kernel-work/lieppos-gpu-pin-mirror` (2.7 GB). Copy it to permanent storage to
  remove the upstream dependency.
* The kbase `srcversion` text (MTK rc-V10.29) is unpublished, so that 24-character modinfo
  value cannot be reproduced. No compiled byte depends on it.
* Build-ids depend on the absolute workspace path. B1/B2 determinism holds within one
  workspace path; across paths, only the build-id changes.
