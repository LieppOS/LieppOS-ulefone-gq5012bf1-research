# RT5133 — STATUS: DONE (static)

| item | result |
|---|---|
| silicon identity | DT `richtek,rt5133`; driver accepts CHIP_INFO[7:4] = 0x7 (RT5133) or 0x8 (RT5133A); reference DT targets RT5133A (LDO8 min 0.855 V). **On GQ5012BF1 no die answers** at 5-0018 |
| bus / address | I2C5 (`/soc/i2c@11280000`), 7-bit `0x18`, CRC-8 (poly 0x07) framed SMBus block transfers, 1 byte per transfer |
| IRQ / GPIO | EINT19 falling (never requested); HWEN = GPIO1 (driven high once by the failed probe; owned afterwards by WL2864C `reset-gpios`) |
| regulator role | **none** — 0/9 regulators and 0/3 GPOs registered |
| consumers | 0 in DT, 0 by name in stock modules |
| source lineage | ALPS `5e415e059253`, DIRECT_SOURCE_MATCH (driver + `extdev_io_class`) |
| function parity | rt5133-regulator 13/13, extdev_io_class 10/10 byte-identical; KCFI 23/23 |
| data parity | 34/34 and 19/19 byte-equal |
| ABI | imports 39/39 + 39/39 (name, CRC and order); exports 0 and 4/4 (CRC); modinfo 11/11 + 6/6 incl. srcversion |
| residuals | `.note.gnu.build-id` only (20 bytes per module); rebuild deterministic (B1 == B2) |
| firmware / calibration | none (see README §Firmware) |
| audio | **RT5133 IS NOT PART OF THE ACTIVE AUDIO SIGNAL PATH** |

Not required for static DONE and not attempted: physical BOM inspection of the
footprint, any register access.
