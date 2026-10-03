# SCP / sensorhub transport topology

Evidence: merged live device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`), stock
`vendor_dlkm` modules, reconstructed source at `kernel_device_modules-6.1`
commit `7d3c303`.

## SCP block (`scp@1c400000`, `compatible = "mediatek,scp"`)

| property | value | meaning |
|---|---|---|
| `scp-sram-size` | `0x100000` | 1 MiB tightly-coupled SRAM at `0x1c400000` |
| `core-nums` / `core-0` | `2` / `enable` | dual core, only core 0 brought up by DT |
| `twohart` | `1` | hart-pair SMT core |
| `mbox-count` | `4` (5 mailbox reg sets wired) | `mbox0..mbox4` at `0x1cba0000`–`0x1cbe0000` |
| `interrupt-names` | `ipc0, ipc1, mbox0..mbox4` | SPI 0x204–0x20a |
| `scp-mem-key` | `mediatek,reserve-memory-scp_share` | DRAM share region for sensor rings |
| `secure-dump` / `secure-dump-size` | enable / `0xe28000` | ~14.2 MiB secure coredump |
| `scp-dram-region`, `scp-protect` | enable | DRAM window + EMI protection |
| `scp-hwvoter`, `scp-pm-notify`, `scp-low-pwr-dbg`, `scp-mbrain` | enable | DVFS voter, PM notifier, low-power debug, mbrain telemetry |
| `scp-thermal-wq`, `scp-ipc-wa`, `scp-resource-dump` | disable | board configuration |
| `awake-timeout` | `0x7530` (30000) | **Ulefone delta**: SCP awake poll budget, see `yft-deltas.md` |
| `scp-bus-tracker-ver` | `2` | bus tracker v2 |

`send-table` / `recv-table` encode the IPI id → mailbox/slot-size mapping used
by `mtk_tinysys_ipi.ko`; `scp-feature-tbl` carries per-feature DVFS cost in
MHz-units (0x28, 0x1a, 0xc8, 0x87, 0x50, 0x2b, 0x16, 0x14, 0x64, 0xc8 …).
`scp-mem-tbl` partitions the share region per feature id (`0xca700` for id 1,
`0x100000` for id 2, `0x180000` for id 3 …).

A second mailbox block, `scp-audio-mbox@1cbe0000`, is owned by the audio scope
(ADSP/VOW/ultrasound) and overlaps `mbox4` — the SCP is shared between the
sensor and audio paths. See `reverse-engineering/audio/`.

## Linux module chain

`modules.load` order (stock):

```
 88 mtk_tinysys_ipi.ko
 89 scp.ko
...
138 hf_manager.ko
139 sensorhub.ko
...
194 yft_devinfo.ko
```

Declared `depends`:

| module | depends |
|---|---|
| `scp` | `mtk_tinysys_ipi, mtk-mbox, mtk-afe-external, aee_aed, clk-common` |
| `hf_manager` | `yft_devinfo` |
| `sensorhub` | `scp, mtk_tinysys_ipi, hf_manager, mtk_disp_notify` |

`hf_manager` is listed before its `yft_devinfo` dependency in `modules.load`;
load is dependency-resolved through `modules.dep` (modprobe), so the file order
is not the probe order. The `mtk_disp_notify` dependency of `sensorhub` is a
Ulefone addition — stock MTK/Nothing `sensorhub` has no display coupling.

## Data path

- `transceiver.c` registers one `hf_device` per SCP-reported sensor built from
  `sensor_list` fetched over `SENS_COMM_CTRL_*` IPI commands.
- Sample delivery is a share-memory ring (`share_memory.c`) read on IPI
  notification; `transceiver_translate()` converts `struct share_mem_data` into
  `struct hf_manager_event` and applies the SCP→AP timestamp remap from
  `timesync.c`.
- `hf_manager.c` fans events out to `hf_client` ring buffers; userspace reads
  them from `/dev/hf_manager`.
- Control (`enable`, `batch`, `flush`, `calibration`, `custom_cmd`,
  `rawdata`) travels the reverse direction as `sensor_comm` IPI messages.
- `ready.c` implements the SCP-ready / SCP-reset handshake: on SCP recovery the
  transceiver re-enables every previously active sensor.

## Firmware boundary

The physical sensor drivers, the fusion engine (orientation, gravity, rotation
vectors, step/tilt/significant-motion detectors), batching and the low-power
trigger logic all live in the SCP firmware image, which is stored in the
dedicated `scp` partition — it is **not** present in `vendor/firmware`
(`vendor/firmware/remoteproc_scp` is a 32-byte stub). That firmware is signed,
proprietary and out of scope for source reconstruction.
