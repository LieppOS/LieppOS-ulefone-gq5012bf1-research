# Kernel ABI parity — GPU-AI-AUX-KERNEL-INTERFACES

All values are from the clean-checkout acceptance run; the complete 294-row ledger is
`evidence/reconstruction/acceptance/abi-parity.tsv`.

## 1. Imports (`__versions`)

| module | import CRCs | mismatches |
|---|---:|---:|
| `gpueb` | 68 | 0 |
| `vcp` | 134 | 0 |
| `vcp_status` | 1 | 0 |
| **total** | **203** | **0** |

179 of the 203 slots resolve against the GKI 12901745 `vmlinux.symvers`; 24 against vendor
modules. Of those 24, **16 are true external providers** and 8 are `vcp_status` exports
consumed by `vcp` inside this component.

## 2. External provider ABI — derived, not copied

`derive-provider-crcs.sh` compiles only the provider *definitions* from the same public
source and harvests the `#SYMVER` records genksyms writes into the `.cmd` files; each
symbol must have exactly one CRC and that CRC must equal the stock-recorded value:

```
PASS: 16/16 source-derived provider CRCs equal stock consumer references
```

| providing module | symbols | defining source |
|---|---|---|
| `mtk_tinysys_ipi` | `mtk_ipi_device_register`, `mtk_ipi_register`, `mtk_ipi_send`, `mtk_ipi_send_compl`, `ipi_monitor_dump` | `soc/mediatek/mtk_tinysys_ipi.c` |
| `mtk-mbox` | `mtk_mbox_probe`, `mtk_mbox_write`, `mtk_smem_init` | `soc/mediatek/mtk-mbox.c` |
| `clk-common` | `mt_get_fmeter_freq`, `mtk_clk_mminfra_hwv_power_ctrl_optional` | `clk/mediatek/clk-fmeter.c`, `clk-mtk.c` |
| `aee_aed` | `aed_common_exception_api` | `misc/mediatek/aee/aed/aee-common.c` |
| `mrdump` | `mrdump_mini_add_extra_file` | `misc/mediatek/aee/mrdump/mrdump_mini.c` |
| `irq-dbg` | `mt_irq_dump_status` | `misc/mediatek/sda/irq-dbg.c` |
| `system_heap` | `mtk_dma_buf_set_name` | `dma-buf/heaps/mtk_system_heap.c` |
| `mtk-smi-dbg` | `mtk_smi_dbg_dump_for_mminfra` | `misc/mediatek/smi/mtk-smi-dbg.c` |
| `device-apc-common` | `register_devapc_power_callback` | `soc/mediatek/devapc/devapc-mtk-multi-ao.c` |

Per-symbol witness: `evidence/reconstruction/build/provider-crc-witnesses.tsv`.
`mtk_tinysys_ipi` and `mtk-mbox` keep their existing DONE owners (MTK-TINYSYS-IPI,
MTK-MBOX); nothing here rebuilds or re-owns them.

## 3. Exports (60 CRCs, all identical)

| module | `EXPORT_SYMBOL_GPL` | `EXPORT_SYMBOL` |
|---|---:|---:|
| `gpueb` | 11 | 3 (`gpueb_dump_status`, `gpueb_trigger_wdt`, `gpueb_get_gpr_addr`) |
| `vcp` | 23 | 4 |
| `vcp_status` | 19 | 0 |

Read through `__crc_<name>` inside `__kcrctab`/`__kcrctab_gpl`, so exported **data**
objects are covered too (`vcp_ipidev`, `vcp_mboxdev`, `feature_table`, `vcp_ao`,
`pwclkcnt`, `mmup_enable_count`, `driver_init_done`, `is_suspending`), with a proven
licence bucket per symbol. The ledger is asserted complete against each module's total
`__kcrctab*` byte size — this is why the authoritative counts (14 / 27 / 19) exceed the
preparation's positional counts (14 / 23 / 15).

Contract shape:

* `gpueb` — reserved-memory accessors (`gpueb_get_reserve_mem_{phys,virt,size}[_by_name]`),
  IPI plumbing (`get_gpueb_ipidev`, `gpueb_get_{send,recv}_PIN_ID_by_name`,
  `gpueb_{get,clr}_mbox1_irq`), GPR address and the debug/WDT hooks.
* `vcp_status` — the **early**, dependency-free surface (`depends=` is empty): readiness
  and suspend state (`is_vcp_ready_ex`, `is_vcp_suspending_ex`, `is_suspending`), feature
  refcounts (`vcp_register_feature_ex`, `vcp_deregister_feature_ex`), reserved memory
  (`vcp_get_reserve_mem_{phys,virt}_ex`), notifier registration, `vcp_cmd_ex`, power
  counters (`pwclkcnt`, `mmup_enable_count`, `vcp_ao`) and the late-binding setters
  (`vcp_set_fp`, `vcp_set_ipidev`, `vcp_set_mminfra_cb`) that `vcp.ko` calls on probe.
* `vcp` — the full host API (`is_vcp_ready`, `vcp_register_feature`, `vcp_awake_lock/unlock`,
  `vcp_get_io_device`, `vcp_get_reserve_mem_*`, `get_vcp_semaphore`, `trigger_vcp_halt`,
  `vcp_wdt_reset`, `wait_vcp_ready_to_reboot`, `vcp_enable/disable_pm_clk`, …).

The two-module split is a deliberate boot-order device: `vcp_status.ko` loads from the
**vendor ramdisk** (`modules.load` line 166) with no dependencies, while `vcp.ko` loads
later from **vendor_dlkm** (line 77) and registers itself into the status module through
`vcp_set_fp` / `vcp_set_ipidev` / `vcp_set_mminfra_cb`. Early clients therefore link only
against `vcp_status`.

## 4. KCFI

13 absolute `__kcfi_typeid_*` values are identical in name and value: `gpueb` 6
(`gpueb_log_if_{read,poll,open}` plus the `seq_read`/`seq_lseek`/`single_release` proc
helpers), `vcp` 7 (`vcp_clr_spm_reg`, `vcp_awake_lock`, `vcp_awake_unlock`,
`vcp_A_irq_handler` plus the same three seq helpers). Because every function byte matches,
the inline KCFI prologues match too.

## 5. `.modinfo`, vermagic, srcversion

18 `.modinfo` records identical, including:

```
gpueb       depends=mtk_tinysys_ipi,mtk-mbox
            alias=of:N*T*Cmediatek,gpueb ; of:N*T*Cmediatek,gpuebC*
            description=MediaTek GPUEB-PLAT driver
vcp         depends=vcp_status,clk-common,mtk-smi-dbg,mtk_tinysys_ipi,irq-dbg,
                    device-apc-common,mtk-mbox,system_heap,mrdump,aee_aed
            import_ns=DMA_BUF ; description=MEDIATEK Module VCP driver
vcp_status  depends=            (intentionally empty)
```

The `depends=` strings are generated by modpost from the derived provider symvers, so they
independently confirm the provider-ownership mapping in §2.
`vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
and `srcversion` match stock for all three with no normalization.

## 6. Cross-component ABI (consumers of this component)

67 edges, **67 MATCH, 0 mismatch**, against the rebuilt exports — see
[cross-component-abi.tsv](cross-component-abi.tsv):

| consumer | owner | symbols |
|---|---|---:|
| `mtk-vcodec-dec-v1`, `mtk-vcodec-enc-v1`, `mtk-vcu` | MTK-VCODEC-KERNEL (DONE) | 26 |
| `mtk_gpufreq_wrapper`, `ged`, `fhctl`, `met_gpueb_api` | MALI-GPU-KERNEL (DONE) | 15 |
| `mmqos-common` | MMQoS owner | 9 |
| `mtk-mmdvfs-v3` | MMDVFS owner | 9 |
| `mtk-cmdq-drv-ext` | CMDQ owner | 5 |
| `mediatek-drm` | MEDIATEK-DRM (DONE) | 1 |
| `mtk-mminfra-debug` | MMINFRA owner | 1 |
| `mtk_imgsys_cmdq` | CAMERA-ISP-KERNEL | 1 |

This is the concrete link to the already-closed components: the VCP host symbols the DONE
VCodec modules import (`feature_table`, `vcp_ipidev`, `is_vcp_ready`, `trigger_vcp_halt`,
`vcp_get_io_device`, …) are produced here with the exact CRCs those modules record, and the
GPUEB symbols the Mali-side GPU-frequency stack imports (`get_gpueb_ipidev`,
`gpueb_get_gpr_addr`, `gpueb_get_send_PIN_ID_by_name`, `gpueb_dump_status`) likewise.
