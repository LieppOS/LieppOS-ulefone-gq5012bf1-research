# Filesystem support versus actual partition format

Kernel support is the GKI 12901745 `.config`, all built-in. No vendor filesystem module ships, and the generic upstream code was not reconstructed.

| filesystem | kernel | used by (stock fstab / props) |
|---|---|---|
| erofs (+ZIP/LZ4) | `CONFIG_EROFS_FS=y`, `_ZIP=y` | `system`, `system_ext`, `vendor`, `product`, `vendor_dlkm`, `system_dlkm`, `odm_dlkm` (first fstab line for each; an ext4 fallback line also exists) |
| f2fs (+compression, security) | `CONFIG_F2FS_FS=y`, `_COMPRESSION=y` | `/data` (inlinecrypt, `checkpoint=fs`, fsverity, quota; compression **not** used: `vold.has_compress=0`), `/metadata` |
| ext4 (+POSIX ACL) | `CONFIG_EXT4_FS=y` | `/mnt/vendor/{protect_f,protect_s,nvdata,nvcfg,persist}`, `mcf_ota_a` (`/mnt/vendor/mdota`) |
| vfat / msdos | `CONFIG_VFAT_FS=y`, `MSDOS_FS=y` | SD (`auto`), USB OTG (`vfat`) |
| exfat | `CONFIG_EXFAT_FS=y` | SD (`auto`); exFAT on SD was proven in the OrangeFox recovery build (MICROSD evidence) |
| fuse (+BPF) | `CONFIG_FUSE_FS=y` | `/storage/emulated` (MediaProvider FUSE) |
| incfs | `CONFIG_INCREMENTAL_FS=y` | incremental APK installs |
| overlayfs | `CONFIG_OVERLAY_FS=y` | adb remount (scratch) only |
| fs-verity, unicode (casefold) | `CONFIG_FS_VERITY=y`, `CONFIG_UNICODE=y` | `/data` `fsverity`; casefolding for emulated storage |
| NTFS / btrfs | **not set** | SD cards formatted NTFS are not mountable by the kernel |
