# OTA / update_engine storage path (static)

## What the stock device uses (proven by stock props, init and existing lpdump)

| property / artifact | value | meaning |
|---|---|---|
| `ro.build.ab_update` | true | A/B (`update_engine`, `update_verifier`, `snapuserd` init services present in `/system/etc/init`) |
| `ro.boot.dynamic_partitions` | true | logical partitions in `super` |
| `ro.virtual_ab.enabled` | true | **Virtual A/B** |
| `ro.virtual_ab.compression.enabled` / `.compression.xor.enabled` | true / true | **VABC** with XOR compression |
| `ro.virtual_ab.userspace.snapshots.enabled` | true | **userspace snapshots**: `snapuserd` + **dm-user**, not kernel dm-snapshot |
| `ro.virtual_ab.io_uring.enabled`, `.batch_writes`, `.compression.threads` | true | snapuserd I/O tuning |
| compression method / COW version | not set in stock props | Android defaults (unproven which; payload-dependent) |
| `ro.product.ab_ota_partitions` | `boot,product,system,system_ext,vendor` | build-time list (payload may contain more) |
| `super` metadata | v10.2, **3 metadata slots**, header flag `virtual_ab_device` | slot 2 is the VAB snapshot metadata slot |
| `super` size | 9 GiB, single block device | |
| COW location | **in `super` free space first, then `/data/gsi/ota/*.cow` images** (Android VAB rule; the `/data` side needs `/metadata/ota` state) | standard for VAB; no COW partition exists |
| snapshot state | `/metadata/ota/` (`snapshot-boot`, state files) | `/metadata` f2fs, first-stage mount |
| merge | `snapuserd` merge after boot, before `markBootSuccessful`. Merge status is kept by the boot HAL in the misc VAB message | |
| postinstall | `fstab.postinstall` mounts the other slot's `system` (`slotselect_other,logical`) | |
| AVB | `vbmeta_a/b`, `vbmeta_system_a/b`, `vbmeta_vendor_a/b`; `ro.boot.avb_version` 1.2, locked, `veritymode=enforcing` | dm-verity on all logical read-only partitions |
| current state (existing capture) | no snapshot present ("current no-snapshot state", OTA-AB-UPDATE component) | |

```text
OTA client (Ulefone/OEM APK, proprietary) ─► update_engine (AOSP) ─► libsnapshot
   ├─ super metadata slot (other) ← lp metadata write
   ├─ COW: super free space / /data/gsi/ota (VABC + XOR)
   ├─ /metadata/ota state
   ├─ boot/vendor_boot/init_boot/dtbo/vbmeta/firmware *_b: raw writes to sdc GPT partitions
   └─ IBootControl.setActiveBootSlot(other)   (BCB @ misc+0x800, UFS bBootLunEn)
reboot ─► first-stage init: snapuserd (dm-user) + dm-snapshot-merge-like view via dm-user
       ─► update_verifier (dm-verity check) ─► markBootSuccessful ─► snapuserd merge
```

## Kernel / storage support (GKI 12901745, built-in)

`CONFIG_BLK_DEV_DM`, `DM_SNAPSHOT`, `DM_USER`, `DM_VERITY` (+FEC), `DM_DEFAULT_KEY`, `DM_CRYPT`, `DM_BUFIO`, `DM_UEVENT`, `BLK_DEV_LOOP`. **No vendor kernel module participates in OTA storage.** The UFS-specific step is the GKI BSG `bBootLunEn` write done by the HAL.

## Out of scope

- OEM OTA server and APK (proprietary).
- Payload production and signing, and runtime validation (owned by the `OTA-AB-UPDATE` component, still PARTIAL).
