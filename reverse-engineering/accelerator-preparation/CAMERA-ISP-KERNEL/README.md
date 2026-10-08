# CAMERA-ISP-KERNEL — DONE

Scoped static reconstruction of the Ulefone Armor 29 Pro Thermal / GQ5012BF1 normal-world
MediaTek MT6878T camera/ISP kernel stack.

## Result

All nineteen owned stock modules rebuild from pinned public source plus explicit device
patches and pass clean-checkout B1/B2 acceptance. The proof covers every function, data
object, section, import/export CRC, KCFI id, `.modinfo` record and relocation. There are
zero unresolved rows; the two bounded non-byte residues are documented and accepted.

Start here:

* [reconstruction report](RECONSTRUCTION-REPORT.md) — per-module results and residues;
* [source recipe](SOURCE.md) and [lineage](source-lineage.md);
* [build reproduction](build-reproduction.md);
* [ABI parity](abi-parity.md);
* [hardware contract](hardware-contract.md) and [DT-to-driver contract](device-tree-contract.md);
* [kernel-to-userspace contract](source-to-userspace-contract.md);
* [firmware/proprietary boundary](firmware-boundary.md);
* [evidence index](evidence/EVIDENCE-INDEX.md) and [status](STATUS.md).

## Owned modules

`mtk_hcp.ko`, `mtk-ipesys-me.ko`, `mtk_imgsys_cmdq.ko`, `mtk_imgsys_v4l2.ko`,
`mtk_imgsys_isp7sp.ko`, `ccd_rpmsg.ko`, `mtk_ccd_remoteproc.ko`, `mtk_ccuv.ko`,
`mtk-cam-isp7sp.ko`, `mtk_aie.ko`, `mtk_aie_debug_7sp_2.ko`,
`camera_dpe_isp7sp.ko`, `pda_drv_mt6878.ko`, `mtk-vmm-isp71-regulator.ko`,
`mtk-vmm-notifier.ko`, `imgsensor-glue.ko`, `imgsensor.ko`, `c2ps_perf_ioctl.ko`,
`mtk_c2ps.ko`.

[module ownership](module-ownership.tsv), [function parity](function-parity.tsv),
[data parity](data-parity.tsv), [stock modules](stock-modules.tsv),
[DT nodes](dt-nodes.tsv), [imports](imports.tsv), [exports](exports.tsv).

## Pack synchronization

Use the established `promote-to-done.py` / `sync-done-pack.py` utilities. After each sync,
run `python3 scripts/relocate-pack-links.py <canonical CAMERA-ISP-KERNEL directory>` from
this package (or the copied pack) to adapt Markdown links to the utilities' `notes/` layout.
It refreshes only adapted camera manifest rows; generated indexes/provenance are untouched.
`--check` verifies that no further adaptation is necessary.

## Boundary

This DONE status is deliberately narrow. It does **not** claim source for proprietary
CCU/ISP firmware, CameraProvider/HAL, 3A, tuning, calibration interpretation or image
quality algorithms; `CAMERA-HAL-ISP` remains PARTIAL. It also does not claim on-device
probe or streaming: runtime acceptance is still required.
