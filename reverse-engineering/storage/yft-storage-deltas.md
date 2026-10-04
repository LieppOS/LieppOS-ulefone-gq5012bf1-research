# YFT / Ulefone storage deltas (GQ5012BF1 vs MTK ALPS mt6878 reference)

The donor is MTK ALPS `5e415e059253` (NothingOSS mt6878 history) together with its `mt6878.dts` and `cust_mt6878_msdc.dtsi`. Every row is proven from stock binaries or the live DT.

| area | donor behaviour | GQ5012BF1 behaviour | evidence | source/config delta | confidence |
|---|---|---|---|---|---|
| RPMB TEE transport | `rpmb-mtk` talks to the Trustonic TA through DCI (`mc_*`) and generic netlink | Trustonic **off**, netlink **off**. New raw-frame ioctls 10–14 on `/dev/rpmb0` for TrustKernel `teed` (`{u32 blk_cnt; u32 rw_size; u8 *frames}`, ≤4096 B) | `rpmb-mtk.ko` 17/17 + all sections byte-exact after the patch; `teed` issues ioctls 0xa/0xb/0xc/0xd | [`reconstruction/kdm-patches/0002`](reconstruction/kdm-patches/) plus `CONFIG_TRUSTONIC_TEE_SUPPORT` unset for this module | **proven** |
| RPMB module dependency | `depends=ufs-mediatek-mod,rpmb` | `depends=ufs-mediatek-mod-ise,rpmb` (built against the iSE UFS module's symvers, but the non-iSE module is shipped; CRC identical) | stock modinfo; exact rebuild with the iSE symvers | build environment | **proven** |
| `ufs-mediatek-dbg.c` layout | — | +69 source lines before `ufs_mtk_eh_abort` (text unknown, no code change) | `__LINE__` immediates 136/160/189 vs 67/91/120 | [`0001`](reconstruction/kdm-patches/) | **proven** (count); content not recoverable |
| ACK headers | Google ACK `ufshcd.h` | MTK ACK `ufshcd.h` (+`check_bus_status`/`dbg_dump` vops under `CONFIG_MTK_UFS_DEBUG_BUILD`) | `__bug_table` lines 1338/1328 vs 1333/1323 | build header (not a board delta; MTK kernel tree) | **proven** |
| UFS feature pack | `CONFIG_UFSFEATURE`/`UFSHID` objects available in KDM | not linked into `ufs-mediatek-mod` | stock symbol set; exact rebuild without them | Kconfig (board defconfig) | **proven** |
| SD card-detect | `cd-gpios = <&pio 14 GPIO_ACTIVE_LOW>` | `<&pio 14 0>` (**active-high**) | live DT | board DT | **proven** |
| SD VMMC rail | `mt6369_vmch_eint_high` | `mt6369_vmch_eint_low` | live DT | board DT | **proven** |
| UFS DT node | — | identical to donor (5 vendor booleans, no clk-scaling clocks) | live DT | none | **proven** |
| eMMC MSDC0 | reference enables it (`cust_mt6878_msdc.dtsi` `&mmc0 { status = "okay"; non-removable; … }`) | `status = "disabled"` (UFS-only board; `cqhci`/`mtk-wp`/eMMC RPMB paths inert) | live DT | board DT | **proven** |
| Storage device | — | Micron UFS 3.1 `MT512GBCAV8U31` FW `0108`; HPB-capable LU2, LU-dedicated WB; RPMB 16 MiB, regions 0/1/2 | PL/LK log | hardware | **proven** (existing capture) |
| OTA | AOSP VABC | VABC + XOR + userspace snapshots + io_uring/batch writes; `ab_ota_partitions=boot,product,system,system_ext,vendor` | stock props | product config | **proven** |
| fstab | MTK `fstab.mt6878` template | userdata `fileencryption=…:v2+inlinecrypt_optimized`; `fstab.emmc` variant without `inlinecrypt_optimized` also shipped | stock vendor | product config | **proven** |
| UFS timing/power, MSDC host code, CQHCI, blocktag, mtk-wp, phy | — | **no delta** (byte-exact ALPS) | parity | — | **proven** |
