# Hynitron rear touch: `hynitron.ko`

**Status: PARTIAL (reclassified from DONE on 2026-10-04).** Hardware, protocol,
ABI and display coupling are closed. The existing source reconstruction is
semantic rather than shipped-binary equivalent, with large unexplained
function gaps.

## Proven facts (unchanged; see `kernel/phase4-hynitron-*.md`)

- **Chip:** Hynitron **CST820**, chip type `0xb7`, CST8xx self-cap line. The
  stock config writes `0xb7`, and the table maps `0xb7` to the CST8xx family at
  0x15.
- **Bus:** I2C0 `i2c@11c20000`, 400 kHz, 7-bit 0x15. IRQ GPIO 11 (EINT 11,
  falling edge), reset GPIO 32, VDD enable GPIO 119.
- **Input:** `hyn_ts`, MT protocol A (`SYN_MT_REPORT`, no slots), 1 contact,
  X/Y 0..340, TOUCH_MAJOR 0..255, WIDTH_MAJOR 0..200, `BTN_TOUCH`. No
  swap/invert/rotation.
- **Report packet:** a register-0 read returns 9 bytes:
  - count = `p[1] & 0x0f`, clamped to 1
  - event = `p[2] >> 6`
  - X = `(p[2] & 0x0f) << 8 | p[3]`
  - id = `p[4] >> 4`
  - Y = `(p[4] & 0x0f) << 8 | p[5]`
  - area = `p[7] >> 4`
- **Gesture:** arm via `0xEC=1` (retried up to 3 times with readback).
  Gesture data is 12 bytes from `0xD3`; the IDs map to DOWN/RIGHT/LEFT/UP/
  O/W/M/E/C/S/V/Z/POWER keys. The IRQ type switches to
  `FALLING|NO_SUSPEND` while gesture mode is armed.
- **Identity:** running info comes from `0xA6` (project, module, fw version,
  checksum). The fallback ROM handshake is `0xA001=0xAA`, then poll
  `0xA003==0x55`.
- **Firmware:** two embedded images. `cst8xx_fw` is 15419 B, SHA-256
  `0566ea77…e1d8` (CST816D/CST820). `cst816t_fw` is 15410 B, SHA-256
  `0d02fde6…4de3`. Selection happens only on the sysfs/debug update path, and
  no reachable erase/program/verify sequence exists in the stock ELF.
- **Coupling:** exports `tiny_tp_power_contorl` and `tiny_tp_gesture_contorl`
  to the display module, which owns all touch power/wake sequencing. See
  `../integration.md`.

## Why this is not DONE

A = shipped `hynitron.ko` (SHA-256 `860f2840…51fb6`, "Hynitron TouchScreen
Qualcomm Driver V2.1 20201222"). B = `lieppos/hynitron-recon` rebuilt
(identical CI-12901745 toolchain, `LTO=none`). Full tables are in `parity/`.

| axis | A vs B |
|---|---|
| function set | 65/65 names shared |
| function bytes | **9/65 size-equal, 8/65 byte-identical** |
| KCFI | 63/65 equal (2 local direct-only functions have no preamble) |
| imports / exports | 54/54 name+CRC equal / 2/2 equal |
| `.text` | **22044 vs 8364 bytes** |
| `.rodata.str1.1` | **10134 vs 750 bytes** (almost all log strings absent) |
| data objects | 40 vs 45; 32 section+size equal |

Many B functions are stubs or heavy simplifications of stock code paths:

| function | A | B |
|---|---:|---:|
| `cst3xx_touch_report` | 1388 | 28 |
| `cst3xx_firmware_info` | 784 | 28 |
| `hyn_detect_bootloader` | 1952 | 236 |
| `hyn_boot_update_fw` | 1492 | 188 |
| `hyn_platform_data_init` | 1240 | 372 |
| `hyn_probe` | 1860 | 576 |

The earlier DONE row rested on semantic contracts for the fitted CST820 path and
on ABI/KCFI exactness. Under the current DONE criteria ("parity exact or every
residual fully explained"), 57 differing functions and a 62% `.text` shortfall
are not explained residuals.

## Path to DONE (bounded, evidence-based)

- **Donor family identified.** The public vendor trees (LineageOS AYN qcs8550
  `qcom/opensource/touch-drivers/hynitron` and scpcom/linux 39971b8
  "Spreadtrum Driver V3.1 20230829") contain **228/258** stock strings once the
  `[HYN][Info|Error]` prefixes are normalized. Stock is the older "V2.1
  20201222" of the same multi-file driver (core/i2c/gesture/update_firmware).
- **Logging.** Stock uses `HYN_INFO`/`HYN_ERROR` (all `KERN_ERR` + `[HYN]`)
  without `__LINE__`. Only `HYN_FUNC_EXIT` passes `__LINE__` (e.g. `0x6bc` in
  `hyn_suspend`, `0xe2` in `hyn_release_all_finger`), so the `#line` technique
  proven on CO5300 applies to a small set of sites.
- **Method.** Start from the donor files, back-port to the stock V2.1 behavior
  function by function (`scripts/symdis.py` diff loop), and reproduce stock
  inlining by matching the file split. The proven CO5300 workflow applies
  unchanged.

## Firmware note

The research repo already holds the two extracted controller images under
`workspace/phase4-hynitron/firmware/` (committed by an earlier phase). They are
proprietary Hynitron images. Keep them private and never copy them into
publishable `source/` trees.
