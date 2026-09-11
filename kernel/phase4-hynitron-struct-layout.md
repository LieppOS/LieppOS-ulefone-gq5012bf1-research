# Hynitron private state layout

Stock probe allocates **584 bytes** (`0x248`) for `struct hynitron_ts_data`.
Only relocation/disassembly-proven fields are named; all gaps are UNKNOWN.

| offset | size | field/evidence |
|---:|---:|---|
| 0x000 | 8 | `i2c_client *`; all I2C helpers |
| 0x008 | 8 | device/client-adjacent pointer saved by sysfs setup |
| 0x010 | 8 | platform-data pointer |
| 0x018 | 8 | `input_dev *`; report/gesture paths |
| 0x020.. | unknown | embedded work/workqueue and IRQ synchronization state |
| 0x0a8..0x0ac | bytes/word | IRQ number/use/disabled state, proven by IRQ helpers |
| 0x158 | mutex-sized | sysfs mutex initialized by `__mutex_init` |
| 0x188 | 2 | running project ID (`A6` byte 1) |
| 0x198 | 2 | running firmware version (`A6` byte 3; initialized ffff) |
| 0x19c | 2 | module ID (`A6` byte 2) |
| 0x19e | 2 | checksum (`A6` byte 4; initialized ffff) |
| 0x1a0 | 2 | auxiliary chip/check field, initialized zero |
| 0x1a6 | 2 | configured chip type `0x00b7` (CST820) |
| 0x1a8 | 4 | packed configured series/product data (`0x00000320`) |
| 0x1b0.. | pointers/length | selected firmware name/data/length |
| 0x1d0 | 8 | `/sys/hynitron_debug` kobject |
| remaining | unknown | GPIO/platform mirrors and bookkeeping proven only by accesses |

Global objects: `hyn_ts_data` pointer (8 bytes),
`tiny_tpgesture_status` (4 bytes), and `hyn_gesture_data` (1034 bytes). The
gesture object contains mode/active/ID/count, coordinate arrays and cached
report key. Exact object sizes/sections are frozen in
`phase4-hynitron-objects.tsv`.

The reconstruction uses a semantic structure rather than claiming binary
layout compatibility: no external consumer accesses this private allocation.
Unknown stock gaps remain intentionally unnamed.
