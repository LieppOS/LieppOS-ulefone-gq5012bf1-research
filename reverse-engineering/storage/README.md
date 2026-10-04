# GQ5012BF1 storage stack: static reverse engineering

Offline and static only. No adb, no device writes, and no access to RPMB contents or keys. Existing read-only captures were used.

## Result

Every shipped vendor storage kernel module rebuilds **byte-identical to stock except `.note.gnu.build-id`**. That covers functions, data, imports with CRCs, exports with CRCs, KCFI, relocations, modinfo and symtab, and two clean rebuilds are file-identical (B1==B2).

| group | module | functions | data | GQ5012BF1 delta |
|---|---|---|---|---|
| UFS | `ufs-mediatek-mod.ko` | 98/98 | 69/69 | none (MTK ACK header layout only) |
| UFS | `ufs-mediatek-dbg.ko` | 32/32 | 31/31 | +69 source lines (layout) |
| UFS | `phy-mtk-ufs.ko` | 11/11 | 19/19 | none |
| RPMB | `rpmb.ko` | 18/18 | 23/23 | none |
| RPMB | `rpmb-mtk.ko` | 17/17 | 16/16 | **TrustKernel raw-frame ioctls 10–14, Trustonic/netlink off** |
| SD/MMC | `mtk-mmc.ko` | 59/59 | 71/71 | none (board deltas in DT) |
| SD/MMC | `mtk-mmc-dbg.ko` | 26/26 | 33/33 | none |
| SD/MMC | `cqhci.ko` | 23/23 | 21/21 | none |
| SD/MMC | `mtk-wp.ko` | 4/4 | 24/24 | none |
| I/O trace | `blocktag.ko` | 88/88 | 79/79 | none |
| total | 10 modules | **376/376** | **386/386** | |

The source base is MTK ALPS MT6878 `5e415e059253` (2025-02-25), the same snapshot proven for `mediatek-drm.ko`. Generic GKI modules (`zram`, `zsmalloc`) and built-in GKI storage code (ufshcd, MMC core, blk-crypto, fscrypt, DM, filesystems) belong to the proven GKI 12901745 binary and were not rebuilt.

## Map

| topic | document |
|---|---|
| module inventory (sha256, vermagic, deps, ABI, parity, role) | [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv), [`kernel/source-map.tsv`](kernel/source-map.tsv), [`kernel/parity/full-module-proof.txt`](kernel/parity/full-module-proof.txt) |
| hardware topology (UFS host/PHY/device/LUs/RPMB, MSDC) | [`hardware/topology.md`](hardware/topology.md), [`hardware/live-dt-storage-nodes.txt`](hardware/live-dt-storage-nodes.txt) |
| partition / super / fstab map | [`hardware/partition-map.md`](hardware/partition-map.md) |
| UFS lineage, DT contract, PM, features, health | [`ufs/`](ufs/) |
| microSD | [`microsd/`](microsd/) |
| inline crypto and FBE boundary | [`crypto/`](crypto/) |
| RPMB transport and boundary | [`rpmb/boundary.md`](rpmb/boundary.md), [`binary-analysis/teed-rpmb-ioctls.md`](binary-analysis/teed-rpmb-ioctls.md) |
| OTA / boot control / DM | [`ab-ota/`](ab-ota/) |
| filesystems | [`kernel/filesystems.md`](kernel/filesystems.md) |
| board deltas | [`yft-storage-deltas.md`](yft-storage-deltas.md) |
| reproduction | [`reconstruction/`](reconstruction/), [`scripts/`](scripts/) |

## Reproduce

```
# tree = git archive of nt6878.git 5e415e059253 + reconstruction/kdm-patches/*
scripts/build-all.sh <tree> B1        # isolated M= builds + parity per module
```

Status and limits: [`STATUS.md`](STATUS.md).
