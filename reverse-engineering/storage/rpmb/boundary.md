# RPMB transport and boundary (static; no RPMB content accessed)

## Kernel modules (A = stock, B = rebuild, debug-stripped)

| module | functions | data | imports | exports / CRCs | relocs | sections | source |
|---|---|---|---|---|---|---|---|
| `rpmb.ko` | **18/18** | 23/23 | 24/24 | 12/12 / 11 CRCs equal | 184/184 | 45/45 except build-id | ALPS `5e415e059253` `drivers/char/rpmb/core.c` only (`CONFIG_RPMB_INTF_DEV` off, so no `cdev.o`) |
| `rpmb-mtk.ko` | **17/17** | 16/16 | 46/46 | 2/2 / 1 CRC equal | 1378/1378 | 46/46 except build-id | ALPS `rpmb-mtk.c` + **GQ5012BF1 patch** [`0002`](../reconstruction/kdm-patches/) |
| `ufs-mediatek-mod.ko` (`ufs-mediatek-rpmb.o`) | part of 98/98 | | | `ufs_mtk_rpmb_get_raw_dev` | | | ALPS, unmodified |

The UFS provider (`ufs-mediatek-rpmb.c`):

- registers an `rpmb_dev` (`rpmb_dev_register`) for the RPMB W-LU, using SECURITY PROTOCOL IN/OUT (`ufs_mtk_rpmb_security_in/out`) with per-region `ufs_mtk_rpmb_cmd_seq`
- runs a purge timer (`ufs_mtk_rpmb_purge_timer_cb`)
- calls the `ufs_mtk_ise_rpmb_probe` dummy (non-iSE build)

## GQ5012BF1 delta in `rpmb-mtk` (proven byte-exact)

Stock `rpmb-mtk.ko` differs from every public MTK tree (NothingOSS mt6878 history, MiCode KDM 16 branches, 13 ALPS snapshots). The reconstruction proves:

1. **Trustonic disabled.** The stock module imports no `mc_*` symbols. It was built with `CONFIG_TRUSTONIC_TEE_SUPPORT` **unset**, and `rpmb_gp_execute_emmc` (which ALPS leaves outside the Trustonic guard) is compiled out with it. The shared `kout` has `=m`; this is a board build-config difference.
2. **Netlink off.** `__RPMB_KERNEL_NL_SUPPORT` is undefined, so the UFS helpers call `rpmb_cmd_req()` directly (the stock strings still mention `nl_rpmb_cmd_req`, which is only a message text).
3. **Multi-block.** `RPMB_MULTI_BLOCK_ACCESS 1`, `MAX_RPMB_TRANSFER_BLK 16`, `MAX_RPMB_REQUEST_SIZE 8192`, defined without the Trustonic `drrpmb_Api.h`.
4. **Raw-frame ioctl ABI for TrustKernel** (`rpmb_ioctl_ufs` on `/dev/rpmb0`). The names are reconstructed; the numbers, layout and limits are proven by both the stock kernel module and stock `/vendor/bin/teed`:

| ioctl `cmd` | kernel action | teed use (static disassembly) |
|---|---|---|
| 1 `RPMB_IOCTL_PROGRAM_KEY` | log only (ALPS) | — |
| 3 / 4 `RPMB_IOCTL_WRITE_DATA` / `READ_DATA` | ALPS keybytes/databytes path | — |
| **10** | `rpmb_req_write_data_ufs(frames, blk_cnt)`, copies 1 result frame back | JEDEC req type 3 (write), `blk_cnt = 1` |
| **11** | `rpmb_req_read_data_ufs(frames, blk_cnt)`, copies `blk_cnt` frames back | req type 4 (read), `blk_cnt = n` |
| **12** | `rpmb_req_get_wc_ufs(region 0, …, frame)`, copies frames back | req type 2 (get write counter) |
| **13** | `rpmb_get_rw_size()` into `param.rw_size` (u16 widened) | read at `param+4` |
| **14** | `rpmb_req_program_key_ufs(region 0, frame, 1)`, requires `blk_cnt == 1` | not issued (teed rejects req type 1) |

The user structure is `{ u32 blk_cnt; u32 rw_size; u8 __user *frames; }` (16 bytes). Limits: `blk_cnt * 512 ≤ 4096` (else `-EINVAL` and "rpmb buffer too large"), so frames are `kmalloc`'d. Before the switch, `blk_cnt` frames are always copied in.

5. The stock module depends on **`ufs-mediatek-mod-ise`**: its modinfo `depends=` names the iSE build of the UFS module, which provides `ufs_mtk_rpmb_get_raw_dev` with the same CRC. The shipped image contains only the non-iSE `ufs-mediatek-mod.ko`. Reproduced by building against symvers that attribute that export to `ufs-mediatek-mod-ise` ([`../reconstruction/build-config/README.md`](../reconstruction/build-config/README.md)).

## Consumers (user space / secure world; proprietary)

| consumer | device node | path | evidence |
|---|---|---|---|
| TrustKernel `teed` (`/vendor/bin/teed --rpmbdev /dev/mmcblk0rpmb --rpmbdev /dev/rpmb0`) | `/dev/rpmb0` (rpmb-mtk cdev, class `rpmb`) | raw frames → ioctls 10–13 → `rpmb_cmd_req` → UFS RPMB W-LU, region 0 | running in live process list (`u:r:tee:s0 teed`). tkcore log: "RPMB size is 16777216", "Reliable Write Sector Count is 64" |
| MTK GenieZone Trusty `mtk_storageproxyd -d /dev/trusty-ipc-dev1 -r /dev/0:0:0:49476` | UFS RPMB W-LU SCSI node `0:0:0:49476` (`0xC144`) | SG_IO / `send_ufs_rpmb_req` straight to the W-LU (does **not** use rpmb-mtk) | running (`mtk_storageproxyd`); `gz_*` modules loaded |
| `tlcrpmb_gp` | Trustonic TLC | unused (no Trustonic driver) | binary present only |
| eMMC path (`emmc_rpmb_*`, `mmc_rpmb_register`) | — | compiled in, unused (MSDC0 disabled) | |

Physical RPMB: 16 MiB W-LU, regions 0/1/2 = 15.75 MiB / 128 KiB / 128 KiB, region 3 = 0 (PL/LK log). Region 0 is the only one addressed by rpmb-mtk; which TEE owns regions 1/2 is not determined.
