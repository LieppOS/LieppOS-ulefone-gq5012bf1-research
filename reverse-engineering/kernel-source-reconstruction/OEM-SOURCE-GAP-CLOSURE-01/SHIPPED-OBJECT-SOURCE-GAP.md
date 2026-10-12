# Shipped-object modules: fpsgo.ko and msync2_frd.ko (both D)

Project rule: linking prebuilt `*_shipped` objects is **not** source reconstruction, so neither module can be
certified from the available material.

| | fpsgo.ko | msync2_frd.ko |
|---|---|---|
| Stock sha256 | `e5ec5051d443…` (vendor_dlkm) | `75405b2f0b7b…` (vendor_dlkm) |
| Stock modinfo | `license=Proprietary`, `author=MediaTek Inc.`, `description=MediaTek FPSGO` | `license=Proprietary`, `author=MediaTek Inc.`, `description=MediaTek MSYNC2` |
| Public recipe | NothingOSS kernel_modules `5f75a3b1`, `fpsgo_cus/Kbuild`: `fpsgo-y = src/fpsgo_main.o` + `src/xgf_v3_ko_quark.o` (CFI) or `_no_cfi.o` | `msync2_frd_cus/build/Kbuild`: `src/msync2_main.o` + `src/mtk_disp_msync.o` |
| Public C | `src/fpsgo_main.c`, `src/fpsgo_ko.h` | `src/msync2_main.c`, `src/mtk_disp_msync.h` |
| Prebuilt only | `xgf_v3_ko_quark.o_shipped` (208,312 B; 24 functions, e.g. `xgf_ko_init`, `xgf_est_runtime`, `fbt_cal_target_time`, `fstb_get_target_fps`, `rl_closed_loop_ko_init`, `fpsgo_set_last_quota`); built with clang r487747c (+pgo +bolt +lto) | `mtk_disp_msync.o_shipped` (12,488 B; 4 functions: `fpsgo2msync_hint_frameinfo`, `mtk_drm_get_target_fps`, `mtk_sync_slow_descent`, `mtk_sync_te_level_decision`); built with **clang r475365** (16.0.1), not the pinned r487747c |
| Config | `CONFIG_MTK_FPSGO_V3=m`, `CONFIG_CFI_CLANG=y` (selects `xgf_v3_ko_quark.o`) | `CONFIG_MTK_FPSGO_V3=m` |

## Licence and obligation

- **The `.modinfo` licence is `Proprietary`.** A GPL source obligation for these two modules cannot be inferred
  from the binaries. Whether loading them into GPL-2.0 Linux raises other questions is a legal matter outside this
  research.
- **The request is therefore a courtesy request**, not an entitlement claim (see `COMPONENT-SOURCE-REQUESTS.md`
  §MediaTek).
- Even with source, `msync2_frd` would need the older compiler (r475365) to reproduce the stock object. That would
  be recorded as an extra pinned toolchain, not a waiver.

## Status

D, unchanged. No experiment can make progress without MediaTek's XGF/FSTB/FBT and MSYNC source. The already-A
`mtk_fpsgo.ko` is a different module and is unaffected.
