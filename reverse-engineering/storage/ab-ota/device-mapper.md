# Device-mapper usage (GQ5012BF1)

All targets are GKI built-in (12901745 `.config`), and there is no vendor DM module. Evidence:

- existing read-only mapper listing `slot-b-investigation/untouched-b-early-boot-forensics/slot-b-write-preflight/android-a-device-mapper.txt` (`dm-0` … `dm-57`; target tables were not captured)
- stock fstab and props

| target | status | evidence / role |
|---|---|---|
| dm-linear | **ACTIVE** | `odm_dlkm_a/b`(dm-0/1), `product_a/b`(2/3), `system_a/b`(4/5), `system_dlkm_a/b`(6/7), `system_ext_a/b`(8/9), `vendor_a/b`(10/11), `vendor_dlkm_a/b`(12/13), `scratch`(14) are logical extents of `super`. Both slots are mapped by first-stage init |
| dm-verity | **ACTIVE** | fstab `avb`/`avb=vbmeta_system` on every logical read-only partition and the ~35 APEX loop devices (`dm-17`…`dm-56`, apexd verity). `ro.boot.veritymode=enforcing` |
| dm-default-key | **ACTIVE (FBE metadata encryption)** | `/dev/block/mapper/userdata → dm-57`; `keydirectory=/metadata/vold/metadata_encryption`; `ro.crypto.metadata.enabled=true` |
| dm-crypt | **NOT USED** | FBE device (`ro.crypto.type=file`). Built in, but no mapping |
| dm-snapshot | **OTA-ONLY** | Virtual A/B; with userspace snapshots enabled, the merge path uses dm-user |
| dm-user | **OTA-ONLY** | `ro.virtual_ab.userspace.snapshots.enabled=true` → `snapuserd` |
| dm-bow | **NOT BUILT** | `checkpoint=fs` (f2fs checkpoint), so dm-bow is not needed |

`scratch` is the adb-remount overlay partition. Its presence reflects development use of the captured unit and is not stock behaviour.
