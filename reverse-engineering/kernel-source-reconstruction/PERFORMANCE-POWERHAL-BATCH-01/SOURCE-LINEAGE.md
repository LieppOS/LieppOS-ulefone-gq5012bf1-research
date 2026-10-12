# Source lineage

The maintained repository is `android_kernel_modules_performance_ulefone_gq5012bf1` @ `7a1a1e298a2a6f6a282a4a8957c23a606616dfd4`
(new). It is a history-preserving fork of `android_kernel_modules_low_power_ulefone_gq5012bf1` 18562149, whose GPL-2.0-only
engine and authorship history it keeps.

- **Scope:** it owns only the 14 frozen identities.
- **Source:** the assembled tree is pure pinned ALPS plus Kbuild route changes (`source-scope.patch`, recorded per
  build).
- **No OEM differences:** no OEM source patch, placeholder or historical modification was needed. All 14 are
  `PUBLIC_EXACT`.

| Input | Commit | Tree | Role |
|---|---|---|---|
| MediaTek ALPS device modules (NothingOSS mirror) | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | complete C/H/Kbuild for all 14 targets and the 12 provider witness units |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` | Kconfig + `mgk_64_k61_defconfig` (all family options `=m`; `MTK_EAS=y`, `MTK_SCHED_*=y`) |
| Android GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` | headers, Kbuild/modpost |
| clang r487747c | `7775eb113f960bc69a780b621d03a715914d4bca` | `8eb8e3afb00a52d48b29381d73daf352362231ad` | compiler |
| GKI 12901745 vmlinux.symvers | sha256 `61933b61…` | — | core CRC input |

No OEM split-BTF base is used, because no target has `.BTF`. The ALPS `drivers/misc/mediatek` tree contains no
`*_shipped` prebuilt objects. Every compiled `.c` is genuine source, including the 36-line GPL-2.0
`sched/eas/flt_cal_build_utility.c`, and no compiled file uses `incbin`.

## Per target

| Module | ALPS Kbuild unit | Distinct KDM inputs (.c / total) |
|---|---|---|
| mtk_perf_ioctl | `performance/Makefile` composite `perf_ioctl/perf_ioctl.o` | 1 / 2 |
| mtk_perf_ioctl_magt | `performance/Makefile` `perf_ioctl/perf_ioctl_magt.o` | 1 / 2 |
| mtk_ioctl_powerhal | `performance/Makefile` `perf_ioctl/ioctl_powerhal.o` | 1 / 2 |
| mtk_ioctl_touch_boost | `performance/Makefile` `perf_ioctl/ioctl_touch_boost.o` | 1 / 2 |
| powerhal_cpu_ctrl | `performance/powerhal_cpu_ctrl` | 1 / 5 |
| touch_boost | `performance/touch_boost` | 1 / 4 |
| mtk_fpsgo | `performance/fpsgo_v3` (base, fbt, fstb, gbe, composer, xgf) | 16 / 50 |
| frs | `performance/frs` | 1 / 7 |
| load_track | `performance/load_track` | 1 / 1 |
| uload_ind | `performance/uload_ind` | 1 / 5 |
| mtk_perf_common | `perf_common` (perf_common, perf_freq_tracker, perf_tracker) | 3 / 17 |
| scheduler | `sched` (common, fair, 17 × eas/*) | 19 / 38 |
| cpuqos_v3 | `cache-auditor/cpuqos_v3` | 2 / 8 |
| task_turbo | `task_turbo` | 1 / 5 |

All paths are relative to `drivers/misc/mediatek/`. The total covers 31,179 input records: KDM/COMMON git blob IDs and
GENERATED sha256 values, taken from the B1 Kbuild `.cmd` records into `evidence/source-inputs/SOURCE-INPUTS.tsv`.

- **Unbuilt Makefile siblings:** `performance/Makefile` can also build `mtk_game` (`CONFIG_MTK_GAME`), and
  `sched/Makefile` can build `mtk_core_ctl` and `cpufreq_sugov_ext`. These are not owned here. mtk_game is not
  shipped; mtk_core_ctl and cpufreq_sugov_ext are canonical A in power_policy, and only cpufreq_sugov_ext is
  routed, as a compile-only witness.
- **Earlier work:** the historical search (EXPERIMENTS P03) found no earlier LieppOS reconstruction.
- **Licensing:** sources are MediaTek GPL-2.0 and retrieved unmodified, with SPDX and copyright headers intact.
