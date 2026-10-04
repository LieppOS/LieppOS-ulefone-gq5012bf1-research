# mediatek-drm.ko (+ mediatek-drm-panel-drv.ko): exact reconstruction

Offline, static work only. The stock module is
`vendor_ramdisk/lib/modules/mediatek-drm.ko`
(sha256 `127e2dd9f5d3d942c3898d14a7707f77ef56335d10c6be7d580559a82104813e`,
5 719 712 bytes, 25 dependencies).

## Result

| axis | mediatek-drm.ko | mediatek-drm-panel-drv.ko |
|---|---|---|
| functions (A stock vs B rebuild) | **2376/2376 byte-identical** (2444 symbols incl. duplicate statics; all 2376 names size+KCFI equal) | **123/123** (was 111/123) |
| data objects | 2072/2072 bytes-equal | 43/43 |
| imports (name + modversion CRC, `__versions` order) | 542/542 | 71/71 |
| exports (name + licence) / export CRCs (`__kcrctab`) | 52/52 / **51/51** | 53/53 / 53/53 |
| modinfo | 569/569 positional | 30/30 |
| relocations (non-DWARF) | 98 557/98 557 | 7010/7010 |
| ELF sections (debug-stripped) | 70/70, only `.note.gnu.build-id` differs | 43/43, only build-id differs |
| symbol table | identical (incl. one WEAK binding) | — |
| B1 vs B2 clean rebuild | file-identical (sha256 `be6ad527…c3648c6`) | file-identical (sha256 `8cd2c907…dbcb14f8`) |
| runtime validation | none (offline) | none (module is unused on this board) |

`.note.gnu.build-id` hashes the pre-strip image (DWARF with the original build
paths) and is the only differing byte range. Proof files:
[`parity/full-module-proof.txt`](parity/full-module-proof.txt),
[`parity/SUMMARY.txt`](parity/SUMMARY.txt), and the per-symbol TSVs (relocations as `relocation-parity.tsv.xz`) in
[`parity/`](parity/). The panel-driver proof is in
[`../backlight-glue/parity/mediatek-drm-panel-drv/`](../backlight-glue/parity/mediatek-drm-panel-drv/).

## Source identity

- **Base:** MediaTek ALPS history for MT6878 as carried in
  `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`, commit
  **`5e415e059253ce0d2e61c97108e5f5785d71f06f`** (2025-02-25,
  `[ALPS09775602] mml: dl for vdo`, the tip of that ALPS batch). Thirteen
  candidate snapshots were rebuilt unmodified and scored. This one was the
  best, at 2218/2376 functions byte-identical, with three others at 2217 and
  the rest between 1536 and 2188.
- **GQ5012BF1/ODM delta:** 10 patches, ~290 changed lines, in
  [`source/series/`](source/series/) (squashed:
  [`source/gq5012bf1-mediatek-drm.patch`](source/gq5012bf1-mediatek-drm.patch)).
- **Build:** isolated `M=` build against the GKI 6.1.115 `kout`, clang-r487747c,
  `CONFIG_LTO_NONE`, `KCFLAGS=-faddrsig`,
  `-fmacro-prefix-map=<tree>/=../kernel_device_modules-6.1/`, stock-harvested
  `Module.symvers` for vendor providers ([`scripts/build.sh`](scripts/build.sh)).

### Object composition (step 1, before any patching)

There are 66 objects in `mediatek-drm.mod` link order. Every stock function
maps to exactly one rebuilt object by symbol name and link order (0 functions
out of order, 0 stock-only). See [`parity/object-map.tsv`](parity/object-map.tsv)
for the stock `.text` ranges and [`parity/object-groups.tsv`](parity/object-groups.tsv)
for the per-object rollup, now all exact. The groups that matter for this
board are:

| group | objects |
|---|---|
| panel / LCM interface | `mtk_dsi.o` (155), `mtk_mipi_tx.o` (104), `mtk_drm_ddp_comp.o`, `mtk_panel_ext.h` ABI |
| panel lifecycle / pipeline | `mtk_drm_drv.o`, `mtk_drm_crtc.o` (289), `mtk_drm_ddp.o`, `mtk_drm_ddp_addon.o`, `mtk_drm_lowpower.o`, `platform/mtk_drm_6835.o` |
| brightness | `mtk_debug.o` (`mtkfb_set_backlight_level`, exported) → `mtk_drm_crtc.o` (`mtk_drm_setbacklight`) → `mtk_dsi.o` → panel `set_backlight`, `mtk_disp_ccorr.o` (`disp_pq_notify_backlight_changed`), `mtk_disp_aal.o` |
| ESD / recovery | `mtk_disp_recovery.o` |
| debug / FP-HBM hook | `mtk_debug.o` (`ddic_dsi_send_cmd_for_fp`) |
| PQ / composition | ovl, rdma, rsz, wdma, color, ccorr, c3d, gamma, aal, dither, chist, tdshp, postmask, dsc, spr, cm, oddmr, merge, splitter, y2r/r2y, inlinerotate, … |
| DisplayPort | `mtk_dp.o`, `mtk_dp_hal.o`, `mtk_dp_intf.o`, `mtk_dp_debug.o`. The live DT has **no DP node**, so these are static-only on this board |

## What the ODM changed (all proven by bytes)

| delta | evidence | effect on GQ5012BF1 |
|---|---|---|
| `__weak void ddic_dsi_send_cmd_for_fp(u8 *tx_buf, unsigned int cmd_num)`, exported (`mtk_debug.c`) | function bytes; symtab `WEAK`; export CRC `0x14818502` reproduced only with `__weak` placed first (genksyms hashes the attribute) | VTDR6115 `set_hbm_backlight` (fingerprint HBM sysfs) sends DCS `0x51` via `mtk_ddic_dsi_send_cmd`: DT `0x05`/`0x15`/`0x39` by length, LP mode |
| new io_cmd `DSI_GET_AOD_STATE` (enum member in `mtk_drm_ddp_comp.h`) + `mtk_dsi_io_cmd` case returning `mtk_dsi_doze_state()` | enum position by code. The **name** was recovered by brute-forcing genksyms over 10 754 candidates against the stock export CRC of `disp_pq_notify_backlight_changed` (`0xb3932c07`), and `DSI_GET_AOD_STATE` was the unique match | ESD check (`mtk_disp_recovery.c`) returns 0 and skips while the panel is in AOD doze |
| `force_high_step`/`force_high_enabled=2` on AOD enter (`mtk_drm_crtc.c`) | bytes + `DDPMSG` string | MMDVFS forced high on doze entry |
| doze switch: `mtk_dsi_tx_buf_rw()` when `dsi_buffer`, `mmclk_by_datarate(dsi, crtc, 1)` (`mtk_dsi.c`) | bytes | DSI clock/buffer handling across doze transitions |
| `DDP_COMPONENT_PWM0` enabled in the mt6878 main path; `mt6878-disp-pwm` match split into `-pwm0`/`-pwm1` (`mtk_drm_drv.c`) | bytes, `.rodata` match table; live DT has `disp-pwm0@1100e000`/`disp-pwm1@1100f000` | PWM component bound, but no PWM backlight consumer (brightness is DCS `0x51`) |
| DP AUX refine (MTK ALPS09011355 variant: fake-complete IRQ handling, EDID-complete IRQ, `REG_36F4` defines, "chia-cheng" debug) | bytes + strings | static only (no DP in DT) |
| `mtk_dp_intf_config` MT6989 buffer golden values; `mt6989_mtk_sodi_config` ovlsys1 `MISC |= 0x280` | bytes; dead code on MT6878 | none |
| source-line layout padding (blank lines, each marked `/* GQ5012BF1 layout … */`) | `__LINE__` immediates in `DDP*`/`DPTX*` logs give exact line-count deltas between proven bounds | none (text not recoverable, count proven) |

## Panel-ext ABI header: the "private mtk_lcm_* layout" was not private

`mediatek-drm-panel-drv.ko` had been stuck at 111/123, which was blamed on a
private `mtk_lcm_dsi_params` layout. The 12 differing functions actually read
`struct mtk_lcm_mode_dsi::ext_param`, which is a `struct mtk_panel_params` from
`mtk_panel_ext.h`. The harness had been building with the
Nothing-tip header, which has `ESD_CHECK_NUM 4`, `READ_DDIC_SLOT_NUM 16`,
`MAX_DYN_CMD_NUM 60`, `change_fps_by_vfp_send_cmd` moved, plus
`delay_first_bl_en` and `vdo_mix_mode_en`. That header gives
`sizeof(mtk_panel_params)` = 69 232, against 66 328 in stock.

The ALPS `5e415e059253` header ([`source/mtk_panel_ext.h`](source/mtk_panel_ext.h),
values 3 / 8 / 20 and without the Nothing members) is proven three
independent ways:

1. `mediatek-drm.ko` is byte-identical when built with it.
2. `mediatek-drm-panel-drv.ko` goes from 111/123 to **123/123**, and the
   whole module matches except build-id.
3. `mtk_panel_ext.ko` rebuilt with it now also matches all **9/9 export
   CRCs**. Before, 5 were mismatched, because genksyms hashes the full type
   graph. Every section except build-id now matches
   ([`../kernel/parity/mtk_panel_ext.header-proof.txt`](../kernel/parity/mtk_panel_ext.header-proof.txt)).

This header also yields the 66 328-byte `mtk_panel_params` that
`vtdr6115/source/mtk_panel_ext_stock_abi.h` had modelled offset-by-offset, so
the VTDR6115 reserved-padding model can be replaced by the real type graph. That
is a follow-up and was not done here.

## Reproduce

```
scripts/build.sh <ALPS 5e415e059253 tree + source/series applied>
python3 ko-parity-tsv.py stock.ko mediatek-drm.stripped.ko par/   # rear-display-input/scripts
python3 scripts/kcrc.py stock.ko mediatek-drm.stripped.ko         # export CRCs
python3 scripts/objmap.py stock.ko <build dir> par/ om/           # object map
```

Helper tools: [`scripts/classify.py`](scripts/classify.py) classifies
residuals into CODE, LINE (only `__LINE__` immediates differ) and RELOC.
[`scripts/linebounds.py`](scripts/linebounds.py) turns `__LINE__` immediates
into proven insertion intervals. [`scripts/ksym.py`](scripts/ksym.py) and
[`scripts/brute.py`](scripts/brute.py) do genksyms CRC recomputation and
identifier/prototype search against stock CRCs.

## Open / not claimed

- Runtime behaviour on hardware: none of this was validated on the device.
- Exact text of the padded source lines (only their count is proven).
- VTDR6115 header model → real header swap (follow-up; VTDR6115 is already DONE).
