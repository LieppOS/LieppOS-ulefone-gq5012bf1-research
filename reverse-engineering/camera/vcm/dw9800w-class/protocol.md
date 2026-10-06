# DW9800W-class actuator — protocol and power sequence (cameras 0, 2, 3)

Everything below is **binary-proven** from two stock artifacts unless marked
*(inferred)*:

* kernel: `main_vcm.ko` / `main2_vcm.ko` / `main4_vcm.ko` (exact rebuilds of ALPS
  `5e415e059253`, so the C source *is* the stock behaviour);
* HAL: `vendor/lib64/mt6878/libcameracustom.lens.so`
  (sha256 `8d5abd97f5d56d86e514ec09c1d1b1f89abdcac2b8aea5b857d45172cb2fbf1e`),
  tables decoded by [`../scripts/decode-vcm-list.py`](../scripts/decode-vcm-list.py)
  → [`../userspace/vcm-list-decoded.tsv`](../userspace/vcm-list-decoded.tsv).

The kernel driver is chip-agnostic: the HAL hands it a 208-byte
`VcmDriverConfig` and the driver replays it. The chip protocol is the table.

## Identity

* `lens_id = 0x9800` in every real entry (MTK lens-ID convention for the DW9800 family).
* Wire address 7-bit `0x0C`, single-byte register writes, two-register 10-bit DAC at `0x03/0x04`.
* Cross-check: ALPS's own chip driver `drivers/misc/mediatek/lens/vcm/v4l2/dw9800w/dw9800w.c`
  (blob `a52114a8`, kept in `../source/`) uses address `0x18`(8-bit), position
  `0x03` (16-bit big-endian word = `0x03`,`0x04`), release `0x02 = 0x20`, and
  init `{02=01, 02=00, delay, 02=02, 06=40, 07=60, delay}` — **identical** to
  the stock `vcm_list_0[5]` (sensor `0x8e1`) entry.
* No chip-ID/status register is ever read, so the die is identified as
  "DW9800W command-set compatible at 0x0C", not by an electronic ID read.
  (DW9800W/V and pin-compatible clones share this set *(inferred)*.)

## Sequence (per camera open)

| # | layer | action |
|---|---|---|
| 1 | imgsensor | sensor power-on sequence enables **AFVDD 2.8 V** (WL2864C custom LDO channel 5 or 6) together with the sensor rails |
| 2 | HAL `VCMDrv::Init` | `GetVcmDriverName(dev, sensor_id, module_id, &lens_id, name, &cfg)` → match in `vcm_list_0`; `I2CSettingForMovePos(0x9800, idx)` patches the move format in place first |
| 3 | HAL | enumerate `/dev/media*`, find entity whose driver name is `main_vcm`/`main2_vcm`/`main4_vcm`, open `/dev/v4l-subdevN` |
| 4 | kernel `open` | `power_on`: enable dummy `vin`/`vdd` regulators (no-op), no pinctrl state → electrically nothing |
| 5 | HAL ioctl `VIDIOC_MTK_S_LENS_INFO` (`_IOWR('V', BASE_VIDIOC_PRIVATE+3, …)`) | kernel copies 208 bytes into the module-global `g_vcmconfig`, `usleep_range(ctrl_delay_us = 10 000)`, then `init`: `client->addr = 0x18 >> 1`; replay `wr_table` (each entry followed by `udelay(100)`) |
| 6 | init table | `W 02=02; W 06=40; W 07=79` (sensors 0x989/0x988/0x38e2/0x566442) — or `W 02=01; W 02=00; mdelay 3; W 02=02; W 06=40; W 07=60; mdelay 2` (0x8e1) |
| 7 | AF operation | `VIDIOC_S_CTRL V4L2_CID_FOCUS_ABSOLUTE pos` (0..1023) → two `i2c_master_send`: `[03, pos>>8]`, `[04, pos&0xff]` (3 attempts shared by both messages, see quirks) |
| 8 | kernel `close` | `release`: step from the last control value toward `origin = 512` in `move_steps = 100` increments, `usleep 5000–6000 µs` each, final write of 512, then replay `wr_rls_table`: `W 02=20` |
| 9 | kernel `close` | `power_off`: disable dummy regulators (no-op), no pinctrl |
| 10 | imgsensor | sensor power-off removes AFVDD |

**Park behaviour:** the lens is walked back to mid-scale 512 (not to 0) before
the release command, at ≤100 DAC per 5 ms.

**Suspend / resume / shutdown:** none in the driver (no `dev_pm_ops`, no
`.shutdown`); AF power follows the sensor power state.

## Error handling

* Position update: one `retry = 3` budget for **both** messages (declared once
  outside the message loop); when exhausted the error is returned (logged
  `puSendCmd I2C failure`). If message 1 succeeds first try, message 2 has 2 attempts left; release stops at the first failure and skips the release table.
* Init-table writes: failures are logged and **ignored**.
* Poll (`cmd 2`) gives up after 11 reads; unused here.

## Stock quirks preserved (not bugs to fix before parity)

* `g_vcmconfig` is a module-global, not per-device (one device per module here, so harmless).
* `release` uses `focus->val` (last control value) as the start point, not hardware state.
* The shared `retry` budget above.
* `power_on`'s `ret` from the regulator loop is overwritten by the pinctrl result.
