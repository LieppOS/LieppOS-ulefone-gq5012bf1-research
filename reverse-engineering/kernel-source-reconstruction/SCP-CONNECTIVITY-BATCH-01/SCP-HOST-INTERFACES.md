# SCP host interfaces (MT6878 tinysys SCP, `scp.ko`)

Evidence labels used below:

- **PROVEN_RUNTIME**: saved read-only live capture (2026-08-31: dmesg, live DT, `dumpsys`).
- **ENABLED_IN_STOCK_DT**: merged stock DTB (`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`).
- **STOCK_BINARY_IMPLEMENTATION**: stock `scp.ko`, now source-identical.
- **PUBLIC_SOURCE_ONLY** and **UNKNOWN**: as named.

`scp.ko` is **pristine ALPS `5e415e05` `drivers/misc/mediatek/scp/rv`**. The stock module is whole-file
identical to it except the GNU build ID: 208/208 functions, 179 data objects, 138 import CRCs,
27 exports, 8 KCFI IDs, 9 309 relocations and `.modinfo`. No ODM delta exists in the SCP host.

> **Correction to `reverse-engineering/sensors/notes/yft-deltas.md`.** The DT-driven `awake-timeout`
> (`scp_awake_timeout`), the separate `SCP_WFI_WAIT_TIMEOUT`, the unconditional freq re-request in
> `scp_control_feature` and the CHRE magic/size `||` check were described there as "Ulefone deltas". They
> are the ALPS 5e41 revision of the public MediaTek source. The historical sensors patch is byte-identical
> to ALPS for `scp/rv`.

## Hardware contract

| Item | Stock value | Evidence |
|---|---|---|
| Core | `scp@1c400000`, `compatible "mediatek,scp"`, status okay; `core-nums 2`, `core-0 enable`, `twohart 1` (RISC-V, RV55) | ENABLED_IN_STOCK_DT |
| SRAM | 1 MiB at `0x1c400000` (`scp-sram-size 0x100000`) | ENABLED_IN_STOCK_DT |
| Register windows | `scp_cfgreg 0x1cb24000`, `scp_clkreg 0x1cb21000`, core0/core1 cfg `0x1cb30000`/`0x1cb40000`, bus tracker, L1C, secure cfg, `mbox0..4` (`0x1cba0000`–`0x1cbe0000`) | ENABLED_IN_STOCK_DT |
| IRQs | GIC SPI 0x204–0x20a: `ipc0 ipc1 mbox0..mbox4` | ENABLED_IN_STOCK_DT |
| IPI routing | `send-table`/`recv-table` (IPI id → mailbox, slot size), `#recv-cells-mode 1`, `mbox-count 4`; consumed through `mtk_tinysys_ipi`/`mtk-mbox` (`mtk_ipi_device_register`, `mtk_mbox_probe`, `scp_ipidev` export) | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Shared DRAM | `scp-mem-key "mediatek,reserve-memory-scp_share"`, `scp-mem-tbl` per-feature partitions; exports `scp_get_reserve_mem_{phys,virt,size}` | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Protection | `scp-dram-region`, `scp-protect` enable | ENABLED_IN_STOCK_DT |
| Crash dump | `secure-dump enable`, `secure-dump-size 0xe28000`, `memorydump <…>`; `scp_excep` → `aed_common_exception_api` (aee_aed) | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Recovery / watchdog | SCP WDT / reset → `scp_A_register_notify` chain (`SCP_EVENT_READY/STOP`); `awake-timeout 0x7530` | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Power / DVFS | `scp-dvfs` node: 10 clock parents, `dvfs-opp`, ULPOSC calibration v2 (`mt_get_fmeter_*` from clk-common), `scp-hwvoter`, `scp-pm-notify`, VLP clocking | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Feature cost | `scp-feature-tbl` (per-feature MHz request) | ENABLED_IN_STOCK_DT |
| Audio relation | `scp-audio-mbox@1cbe0000` shares the SCP with ADSP/VOW/ultrasound (AUDIO-BATCH-01, `mtk-dsp-type "RV55"`); `register_3way_semaphore_notifier` from `mtk-afe-external` | ENABLED_IN_STOCK_DT + STOCK_BINARY_IMPLEMENTATION |
| Loading | `scp.ko` vendor_dlkm, `insmod_sh:vendor` order 307; `RECORDED_LOADED` | PROVEN_RUNTIME (module-load capture) |
| Firmware image | dedicated signed `scp` partition; `vendor/firmware/remoteproc_scp` is a 32-byte stub; loaded/verified before Linux (no Linux firmware-loader path) | STOCK artifact inspection (see FIRMWARE-BOUNDARIES.md) |

## Exports consumed by this batch

| Consumer | SCP exports (CRC witnessed from ALPS source) |
|---|---|
| sensorhub | `scp_A_register_notify`, `scp_A_unregister_notify`, `scp_ipidev`, `scp_get_reserve_mem_{phys,virt,size}`, `scp_wdt_reset`, `sensor_control_scp`, `sap_enabled`, `sap_ipidev` (10, in-batch, same recipe) |
| connscp | `is_scp_ready`, `scp_A_register_notify`, `scp_get_reserve_mem_size`, `scp_get_reserve_mem_virt`, `scp_ipidev` (ALPS witness in the connectivity recipe) |
| audio (AUDIO-BATCH-01) | 13 symbols, previously witnessed; now backed by a certified-source `scp.ko` |

`scp.ko` was the largest uncertified provider behind the audio boundary. With this batch, the entire
SCP host is source-identical. The SCP firmware remains proprietary.
