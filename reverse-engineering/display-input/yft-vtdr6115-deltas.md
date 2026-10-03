# Ulefone / YFT deltas — VTDR6115 main panel and `mtk_panel_ext`

## Donor situation

There is **no VTDR6115 panel driver in any locally available donor tree**:

- `kernel_device_modules-6.1` (NothingOSS MT6878 `957dac1`, commit `0579490`)
  contains no `*vtdr6115*` file at all;
- the only other VTDR6115 source on disk is
  `lieppos/panel-vtdr6115-donor-red/panel/dsi-panel-mot-csot-vtdr6115-655-fhdp-dphy-vdo-144hz.c`
  — a **Motorola/CSOT 6.55" 144 Hz** panel using the same DDIC, with a
  different module layout, different timings, an LHBM alpha table and a
  Qualcomm-style `dsi_panel` framework. It is not the donor; it only confirms
  the DDIC's command vocabulary.

So this driver is **reconstructed from the stock binary**, not grafted:
`reverse-engineering/display-input/vtdr6115/source/panel-ky-vtdr6115-dphy-cmd.c`
(1 066 lines) plus `mtk_panel_ext_stock_abi.h`, a layout-exact model of the
vendor header. Validation is by binary parity, not by diff against a donor.

The entire file is therefore, in a sense, "the delta". What follows records the
deltas that are *provable statements about Ulefone's build* rather than about
reconstruction technique.

## Confirmed deltas

### 1. YFT branding is compiled into the panel driver

| | |
|---|---|
| donor behaviour | MediaTek reference panels log with `pr_info("%s+\n", __func__)` |
| stock GQ5012BF1 | 11 distinct log strings carrying `yft-lcm-vtdr6115-drv` and `yft-drv-`, e.g. `"%s+ yft-lcm-vtdr6115-drv- start reset_gpio H-L-H,%d"`, `"yft-drv- %s vci_gpio is on !"` |
| evidence | `.rodata.str1.1` of the stock module (byte-identical in the rebuild) |
| confidence | **PROVEN** |

`yft` = Shenzhen YFT, Ulefone's ODM; the same tag appears in `yft_devinfo.ko`,
`yft_tpd_gesture.ko` and the FocalTech touch driver.

### 2. Rails are GPIOs, acquired and released per transition

| | |
|---|---|
| donor behaviour | `devm_regulator_get(dev, "vci"/"dvdd")` or a descriptor requested once at probe |
| stock GQ5012BF1 | `vci-gpios`/`dvdd-gpios` in DT; each transition does `devm_gpiod_get()` → `gpiod_set_value()` → `devm_gpiod_put()` |
| evidence | DT node `panel1@0`; `lcm_prepare` / `lcm_unprepare` / `lcm_panel_init` / `panel_ext_reset`, all byte-identical in the rebuild |
| confidence | **PROVEN** |

### 3. `powerdm-gpios` is declared but never used

| | |
|---|---|
| stock DT | `powerdm-gpios = <&pio 0xc2 0>` (GPIO 194) on `panel1@0` |
| stock driver | never requests it — only `reset`, `vci`, `dvdd` appear in the module's string table |
| confidence | **PROVEN** (dead board property) |

### 4. Double-pulse reset with 15/15/15/20 ms

| | |
|---|---|
| donor behaviour | MTK reference VTDR6115-class panels use a single L–H pulse of 1–10 ms |
| stock GQ5012BF1 | L 15 ms → H 15 ms → L 15 ms → H 20 ms (65 ms) |
| evidence | `lcm_panel_init` (byte-identical) |
| confidence | **PROVEN** |

### 5. Bootloader hand-off is assumed

| | |
|---|---|
| stock | `lcm_probe()` sets `prepared = enabled = true` and logs `"vtdr6115,120hz dsi_node:%s set prepared = enabled = false"` |
| effect | the first `lcm_prepare()` is a no-op; the kernel never re-inits the panel on the boot path |
| confidence | **PROVEN** |

### 6. Three modes only, vfp-based

60 / 90 / 120 Hz, identical horizontal timing, `change_fps_by_vfp_send_cmd = 1`,
2-byte `dfps_cmd_table0` per mode. No 144 Hz and no 48/30 Hz low-power mode,
unlike the Motorola VTDR6115 variant. **PROVEN** from the three byte-identical
66 328-byte `ext_params` objects.

### 7. HBM is a brightness override, not a panel feature

`sethbm_cmdq` writes `0x51 0x0F 0xFF` / `0x51 0x03 0xFF`. No vendor HBM
register, `hbm_en_time = hbm_dis_time = 0`, no LHBM alpha table (the Motorola
variant has one). **PROVEN**.

### 8. No CABC, no AOD/doze, no panel-ID read, no ATA

`panel_ata_check()` is 8 bytes (`mov w0, #1; ret`). None of the doze slots in
`ext_funcs` is populated. No `read_panelid`. **PROVEN**.

### 9. `mtk_panel_ext`: the stock header has 40 `mtk_panel_funcs` slots, the donor 42

Two donor members do **not** exist in the stock vendor header:

| donor offset | member | stock |
|---|---|---|
| 24 | `set_backlight_pack` | absent |
| 224 | `hbm_set_pack` | absent |

Both are the `dcs_write_gce_pack` variants of existing calls.

**Evidence (independent, three sources agreeing):**

1. `pahole` on a rebuild against the donor header: `struct mtk_panel_funcs` =
   336 B, 42 members, `get_lcm_version` at 264.
2. Stock `mediatek-drm-panel-drv.ko` object `mtk_drm_panel_ext_funcs` is
   **320 B** and its 30 populated slots hold handlers *named after the member
   they implement* (`mtk_panel_set_bl_elvss_cmdq` at 0, `mtk_panel_reset` at 48,
   `mtk_panel_get_lcm_version` at 248, `mtk_panel_read_panelid` at 288, …),
   which pins 30 of the 40 stock slots by name.
3. Stock `panel-ky-vtdr6115-dphy-cmd.ko` object `ext_funcs` pins two more:
   `mtk_get_res_switch_type` at 80 and `mtk_scaling_mode_mapping` at 88.

Aligning the two tables leaves exactly one unmatched donor member before
offset 88 (`set_backlight_pack`) and exactly one between 88 and 264
(`hbm_set_pack`), with every other member matching by name. Removing those two
makes `get_lcm_version` land at `0xf8` — the value stock's
`mtk_panel_ext_create` loads.

**Result:** rebuilding `mtk_panel_ext.c` against the corrected header gives
**12/12 functions byte-identical** (was 11/12), 13/13 data objects, 6/6 import
CRCs, identical `.modinfo`. Confidence: **PROVEN**.

### 10. `mtk_panel_ext`: the Nothing fingerprint/HBM block is absent from stock

Already recorded in [`kernel/notes.md`](kernel/notes.md): the donor's
`g_lcm_hbm_status` / `g_lcm_ui_status` statics, the four exported
`mtk_panel_*_ui_status` / `proc_hbm` / `update_lcm_state_to_fingerprint`
functions, the `FP_NOTIFIER_EVENT_UI` notifier call and its 273-byte string
block do not exist in the shipped module. **PROVEN** from symbol and section
comparison.

Note the consequence for the panel: the fingerprint-HBM path on this device is
**only** `/sys/class/primary_lcm/set_hbm_backlight` →
`ddic_dsi_send_cmd_for_fp()`, which is in the panel driver itself and proven
from its own imports and strings — not the Nothing notifier path.

## Reconstruction-level source deltas recovered this pass

These are differences between the previous frozen reconstruction and the stock
binary, now fixed:

| # | construct | before | after | effect |
|---|---|---|---|---|
| 1 | the `0x6C` refresh-select in `lcm_panel_init` | `if (fps==60) … else if (fps==120) … else if (fps==90) …` | `switch (current_fps) { case 120: 0x02; case 90: 0x01; case 60: 0x00; }` | reproduces stock's compare order (`0x3c`, `0x78`, `0x5a`) **and** stock's `.rodata` allocation order (`6c02`, `6c01`, `6c00`) — `lcm_panel_init` and `lcm_unprepare` became byte-identical, and all three 2-byte objects now match |
| 2 | provider CRCs | source-built harness providers → 7 mismatching modversion CRCs | `Module.symvers` harvested from the **stock** `mtk_panel_ext.ko` / `mediatek-drm.ko` `__kcrctab` | 45/45 import CRCs exact; module is no longer a "comparison artifact" |
| 3 | build tree | out-of-tree build with `vermagic …-maybe-dirty` | isolated `M=` build in the exact GKI tree with `module_scmversion=` | `.modinfo` and `vermagic` identical |

## Zero-delta statements

- `mtk_disp_notify.c`: **zero source deltas** — the donor file is the shipped
  file (see `kernel/notes.md`).
- `mtk_panel_ext.c`: exactly one delta (the Nothing fingerprint/HBM block) plus
  the two header members above; no other difference.
