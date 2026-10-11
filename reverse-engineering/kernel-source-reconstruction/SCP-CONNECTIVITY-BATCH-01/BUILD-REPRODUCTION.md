# SCP-CONNECTIVITY-BATCH-01 build reproduction

| Repository | Commit | Bundle (sha256 in evidence/*/cleancheck/*.bundle.sha256) |
|---|---|---|
| `../android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1` | `26507aa653a09f907329795b6c31c6ec1bd694dd` | `/home/armol/kernel-work/codex-conn-batch-01/bundle/scp-sensorhub-26507aa6….bundle` |
| `../android_kernel_modules_connectivity_ulefone_gq5012bf1` | `d0b9e10fbb3bb4810de79fda190a4216cec65b00` | `/home/armol/kernel-work/codex-conn-batch-01/bundle/connectivity-d0b9e10f….bundle` |

Both bundles were re-cloned and their trees match the commits (`evidence/bundle-recovery.log`). Nothing is pushed.

## Immutable inputs

| Input | Pin | Verification | Offline location (read-only) |
|---|---|---|---|
| kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | tree `710eb859` | `interconnect-pin-mirror/common.git` |
| clang r487747c | prebuilts `7775eb113f96` | tree `8eb8e3af` | `interconnect-pin-mirror/clang-r487747c.tar` |
| NothingOSS KDM (Kconfig) | `957dac185efe` | tree `05f9c65d` | `interconnect-pin-mirror/kdm.git` |
| NothingOSS ALPS (compiled C) | `5e415e059253` | tree `9c61acc3` | `interconnect-pin-mirror/alps5e41.git` |
| NothingOSS kernel_modules | `2115d278396fe63bd7d021e46091f3c44af64011` (`connectivity` subtree) | tree `d7cfca48` | `codex-conn-batch-01/mirror/nkm.git` (fetched by SHA from GitHub; the shared blobless clone was not modified) |
| kernel/prebuilts/build-tools | `e905be252a53` (pahole v1.23) | tree `e08e74fb` | `platform-batch-03-native-inputs/kernel-build-tools.git` |
| Public GKI 12901745 vmlinux | CI artifact | sha256 `27abab46…` | `platform-batch-03-native-inputs/gki12901745-vmlinux` |
| GKI 12901745 vmlinux.symvers | CI artifact | sha256 in `reference/` | mirror + `.xz` copy in each repo |

## Commands

```sh
export TMPDIR=/tmp LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
# SCP-SENSORHUB
R=../android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1
bash $R/scripts/bootstrap.sh <ws>; bash $R/scripts/bulk-build.sh <ws> B1; bash $R/scripts/accept.sh <ws>/out/B1 <stock3>
# CONNECTIVITY
export LIEPPOS_CONN_MIRROR=/home/armol/kernel-work/codex-conn-batch-01/mirror \
       LIEPPOS_NATIVE_MIRROR=/home/armol/kernel-work/platform-batch-03-native-inputs
R=../android_kernel_modules_connectivity_ulefone_gq5012bf1
bash $R/scripts/bootstrap.sh <ws>; bash $R/scripts/bulk-build.sh <ws> B1; bash $R/scripts/accept.sh <ws>/out/B1 <stock17>
```

The vendor `.config` sha256 is `b826d842…`, the same file as AUDIO-BATCH-01. The native in-tree `.config` is `841b4ed8…`; the
difference is the pahole-dependent BTF Kconfig.

## Independent clean-clone checks (as run)

Each `scripts/cleancheck.sh <bundle> <commit> <base> <stock>` was run inside
`bwrap --dev-bind / / --tmpfs <dev repo> --tmpfs <dev workspace>`. The development checkout and
workspace were empty inside the namespace (logged), and nothing was renamed or modified. Claude's
directories were not touched. Each check clones the bundle, bootstraps two fresh workspaces (B1, B2),
builds both from scratch and compares them:

| Family | Raw / stripped .ko | Objects | Symbols | Witnesses, configs, source trees | Stock acceptance | Mutations |
|---|---|---|---|---|---|---|
| SCP-SENSORHUB | 3 + 3 identical | 54 identical | 42 exports identical | identical | 3 A in B1 and B2 | 23/23 detected |
| CONNECTIVITY | 17 + 17 identical | 577 identical | 725 records identical (workspace path column normalised) | identical | 14 A + 3 C (BTF residual only) in B1 and B2 | 29/29 detected (incl. 6 C-gate cases) |

## Recipe-owned deltas over pristine inputs

- scp-sensorhub `patches/0002`: the four sensor-2.0 YFT files (historical, re-expressed on ALPS).
- connectivity `patches/nkm/0003`: 13 recovered ALPS V11.24 wlan hunks (historical, verbatim).
- `patches/*0009-kbuild-scope.patch`: `obj-*` routing only. For connectivity it also respells
  `$(srctree)/$(src)` as `$(src)`, equivalent for the absolute-M external build.
- Build inputs recovered from stock:
  - `DRIVER_BUILD_DATE=20251022145214` (wlan version string);
  - empty `TARGET_BUILD_VARIANT`;
  - `KERNEL_RELEASE 6.1.115-android14-11-g945dff7bc1bf`;
  - `module_scmversion=g945dff7bc1bf` for the 3 in-tree modules only.
- `-fdebug-prefix-map` only rewrites DWARF and does not affect stripped acceptance.

## Normalization

The only normalization is zeroing the 20-byte GNU build-ID descriptor (class A). For the three class-C
modules, `residual-btf.py` treats nothing as equal. It proves that every byte outside `.BTF` is identical,
and that each differing `.BTF` word is a type-ID or name-offset reference under a bijective, constant-shift mapping.
