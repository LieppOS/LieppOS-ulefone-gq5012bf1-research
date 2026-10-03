# VTDR6115 — ESD check and recovery

## What the panel driver owns

Exactly one thing: the ESD *check descriptor*, inside each of the three
66 328-byte `mtk_panel_params` objects (all three byte-identical to stock):

```
.cust_esd_check            = 1        /* custom read, not the generic 0x0A/0x9C default */
.esd_check_enable          = 1
.lcm_esd_check_table[0]    = {
        .cmd          = 0x0A,         /* DCS get_power_mode */
        .count        = 1,
        .para_list[0] = 0x9C,         /* expected value */
}
```

`lcm_esd_check_table[1]` and `[2]` are all-zero — **one** check item only.
`0x9C` = `0b1001_1100` from DCS `get_power_mode`: display on (bit 2),
normal mode (bit 3), sleep out (bit 4), booster on (bit 7).

There is **no** `esd_recovery` callback, no `ata_check` logic
(`panel_ata_check()` is a 8-byte function that returns `1` unconditionally),
and no panel-ID read in the whole module.

## Where the recovery actually happens

In `mediatek-drm.ko`, not here. The DT enables it explicitly on dsi0:

```
MTK_DRM_OPT_ESD_CHECK_RECOVERY = 1
MTK_DRM_OPT_ESD_CHECK_SWITCH   = 1
```

(`helper-name` / `helper-value` arrays of the `mediatek,disp_dsi0` node). The
MTK DRM core therefore:

1. runs a periodic read of DCS `0x0A` (1 byte) through the DSI read path,
2. compares against `0x9C`,
3. on mismatch calls the panel's `drm_panel_funcs`:
   `lcm_disable()` → `lcm_unprepare()` → `lcm_prepare()` → `lcm_enable()`.

So recovery on this device is a **full rail power cycle**: display-off →
sleep-in → reset low → VCI off → DVDD off → DVDD on → VCI on → the complete
65 ms double-pulse reset → the full 44-command init stream → sleep-out →
display-on. Timings are in [`power-sequence.md`](power-sequence.md).

## What is restored after recovery

| item | restored by | how |
|---|---|---|
| refresh rate | the panel driver itself | `lcm_panel_init()` re-reads the module-global `current_fps` and emits `0x6C 0x02/0x01/0x00` |
| DSC / PPS | the panel driver | the 95-byte `0x70` PPS is part of the same init stream |
| brightness | the panel driver | the final `0x51` of the init stream uses the module-global `current_backlight` |
| HBM state | **not restored** | `sethbm_cmdq` has no state memory; `ctx->hbm_flag` is only the sysfs mirror |
| mode timings (vfp) | MTK DRM | re-applies the `mtk_panel_params` of the active mode |

`current_fps` and `current_backlight` are module-level globals in `.data` that
survive the recovery cycle, which is why no mode or brightness glitch is
expected after an ESD event.

## Generic or panel-specific?

**Generic MTK DRM mechanism, panel-specific descriptor.** The only panel
contribution is `cust_esd_check = 1` plus the single `0x0A → 0x9C` item. No
part of the recovery control flow lives in
`panel-ky-vtdr6115-dphy-cmd.ko`.

## Known evidence of it firing

Ulefone/stock logs show ESD recovery activity on this device; the static path
above is what those logs exercise. No runtime test was performed here
(offline static analysis only).
