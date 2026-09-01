# Slot-B ROM / Kernel Development Investigation

Device: Ulefone Armor 29 Pro (`GQ5012BF1`)  
Investigation mode: read-only on-device; no partition was flashed, erased, resized, or formatted  
Final device state: booted normally from slot A; A remains active and successful

## Evidence index

- `01-android-properties.txt` — Android identity and A/B properties
- `02-android-topology.txt` — by-name links, mapper devices, mounts
- `03-root-lp-dm-bootctl.txt` — `lpdump`, mapper, and boot-control evidence
- `04-focused-android.txt`, `06-android-followup.txt`, `11-final-android-facts.txt` — kernel, module, DSU, AVB, fstab, and slot facts
- `05-device-dump-manifest.txt`, `device-dumps/` — exact read-only boot-chain and `vendor_dlkm` captures
- `07-avbtool-info.txt` — offline AVB analysis
- `08-bootloader-fastboot.txt` — bootloader-fastboot evidence
- `09-fastbootd.txt` — userspace-fastboot evidence
- `10-boot-header-analysis.txt` — boot/vendor-boot headers and recovery ramdisk table
- `12-local-firmware-inventory.txt` — local stock-firmware search
- `EVIDENCE-SHA256SUMS.txt` — hashes of the evidence files

## Executive findings

1. Virtual A/B is enabled and compressed userspace snapshots are supported:
   - `ro.virtual_ab.enabled=true`
   - `ro.virtual_ab.compression.enabled=true`
   - `ro.virtual_ab.userspace.snapshots.enabled=true`
   - `ro.boot.dynamic_partitions=true`
2. No OTA snapshot or merge is active. `bootctl get-snapshot-merge-status` and `lpdump` both report `none`; `lpdump` reports no active COW/snapuserd mapping.
3. Slot A is active and successful. Slot B is bootable but not marked successful:
   - A: bootable=yes, successful=yes, retry count=1
   - B: bootable=yes, successful=no, retry count=2
4. Bootloader fastboot reports `unlocked=yes` and `secure=no`. Android's `ro.boot.vbmeta.device_state=locked` and `verifiedbootstate=green` conflict with this and should not be treated as authoritative; the active GSI appears to spoof or normalize those properties.
5. `boot`, `vendor_boot`, `init_boot`, `dtbo`, `vbmeta`, `vbmeta_system`, and `vbmeta_vendor` have distinct physical A/B block devices.
6. There is no standalone recovery partition. Recovery is a type-2 vendor ramdisk inside each `vendor_boot` image.
7. Dynamic partitions are stored in one shared, non-slotted 9 GiB `super` partition, but every discovered A/B logical payload currently has separate, non-overlapping linear extents.
8. Slot B already contains a complete custom Android 15 ROM set (`lineage_armol`, userdebug/test-keys), not an empty or virtual placeholder.
9. A/B `vendor_dlkm` images are separate logical extents but currently byte-identical.
10. Only about 63.45 MiB of allocatable `super` space is presently free. A larger B ROM would require deleting/shrinking `scratch` or resizing groups/partitions, which increases risk to A.

## Current software identity

The stock/vendor base is Android 15, while the running LieppOS GSI reports Android 16:

- Running OS: Android 16, LieppOS 23.2 GSI
- Vendor fingerprint: Ulefone Android 15 release build
- First API level: 35
- Treble: enabled
- ABI: arm64-v8a
- Kernel: `6.1.115-android14-11-g6b18f0b574ab-ab12901745`
- Fastboot product/platform: `k6878v1_64`
- MediaTek platform files and modules consistently identify MT6878; `ro.soc.model` reports `MT8873`, so that single property should not replace the platform evidence.

## Physical partition topology

### Relevant independent physical A/B partitions

| Partition | A target | B target | Size each | Independent storage? |
|---|---|---|---:|---|
| `boot` | `/dev/block/sdc36` | `/dev/block/sdc65` | 64 MiB | Yes |
| `vendor_boot` | `/dev/block/sdc37` | `/dev/block/sdc66` | 64 MiB | Yes |
| `init_boot` | `/dev/block/sdc38` | `/dev/block/sdc67` | 8 MiB | Yes |
| `dtbo` | `/dev/block/sdc39` | `/dev/block/sdc71` | 8 MiB | Yes |
| `vbmeta` | `/dev/block/sdc10` | `/dev/block/sdc13` | 8 MiB | Yes |
| `vbmeta_system` | `/dev/block/sdc11` | `/dev/block/sdc14` | 8 MiB | Yes |
| `vbmeta_vendor` | `/dev/block/sdc12` | `/dev/block/sdc15` | 8 MiB | Yes |
| `recovery` | absent | absent | — | Stored inside each `vendor_boot` |

The device also has distinct A/B physical pairs for `apusys`, `ccu`, `connsys_bt`, `connsys_gnss`, `connsys_wifi`, `dpm`, `gpueb`, `gz`, `lk`, `logo`, `mcf_ota`, `mcupm`, `modem`, `pi_img`, `pvmfw`, `scp`, `spmfw`, `sspm`, `tee`, and `vcp`. These are outside the normal ROM/kernel test set and should not be modified.

### Shared/non-slotted physical state

`super`, `metadata`, `userdata`, `persist`, `misc`, `nvcfg`, `nvdata`, `nvram`, `protect1`, `protect2`, `frp`, `proinfo`, `seccfg`, and other calibration/security partitions are non-slotted.

## Dynamic partition topology

Both `lpdump --slot 0` and `lpdump --slot 1` returned the same current metadata layout. The payload extents below are disjoint even though they share `/dev/block/sdc75` (`super`). All discovered logical filesystems are EROFS.

| Partition | Slot A size | Slot B size | A extents | B extents | Independent? | Notes |
|---|---:|---:|---|---|---|---|
| `odm_dlkm` | 0.33 MiB | 0.33 MiB | `2048..2727` | `18741656..18742335` | Payload: yes | Byte-identical A/B |
| `product` | 1769.85 MiB | 322.04 MiB | one range | `16438840..17098383` | Payload: yes | Different filesystem headers/content |
| `system` | 1905.64 MiB | 634.57 MiB | ten ranges | three ranges | Payload: yes | A is current GSI payload; B is custom Android 15 |
| `system_dlkm` | 7.12 MiB | 7.12 MiB | `6361088..6375679` | `18727064..18741655` | Payload: yes | Byte-identical header |
| `system_ext` | 626.59 MiB | 349.89 MiB | `6377472..7660735` | `15722256..16438839` | Payload: yes | Different A/B content |
| `vendor` | 1224.07 MiB | 778.53 MiB | two ranges | `17098384..18692815` | Payload: yes | Different A/B content |
| `vendor_dlkm` | 16.72 MiB | 16.72 MiB | `10170368..10204615` | `18692816..18727063` | Payload: yes | Exact-byte identical A/B |
| `odm` | absent | absent | — | — | N/A | Only `odm_dlkm` exists |

Allocation totals:

- `main_a`: 5550.33 MiB
- `main_b`: 2109.21 MiB
- `scratch`: 1491.00 MiB
- free versus logical-group maximum: approximately 63.45 MiB

Therefore B has real independent ROM payloads, not alias names or zero-length virtual placeholders. However, creating/resizing/deleting logical partitions changes shared `super` metadata and can affect both slots.

## Fastboot versus fastbootd

### Bootloader fastboot

- `is-userspace=no`
- current slot A, slot count 2
- bootloader unlocked and non-secure
- proves the physical boot-chain partitions are slotted
- reports A/B successful, bootable, and retry metadata
- sees `super` as a non-slotted raw partition

### Fastbootd

- `is-userspace=yes`
- recognizes every suffixed logical partition (`system_a`, `system_b`, `vendor_a`, `vendor_b`, etc.) as logical
- sees physical boot-chain partitions as non-logical
- reports `slot-count=0` and an empty current slot despite exposing suffixed A/B logical names

The fastbootd slot reporting is incomplete. Development commands must name explicit `_b` targets; unsuffixed `system`, `vendor`, or `product` targets are unsafe because fastbootd does not provide a reliable current-slot value.

## Boot-chain and AVB comparison

| Image pair | A/B result | Important evidence |
|---|---|---|
| `boot_a` / `boot_b` | Exact-byte identical | Same kernel and signed boot hash |
| `dtbo_a` / `dtbo_b` | Exact-byte identical | Same DTBO hash |
| `vendor_boot_a` / `vendor_boot_b` | Different | A includes a 33.58 MiB recovery ramdisk; B has a 4.71 MiB recovery ramdisk |
| `init_boot_a` / `init_boot_b` | Different | A has a 2.56 MiB LZ4 ramdisk; B has a 2.34 MiB gzip ramdisk and `lineage_armol` fingerprint |
| `vbmeta_a` / `vbmeta_b` | Different | A flags=3; B flags=0 and has a coherent custom chain |
| `vbmeta_system_a` / `_b` | Different | A stock-key descriptor; B custom Lineage system descriptor |
| `vbmeta_vendor_a` / `_b` | Different | A stock-key descriptor; B custom Lineage vendor descriptor |

`vendor_boot_a` and `vendor_boot_b` both contain independent recovery entries. This proves that modifying `vendor_boot_b` does not directly overwrite A's known-good recovery image.

Slot B's AVB chain is internally coherent:

- `vbmeta_b` chains to B's custom `vbmeta_system` and `vbmeta_vendor` keys.
- Its descriptors match the current B `init_boot`, stock-derived `vendor_boot`, common `dtbo`, `vendor_dlkm`, and other B dynamic payloads.
- All inspected image rollback indexes are zero.
- B is marked bootable by the boot-control HAL and bootloader, but it has not been live-boot-tested during this read-only investigation.

Slot A's top-level `vbmeta_a` has flags `3` (verification and hashtree disabled), explaining why its active GSI payload can differ from stale stock descriptors. A is currently known-good, so its AVB and boot-chain files must be treated as untouchable.

## Kernel-development suitability

| Experiment | B independent? | A directly protected? | Recovery method | Risk |
|---|---|---|---|---|
| Kernel in `boot_b` | Yes, physical | Yes | Re-enter bootloader and reactivate A; restore captured `boot_b` | YELLOW |
| Boot ramdisk in `init_boot_b` | Yes, physical | Yes | Restore captured `init_boot_b`; return to A | YELLOW |
| `vendor_boot_b` / recovery | Yes, physical | Yes | Restore captured image; A keeps its separate recovery | YELLOW |
| `dtbo_b` | Yes, physical | Yes | Restore captured `dtbo_b`; return to A | YELLOW |
| B bootconfig | Yes, as part of B boot images | Yes | Restore the corresponding B image | YELLOW |
| `vbmeta_b` chain | Yes, physical | Mostly | Restore all captured B vbmeta images; return to A | ORANGE |
| Custom `vendor_dlkm_b` | Separate logical extent | Yes at payload level | Restore captured B logical image in fastbootd | ORANGE |

A boot-chain-only experiment is the safest starting point. A custom kernel must preserve the MediaTek/GKI module ABI expected by the vendor modules.

## `vendor_dlkm` result

- logical dynamic partition inside shared `super`
- explicit A/B suffixes
- separate, non-overlapping linear extents
- device-mapper devices: `dm-12=vendor_dlkm_a`, `dm-13=vendor_dlkm_b`
- both map to the shared physical `super` block device
- EROFS
- 17,534,976 bytes allocated per slot; 17,125,376-byte AVB data image
- A/B images are currently exactly identical (`fce7acfb...aaa40297`)
- current A mounts `vendor_dlkm_a` read-only at `/vendor_dlkm`
- 195 modules are listed in `modules.load`
- representative module vermagic: `6.1.115-android14-11-g945dff7bc1bf ... modversions aarch64`
- current kernel is `6.1.115-android14-11-g6b18f0b574ab...`; the vendor modules are nevertheless loaded on A, proving the current combination works in practice

An experimental `boot_b` kernel can reuse the existing `vendor_dlkm_b` only if it preserves the required GKI/KMI symbols, module versioning, configuration, and MediaTek interfaces. A generic kernel build is not automatically compatible.

A custom `vendor_dlkm_b` can be isolated from A at the payload-extent level. It still requires a write through shared `super` metadata and a matching B-only AVB chain, so it is not as safe as changing physical `boot_b`.

## Shared-state risk

| State | Classification | Reason |
|---|---|---|
| `/data` / userdata | Shared and dangerous | One encrypted F2FS filesystem used by both slots; a faulty kernel/ROM can corrupt it |
| `metadata` | Shared and dangerous | Contains metadata-encryption/FBE state, OTA state, and GSI state |
| FBE keys | Shared and dangerous | Stored through shared metadata and hardware-backed services |
| filesystem journals/checkpoints | Shared and dangerous | Shared F2FS/ext4 state persists across slot changes |
| `persist` | Shared and dangerous | Non-slotted calibration/persistent state |
| `nvcfg`, `nvdata`, `nvram` | Shared and dangerous | Non-slotted modem and calibration state |
| Wi-Fi/Bluetooth calibration | Shared/unknown exact files | Must not be modified during slot development |
| thermal/sensor calibration | Shared/unknown exact files | Likely persistent vendor state; not isolated by boot slot |
| boot-control metadata | Shared but controlled | Stores active/bootable/success/retry state for both slots |
| snapshot metadata | Shared and dangerous | Located in shared metadata/super state; currently inactive |
| `super` metadata | Shared and dangerous | Corruption or incorrect resizing can lose both logical slot layouts |
| AVB rollback indexes | Unknown persistent scope | Images use zero; enforcement was not destructively tested |

## Recovery assessment

1. Bootloader fastboot can be entered and was successfully used read-only.
2. A remains current, bootable, and successful.
3. `boot_a`, `vendor_boot_a`, `init_boot_a`, `dtbo_a`, and all A vbmeta partitions have separate physical storage.
4. Boot retry/success metadata is implemented and visible. B currently has two retries and is not successful.
5. Automatic fallback after exhausting B retries is strongly indicated by the boot-control metadata but was not destructively tested.
6. `fastboot --set-active=a` was not executed because it writes persistent boot-control state. Device slot support, an unlocked bootloader, and the AIDL Boot Control HAL strongly indicate support; this remains an explicit first controlled recovery test.
7. An incorrect B-only boot-chain image should leave A's physical boot chain intact.
8. A whole-`super` flash, bad logical metadata update, FBE corruption, or rollback-index change could still compromise A or both slots.

## DSU assessment

- `gsid` exists and `/metadata/gsi` exists.
- `gsid.image_installed=0`, `ro.gsid.image_running=0`, and `gsi_tool status` reports `normal`.
- The framework does not advertise `android.software.dynamic_system` in `pm list features`.
- Current LieppOS is therefore a conventional GSI in `system_a`, not an active DSU session.

DSU availability is not proven and should not be part of the initial workflow. If enabled later, DSU supplies the system environment but uses the active slot's kernel and boot chain; an experimental B kernel would therefore need B active. That combined architecture remains a later test.

## Final classification table

| Area | Ready for B development? | Isolation from A | Risk | Evidence |
|---|---|---|---|---|
| Kernel / `boot_b` | Yes | Separate physical block device | YELLOW | by-name links, bootloader `has-slot:boot=yes`, 64 MiB dump |
| `vendor_boot_b` | Yes | Separate physical block device and recovery ramdisk | YELLOW | `/dev/block/sdc66`, parsed ramdisk table |
| `init_boot_b` | Yes | Separate physical block device | YELLOW | `/dev/block/sdc67`, distinct B image |
| `dtbo_b` | Yes | Separate physical block device | YELLOW | `/dev/block/sdc71`, bootloader slot evidence |
| `vbmeta_b` | Yes, coordinated writes only | Separate physical image; persistent rollback behavior still matters | ORANGE | independent vbmeta devices and coherent B AVB chain |
| `system` | Yes within current allocation | Separate logical extents; shared `super` metadata | ORANGE | `system_b` has 634.57 MiB and three disjoint extents |
| `vendor` | Yes within current allocation | Separate logical extents; shared `super` metadata | ORANGE | `vendor_b` has 778.53 MiB and its own AVB descriptor |
| `vendor_dlkm` | Yes, ABI-sensitive | Separate extent; shared `super` metadata | ORANGE | distinct extent and exact local backup |
| `product` | Yes within current allocation | Separate logical extent; shared `super` metadata | ORANGE | `product_b` has 322.04 MiB distinct content |
| `odm` | No partition present | N/A | YELLOW | only `odm_dlkm_a/b` exist |
| userdata | No isolation | Fully shared | RED | single encrypted `/data` device |
| `super` | Do not flash/resize as a whole | Shared physical container and metadata | RED | one non-slotted 9 GiB partition |
| Full independent ROM | Yes, with constraints | Boot chain and payload extents independent; persistent state/shared container remain | ORANGE | B already contains a complete custom ROM and coherent AVB set |

## Safest proposed development workflow

These commands were **not executed**. Obtain a verified stock firmware package and retain the captured current-B images before any write.

1. Never touch an A-suffixed target during normal development.
2. Start with one physical B component, preferably `boot_b`.
3. Always use explicit suffixed names:

```bash
# bootloader fastboot; proposed only
fastboot flash boot_b EXPERIMENTAL_BOOT_B.img

# fastbootd; proposed only and only if image fits current allocation
fastboot flash system_b SYSTEM_B.img
```

4. Do not use unsuffixed logical names in fastbootd.
5. Do not resize/delete logical partitions, groups, `scratch`, or `super` during initial development.
6. If a changed B image is AVB-covered, update only the corresponding B vbmeta chain. Never alter `vbmeta_a`.
7. Before selecting B, verify A is bootable/successful, all target B images have local hashes/backups, and bootloader fastboot is reachable.
8. The proposed first recovery-control test is selecting A while A is already active, then verifying slot metadata. Only after that should B be selected for a controlled boot.
9. If B fails, immediately return to bootloader and select A; do not erase userdata or flash `super`.

VERDICT: FULL_DEV_SLOT

Slot B has independent physical boot-chain partitions and fully allocated, non-overlapping logical ROM payloads for `system`, `system_ext`, `product`, `vendor`, `vendor_dlkm`, `system_dlkm`, and `odm_dlkm`. It already contains a coherent custom Android 15 ROM set. This satisfies the full-development-slot definition. It is not equivalent to a second completely separate phone: `super` metadata, userdata, metadata/FBE state, calibration data, boot-control state, and possible rollback state remain shared. B development is safe only with explicit `_b` targets, no `super` resizing, verified backups, and a tested return-to-A procedure.

```text
SAFE_TO_TEST_ON_B:
- boot_b kernel changes that preserve the required GKI/KMI ABI
- vendor_boot_b and its B-only recovery ramdisk
- init_boot_b
- dtbo_b
- coordinated vbmeta_b / vbmeta_system_b / vbmeta_vendor_b changes
- existing-size logical B images through fastbootd, after backups and AVB planning

DO_NOT_TOUCH_YET:
- boot_a, vendor_boot_a, init_boot_a, dtbo_a, or any A vbmeta image
- whole super partition
- dynamic partition resizing, group changes, or scratch deletion
- userdata, metadata, persist, nvcfg, nvdata, nvram, protect1, protect2
- rollback indexes, snapshot creation/merge, or OTA operations
- unsuffixed fastbootd partition names

SHARED_WITH_A:
- super physical container and logical metadata
- userdata and all user data
- metadata, FBE state, OTA/snapshot state, and GSI state
- persist and calibration/NVRAM state
- boot-control metadata
- hardware-backed security/rollback state

UNKNOWN / NEEDS_MORE_EVIDENCE:
- an actual successful B boot (not attempted read-only)
- runtime proof of fastboot --set-active=a and automatic fallback
- exact rollback-index enforcement behavior
- usable DSU support (framework feature is not advertised)
- a complete external stock firmware package for guaranteed restoration
- compatibility of any future experimental kernel with the MediaTek vendor module ABI
```
