# VTDR6115 main panel — `panel-ky-vtdr6115-dphy-cmd.ko`

## Stock artifact identity (Phase 1)

| item | value |
|---|---|
| path | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/panel-ky-vtdr6115-dphy-cmd.ko` (vendor **ramdisk**, not `vendor_dlkm`) |
| sha256 | `1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07` |
| size | 246 288 B |
| build-id | `c86ee66361fe30b7b27e0c1a11edb1b81eafd2b0` |
| `name` | `panel_ky_vtdr6115_dphy_cmd` |
| `vermagic` | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| `depends` | `mtk_panel_ext,mediatek-drm` |
| `author` | `shaohua deng <shaohua.deng@mediatek.com>` |
| `description` | `vtdr6115 VDO 120HZ AMOLED Panel Driver` |
| `license` | `GPL v2` |
| aliases | `of:N*T*Chx,vtdr6115,cmd,120hz,ky`, `of:N*T*Chx,vtdr6115,cmd,120hz,kyC*` |
| functions | 24 |
| data objects | 83 |
| imports | **45** (`__versions`, 64-byte entries, 2 880 B) |
| exports | **0** |
| KCFI | none (no `__cfi` symbols) |
| `.text` | 5 280 B (0x14a0) |
| `.data` | **199 816 B** (0x30c88) — three 66 328-byte `mtk_panel_params` + `ext_funcs` + globals |
| `.rodata` | 1 123 B; `.rodata.str1.1` 1 955 B |
| relocations | 634 total (`.rela.text` 563, `.rela.data` 30, …) |
| embedded source strings | 11 `yft-lcm-vtdr6115-drv` log strings, `lcm,vtdr6115,vdo,120hz`, `yft-drv- %s vci_gpio/dvdd_pin/reset_gpio is on/off !` |

## Hardware (Phase 3)

See [`dt-contract.md`](dt-contract.md). Short form: VTDR6115 AMOLED DDIC,
1080×2400, 4-lane **D-PHY** video mode on **dsi0**, PLL 435 MHz / 870 Mbps,
DT node `panel1@0` compatible `hx,vtdr6115,cmd,120hz,ky`, **reset GPIO 90**,
**VCI GPIO 39**, **DVDD GPIO 38**, unused `powerdm-gpios` GPIO 194, TE on
**EINT 89**, no regulators, no pinctrl state, no gate IC.

## Modes (Phase 5) — [`modes.tsv`](modes.tsv)

Three modes, all 1080×2400 with identical horizontal timing
(hfp 100 / hsa 8 / hbp 16) and vfp-based switching:

| id | Hz | clock | vfp | vtotal | dfps cmd |
|---|---|---|---|---|---|
| 0 | 60 | 357 732 kHz | 2528 | 4952 | `0x6C 0x00` |
| 1 | 90 | 358 671 kHz | 886 | 3310 | `0x6C 0x01` |
| 2 | 120 | 358 888 kHz | 60 | 2484 | `0x6C 0x02` |

`change_fps_by_vfp_send_cmd = 1`, so switching is seamless (vfp change plus the
2-byte `dfps_cmd_table0`). `mode_switch()` validates the target rate and
returns 0 for 60/90/120 — it sends no commands itself.

## DSC (Phase 6)

DSC **1.1** (`ver = 17` = 0x11), enabled, RCT on, **8 bpc**, **8 bpp**
(`bit_per_pixel = 128` in 1/16 units), picture 1080×2400, **slice 540×12**,
2 slices per line (`slice_mode = 1`), chunk 540, `xmit_delay 512`,
`dec_delay 526`, `scale_value 32`, `increment_interval 287`,
`decrement_interval 7`, `line_bpg_offset 12`, `nfl_bpg_offset 2235`,
`slice_bpg_offset 2170`, `initial_offset 6144`, `final_offset 4336`,
`flatness_minqp 3`, `flatness_maxqp 12`, `rc_model_size 8192`,
`rc_edge_factor 6`, `rc_quant_incr_limit0/1 = 11`, `rc_tgt_offset_hi/lo = 3`,
`dsc_line_buf_depth 9`, `dsc_cfg 34`, `bp_enable 1`, `rgb_swap 0`.

`ext_pps_cfg.enable = 1` with vendor RC tables
(`vtdr6115_vdo_120hz_dphy_buf_thresh`, `…range_min_qp`, `…range_max_qp`,
`…range_bpg_ofs`) — i.e. **vendor-tuned RC, not the DSC 1.1 defaults**. The
same configuration is also pushed to the DDIC as the literal 95-byte PPS of DCS
`0x70` in the init stream, and host and panel agree byte-for-byte (both are
inside the byte-identical `.data`/`.rodata`).

## Command tables (Phase 4) — [`command-tables.tsv`](command-tables.tsv)

46 compiled `lcm_dcs_write_seq_static()` statements in `lcm_panel_init`
(44 executed per boot; the three `0x6C` variants are mutually exclusive),
2 in `lcm_unprepare`, plus the runtime brightness/HBM paths.
**All 46 static command arrays are byte-identical to stock**, and so are the
three 66 328-byte `ext_params` blobs that carry the DSC, ESD and dfps tables.

## Power / reset (Phase 7) — [`power-sequence.md`](power-sequence.md)

DVDD → 10 ms → VCI → reset **L15/H15/L15/H20 ms** → 44-command init →
`0x11` +120 ms → `0x29` +50 ms → `0x51` brightness.
Down: `0x28` +20 ms → `0x10` +200 ms → reset 0 → 10 ms → VCI 0 → 10 ms → DVDD 0.

## ESD (Phase 8) — [`esd-recovery.md`](esd-recovery.md)

`cust_esd_check = 1`, one item: read DCS `0x0A`, expect `0x9C`. Recovery is the
generic MTK DRM path (`MTK_DRM_OPT_ESD_CHECK_RECOVERY = 1` on dsi0) that calls
the panel's disable/unprepare/prepare/enable — a full rail power cycle. Mode,
DSC and brightness are restored by the init stream from the `current_fps` /
`current_backlight` globals; HBM state is not.

## Brightness / HBM / doze (Phase 9)

| path | mechanism |
|---|---|
| brightness | DCS `0x51`, **12-bit** (`0x51, (level>>8)&0xF, level&0xFF`), via `lcm_setbacklight_cmdq`; `current_backlight` cached in `.data` |
| boot brightness | same 3-byte write at the end of `lcm_panel_init` |
| HBM | `sethbm_cmdq`: `0x51 0x0F 0xFF` on, `0x51 0x03 0xFF` off — **there is no dedicated HBM register on this panel**, HBM is just a brightness override; `hbm_en_time = hbm_dis_time = 0` |
| fingerprint HBM | `/sys/class/primary_lcm/set_hbm_backlight` → `set_hbm_backlight_store()` → `ddic_dsi_send_cmd_for_fp()` in `mediatek-drm.ko`. Present in **this** driver and proven from stock strings/imports — this is *not* inferred from the Nothing `mtk_panel_ext` block, which was separately proven absent. The device's fingerprint reader is side-mounted; this sysfs path is the stock vendor's generic hook and its only effect is a brightness override |
| CABC | **absent** — no CABC command, no `set_aod_light_mode`, `0x55` never written |
| doze / AOD | **absent** — none of `doze_enable`, `doze_disable`, `doze_area`, `doze_get_mode_flags` is populated in `ext_funcs` |
| DC dimming | **absent** |

`ext_funcs` populates exactly 10 of 40 slots:
`set_backlight_cmdq`, `reset`, `ata_check`, `ext_param_set`, `ext_param_get`,
`get_res_switch_type`, `scaling_mode_mapping`, `mode_switch`, `hbm_set_cmdq`,
`set_value`.

## Parity (Phase 10)

**A** = the stock module above.
**B** = rebuild of [`source/panel-ky-vtdr6115-dphy-cmd.c`](source/) at GKI
`6.1.115-android14-11-g945dff7bc1bf`, clang r487747c, isolated `M=` build with
`KBUILD_EXTRA_SYMBOLS` pointing at
[`source/stock-providers.symvers`](source/stock-providers.symvers) — CRCs
harvested from the **stock** `mtk_panel_ext.ko` and `mediatek-drm.ko`
`__kcrctab` by [`source/mk_symvers.py`](source/mk_symvers.py).

| axis | result | file |
|---|---|---|
| functions | 24/24 present, 22/24 size-identical, **20/24 byte-identical** | [`parity/function-parity.tsv`](parity/function-parity.tsv) |
| data objects | 83/83 shared, **83/83 byte-identical** (10 one-sided rows are `__UNIQUE_ID_*` counter names only) | [`parity/data-parity.tsv`](parity/data-parity.tsv) |
| `.data` | **199 816 B byte-identical** | [`parity/section-parity.tsv`](parity/section-parity.tsv) |
| `.rodata.str1.1` | byte-identical | same |
| imports / modversions | **45/45 names and CRCs exact** | [`parity/abi-parity.tsv`](parity/abi-parity.tsv) |
| exports | 0/0 | — |
| KCFI | n/a both sides | — |
| `.modinfo` incl. `vermagic` | **identical** | [`parity/panel-ky-vtdr6115.parity.txt`](parity/panel-ky-vtdr6115.parity.txt) |
| `.gnu.linkonce.this_module` | byte-identical (1 088 B) | same |
| `.init.text`, `.exit.text`, `.init.eh_frame` | byte-identical | same |
| relocation counts | `.rela.data` 30/30, `.rela.rodata` 5/5, `.rela.init.text` 5/5, `.rela.exit.text` 3/3, `.rela.text` 563 vs 561 | [`parity/relocation-parity.tsv`](parity/relocation-parity.tsv) |
| build-id | differs (expected — different build) | — |

This improves on the previous frozen reconstruction (19/24 functions, 7 CRC
mismatches, wrong `vermagic`) and removes the "comparison artifact" caveat: the
module is now linked against the real stock provider ABI.

## Residual deltas (Phase 11)

Four functions differ; **all four trace to the placement of one 3-byte
constant** (`__const.lcm_panel_init.bl_tb0 = {0x51, 0x07, 0xFF}`) plus local
scheduling, and none changes behaviour:

| function | A | B | cause |
|---|---|---|---|
| `lcm_panel_init` | 1276 | 1276 | **now byte-identical** after two recovered source deltas (see deltas doc) |
| `lcm_unprepare` | 520 | 520 | **now byte-identical** |
| `sethbm_cmdq` | 232 | 220 | stock materialises the full 3-byte `bl_tb0` initialiser from `.rodata` before overwriting `[1]`/`[2]`; the rebuild folds it. Identical calls, identical transmitted bytes |
| `lcm_setbacklight_cmdq` | 264 | 264 | two `ldrb` loads scheduled in the opposite order; identical instruction multiset |
| `set_hbm_backlight_store` | 316 | 316 | register allocation + branch form (`cbz`/`b` vs `b.eq`/`cbnz`); identical calls and stored bytes |
| `lcm_probe` | 1236 | 1240 | stock keeps two adjacent 4-byte locals separate (`str wzr,[sp]`, `str wzr,[sp,#4]`); the rebuild merges them into one `str xzr,[sp]` — a stack-slot assignment difference |

In stock the constant lives at `.rodata+0x462` (the very end, after the three
`drm_display_mode` objects); in the rebuild clang places it at `.rodata+0x1d0`.
It is referenced by exactly two functions (`lcm_panel_init`, `sethbm_cmdq` —
proven from `.rela.text`), and no source ordering that keeps the code faithful
reproduces the stock placement; forcing it (by adding an initialiser to
`set_hbm_backlight_store`, which stock does **not** have) makes `.rodata`
byte-exact but corrupts that function. The faithful variant is kept.

## Ulefone/YFT deltas (Phase 12)

See [`../yft-vtdr6115-deltas.md`](../yft-vtdr6115-deltas.md).
