# Phase 4 — VTDR6115 hardware/display contract

## Physical / DSI link

- Main panel DDIC: Viewtrix VTDR6115-family AMOLED, 1080×2400 active pixels; physical size 69×155 mm.
- MIPI DSI: four lanes, RGB888, 870 Mbit/s per lane, 435 MHz PLL.
- `mode_flags = 0x0e05`: `MIPI_DSI_MODE_VIDEO`, `VIDEO_SYNC_PULSE`, `MODE_LPM`, `CLOCK_NON_CONTINUOUS`, and `NO_EOT_PACKET`.
- Therefore `cmd` in the filename/compatible is a vendor naming artifact. This driver operates the link in video mode; stock `MODULE_DESCRIPTION` correctly says `VDO`.
- `mode_switch()` sends no command. Refresh selection is VFP-based and panel-ext supplies the matching `0x6c` DFPS command.

## Modes

| Mode | Pixel clock (kHz) | H active/fp/sync/bp/total | V active/fp/sync/bp/total | Preferred |
|---|---:|---|---|---|
| 60 Hz | 357732 | 1080/100/8/16/1204 | 2400/2528/4/20/4952 | no |
| 90 Hz | 358671 | 1080/100/8/16/1204 | 2400/886/4/20/3310 | no |
| 120 Hz | 358888 | 1080/100/8/16/1204 | 2400/60/4/20/2484 | yes |

Each clock equals `htotal × vtotal × refresh / 1000`. Stock DT parent property `switch-fps = <120>` agrees with preferred 120 Hz.

## DSC 1.1 contract

DSC is enabled, single-port, 8 bits/component, 8 bpp (`bit_per_pixel = 128` in 1/16 units), picture 1080×2400, two 540×12 slices per line, chunk size 540. Key encoder values: line buffer depth 9, xmit/dec delay 512/526, initial scale 32, scale increment/decrement 287/7, line/NFL/slice BPG 12/2235/2170, initial/final offset 6144/4336, flatness QP 3..12, RC model 8192, edge factor 6, quant limits 11/11 and target offsets 3/3.

The exact 95-byte DSI `0x70` PPS appears in `phase4-panel-vtdr6115-command-table.tsv`. Its bytes and all external RC tables are recovered from the stock ELF. The four RC arrays are `{14,15,15,15}` elements and byte-identical in the reconstruction.

## DSI command contract

Runtime init is exactly **45 writes / 287 bytes**: 44 stock `.rodata` payloads plus one stack-built `0x51` brightness write. The only refresh-dependent payload is:

- 60 Hz: `6c 00`
- 90 Hz: `6c 01`
- 120 Hz: `6c 02`

At initial probe brightness 0x07ff, concatenated stream SHA-256 is:

- 60: `6dc2e822e771fb7c97b0ba80b0050e0d6e3667aa51504469d2bb77db6c2c6d16`
- 90: `e3bab654eb1c05926f17672006e672fa1b176720b0821542a3ffdaf2c2a4adf`
- 120: `ba20b2e6800fe143d9bb5cdeffda4e677055afc63048d3675d11f66698eb4e4c`

All 46 static `lcm_panel_init` command objects (including all three branch alternatives) match stock byte-for-byte. Opcode `<= 0xaf` uses `mipi_dsi_dcs_write_buffer`; higher opcodes use generic write. Stock retries a failed write once and latches the second error.

## Power/reset lifecycle

Prepare sequence: DVDD high → 10 ms → VCI high → reset low/high/low/high with 15/15/15/20 ms delays → command init. GPIOs are requested and released around each operation; regulators are not used.

Suspend/unprepare: `0x28` → 20 ms → `0x10` → 200 ms → reset low → 10 ms → VCI low → 10 ms → DVDD low → 10 ms. `powerdm-gpios` is not used.

## Backlight and HBM

- Brightness: DCS `0x51 HH LL`, 12-bit; callback clamps levels 0..21 to 22 and remembers the sent value.
- Panel-ext HBM callback: enabled `51 0f ff`; disabled `51 03 ff`.
- Fingerprint/sysfs path: class `/sys/class/primary_lcm`, attribute `set_hbm_backlight` mode 0664, using imported `ddic_dsi_send_cmd_for_fp`; input 1 sends max, input 0 restores remembered brightness, other values send `51 00 ff`.
- No AOD/doze, CABC, or local-HBM command implementation was found.
- ATA/ID callback is a stub returning 1; no ID register/readback validation exists.
