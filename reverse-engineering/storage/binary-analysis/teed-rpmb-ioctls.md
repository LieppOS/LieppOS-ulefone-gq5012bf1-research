# Stock `/vendor/bin/teed`: RPMB ioctl usage (static disassembly)

The binary is stock `partitions/vendor/bin/teed` (TrustKernel supplicant). It imports `ioctl@LIBC`, whose PLT stub is at `0x24b0`. Six call sites. The service line in stock init is `teed --tzdev /dev/tkcore_admin … --rpmbdev /dev/mmcblk0rpmb --rpmbdev /dev/rpmb0 …`:

| call site | request (`w1`) | context |
|---|---|---|
| `0x4750` | `0xc008b301` | tkcore driver ioctl (`_IOWR(0xb3, 1, 8)`) |
| `0x4850` | `0xc048b300` | tkcore driver ioctl (`_IOWR(0xb3, 0, 0x48)`) |
| `0x4998` | **`0xa` / `0xb` / `0xc`** (selected by request type 3 / 4 / 2; `blk_cnt` forced to 1 for types 3 and 2, caller count for 4) | `--rpmbdev /dev/rpmb0` UFS RPMB transport (`proprietary_rpmb_operations`). The arg is `{u32 blk_cnt @sp+8; u32; u8 *frames @sp+0x10}`; the first 0x200-byte frame is copied into the request buffer before the call |
| `0x4a04` | **`0xd`** | `/dev/rpmb0` get reliable-write size. Reads `param+4` (`rw_size`) |
| `0x56f4` / `0x6590` | `0xc01874a5` / `0xc01874a7` | `--rpmbdev /dev/mmcblk0rpmb` eMMC path (`emmc_rpmb_operations`; this device node does not exist on this UFS board) |

Request type 1 (program key) is rejected by teed with `-EINVAL` before any ioctl. Kernel ioctl 14 is present but unused by this teed. These request numbers, the argument layout and the `blk_cnt` semantics match the exact reconstruction of `rpmb_ioctl_ufs` in stock `rpmb-mtk.ko`.
