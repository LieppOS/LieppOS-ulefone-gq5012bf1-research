# Ulefone/YFT deltas in the sensor stack

Donor baseline: NothingOSS `device_modules` `957dac1` (pristine import,
`kernel_device_modules-6.1` commit `0579490`).
Reconstruction: commit `7d3c303`, exported as
[`../reconstruction/0001-sensors-reconstruct-GQ5012BF1-sensorhub-and-SCP-source.patch`](../reconstruction/0001-sensors-reconstruct-GQ5012BF1-sensorhub-and-SCP-source.patch).

Every delta below was derived from the shipped stock `.ko` (function bytes,
relocation targets, string/rodata contents, `depends`) and is confirmed by
byte-identical rebuild — not guessed.

## 1. `hf_manager` ↔ `yft_devinfo` hardware registry

`hf_manager_device_info()` registers the first-seen device of each class into
the Ulefone device-info driver and marks it "used":

```c
case SENSOR_TYPE_ACCELEROMETER:  yft_accsensor_device_add(info, 0);
                                 yft_set_accsensor_device_used(name, 1);
case SENSOR_TYPE_MAGNETIC_FIELD: yft_msensor_device_add / yft_set_msensor_device_used
case SENSOR_TYPE_LIGHT:          yft_alspssensor_device_add / ..._used
case SENSOR_TYPE_PRESSURE:       yft_barosensor_device_add / ..._used
case SENSOR_TYPE_SAR:            yft_sarsensor_device_add / ..._used
```

Each class caches the name in a static `char [16]` (`accelhub_used`,
`maghub_used`, `alspshub_used`, `barohub_used`, `sarhub_used`) so the
registration happens exactly once. This is why stock `hf_manager.ko` carries
`depends=yft_devinfo`, which upstream MTK/Nothing builds do not.

Consumer: `yft_devinfo.ko` (98 040 bytes, `vendor_dlkm`, load slot 194) — the
ODM "hardware info" node used by Ulefone's factory/engineering menus.

## 2. `hf_sensor_type.h` enum reshape

- `SENSOR_TYPE_POCKET_MODE` **removed** (Nothing-only sensor type).
- `SENSOR_TYPE_NT_SAR` kept.
- ID enum gains `ID_OIS1`, `ID_OIS2`, `ID_OIS_IMU` (multi-OIS camera module —
  matches the camera-stack scope: `dw9781c` OIS plus IMU feed),
  `ID_FINGERPRINT_DISPLAY` and `ID_AMBIENT_LIGHT`.

The enum shape is load-bearing: it fixes the numeric sensor ids used in the SCP
IPI protocol and in the sensor-type switch tables, and it is what makes the
rebuilt jump tables byte-match stock.

## 3. `sensorhub` transceiver: display coupling

Added (not present in donor):

```c
#include "mtk_disp_notify.h"
static int transceiver_fb_notifier_callback(...)   /* MTK_DISP_EVENT_BLANK */
    MTK_DISP_BLANK_UNBLANK   -> transceiver_restart_timer()
    MTK_DISP_BLANK_POWERDOWN -> transceiver_stop_timer()
static struct notifier_block transceiver_fb_notifier;
/* in transceiver_init(): */
ret = mtk_disp_notifier_register("mtk_transceiver", &transceiver_fb_notifier);
```

`transceiver_init()` now returns `ret` from the notifier registration instead of
a hard `0`. `transceiver_stop_timer()` / `transceiver_restart_timer()` are
externally visible but are **log-only stubs** in the shipped module (they print
`-IN` / `-OUT` and do nothing) — the screen-state hook is wired but inert, i.e.
the feature was stubbed before shipping. This is the origin of the
`depends=mtk_disp_notify` entry on stock `sensorhub.ko`.

## 4. `sensorhub` transceiver: removed Nothing features

- `transceiver_print_event()` (per-event `pr_info` tracing of prox,
  fingerprint-display, ambient-light, pocket-mode, SAR, device-orientation and
  wake-gesture events) — removed entirely.
- The charger-status→magnetometer feedback path — `power_supply` lookup of
  `"battery"`, `POWER_SUPPLY_PROP_STATUS` / `POWER_SUPPLY_PROP_CURRENT_NOW`,
  and the `SENS_COMM_CTRL_DEBUG_CMD` push to `SENSOR_TYPE_MAGNETIC_FIELD` —
  removed, along with the `#include <linux/power_supply.h>`.

## 5. `sensorhub` transceiver: translate table

`transceiver_translate()` groups differently from the donor:

- 3-word group: `ACCELEROMETER`, `MAGNETIC_FIELD`, `GYROSCOPE`,
  `AMBIENT_LIGHT`, `NT_SAR`.
- 1-word group: `LIGHT`, `PRESSURE`, `PROXIMITY`, `STEP_COUNTER`,
  `FINGERPRINT_DISPLAY` (the donor passed 6 words for light/pressure/proximity).

## 6. `__COUNTER__` alignment shim

The stock YFT `transceiver.o` was compiled inside a larger vendor include
context that advanced Clang's `__COUNTER__` by 194 before `module_init` /
`module_exit`. The reconstruction reproduces the resulting addressable-symbol
names (`__UNIQUE_ID_*`) with a pure-preprocessor padding enum that emits no code
and no data. Without it the rebuild is functionally identical but the symbol
names differ, which would break the byte-level proof.

## 7. `scp.ko` deltas

| change | detail |
|---|---|
| DT-driven awake timeout | new global `unsigned int scp_awake_timeout`, read from `awake-timeout` in `scp_device_probe()` (DT says `0x7530` = 30000), default `100000` if absent; `SCP_AWAKE_TIMEOUT` becomes that variable instead of a `100000` literal |
| separate reboot wait | new `SCP_WFI_WAIT_TIMEOUT 100000`; `wait_scp_ready_to_reboot()` uses it so shortening the awake budget does not shorten the reset wait |
| unconditional freq request | `scp_control_feature()` drops the `scp_current_freq != scp_expected_freq \|\| sap_expected_freq != last_sap_expected_freq` guard and always calls `scp_request_freq()` when DVFS is enabled |
| CHRE write validation | `scp_chre_manager_write()` rejects on `msg.magic != SCP_CHRE_MAGIC \|\| msg.size > PAYLOAD_MAXIMUM` (donor used `&&`, which let over-sized payloads with a valid magic through) |
