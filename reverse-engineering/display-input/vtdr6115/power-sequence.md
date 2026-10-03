# VTDR6115 — power / reset sequencing (exact)

Every value below is taken from the reconstructed source whose `.rodata`,
`.rodata.str1.1` and 199 816-byte `.data` are byte-identical to the shipped
module, and whose `lcm_prepare` / `lcm_unprepare` / `lcm_panel_init` are
**byte-identical** machine code.

## Power on — `lcm_prepare()`

```
if (ctx->prepared) return 0;              /* bootloader handoff: true at probe */
DVDD  (GPIO 38) -> 1                       devm_gpiod_get("dvdd", OUT_HIGH) + put
msleep(10)
VCI   (GPIO 39) -> 1                       devm_gpiod_get("vci", OUT_HIGH) + put
lcm_panel_init(ctx)
if (ctx->error < 0) lcm_unprepare(panel)
ctx->prepared = true
```

There is **no delay between VCI-on and the reset sequence** — `lcm_panel_init`
is entered immediately.

## Reset + init — `lcm_panel_init()`

```
reset (GPIO 90) acquired OUT_HIGH
  -> 0 ; usleep_range(15000, 15000)
  -> 1 ; usleep_range(15000, 15000)
  -> 0 ; usleep_range(15000, 15000)
  -> 1 ; usleep_range(20000, 20000)
reset descriptor released (devm_gpiod_put)
printk("%s+ yft-lcm-vtdr6115-drv- start reset_gpio H-L-H,%d", __func__, current_fps)
```

i.e. **L(15 ms) – H(15 ms) – L(15 ms) – H(20 ms)**, 65 ms total, then the DCS
stream:

| order | command | payload | delay after |
|---|---|---|---|
| 1 | `0x03` | `0x01` | — |
| 2 | `0x53` | `0x20` | — |
| 3 | `0x51` | `0x00 0xFF` | — |
| 4 | `0x6F` | `0x01` | — |
| 5 | `0x35` | `0x00` | — (TE on) |
| 6 | `0x59` | `0x00` | — |
| 7 | `0x6C` | `0x02` / `0x01` / `0x00` for 120 / 90 / 60 Hz | — |
| 8 | `0x6D` | `0x00` | — |
| 9 | `0x70` | 95-byte **DSC PPS** | — |
| 10… | `0xF0 0xAA 0x19`, `0xD0 …`, `0xF0 0xAA 0x18`, `0xB0 0x13`, `0xB2 0x13`, `0xFF 0x5A 0x81`, `0x65 0x03`, `0xF4 0x03`, `0xF0 0xAA 0x12`, `0x65 0x09`, `0xC5 0x07`, … | vendor page-select / analogue trim block | — |
| n−3 | `0x11` (`MIPI_DCS_EXIT_SLEEP_MODE`) | — | **msleep(120)** |
| n−2 | `0x29` (`MIPI_DCS_SET_DISPLAY_ON`) | — | **msleep(50)** |
| n−1 | `0x51` | `bl_tb0[] = {0x51, (current_backlight>>8)&0xF, current_backlight&0xFF}` | — |

46 `lcm_dcs_write_seq_static()` statements are compiled in; **44 execute per
boot** because the three `0x6C` variants are mutually exclusive. The prior
measurement of the executed stream is **45 writes / 287 bytes** per refresh-rate
path (the extra entry is the runtime `0x51` built from `bl_tb0`), with per-fps
hashes recorded in
[`parity/panel-ky-vtdr6115.parity.txt`](parity/panel-ky-vtdr6115.parity.txt)
and in `kernel/phase4-panel-vtdr6115-verify-recon-vs-stock.txt`.

## Power off — `lcm_unprepare()`

```
if (!ctx->prepared) return 0;
0x28  MIPI_DCS_SET_DISPLAY_OFF     ; msleep(20)
0x10  MIPI_DCS_ENTER_SLEEP_MODE    ; msleep(200)
reset (GPIO 90) -> 0               ; msleep(10)
VCI   (GPIO 39) -> 0               ; msleep(10)
DVDD  (GPIO 38) -> 0
ctx->error = 0 ; ctx->prepared = false ; msleep(10)
```

Rail order is strictly **reset → VCI → DVDD** on the way down and
**DVDD → VCI → reset** on the way up, which is the correct AMOLED ordering
(digital before analogue on, analogue before digital off).

## Shutdown / remove — `lcm_remove()`

`drm_panel_remove()` + `mtk_panel_detach()` + `mtk_panel_remove()`; no extra
DSI traffic and no rail changes, so a kernel `shutdown` leaves the panel in
whatever state the last `unprepare` left it.

## Bootloader-prepared state

`lcm_probe()` ends with `ctx->prepared = true; ctx->enabled = true;` and the log
`"vtdr6115,120hz dsi_node:%s set prepared = enabled = false"`. Consequences:

- the **first** `lcm_prepare()` after boot returns immediately — the panel is
  never re-initialised on the normal boot path, so LK's init stream stays live;
- the first real initialisation happens only after a suspend/resume cycle or
  after an ESD-triggered `unprepare`/`prepare` pair;
- recovery `prepare` is identical to a cold `prepare` (there is no separate
  recovery path in the driver).

## GPIO acquisition idiom (Ulefone-specific)

Each transition does `devm_gpiod_get()` → `gpiod_set_value()` →
`devm_gpiod_put()`. The descriptor is never held. MediaTek's own reference
panels request the descriptor once in `probe`. This idiom appears in every
power function of this driver and in `panel_ext_reset()`.
