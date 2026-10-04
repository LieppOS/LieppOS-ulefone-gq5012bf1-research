# FT3680 hardware topology and sequencing

## Topology

```text
MT6878 SPI3 @ 0x11013000, CS0, mode 0, 6 MHz
  └─ FocalTech FT3680 family controller
       ├─ IRQ: GPIO/EINT 7, falling-edge threaded IRQ
       ├─ reset: GPIO 6
       ├─ VDD: mt6369_vtp, fixed 3.3 V
       ├─ VDDI switch: GPIO 183
       ├─ input: fts_ts, MT protocol B, 10 slots, 1080×2400
       ├─ display state: mtk_disp_notify (label Touch_fts)
       ├─ gesture policy: yft_tpd_gesture
       └─ identity/version publication and SPI registration: yft_devinfo
```

The driver banner is `FocalTech V4.2 20240407`. The recovered chip mapping is:

```c
{ 0x8A, 0x56, 0x62, 0x56, 0x62, 0x56, 0xE2, 0x00, 0x00 }
```

`0x8A` is the FT3680 family/type selector; normal/ROM/PRAM/boot IDs are the remaining tuple. The selected upgrade-setting record is the stock 18-record table entry matching the runtime ROM ID. This proves the shipped family/revision contract; no physical package or panel-bonding detail is inferred from generic FocalTech documentation.

## Probe and power-on sequence

1. SPI core sets mode 0 and 8 bits/word.
2. Parse GPIO 6, GPIO 7, GPIO 183, 1080×2400 and ten touches.
3. Request IRQ/reset GPIOs, obtain `vdd`, attempt optional `iovcc`, and request GPIO 183 as `fts_vddi_gpio`.
4. Drive reset low; wait about 1 ms through `fts_msleep(1)`.
5. Enable the 3.3 V VDD regulator; optional IOVCC is skipped on this DT.
6. Drive VDDI GPIO 183 high.
7. Wait 200 ms.
8. Up to five identification attempts: reset low, 2–4 ms, reset high, then delay `FTS_CMD_START_DELAY + 4*retry` before boot-ID read.
9. Match the recovered FT3680 ID tuple; initialise input, IRQ, gesture, FHP, firmware-debug, ESD and upgrade interfaces.

On final teardown, reset is driven low, VDD/optional IOVCC are disabled, VDDI is driven low, and regulator references/GPIOs are released.

## Display notifier sequence

The MediaTek display notifier callback handles:

- `MTK_DISP_EARLY_EVENT_BLANK` + powerdown: cancel pending resume work, then suspend synchronously.
- `MTK_DISP_EVENT_BLANK` + unblank: queue `resume_work` on `fts_wq`.

The stock `struct fts_ts_data` layout places `resume_work` at offset `0x60` and `disp_notifier` at `0x4f0`; the complete stock-visible structure ends at `0x508`.

## Suspend

Suspend is refused while firmware loading or when already suspended. Otherwise:

1. Read `tpgesture_status`, store it as the active `gesture_support` flag, and clear `tpgesture_value[10]`.
2. Suspend ESD checking.
3. If gesture wake is enabled:
   - write `0xFF` to gesture masks D1, D2 and D5–D8;
   - retry D0=`1` and verify D0;
   - leave the IRQ active and call `enable_irq_wake()`;
   - keep controller power available.
4. If gesture wake is disabled:
   - disable the IRQ;
   - write sleep mode to register A5.
5. Release all reported contacts and mark suspended.

Normal display suspend does not cut the 3.3 V/VDDI rails; regulator/GPIO power-off is a driver teardown path.

## Resume

Resume is refused while firmware loading, when already awake, or while `yft_aod_state` is asserted. Otherwise:

1. Clear suspended state and release stale contacts.
2. Reset non-incell hardware as required and enter normal firmware.
3. If gesture mode was active, retry D0=`0` and verify it.
4. Restore glove/cover/charger/earphone/edge-palm state and resume ESD checking.
5. Re-enable the IRQ for normal suspend, or remove IRQ-wake for gesture suspend.
6. Clear `tpgesture_value`.

The global `yft_fts_ts_aod_contorl()` and `aod_state` sysfs control provide the Ulefone AOD override.

## Gesture reporting

The IRQ path verifies D0 before consuming gesture data. Data comes either from the appended touch packet when gesture buffer mode is active and valid, or from register D3. Six coordinate pairs are decoded. Recognised names are published through `tpgesture_value`/`tpgesture_hander()`; the input device reports the corresponding key pulse.
