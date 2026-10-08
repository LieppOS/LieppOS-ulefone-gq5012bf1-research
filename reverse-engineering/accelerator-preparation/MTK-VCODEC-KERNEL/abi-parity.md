# Kernel ABI parity — MTK-VCODEC-KERNEL

All rows below are **measured** against the shipped stock binaries by `verify.py` on a clean
checkout. Machine-readable ledger: `evidence/reconstruction/acceptance/abi-parity.tsv`
(937 rows, every one `IDENTICAL`).

## Axis totals

| Module | import CRCs | export CRCs | absolute KCFI ids | `.modinfo` keys |
|---|---:|---:|---:|---:|
| `mtk-vcodec-common` | 92 | 61 | 1 | 7 |
| `mtk-vcodec-dec-v1` | 254 | 0 | 20 | 55 |
| `mtk-vcodec-enc-v1` | 230 | 0 | 22 | 50 |
| `mtk-vcu` | 100 | 14 | 1 | 19 |
| `clk-mt6878-vcodec` | 7 | 0 | 0 | 4 |

Export CRCs are read from the `__crc_<name>` symbols that address their own `u32` inside
`__kcrctab` / `__kcrctab_gpl`; the ledger is asserted complete against the total `__kcrctab*`
size, so exported **data** objects (module parameters such as `mtk_v4l2_dbg_level`,
`mtk_vcodec_vcp`, `vcu_func`, `support_svp_region`) are covered, not only exported functions.

In-function KCFI type words are part of the compared function bytes and are therefore covered
by the 100 % byte-identical function result; the counts above are the additional absolute
`__kcfi_typeid_*` symbols.

## Import resolution

| Source of the export | symbols |
|---|---:|
| GKI `vmlinux.symvers`, build 12901745 | 242 distinct |
| Owned modules of this component | 52 distinct |
| External vendor providers (other components) | 60 distinct |

The 60 external CRCs were **generated from public provider source** by genksyms and compared
to the CRCs the stock modules record; all 60 agree. Witness `.cmd` records:
`evidence/reconstruction/build/provider-crc-witnesses.tsv`. Provider ownership stays with the
existing components — this component does not absorb VCP, TinySys IPI, CMDQ, SMI, SLBC,
IOMMU-debug, MMQoS/ICC, EMI, scheduler, system_heap or clk-common.

## `.modinfo` and load contract (stock, reproduced byte-identically)

| Module | `name` | `depends` | notable |
|---|---|---|---|
| `mtk-vcodec-common` | `mtk_vcodec_common` | `scheduler,system_heap` | `parm fence_debug:int`, `import_ns=DMA_BUF` |
| `mtk-vcodec-dec-v1` | `mtk_vcodec_dec_v1` | `mtk-vcodec-common,mtk-icc-core,vcp,mtk_tinysys_ipi,emi,mtk-mmdvfs-v3,vcp_status,system_heap,iommu_debug,mtk_slbc` | 10 decoder module parameters |
| `mtk-vcodec-enc-v1` | `mtk_vcodec_enc_v1` | `mtk-vcodec-common,mtk-icc-core,mtk-mmdvfs-v3,mtk-smi-dbg,vcp,mtk_slbc,mtk_tinysys_ipi,emi,mtk-smi,iommu_debug` | encoder parameters incl. SMI monitor |
| `mtk-vcu` | `mtk_vcu` | `mtk-vcodec-common,mtk-cmdq-drv-ext,vcp` | 12 OF aliases, none matching a node in the stock DTB |
| `clk-mt6878-vcodec` | `clk_mt6878_vcodec` | `clk-common` | vendor-ramdisk module |

Stock load order (`modules.load`): `clk-mt6878-vcodec.ko` from the vendor ramdisk (line 32,
after `clk-common`), then in `vendor_dlkm` `mtk-vcu.ko` (78) → `mtk-vcodec-common.ko` (80) →
`mtk-vcodec-dec-v1.ko` (81) → `mtk-vcodec-enc-v1.ko` (82). Note that modprobe resolves
`mtk-vcu`'s dependency on `mtk-vcodec-common` regardless of the listed order.

`vermagic` on all five: `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload
modversions aarch64` — reproduced, not stamped.
