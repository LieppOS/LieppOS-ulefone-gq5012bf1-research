# TKCore ↔ RPMB boundary

**Who requests RPMB:** only the TrustKernel OS (secure storage / anti-rollback inside TKCore
and TAs). The normal world never initiates RPMB for TKCore.

**Path (normal-world side, proven):**

1. Secure world returns RPC `CMD` (0xffff0005) whose `teesmc64_arg.cmd = TEE_RPC_RPMB_CMD
   (0x1000000A)` with exactly two params: `p0 MEMREF_INPUT` (request frames) and
   `p1 MEMREF_OUTPUT` (response frames), laid out contiguously in one shared buffer.
2. `tkcore_drv` `handle_rpmb_cmd` checks the shape (else `TEEC_ERROR_BAD_PARAMETERS`), builds a
   `tee_rpc_invoke {cmd=0x1000000A, res=NOT_IMPLEMENTED, nbr_bf=1, cmds[0]={buffer=p0.buf_ptr,
   size=p0.size+p1.size, type=BUFFER}}` and calls `tee_supp_cmd(tee, TEE_RPC_ICMD_INVOKE 0x1003,
   &inv, 0x88)` (tkcore.ko).
3. tkcore queues it on the supplicant mailbox; **teed** (`--tzdev /dev/tkcore_admin`) reads it,
   maps the buffer, and performs the frame exchange on `--rpmbdev /dev/rpmb0` (UFS, MediaTek
   `rpmb` char device, ioctls 0xa/0xb/0xc/0xd per `reverse-engineering/storage/binary-analysis/teed-rpmb-ioctls.md`),
   then writes the result back; `inv.res` becomes `arg->ret`.

So **teed mediates every RPMB access**; `tkcore_drv` only forwards frames, and the kernel UFS
RPMB driver (closed in STORAGE) only executes them. No RPMB key, counter or MAC is visible to or
computed by the kernel: the authentication key and HMAC verification stay in TKCore
(secure, proprietary).

**Correction flag for STORAGE (not edited here):** in `teed-rpmb-ioctls.md` the first two
rows (`0xc008b301`, `0xc048b300`, i.e. `_IOWR(0xb3,…)` = `MMC_IOC_MULTI_CMD` / `MMC_IOC_CMD`) are
the **eMMC** RPMB path (`/dev/mmcblk0rpmb`, opcode 18 / flags 0xb5 visible at teed `0x4708`),
and `0xc01874a5` / `0xc01874a7` (teed `main`, `0x56f4` / `0x6590`) are **tkcore**
`TEE_ALLOC_SHM_IOC` / `TEE_GET_FD_FOR_RPC_SHM_IOC` on `/dev/tkcore_admin` — the two labels are
swapped in that note. The UFS rows (0xa–0xd) are unaffected.
