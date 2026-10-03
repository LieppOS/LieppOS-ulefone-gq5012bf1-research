# Sensors RE status

Scope: MT6878 SCP host + MediaTek sensor 2.0 (sensorhub) Linux stack + sensors
multi-HAL on GQ5012BF1.

## Phase audit

| component | prior state | gap at start | donor | offline-solvable | result |
|---|---|---|---|---|---|
| `hf_manager` (sensor 2.0 core) | undocumented | source/parity, ODM hooks | NothingOSS `device_modules` 957dac1 | yes | **DONE** — 41/41 funcs, 33/33 data byte-exact |
| `sensorhub` (SCP transceiver) | undocumented | source/parity, display coupling, translate table | same | yes | **DONE** — 102/102 funcs, 82/82 data byte-exact |
| `scp` (tinysys remoteproc host) | referenced by audio scope, never source-closed | source/parity, DVFS/awake deltas | same | yes | **DONE** — 196/196 funcs, 178/178 data byte-exact |
| physical sensor drivers | unknown | which parts, where they run | none | identification only | **mapped**: all run on SCP firmware, no Linux driver exists |
| SCP sensor firmware | undocumented | algorithms, fusion, batching | none | no | **PARTIAL boundary** — signed `scp` partition, proprietary |
| sensors multi-HAL / subhal | undocumented | service, version, config chain | no public exact source | interface mapping only | **mapped** (`userspace/hal-map.md`) |
| YFT `sensorcali` HAL + `yft_devinfo` | undocumented | role and kernel coupling | none | interface + kernel ABI yes | **mapped**; HAL body proprietary |
| sensor calibration data | undocumented | per-device values | n/a | no | out of scope — `/data/vendor/sensor`, device-unique |

## Exact kernel closure

[`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) is authoritative.
Per-module reports in [`kernel/parity/`](kernel/parity).

Aggregate: **339/339 functions and 293/293 data objects byte-identical** across
`hf_manager`, `sensorhub` and `scp`. Imports match by modversion CRC
(68 + 87 + 138 = 293/293), exports match by name and licence, `.modinfo`
(`vermagic`, `depends`, `license`) is identical, and all non-debug content
sections are byte-equal.

Residual differences, all explained and benign:

- the rebuild carries DWARF (`.debug_*`, `.rela.debug_*`); the shipped modules
  are stripped;
- `.symtab` / `.strtab` / `.shstrtab` differ in size for the same reason;
- consequently every `.rela*` section differs in raw bytes while the relocation
  **target multiset is identical** (`target-count diff={}` in the reports) —
  the deltas are symbol-index renumbering, not different relocations.

Build: exact GKI `6.1.115-android14-11-g945dff7bc1bf`;
`kernel_device_modules-6.1` commit `7d3c303` on the pristine NothingOSS
`device_modules` `957dac1` import (`0579490`). Verification tool:
[`../scripts/ko-pair-parity.py`](../scripts/ko-pair-parity.py).

Board configuration recovered from stock:

- SCP `awake-timeout` is DT-driven (`0x7530` = 30000), not the MTK `100000`
  literal; the reboot wait uses its own `SCP_WFI_WAIT_TIMEOUT 100000`;
- `sensorhub` is display-notifier coupled (`depends=mtk_disp_notify`), but the
  screen-on/off handlers are shipped as log-only stubs;
- `hf_manager` is ODM coupled (`depends=yft_devinfo`);
- Nothing-specific `SENSOR_TYPE_POCKET_MODE`, per-event tracing and the
  charger-status→magnetometer feedback path are absent from the Ulefone build.

Details: [`notes/yft-deltas.md`](notes/yft-deltas.md).

## Boundaries

### Reconstructable (done)

- SCP host driver, IPI/mailbox plumbing, DVFS request path, logger, recovery
  and CHRE manager (`scp.ko`).
- Sensor 2.0 core, client ring buffers and `/dev/hf_manager` ABI
  (`hf_manager.ko`).
- SCP transceiver: share memory rings, timesync, sensor list, ready handshake,
  event translation (`sensorhub.ko`).
- Device-tree contract for `scp@1c400000` (mailboxes, feature table, memory
  table, reserved share memory).

### Proprietary, mapped but not source-closed

- SCP sensor firmware (`scp` partition): physical sensor drivers, the fusion
  engine behind the 16 virtual sensors, batching and low-power triggers.
- `sensors.mediatek.V2.0.so` and `android.hardware.sensors@2.X-subhal-mediatek.so`.
- `vendor.yft.hardware.sensorcali@2.0-service-lazy` and `yft_devinfo.ko`
  internals (ABI is known: the ten `yft_*sensor_device_add` /
  `yft_set_*sensor_device_used` entry points).

### Physical/runtime only

- Board placement and orientation matrices of the IMU/mag/ALS-PS/baro parts.
- SCP-side I²C bus assignment and slave addresses (not expressed in the Linux
  device tree — only the SCP firmware knows them).
- Per-device calibration values under `/data/vendor/sensor`.
- Live confirmation that the display-blank notifier has no behavioural effect
  (statically it cannot: both handlers are stubs).

## Scope state

**DONE** for the Linux sensor stack. The parent "sensors" feature scope remains
**PARTIAL** only because the sensing algorithms execute in proprietary SCP
firmware that no public source reproduces.

## Workspace classification (2026-10-03)

Recorded in the organized workspace (`../../../Reverse Engineer - *`, indexed by
`REVERSE-ENGINEERING-STATUS.md`):

- **new:** `DONE/SENSOR-HUB-KERNEL` — this scope (source, patch, parity reports,
  notes). DONE count 43 → 44, total 128 → 129.
- **stays PARTIAL:** `SENSOR-HUB` — re-scoped to the SCP firmware and
  calibration data only; its README now records the split and the two questions
  this closure answered (no AP-direct sensor channel exists; the cross-socket
  timestamp gap lives in `sensorhub`'s `timesync.c`).
- **stays PARTIAL:** `ICM4N607-IMU`, `MMC5603-MAGNETOMETER`, `STK3A5X-ALS-PS`,
  `SPL07-BAROMETER` — no Linux driver exists for any of them to reconstruct;
  their register-level drivers run inside the SCP image.
- **unchanged:** `YFT-DEVINFO` (ten export prototypes still unresolved) and
  `MTK-TINYSYS-IPI` / `MTK-MBOX` / `MTK-DISP-NOTIFY`, which were not parity-
  checked in this pass.
