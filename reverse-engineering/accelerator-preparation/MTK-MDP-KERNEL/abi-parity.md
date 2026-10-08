# Kernel ABI parity — MTK-MDP-KERNEL

All values below are from the clean-checkout acceptance run; the complete 938-row ledger is
`evidence/reconstruction/acceptance/abi-parity.tsv`.

## 1. Imports (`__versions`)

| module | import CRCs | mismatches |
|---|---:|---:|
| `clk-mt6878-mdpsys` | 7 | 0 |
| `mdp_drv_mt6878` | 223 | 0 |
| `mtk-mml` | 249 | 0 |
| `mtk-mml-mt6878` | 15 | 0 |
| **total** | **494** | **0** |

Of the 494 import slots, 376 resolve against the GKI 12901745 `vmlinux.symvers` and 118
against other vendor modules. Of those 118, **111 are external providers** and 7 are
`mtk-mml` exports consumed by `mtk-mml-mt6878`.

## 2. External provider ABI — derived, not copied

`derive-provider-crcs.sh` compiles only the provider *definitions* from the same public
source and harvests the `#SYMVER` records genksyms writes into the `.cmd` files. Every
required symbol must have exactly one CRC and that CRC must equal the value stock records:

```
PASS: 111/111 source-derived provider CRCs equal stock consumer references
```

| providing module | exports consumed | defining source |
|---|---:|---|
| `mtk-cmdq-drv-ext` | 78 | `cmdq/mailbox/{mtk-cmdq-helper-ext,mtk-cmdq-mailbox-ext,cmdq-util}.c` |
| `cmdq_helper_inf` | 8 | `misc/mediatek/mdp/cmdq_helper_inf.c` |
| `mmprofile` | 5 | `misc/mediatek/mmp/src/mmprofile.c` |
| `mtk_slbc` | 4 | `misc/mediatek/slbc/slbc.c` |
| `mtk_sync` | 3 | `gpu/drm/mediatek/mediatek_v2/mtk_sync.c` |
| `aee_aed` | 2 | `misc/mediatek/aee/aed/aee-common.c` |
| `tinysys-scmi` | 2 | `misc/mediatek/tinysys_scmi/tinysys-scmi-drv.c` |
| `clk-common` | 2 | `clk/mediatek/{clk-gate,clk-mtk}.c` |
| `mtk-icc-core` | 2 | `misc/mediatek/mtk-interconnect/core.c` |
| `mtk-smi-dbg` | 2 | `misc/mediatek/smi/mtk-smi-dbg.c` |
| `system_heap` | 1 | `dma-buf/heaps/mtk_system_heap.c` |
| `iommu_debug` | 1 | `misc/mediatek/iommu/iommu_debug.c` |
| `mtk-mmdvfs-v3` | 1 | `soc/mediatek/mtk-mmdvfs-v3.c` |

Per-symbol witness (which `.cmd` record produced each CRC):
`evidence/reconstruction/build/provider-crc-witnesses.tsv`.

Two symbol groups are defined in more than one place in the tree; the shipped variant was
selected from the config and the stock dependency list, and the derived CRC confirmed it:
`mmprofile_*` (real `mmp/src`, not `mmp/dummy`; `CONFIG_MTK_MMPROFILE_SUPPORT=y`) and
`mtk_sync_*` (`mediatek_v2`, not `dummy_drm`; `CONFIG_DRM_MEDIATEK_V2=y`).

## 3. Exports

| module | `EXPORT_SYMBOL_GPL` | `EXPORT_SYMBOL` | CRC mismatches |
|---|---:|---:|---:|
| `mdp_drv_mt6878` | 1 (`mdp_dpc_register`) | 0 | 0 |
| `mtk-mml` | 31 | 5 | 0 |

Export CRCs were read through the `__crc_<name>` symbols inside `__kcrctab` /
`__kcrctab_gpl`, so exported *data objects* are covered as well as functions, and the
licence bucket is proven per symbol. The ledger is asserted complete against the total
`__kcrctab*` byte size of each module.

`mtk-mml`'s 36 exports are the MML consumer contract: the 14 `mml_drm_*` DRM-adaptor
entry points (`get_context`, `put_context`, `query_cap`, `try_frame`, `submit`,
`submit_timeout`, `stop`, `ctx_idle`, `config_rdone`, `dump`, `set_panel_pixel`,
`racing_config_sync`, `racing_stop_sync`, `split_info`), the component/topology
registration API (`mml_register_comp`, `mml_unregister_comp`, `mml_comp_init`,
`mml_subcomp_init`, `mml_topology_register_ip`, `mml_topology_unregister_ip`,
`mml_topology_get_cache`, `mml_dev_get_comp_by_id`, `mml_get_plat_device`,
`mml_get_mmu_dev`), the direct-link/racing controls (`mml_dl_enable`, `mml_dl_vdo`,
`mml_racing_enable`), DPC hooks (`mml_dpc_register`, `mml_dpc_disable`), logging
(`mml_save_log_record`) and the `EXPORT_SYMBOL` tunables
(`mml_get_swpm_func`, `mml_tablet_ext`, …).

## 4. KCFI

34 absolute `__kcfi_typeid_*` values (`mdp_drv_mt6878` 8, `mtk-mml` 26) are identical in
name and value. Because every function byte is identical, the inline KCFI type prologues
are identical too; no type had to be recovered by hand.

## 5. `.modinfo`, vermagic, srcversion

373 `.modinfo` records are identical, including every `parm`/`parmtype` of `mtk-mml`
(31 tunables such as `mtk_mml_msg`, `mml_qos`, `mml_pq_disable`, `mml_racing`,
`mml_trace`, `mml_pkt_dump`) and `mtk-mml-mt6878` (`mml_force_rsz`, `mml_path_mode`),
the `import_ns=DMA_BUF` of `mdp_drv_mt6878`, and these dependency strings:

```
clk-mt6878-mdpsys  depends=clk-common
mdp_drv_mt6878     depends=cmdq_helper_inf,mtk-cmdq-drv-ext,iommu_debug,mtk-icc-core,
                           system_heap,mmprofile,aee_aed,mtk-smi-dbg,mtk-mmdvfs-v3
mtk-mml            depends=mtk-cmdq-drv-ext,mtk-mmdvfs-v3,mtk-icc-core,mtk_slbc,
                           mtk-smi-dbg,aee_aed,mtk_sync,system_heap,tinysys-scmi
mtk-mml-mt6878     depends=mtk-mml,…
```

The `depends=` strings are *produced by modpost from the derived provider symvers*, so they
are themselves a check that the provider ownership mapping above is right.

`vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`
and `srcversion` match stock for all four modules with no normalization.

## 6. Module aliases

`mtk-mml`'s `MODULE_DEVICE_TABLE` aliases (the long `of:N*T*Cmediatek,mt69xx-mml*` list
covering mt6983/6893/6879/6895/6985/6886/6897/6989/**6878** and each component type) are
byte-identical, i.e. the shipped module advertises exactly the same OF match surface.
