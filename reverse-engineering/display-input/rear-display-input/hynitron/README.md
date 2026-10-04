# Hynitron rear touch: `hynitron.ko`

**Status: DONE (static, 2026-10-04).** This status was reclassified DONE →
PARTIAL earlier the same day, then closed by exact reconstruction (see
`phase4-hynitron-v21-RED.md`).

A = shipped `hynitron.ko` (SHA-256 `860f2840…51fb6`, "Hynitron TouchScreen
Qualcomm Driver V2.1 20201222"). B = `source/` built with the CI-12901745
toolchain (`LTO=none`, `-faddrsig`) and debug-stripped.

| axis | result |
|---|---|
| functions | **65/65 byte-identical** (size, KCFI, relocations equal) |
| data objects | 40/40 bytes (firmware arrays hash-equal; payload private) |
| strings | 258/258 at identical offsets |
| imports / exports | 54/54 CRC, order equal / 2/2 CRC |
| modinfo / vermagic / depends | equal |
| sections | 41/42 byte-equal; only `.note.gnu.build-id` (hashes pre-strip DWARF paths) |
| clean rebuild | B1 == B2 file-identical |

Old rebuild for provenance: 8/65 byte-identical, 9/65 size-identical, `.text`
8364 vs 22044 B (`parity/before-2026-10-04-semantic-recon/`).

## Facts

- **Chip:** Hynitron CST820 (type 0xB7), CST8xx self-cap (SEL_CAP) series.
- **Bus:** I2C0 `i2c@11c20000`, 400 kHz, 0x15. IRQ GPIO 11, falling+ONESHOT,
  wake-capable. Reset GPIO 32. VDD enable GPIO 119 (set high once at probe).
- **Input:** `hyn_ts`, MT protocol A, 1 contact, X/Y 0..340, `BTN_TOUCH`. The
  report is 9 B from register 0x00 (layout in `register-map.tsv`).
- **Gesture:** arm 0xEC=1, then 0xE5=1 (each with readback ×3); IRQ becomes
  FALLING|NO_SUSPEND. Data is 8 B from 0x01 with the ID in byte 0. Stock defect:
  gesture coordinates are always 0. Correction of the earlier note: this is
  **not** 12 B from 0xD3 (`HYN_GESTURE_CAP_CST8XX=0`).
- **ROM handshake (CST8XX):** 0xA001=**0xAB**, poll 0xA003==**0xC1**, reset
  width 6..15 ms. This corrects the earlier `0xAA`/`0x55` note, which is the
  CST3xxSE handshake and unreachable here.
- **Firmware:** `cst8xx_fw` 15419 B (`0566ea77…1e1d8`) and `cst816t_fw` 15410
  B (`0d02fde6…04de3`). They are dead payload: selectable via sysfs, but
  programming is compiled out.
- **Coupling:** exports `tiny_tp_power_contorl` (`0xfcc94fc7`) and
  `tiny_tp_gesture_contorl` (`0x4e4b7919`). CO5300 owns all sequencing (see
  `../integration.md`).

## Files

| file | content |
|---|---|
| `source/` | exact reconstructed source (firmware regenerated privately via `extract-firmware.py`) |
| `lineage.md` | historical source search and donor lineage |
| `phase4-hynitron-v21-RED.md` | false DONE → RED → reconstruction → exact |
| `stock-string-provenance.tsv` | all 258 strings: offset, refs, donor A/B presence, rebuild, file, class |
| `stock-function-inventory.tsv` | all 65 functions: addr, size, section, KCFI, callers/callees, imports, strings, data, source file |
| `non-exact-function-classification.tsv` | 57 old non-exact functions, A/B/E classification |
| `build-config.md` | every proven define/flag |
| `struct-layouts.md` | context, platform, table, gesture structs |
| `register-map.tsv` | I2C protocol map (reachable and dead branches) |
| `power-reset-gesture-firmware.md` | probe/suspend/resume/gesture/unwind sequences, firmware boundary, feature blocks |
| `parity/` | function/data/ABI/relocation/string/section parity |
| `scripts/` | `hyn_index.py`, `generate-reports.py` |

Safety: offline static only. Nothing was loaded and no I2C, GPIO or firmware
operation was performed.
