# Storage-facing partition map (concise, read-only evidence)

This page summarises existing captures and does not duplicate the Slot-B research. Sources:

- `slot-b-investigation/03-root-lp-dm-bootctl.txt` and `06-android-followup.txt` (by-name links)
- `workspace/phase4-tkcore-island/phase3g/device-before/root-lpdump-slot{0,1}.txt` (lpdump)
- stock `vendor/etc/fstab.mt6878`
- `slot-b-investigation/untouched-b-early-boot-forensics/slot-b-write-preflight/android-a-device-mapper.txt` (mapper names)
- PL/LK UFS log (LU layout)

Nothing was written or remounted for this page.

## Physical layout (UFS, Micron MT512GBCAV8U31, 4 KiB LBA)

| SCSI disk | UFS LU | content |
|---|---|---|
| `sda` | LU0, `bBootLunID = 1` (Boot LU A) | preloader A |
| `sdb` | LU1, `bBootLunID = 2` (Boot LU B) | preloader B |
| `sdc` | LU2 (user, HPB-enabled LU, LU-dedicated WriteBooster) | GPT with 78 partitions (below) |
| `0:0:0:49476` | RPMB W-LU `0xC4` | 16 MiB, regions 0/1/2 = 15.75 MiB / 128 KiB / 128 KiB |

## `sdc` GPT (by-name, live)

| range | partitions |
|---|---|
| shared, no slot | `misc`(1) `vb`(2) `para`(3) `expdb`(4) `frp`(5) `nvcfg`(6) `nvdata`(7) `md_sec`(8) `persist`(9) `metadata`(16) `protect1`(17) `protect2`(18) `seccfg`(19) `otp`(20) `pstore`(21) `sec1`(46) `proinfo`(47) `nvram`(48) `boot_para`(49) `dram_para`(50) `super`(75) `userdata`(76) `mrdump`(77) `flashinfo`(78) |
| AVB A/B | `vbmeta_a/_system_a/_vendor_a` (10–12), `vbmeta_b/_system_b/_vendor_b` (13–15) |
| slot A firmware/boot | `modem_a`(22) `spmfw_a` `mcf_ota_a` `pi_img_a` `dpm_a` `scp_a` `ccu_a` `vcp_a` `sspm_a` `mcupm_a` `gpueb_a` `apusys_a` `gz_a` `lk_a`(35) `boot_a`(36) `vendor_boot_a`(37) `init_boot_a`(38) `dtbo_a`(39) `tee_a`(40) `connsys_bt_a` `connsys_wifi_a` `connsys_gnss_a` `pvmfw_a`(44) `logo_a`(45) |
| slot B firmware/boot | `modem_b`(51) … `lk_b`(64) `boot_b`(65) `vendor_boot_b`(66) `init_boot_b`(67) `connsys_*_b`(68–70) `dtbo_b`(71) `pvmfw_b`(72) `logo_b`(73) `tee_b`(74) |

`vendor_dlkm`, `system_dlkm` and `odm_dlkm` are **logical** partitions in `super`, not GPT partitions.

## `super` (lpdump, live, slot 0)

- Metadata version 10.2, size 1892 of max 65 536, **3 metadata slots**.
- Header flags `virtual_ab_device` plus bit 1.
- One block device of 9 663 676 416 bytes (9 GiB).
- Logical partitions, all `readonly`: `system_a/_b`, `system_ext_a/_b`, `vendor_a/_b`, `product_a/_b`, `vendor_dlkm_a/_b`, `system_dlkm_a/_b`, `odm_dlkm_a/_b`, plus `scratch` (attributes none; an adb-remount/overlayfs scratch partition, **not stock-shipped behaviour**).

## Mounts that matter for storage (stock fstab)

| mount | fs | device | flags of interest |
|---|---|---|---|
| `/system`, `/system_ext`, `/vendor`, `/product`, `*_dlkm` | erofs (ext4 fallback line) | logical | `slotselect`, `avb[=vbmeta_system]`, `first_stage_mount` |
| `/metadata` | f2fs | `by-name/metadata` | `formattable`, `first_stage_mount`; holds `vold/metadata_encryption` keys dir |
| `/data` | f2fs | `by-name/userdata`, through dm-default-key (`/dev/block/mapper/userdata` → `dm-57` live) | `inlinecrypt`, `checkpoint=fs`, `fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized`, `keydirectory=/metadata/vold/metadata_encryption`, `fsverity`, `reservedsize=128m` |
| `/mnt/vendor/{protect_f,protect_s,nvdata,nvcfg,persist}` | ext4 | by-name | factory/NV (read-only for research) |
| SD | auto | `/devices/platform/soc/11240000.mmc*` | `voldmanaged=sdcard1:auto`, `encryptable=userdata` (adoptable) |
| swap | zram | `/dev/block/zram0` | `zramsize=100%` (`fstab.enableswap`) |

`fstab.emmc` differs only in the userdata line (it has no `+inlinecrypt_optimized`) and in `lk1`-style raw entries. It is the eMMC variant and is not used on this UFS board.

Ownership and risk for each partition is tracked by the workspace component `PARTITION-OWNERSHIP`, which is still PARTIAL.
