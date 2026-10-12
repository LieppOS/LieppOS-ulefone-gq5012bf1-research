# Source lineage

Maintained repository: `android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` (new). It is a
history-preserving fork of `android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1`
4697eac32544, keeping that repository's GPL-2.0 engine, LICENSE and authorship history. It owns only
the 16 frozen identities. Full per-object input lists are in `evidence/source-inputs/` (generated from
the B1 Kbuild `.cmd` dependency records).

## Pinned donors (exact commit / tree)

| Input | Commit | Tree | Role |
|---|---|---|---|
| MediaTek ALPS device modules (NothingOSS mirror) | `5e415e059253ce0d2e61c97108e5f5785d71f06f` | `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c` | complete C/H/Kbuild for the 13 KDM targets and the provider witnesses |
| NothingOSS device modules | `957dac185efe46cbf6336b0fff9516d84c8cd78f` | `05f9c65d40ef9e4bdbe17397a90edd303a5da6dd` | Kconfig + `mgk_64_k61_defconfig` |
| Android GKI kernel/common | `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09` | `710eb859513863cda0204995a411d5795ad3fe92` | headers, Kbuild/modpost, in-tree sources of arm_dsu_pmu, kfifo_buf, industrialio-triggered-buffer |
| NothingOSS MTK ACK | `c364c39ae8d83dfb5d72802a7718b756c238b07e` | `fb0bf39188577b248bb2bc537856964e13e1746c` | OEM split-BTF base vmlinux (provider input only) |
| clang r487747c (prebuilts) | `7775eb113f960bc69a780b621d03a715914d4bca` | `8eb8e3afb00a52d48b29381d73daf352362231ad` | compiler |
| kernel build-tools | `e905be252a53d20c52bd9e59df3ff8fdd46b9eab` | `e08e74fba3ff91905855d802827db39278a8d15d` | pahole 1.23 |
| GKI 12901745 vmlinux.symvers / vmlinux | sha256 `61933b61…` / `27abab46…` | — | core CRC input / native preparation |

The in-tree sources are blob-identical between GKI common 6b18f0b5 and MTK ACK c364c39ae8d
(`drivers/perf/arm_dsu_pmu.c`, `drivers/iio/buffer/{kfifo_buf,industrialio-triggered-buffer}.c`, both
Makefiles, `include/linux/iio/{iio,kfifo_buf,triggered_buffer,buffer_impl}.h`,
`include/linux/perf/arm_pmu.h`, `include/linux/perf_event.h`). Building from the GKI pin is therefore
source-faithful to the OEM kernel tree.

## Per target

| Module | Source | OEM delta | Provenance class |
|---|---|---|---|
| timer-mediatek | ALPS `drivers/clocksource/timer-mediatek.c` | none | PUBLIC_EXACT |
| 8250_mtk | ALPS `drivers/tty/serial/8250/8250_mtk.c` | none | PUBLIC_EXACT |
| i2c-mt65xx | ALPS `drivers/i2c/busses/i2c-mt65xx.c` | `patches/source/0001`: DT property literal `mediatek-fifo-use-polling` | PUBLIC + OEM_LITERAL (stock string and stock base DTB corroborate; no public revision found) |
| reset-ti-syscon | ALPS `drivers/reset/reset-ti-syscon.c` | none | PUBLIC_EXACT |
| rtc-mt6685 | ALPS `drivers/rtc/rtc-mt6685.c` | none | PUBLIC_EXACT |
| regulator-vibrator | ALPS `drivers/leds/regulator-vibrator.c` | `patches/source/0002` (canonical research f23516c4): 3×9 placeholder non-code lines | PUBLIC + LAYOUT_PLACEHOLDER (count proven by `__LINE__`; original text not recoverable) |
| nvmem_mtk-devinfo | ALPS `drivers/nvmem/mtk-devinfo.c` | none | PUBLIC_EXACT |
| mtk-vmm-spm | ALPS `drivers/misc/mediatek/vmm_spm/mtk-vmm-spm.c` | none | PUBLIC_EXACT |
| mtk-mminfra-imax | ALPS `drivers/misc/mediatek/mminfra/mtk-mminfra-imax.c` | none | PUBLIC_EXACT |
| mtk_dpc | ALPS `drivers/gpu/drm/mediatek/dpc/{mtk_dpc_driver,mtk_dpc_mmp}.c` | none. The only mediatek_v2 file it compiles is `mtk_disp_vidle.h`, which no historical-drm patch touches. The inherited OEM display patches therefore affect only the mediatek-drm provider witnesses, keeping them at the owner's certified state | PUBLIC_EXACT |
| mtk-swpm-perf-arm-pmu | ALPS `drivers/misc/mediatek/swpm/swpm_perf_arm_pmu.c` | none | PUBLIC_EXACT |
| sec | ALPS `drivers/misc/mediatek/masp/asfv3/*` (`Makefile.sec` object list) | none | PUBLIC_EXACT |
| teeperf | ALPS `drivers/tee/teeperf/{main,user}.c` | none | PUBLIC_EXACT |
| arm_dsu_pmu | common `drivers/perf/arm_dsu_pmu.c` | none | PUBLIC_EXACT + source-built OEM BTF base |
| kfifo_buf | common `drivers/iio/buffer/kfifo_buf.c` | none | PUBLIC_EXACT + source-built OEM BTF base |
| industrialio-triggered-buffer | common `drivers/iio/buffer/industrialio-triggered-buffer.c` | none | PUBLIC_EXACT + source-built OEM BTF base |

## Search for authentic OEM text

Locations searched for the two OEM deltas (`evidence/source-search/`):
- 20 local ALPS revision snapshots (`gki-12901745-workspace/lieppos/*/alps|trees`).
- The NothingOSS trees.
- The 1.1M-commit `micode-kdm.git` history (195 i2c-mt65xx revisions, 16 regulator-vibrator revisions).

No public revision carries the hyphenated property or the stock vibrator line layout. The i2c literal is
nevertheless fixed by two independent stock artefacts: the module's own string table and the board's
vendor_boot DTB. The vibrator placeholder follows the canonical project precedent of certified
mediatek-drm patches 0003/0006, and is disclosed as a residual in BLOCKERS.tsv.

Licensing: all target and provider sources are GPL-2.0 MediaTek, Linux or ARM sources retrieved
unmodified from the pins. Their SPDX and copyright headers survive assembly, and patches add no new
copyright claims.
