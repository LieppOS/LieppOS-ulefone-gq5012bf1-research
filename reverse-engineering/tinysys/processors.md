# TinySys processors on GQ5012BF1: platform capability vs board/build enablement

`enum mtk_ipi_dev` in `mtk_tinysys_ipi.h` (KDM `5e415e059253`) lists the processors the framework can serve:

`SCP, SAP, SSPM, ADSP, MCUPM, CPUEB, APUSYS, GPUEB, VCP`.

That enum is **platform capability**. It is not even read by the framework (`mtk_ipi_device.id` is never used). What matters on this board is:

1. which owner module ships and loads,
2. whether its DT node exists and is enabled,
3. whether it calls `mtk_ipi_device_register()` against `mtk_tinysys_ipi`.

| processor | owner module (stock) | loaded | DT node (live capture) | transport used | registers with `mtk_tinysys_ipi`? | verdict |
|---|---|---|---|---|---|---|
| **SCP** (sensor/audio/CHRE co-processor, 2 harts) | `scp.ko` (exact rebuild in `sensors/`) | `vendor_dlkm` `modules.load` l.89 | `/scp@1c400000` `status="okay"`, `mbox-count=4`, `core-nums=2`, `twohart=1` | TinySys IPI over `mtk-mbox` (direct mode) | yes: `scp_device_probe` → `mtk_ipi_device_register(&scp_ipidev, pdev, &scp_mboxdev, 50)` | **ENABLED**: 36 channel ids configured |
| **SAP** (sensor-assist processor, under `scp.ko`) | `scp.ko` `sap_device_probe` | (part of scp) | **no SAP node** (only unrelated `sapu*` APU nodes) | — | no (probe never runs) | **CAPABILITY ONLY**: `sensorhub` `sap_custom_cmd_*` gets `IPI_DEV_ILLEGAL` |
| **VCP** (video/MM co-processor) | `vcp.ko`, `vcp_status.ko` | `modules.load` l.77; `vcp_status` vendor_boot l.166 | `/soc/vcp@1ea00000` `status="okay"`, `mbox-count=5` | TinySys IPI over `mtk-mbox` | yes: `vcp_device_probe` → `(&vcp_ipidev, …, 30)`; `vcp_status` re-exports it as `vcp_get_ipidev` | **ENABLED**: 28 ids |
| **GPUEB** (GPU embedded controller) | `gpueb.ko` | `modules.load` l.37 | `/soc/gpueb@13c00000` (no status = okay), `mbox-count=1`, `mbox-size=160`, `ts-mbox=0` | TinySys IPI over `mtk-mbox` (SMEM) | yes: `gpueb_ipi_init` → `(&gpueb_ipidev, …, send_count=11)` | **ENABLED**: 11 ids |
| **MCUPM** (CPU power-management MCU) | `mcupm.ko` | `modules.load` l.92 | `/mcupm@c540000` (no status), 8 `mboxN` interrupts, no `mbox-extend` | TinySys IPI over `mtk-mbox` (one mailbox per channel) | yes: `mcupm_device_probe` → `(&mcupm_ipidev, …, 8)` | **ENABLED**: 8 ids; static rows 8–15 inactive |
| **SSPM** (system power MCU) | `sspm_v3.ko` | `modules.load` l.26 (`mtk-mbox-mailbox`, `tinysys-scmi`: vendor_boot l.155/156) | `/sspm@1c300000`, `/firmware/scmi` (`arm,scmi`, `protocol@80`), `tiny-mbox@0/@1` (`mediatek,tinysys_mbox`) | **SCMI** over `mtk-mbox-mailbox.ko` + `tinysys-scmi.ko` | **no**: `sspm_v3` imports only `tinysys-scmi` | ENABLED, **but not on this transport** |
| **ADSP** (audio DSP) | `adsp.ko` | vendor_boot `modules.load` l.162 | **no ADSP node** (only the `adsp_shared_reserved` memory region) | own IPI over `mtk-mbox` (queue mode, `mtk_mbox_write_hd`) | **no**: `adsp` imports `mtk_mbox_*` only | **CAPABILITY ONLY** (no DT node → no probe) |
| SCP audio mailbox | `mtk-scp-audiocommon.ko` | `modules.load` l.48 | `/scp-audio-mbox@1cbe0000` `okay` | own queue-mode messages over `mtk-mbox` (1 send/1 recv pin) | no | ENABLED, not TinySys IPI |
| **CCU** (camera control unit) | `mtk_ccuv.ko` | `modules.load` l.84 | `ccu_rproc@1b080000`, `ccu_rproc1@1b180000` | CCU rproc path | no (no TinySys import) | not on this transport |
| **APUSYS** | `apusys.ko` | `modules.load` l.180 | `apusys-rv@190e1000` + `*-rpmsg` children | GKI rpmsg via APU's own rpmsg | no (does not use `mtk_rpmsg_mbox`) | not on this transport |
| **CPUEB** | — (no module) | — | — | — | — | **ABSENT** |

The "loaded" column cites line numbers in the stock `vendor_dlkm/lib/modules/modules.load` and the vendor_boot platform `modules.load`. The DT facts come from `devicetree.tar` in the `live-stock-adb-20260831-115649` snapshot.

## What this means for later SCP/ADSP/CCU work

- Only **four** remote cores use `mtk_tinysys_ipi` on this phone: SCP, VCP, GPUEB and MCUPM. Their AP-side channel contracts (ids, sizes, ACK pairing, slot offsets) are fully specified in [`protocol/ipi-channel-map.tsv`](protocol/ipi-channel-map.tsv).
- **Payload semantics** inside each channel belong to the client driver (e.g. `sensorhub`'s `struct sensor_comm_*`, `ccci_fsm_scp`, `vow`) and to the proprietary firmware. They are out of scope for this transport.
- **ADSP** is not instantiated on this board. **CCU/APU/SSPM** use other transports, so this closure does not cover them.
