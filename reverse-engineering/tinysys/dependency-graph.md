# TinySys messaging dependency graph (GQ5012BF1 stock)

This graph was derived statically from all 398 shipped vendor modules: `vendor_dlkm` plus the `vendor_boot` platform ramdisk. Edge data comes from `.symtab` SHN_UNDEF references, `__versions` CRCs and RELA streams. Raw edges are in [`kernel/dependency-edges.tsv`](kernel/dependency-edges.tsv) (102 edges), produced by [`scripts/depgraph.py`](scripts/depgraph.py).

**Result: 102/102 edges have an import CRC equal to the provider export CRC. 9/9 address-taken edges have a consumer `__kcfi_typeid_<sym>` equal to the provider function's KCFI preamble word.**

## Layering

```
                                   AP kernel                                        remote core
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ clients: sensorhub, ccci_fsm_scp, connscp, mtk-vow, snd-soc-mtk-scp-ultra, │
 │   snd-soc-audiodsp-common (SCP) | mtk-vcodec-{dec,enc}-v1, mmqos-common,    │
 │   mtk-mmdvfs-v3 (VCP) | fhctl, ged, mtk_gpufreq_wrapper (GPUEB/MCUPM),      │
 │   met_ipi_api (function-pointer bridge into met.ko)                         │
 └──────────────┬───────────────────────────────────────────────────────────────┘
                │ mtk_ipi_register/send/send_compl/recv_reply/unregister (10 exports)
 ┌──────────────▼──────────────┐   per-processor owner modules create the device:
 │ mtk_tinysys_ipi.ko          │◄── scp.ko (scp_ipidev, sap_ipidev), vcp.ko (vcp_ipidev,
 │ IPI framework: per-channel  │    re-exported by vcp_status.ko vcp_get_ipidev),
 │ table, send/ack/recv, ISR cb│    gpueb.ko (get_gpueb_ipidev), mcupm.ko (get_mcupm_ipidev)
 └───────┬───────────────┬─────┘    call mtk_ipi_device_register() and mtk_mbox_probe()
  TX path│               │ RX path (mbox->ipi_cb = ipi_isr_cb)
 ┌───────▼──────────┐    │
 │ mtk_rpmsg_mbox.ko│    │  rpmsg_trysend(ept) -> mtk_rpmsg_trysend -> mtk_mbox_send
 │ rpmsg device +   │    │  (rpmsg core from GKI: rpmsg_register_device/create_ept/trysend)
 │ 1 ept per channel│    │
 └───────┬──────────┘    │
         │ check_send_irq / write / trigger_irq
 ┌───────▼───────────────▼──────────────────────────────────────┐
 │ mtk-mbox.ko (DONE separately: DIRECT_SOURCE_MATCH)            │
 │ SRAM slot copy, set/clr IRQ regs, ISR -> pin_buf -> ipi_cb    │ ◄──── mailbox HW ────► SCP / VCP / GPUEB / MCUPM firmware
 └──────────────────────────────────────────────────────────────┘
```

`modinfo depends=` agrees:

- `mtk_rpmsg_mbox` → `mtk-mbox`
- `mtk_tinysys_ipi` → `mtk_rpmsg_mbox,mtk-mbox`
- `scp` / `vcp` / `mcupm` / `gpueb` → `mtk_tinysys_ipi,mtk-mbox` (and others)

Load order (`vendor_dlkm/modules.load` lines 86, 87, 88, 89, 92) is `mtk_rpmsg_mbox`, `mtk-mbox`, `mtk_tinysys_ipi`, `scp`, `mcupm`. In `modules.load.recovery` they are lines 179/180/181. `vcp` (line 77) and `gpueb` (line 37) appear earlier in `modules.load`, but modprobe resolves `depends=`.

## What each layer contributes

| layer | contributes | does NOT do |
|---|---|---|
| `mtk-mbox` | mailbox register/SRAM access; ISR copies the inbound slot into the registered `pin_buf`; ISR-context user callback; calls `mbdev->ipi_cb` | channel naming, waiting, ACK pairing |
| `mtk_rpmsg_mbox` (3 exports) | Wraps a `mtk_mbox_device` as a GKI `rpmsg_device` (`rpdev.src` = channel count). For every channel it builds a `mtk_rpmsg_channel_info` (send/recv slot, size, pin index found by `chan_id` in the pin tables) and an endpoint (`ept.addr` = chan_id). TX is a single non-blocking `mtk_mbox_send`: busy check → SRAM write → `mb()` → IRQ trigger. | **No RX path at all**: endpoints get `cb = NULL` and inbound messages never traverse rpmsg. No probe/remove/PM, no module_init. `wait` is ignored, so `send` and `trysend` are identical. |
| `mtk_tinysys_ipi` (10 exports) | per-device channel table; registration of receive buffers/callbacks; WAIT (mutex) vs POLLING (spinlock, IRQs off) send modes; retry-until-deadline on busy pin; `send_compl` ACK wait (completion or `mtk_mbox_polling`); `recv`/`recv_reply`; stage timestamps (IPIMonitor); timeout dump + optional `timeout_handler` | MMIO, IRQ registration, firmware loading, PM (owned by scp/vcp/gpueb/mcupm) |

## Exported-symbol edges

Each row: provider symbol, export CRC (`__kcrctab`) and the provider's KCFI type id (the word at function−4). Each consumer is listed with the number of `CALL26`/`JUMP26` call sites and address-taking relocations, then the functions that contain them. The consumer `__versions` CRC equals the export CRC on every edge (column `crc_match` in the TSV).

### `mtk-mbox.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `mtk_mbox_check_send_irq` | `0x80bd521e` | `0xabe00fc8` | `adsp` (4/0) — adsp_mbox_send, adsp_mbox_send_irq<br>`mcupm` (1/0) — mcupm_mbox_write<br>`mtk-scp-audiocommon` (2/0) — audio_mbox_send<br>`mtk_rpmsg_mbox` (1/0) — mtk_mbox_send |
| `mtk_mbox_clr_index_record` | `0xa83c1d47` | `0x9481d03c` | `scp` (5/0) — scp_suspend_cb |
| `mtk_mbox_dump_recv_pin` | `0xe5fbbdd9` | `0x935bbd45` | `adsp` (2/0) — adsp_mbox_dump<br>`mtk_tinysys_ipi` (1/0) — mtk_ipi_send_compl |
| `mtk_mbox_get_index_record` | `0x62943794` | `0x0f1026e2` | `scp` (1/0) — scp_resume_cb |
| `mtk_mbox_polling` | `0x1208cd68` | `0x560ac8ae` | `mtk_tinysys_ipi` (1/0) — mtk_ipi_send_compl |
| `mtk_mbox_probe` | `0x5c3b8200` | `0x2199da25` | `adsp` (4/0) — adsp_mbox_probe<br>`gpueb` (1/0) — gpueb_ipi_init<br>`mcupm` (1/0) — mcupm_device_probe<br>`mtk-scp-audiocommon` (1/0) — scp_audio_mbox_dev_probe<br>`scp` (2/0) — sap_device_probe, scp_device_probe<br>`vcp` (1/0) — vcp_device_probe |
| `mtk_mbox_read` | `0xf2910de5` | `0xf4fae0f5` | `mcupm` (1/0) — mcupm_mbox_read<br>`scp` (2/0) — mt_print_scp_ipi_id |
| `mtk_mbox_read_recv_irq` | `0x4d87de50` | `0x0f1026e2` | `scp` (1/0) — mt_print_scp_ipi_id |
| `mtk_mbox_reset_record` | `0x4722108b` | `0x9ae62d8a` | `mtk_tinysys_ipi` (1/0) — mtk_ipi_device_reset |
| `mtk_mbox_trigger_irq` | `0x7170bb6f` | `0xbd6e259c` | `adsp` (2/0) — adsp_mbox_send, adsp_mbox_send_irq<br>`mtk-scp-audiocommon` (1/0) — audio_mbox_send<br>`mtk_rpmsg_mbox` (1/0) — mtk_mbox_send |
| `mtk_mbox_write` | `0xd60fa245` | `0xf4fae0f5` | `adsp` (1/0) — adsp_mbox_send_irq<br>`gpueb` (4/0) — timesync_sync_base<br>`mcupm` (1/0) — mcupm_mbox_write<br>`mtk_rpmsg_mbox` (1/0) — mtk_mbox_send |
| `mtk_mbox_write_hd` | `0x987931e5` | `0x9201af70` | `adsp` (1/0) — adsp_mbox_send<br>`mtk-scp-audiocommon` (1/0) — audio_mbox_send |
| `mtk_smem_init` | `0x124493ab` | `0xa2c6ee28` | `gpueb` (1/0) — gpueb_ipi_init<br>`mcupm` (1/0) — mcupm_device_probe |

### `mtk_rpmsg_mbox.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `mtk_rpmsg_create_channel` | `0xb1fef50a` | `0x0870a6b9` | `mtk_tinysys_ipi` (1/0) — mtk_ipi_device_register |
| `mtk_rpmsg_create_device` | `0x639753b0` | `0xbc43f757` | `mtk_tinysys_ipi` (1/0) — mtk_ipi_device_register |

### `mtk_tinysys_ipi.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `ipi_monitor_dump` | `0xe9c9605c` | `0xb340ff51` | `gpueb` (1/0) — gpueb_plat_ipi_timeout_cb |
| `mtk_ipi_device_register` | `0xbdb7a098` | `0x3af51544` | `gpueb` (1/0) — gpueb_ipi_init<br>`mcupm` (1/0) — mcupm_device_probe<br>`scp` (2/0) — sap_device_probe, scp_device_probe<br>`vcp` (1/0) — vcp_device_probe |
| `mtk_ipi_recv_reply` | `0x35a6e1e2` | `0x0ca0d288` | `met_ipi_api` (0/2) — init_module [typeid 0x0ca0d288]<br>`scp` (1/0) — scp_chre_manager_read |
| `mtk_ipi_register` | `0x825ce65b` | `0x5b71d57f` | `ccci_fsm_scp` (1/0) — fsm_scp_init0<br>`connscp` (1/0) — conap_scp_ipi_init<br>`fhctl` (2/0) — gpueb_init_v1, mcupm_init_v1<br>`ged` (2/0) — fdvfs_init<br>`gpueb` (3/0) — gpueb_gpumpu_init, gpueb_hw_voter_dbg_init, gpueb_plat_service_init<br>`mcupm` (1/0) — mcupm_device_probe<br>`met_ipi_api` (0/2) — init_module [typeid 0x5b71d57f]<br>`mtk-vcodec-dec-v1` (1/0) — vdec_vcp_probe<br>`mtk-vcodec-enc-v1` (1/0) — venc_vcp_probe<br>`mtk-vow` (2/0) — vow_ipi_register<br>`mtk_gpufreq_wrapper` (1/0) — gpufreq_wrapper_pdrv_probe<br>`scp` (22/0) — init_module, mt_scp_dump_sleep_count, mt_scp_dvfs_sleep_cnt_proc_show, mt_scp_dvfs_sleep_cnt_proc_write, mt_scp_dvfs_sleep_proc_show, mt_scp_dvfs_sleep_proc_write, scp_chre_manager_init, scp_hw_voter_dbg_init, scp_legacy_ipi_init, scp_logger_init, sync_ulposc_cali_data_to_scp<br>`sensorhub` (3/0) — ipi_comm_init, sap_custom_cmd_init<br>`snd-soc-audiodsp-common` (1/0) — mtk_dsp_probe<br>`snd-soc-mtk-scp-ultra` (2/0) — ultra_ipi_register<br>`vcp` (5/0) — init_module, vcp_hw_voter_dbg_init, vcp_logger_init |
| `mtk_ipi_send` | `0x19bb8852` | `0x14f748fc` | `ccci_fsm_scp` (11/0) — ccci_scp_ipi_send<br>`connscp` (6/0) — conap_scp_ipi_send<br>`met_ipi_api` (0/2) — init_module [typeid 0x14f748fc]<br>`mmqos-common` (1/0) — mmqos_vcp_ipi_send<br>`mtk-mmdvfs-v3` (1/0) — mmdvfs_vcp_ipi_send<br>`mtk-vcodec-dec-v1` (2/0) — vcp_dec_ipi_handler, vdec_vcp_ipi_send<br>`mtk-vcodec-enc-v1` (2/0) — vcp_enc_ipi_handler, venc_vcp_ipi_send<br>`mtk-vow` (1/0) — vow_ipi_send<br>`scp` (12/0) — mt_scp_dvfs_sleep_cnt_proc_write, mt_scp_dvfs_sleep_proc_write, scp_debug_write, scp_device_shutdown, scp_ipi_send, scp_logger_notify_ws, scp_request_freq, scp_resume_cb, scp_suspend_cb<br>`sensorhub` (5/0) — ipi_comm_noack, ipi_transfer_messages, sap_custom_cmd_comm<br>`snd-soc-mtk-scp-ultra` (2/0) — ultra_ipi_send_msg<br>`vcp` (1/0) — vcp_logger_notify_ws |
| `mtk_ipi_send_compl` | `0x705006af` | `0x68725260` | `fhctl` (22/0) — gpueb_hopping_v1, gpueb_ssc_disable_v1, gpueb_ssc_enable_v1, mcupm_hopping_v1, mcupm_ssc_disable_v1, mcupm_ssc_enable_v1<br>`ged` (3/0) — ged_to_fdvfs_command<br>`gpueb` (3/0) — gpueb_gpumpu_init, gpueb_hw_voter_dbg_proc_write, gpueb_mobile_log_store<br>`mcupm` (6/0) — mcupm_alive_show, mcupm_dvcs_enable_show, mcupm_efuse_read_show, mcupm_mobile_log_store, mcupm_plt_module_init<br>`met_ipi_api` (0/2) — init_module [typeid 0x68725260]<br>`mtk_gpufreq_wrapper` (1/0) — gpufreq_ipi_to_gpueb<br>`scp` (12/0) — mt_scp_dump_sleep_count, mt_scp_dvfs_sleep_cnt_proc_show, mt_scp_dvfs_sleep_proc_show, scp_chre_manager_write, scp_hw_voter_dbg_proc_write, scp_pm_event, sync_ulposc_cali_data_to_scp<br>`vcp` (6/0) — vcp_deregister_off_store, vcp_disable_pm_clk, vcp_enable_pm_clk, vcp_hw_voter_dbg_proc_write, vcp_register_on_store |
| `mtk_ipi_unregister` | `0xa55a0ebf` | `0x30ec1cfc` | `connscp` (1/0) — conap_scp_ipi_deinit<br>`met_ipi_api` (0/2) — init_module [typeid 0x30ec1cfc]<br>`sensorhub` (3/0) — ipi_comm_exit, sap_custom_cmd_exit |

### `scp.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `sap_ipidev` | `0x23a25986` | `-` | `sensorhub` (0/6) — sap_custom_cmd_comm, sap_custom_cmd_exit, sap_custom_cmd_init |
| `scp_ipidev` | `0x275789bb` | `-` | `ccci_fsm_scp` (0/24) — ccci_scp_ipi_send, fsm_scp_init0<br>`connscp` (0/16) — conap_scp_ipi_deinit, conap_scp_ipi_init, conap_scp_ipi_send<br>`mtk-vow` (0/4) — vow_ipi_register, vow_ipi_send<br>`sensorhub` (0/14) — ipi_comm_exit, ipi_comm_init, ipi_comm_noack, ipi_transfer_messages<br>`snd-soc-audiodsp-common` (0/2) — mtk_dsp_probe<br>`snd-soc-mtk-scp-ultra` (0/6) — ultra_ipi_register, ultra_ipi_send_msg |

### `vcp.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `vcp_ipidev` | `0x560025f9` | `-` | `mtk-vcodec-dec-v1` (0/6) — vcp_dec_ipi_handler, vdec_vcp_ipi_send, vdec_vcp_probe<br>`mtk-vcodec-enc-v1` (0/6) — vcp_enc_ipi_handler, venc_vcp_ipi_send, venc_vcp_probe |

### `vcp_status.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `vcp_get_ipidev` | `0xe21b867b` | `0xc95d2c54` | `mmqos-common` (3/0) — mmqos_vcp_init_thread, mmqos_vcp_ipi_send<br>`mtk-mmdvfs-v3` (3/0) — mmdvfs_vcp_init_thread, mmdvfs_vcp_ipi_send |
| `vcp_set_ipidev` | `0x95f5de9f` | `0xb340ff51` | `vcp` (1/0) — init_module |

### `mcupm.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `get_mcupm_ipidev` | `0x73e08ef8` | `0xa402679d` | `fhctl` (12/0) — mcupm_hopping_v1, mcupm_init_v1, mcupm_ssc_disable_v1, mcupm_ssc_enable_v1<br>`met_mcupm_api` (0/2) — init_module [typeid 0xa402679d] |

### `gpueb.ko` exports

| symbol | CRC | KCFI type id | consumer (call sites / address refs) — calling functions |
|---|---|---|---|
| `get_gpueb_ipidev` | `0x0fbee3af` | `0xa402679d` | `fhctl` (12/0) — gpueb_hopping_v1, gpueb_init_v1, gpueb_ssc_disable_v1, gpueb_ssc_enable_v1<br>`ged` (6/0) — fdvfs_init, ged_to_fdvfs_command<br>`met_gpueb_api` (0/2) — init_module [typeid 0xa402679d]<br>`mtk_gpufreq_wrapper` (2/0) — gpufreq_ipi_to_gpueb, gpufreq_wrapper_pdrv_probe |
| `gpueb_get_recv_PIN_ID_by_name` | `0xa3c8b3eb` | `0x421d93ee` | `ged` (1/0) — fdvfs_init<br>`met_gpueb_api` (0/2) — init_module [typeid 0x421d93ee] |
| `gpueb_get_send_PIN_ID_by_name` | `0x2fae0e87` | `0x421d93ee` | `fhctl` (1/0) — gpueb_init_v1<br>`ged` (1/0) — fdvfs_init<br>`met_gpueb_api` (0/2) — init_module [typeid 0x421d93ee]<br>`mtk_gpufreq_wrapper` (1/0) — gpufreq_wrapper_pdrv_probe |

## Exports with no in-image consumer

These are still exported and ABI-exact, but no shipped module imports them:

- `mtk_rpmsg_mbox`: `mtk_mbox_send`. It is reached only through `mtk_rpmsg_ops.mbox_send`.
- `mtk_tinysys_ipi`: `mtk_ipi_device_reset`, `mtk_ipi_recv`, `mtk_ipi_tracking`.
- `mtk-mbox`: 13 debug/legacy helpers (`mtk_mbox_cb_register`, `_clr_irq`, `_dump*`, `_print*`, `_read_hd`, `_set_base_*`, `_log_enable`). They are listed for completeness; MTK-MBOX is closed separately.

## Not on this transport (verified by imports)

- **SSPM.** `sspm_v3.ko` depends only on `tinysys-scmi`. Its path is: GKI `arm,scmi` (`/firmware/scmi`, `protocol@80`) → `mboxes` → `mediatek,tinysys_mbox` (`mtk-mbox-mailbox.ko`, a mailbox-framework controller on `ssram1@1c350000/tiny-mbox@0` and `ssram2@1c360000/tiny-mbox@1`) → `tinysys-scmi.ko`. Neither `sspm_v3` nor `mtk_cm_ipi` imports any `mtk_ipi_*`, `mtk_mbox_*` or `mtk_rpmsg_*` symbol.
- **ADSP.** `adsp.ko` and `mtk-scp-audiocommon.ko` use `mtk-mbox` directly, with their own queue-mode (`mtk_mbox_write_hd`) IPI, and never touch `mtk_tinysys_ipi`. See [`processors.md`](processors.md) for enablement.
- **CCU.** `mtk_ccuv.ko` imports no TinySys messaging symbol; its transport is the CCU rproc path.
- **APU.** `apusys.ko` uses GKI rpmsg with its own `apusys-rv` rpmsg devices, not `mtk_rpmsg_mbox`.
