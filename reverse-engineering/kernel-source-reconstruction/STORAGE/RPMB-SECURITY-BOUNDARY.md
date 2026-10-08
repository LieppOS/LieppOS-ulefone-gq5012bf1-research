# RPMB and trusted-world boundary

Scope of this certification: the **normal-world kernel transport** only (`rpmb.ko`,
`rpmb-mtk.ko`, the RPMB provider inside `ufs-mediatek-mod.ko`). Detailed transport/ioctl
analysis: `../../storage/rpmb/boundary.md`, `../../storage/binary-analysis/teed-rpmb-ioctls.md`.

**Not done, by rule:** no RPMB frame was read or written; no key, nonce, MAC or write counter was
handled; no authenticated operation was attempted; no secure-world binary or persistent security
state was modified; no device interaction of any kind.

## Layers

```
TA (TrustKernel, secure world) ── tkcore (SMC) ── teed (/vendor/bin, proprietary)
                                                      │ ioctl 10..13 on /dev/rpmb0
rpmb-mtk.ko  rpmb_fops_ufs ── rpmb_req_{write_data,read_data,get_wc}_ufs ── rpmb_cmd_req()
rpmb.ko      RPMB class core (rpmb_dev_register / rpmb_cmd_req / rpmb_get_rw_size)
ufs-mediatek-mod.ko  ufs-mediatek-rpmb.o: rpmb_dev for UFS W-LU 0xC4, SECURITY PROTOCOL IN/OUT
GKI ufshcd/scsi ── UFS device RPMB W-LU (16 MiB; regions 0/1/2 = 15.75 MiB / 128 KiB / 128 KiB)

GenieZone Trusty: mtk_storageproxyd -r /dev/0:0:0:49476 ── SG_IO to the W-LU directly
                  (does not use rpmb-mtk)
```

## Interfaces and what the kernel side does with them

| interface | normal-world role | secret material in the kernel? |
|---|---|---|
| `/dev/rpmb0` ioctls 10/11/12 (write/read/get-counter, raw 512-byte JEDEC frames incl. MAC/nonce) | pass-through: copies the frames in and out, issues the RPMB sequence | frames carry MACs computed by the TEE; the kernel never holds the key and does not compute or check MACs |
| ioctl 13 (reliable-write size) | returns `rpmb_get_rw_size()` | no |
| ioctl 14 (program key) | present in the stock module; `teed` never issues it (rejects request type 1) | key frame would pass through; not used |
| ioctls 1/3/4 (ALPS keybytes paths) | log/legacy | not used by teed |
| `atag,ufs` from `/chosen` | stored in `host->atag`; consumed only by the iSE variant (not shipped) | contains RPMB key **state**, not a key; untouched |
| eMMC RPMB (`mmc_rpmb_register`, `emmc_rpmb_*`) | compiled in, unused (MSDC0 disabled) | — |
| Trustonic path (`rpmb_gp_*`, `tlcrpmb_gp`) | compiled out (`CONFIG_TRUSTONIC_TEE_SUPPORT` unset for this board) | — |
| KeyMint / trusted storage | consumers of TA-side storage via `teed`; proprietary | outside scope |

## What the byte-exact reconstruction proves

* The ioctl numbers, argument layout `{u32 blk_cnt; u32 rw_size; u8 *frames}`, limits
  (`blk_cnt*512 ≤ 4096`), frame copying and region-0 addressing of stock `rpmb-mtk.ko` are
  exactly the reconstructed source (17/17 functions, 1378/1378 relocations).
* The ioctl constant names are reconstructed (not recovered); behaviour is proven.
* Which TEE owns RPMB regions 1 and 2 remains **UNKNOWN**.

## Rebuilt-module risk statement

Because the rebuilt modules are byte-identical to stock except the build ID, swapping them
cannot change RPMB protocol behaviour. A wrong `rpmb-mtk` would be the most dangerous storage
change: a malformed write could advance the write counter or corrupt TA anti-rollback data.
Any Slot B test must therefore be observe-only for RPMB (`EARLY-BOOT-DEPENDENCIES.md`).
