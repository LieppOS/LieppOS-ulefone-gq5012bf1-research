# Summary

`android.hardware.boot-service.mtk` is a **hybrid boot-control implementation**.

It does both of the following when `setActiveBootSlot(slot)` is called:

1. Updates the standard Android `bootloader_control` record in the block device backing the fstab mount point `/misc`.
2. Calls MediaTek `SetBootRegionSlot(slot)`, which switches the UFS boot LUN on this phone. The same function contains an eMMC `/dev/block/mmcblk0` fallback.

Therefore the answer is **C: hybrid**, not BCB-only and not boot-region-only.

The Android slot (`boot_a/b`, `vendor_a/b`, `system_a/b`, `vbmeta_a/b`) is still represented by standard BCB slot metadata and selected by the later bootloader/LK path. The UFS boot-LUN switch changes the physical boot region from which the earliest boot stage is fetched. It does not itself select the `boot_a` or `boot_b` GPT partition.

A particularly important correction is that the saved misc dump is **not all zero**. Its first displayed bytes were zero, but a valid 32-byte `bootloader_control` record exists at offset `0x800`:

```text
5f610000 42434142 01020000 97004600
00000000 00000000 00000000 efab3021
```

Decoded:

- suffix: `_a`
- magic: `0x42414342` (`BCAB` on disk)
- version: `1`
- number of slots: `2`
- slot A: priority `7`, tries `1`, successful `1`
- slot B: priority `6`, tries `4`, successful `0`
- stored CRC32: `0x2130abef`
- calculated CRC32 over the first 28 bytes: `0x2130abef` — valid

The recorded whole-image hash, `4ba901cf...`, also differs from the SHA-256 of a zero-filled 512 KiB image. The prior hex listing stopped before offset `0x800`.

Binary analyzed:

```text
/tmp/boot-service.mtk
SHA256 f247dde932626cbec40b0f599c3eca0bb90f32a07ef6ede108587a3dccf112c3
AArch64 Android 34 PIE, stripped
```

# Discovered Functions

## AIDL-facing methods

The public wrappers are before `0x9800`; they delegate to the real implementation helpers in the requested `0x9800`–`0x12000` region.

| AIDL operation | Wrapper | Real helper(s) | Reconstructed behavior |
|---|---:|---:|---|
| `getActiveBootSlot()` | `0x8c30–0x8c64` | `0xb090–0xb200` | Loads BCB and returns the slot with greatest priority, defaulting to current slot |
| `getCurrentSlot()` | `0x8c70–0x8ca4` | `0xa860–0xa868` | Returns cached current slot from `ro.boot.slot_suffix` |
| `getNumberSlots()` | `0x8cb0–0x8ce4` | `0xafe0–0xafe8` | Returns cached `boot_ctrl.nb_slot` |
| `getSnapshotMergeStatus()` | `0x8f10–0x8f44` | `0xb7f0–0xb84c` | Reads Virtual A/B merge status |
| `getSuffix(slot)` | `0x8f50–0x8fcc` | `0xb980–0xb9ac` | Returns suffix table entry (`_a`, `_b`, …) |
| `isSlotBootable(slot)` | `0x8fd0–0x9134` | `0xb500–0xb59c` | Tests `tries_remaining != 0` |
| `isSlotMarkedSuccessful(slot)` | `0x9140–0x92a4` | `0xb5a0–0xb640` | Tests `successful_boot && tries_remaining` |
| `markBootSuccessful()` | `0x92b0–0x932c` | `0xaff0–0xb090`, then `0x8cf0–0x8f10` | Marks current slot successful/bootable, then clears MTK AVB conversion flag |
| `setActiveBootSlot(slot)` | `0x9330–0x94b4` | `0xb200–0xb450`, then `0x9840–0x9cb4` | Updates BCB, then switches MTK boot region |
| `setSlotAsUnbootable(slot)` | `0x94c0–0x9628` | `0xb450–0xb500` | Clears successful and sets tries to zero |
| `setSnapshotMergeStatus(status)` | `0x9630–0x9674` | `0xb660–0xb668` → `0xb670–0xb7f0` | Writes Virtual A/B merge status for current slot |

`0x8cf0–0x8f10` is a MediaTek-specific helper, tentatively named `ClearAvbBootControlConvertFlag()`. It resolves the misc device, loads and CRC-validates the BCB, tests the byte at BCB offset `0x14`, clears it when it equals `1`, and saves the record. It is called after the normal `MarkBootSuccessful()` helper.

## Core helpers in `0x9800`–`0x12000`

| Address | Reconstructed name |
|---:|---|
| `0x9840–0x9cb4` | `SetBootRegionSlot(unsigned slot)` |
| `0x9cc0–0x9f20` | `BootloaderControlLECRC()` / CRC32 helper |
| `0x9f20–0xa14c` | `LoadBootloaderControl()` |
| `0xa150–0xa38c` | `UpdateAndSaveBootloaderControl()` |
| `0xa390–0xa854` | `InitDefaultBootloaderControl()` |
| `0xa860–0xa868` | `GetCurrentSlot()` |
| `0xa870–0xae28` | `BootControl::Init()` |
| `0xae30–0xafe0` | Virtual A/B misc-message initialization helper |
| `0xafe0–0xafe8` | `GetNumberSlots()` |
| `0xaff0–0xb090` | `MarkBootSuccessful()` |
| `0xb090–0xb200` | `GetActiveBootSlot()` |
| `0xb200–0xb450` | `SetActiveBootSlot()` BCB portion |
| `0xb450–0xb500` | `SetSlotAsUnbootable()` |
| `0xb500–0xb59c` | `IsSlotBootable()` |
| `0xb5a0–0xb640` | `IsSlotMarkedSuccessful()` |
| `0xb640–0xb654` | slot-number validation helper |
| `0xb660–0xb668` | current-slot thunk for merge-status setter |
| `0xb670–0xb7f0` | `SetSnapshotMergeStatus()` helper |
| `0xb7f0–0xb84c` | `GetSnapshotMergeStatus()` helper |
| `0xb980–0xb9ac` | `GetSuffix()` |
| `0xbaa0–0xbc4c` | find `/misc` entry in default fstab |
| `0xbe90–0xbf44` | resolve/wait for bootloader-message block device |
| `0xc900–0xecfc` | linked fs_mgr/fstab parser (contains `slotselect_other` XREF; not an IBootControl method) |

The later large functions through `0x12000` are primarily statically linked fstab/fs_mgr support, not additional BootControl interface methods.

# Decompiled Logic

## Initialization

Approximate reconstruction of `0xa870`:

```cpp
bool BootControl::Init() {
    suffix = GetProperty("ro.boot.slot_suffix", "");
    if (suffix.empty()) return false;
    current_slot_ = SlotSuffixToIndex(suffix);  // _a -> 0, _b -> 1

    misc_device_ = get_bootloader_message_blk_device();
    if (misc_device_.empty()) return false;

    bootloader_control bc;
    if (!LoadBootloaderControl(misc_device_, &bc)) return false;

    if (bc.crc32_le != CRC32(bc[0..27])) {
        InitDefaultBootloaderControl(this, &bc);
        UpdateAndSaveBootloaderControl(misc_device_, &bc);
    }

    InitMiscVirtualAbMessageIfNeeded();
    num_slots_ = bc.nb_slot;
    return true;
}
```

`/misc` is a **fstab mount-point lookup**, not a hard-coded assumption that the device path is literally `/dev/block/by-name/misc`. On this repository's stock fstab it resolves to:

```text
/dev/block/by-name/misc /misc emmc defaults defaults
```

## BCB I/O

`0x9f20` and `0xa150` show the exact storage contract:

```cpp
bool LoadBootloaderControl(path, bootloader_control* bc) {
    fd = open(path, O_RDONLY);
    lseek(fd, 0x800, SEEK_SET);
    return ReadFully(fd, bc, 0x20);
}

bool UpdateAndSaveBootloaderControl(path, bootloader_control* bc) {
    bc->crc32_le = CRC32(bc, 0x1c);
    fd = open(path, O_WRONLY | O_SYNC);
    lseek(fd, 0x800, SEEK_SET);
    return WriteFully(fd, bc, 0x20);
}
```

This is the standard 32-byte Android `bootloader_control` record at offset 2048.

## `getActiveBootSlot()`

`0xb090`:

```cpp
unsigned GetActiveBootSlot() {
    bootloader_control bc;
    if (!LoadBootloaderControl(misc_device_, &bc)) return 0;

    unsigned active = current_slot_;
    unsigned max_priority = bc.slot_info[current_slot_].priority;
    for (unsigned i = 0; i < num_slots_; ++i) {
        if (bc.slot_info[i].priority > max_priority) {
            max_priority = bc.slot_info[i].priority;
            active = i;
        }
    }
    return active;
}
```

With the captured BCB, this returns slot `0` (`_a`): A priority `7` is greater than B priority `6`.

## `setActiveBootSlot()`

The AIDL wrapper at `0x9330` makes the hybrid behavior explicit:

```cpp
if (!IsValidSlot(slot))
    return service_error(INVALID_SLOT);
if (!SetActiveBootSlotBCB(slot))
    return service_error(COMMAND_FAILED);
if (!SetBootRegionSlot(slot))
    return service_error(COMMAND_FAILED);
return ok();
```

The BCB helper at `0xb200` implements standard Android semantics:

```cpp
for (i = 0; i < num_slots_; ++i) {
    if (i != slot && bc.slot_info[i].priority >= 15)
        bc.slot_info[i].priority = 14;
}
bc.slot_info[slot].priority = 15;
bc.slot_info[slot].tries_remaining = 6;
if (slot != current_slot_)
    bc.slot_info[slot].verity_corrupted = 0;
// successful_boot is deliberately not changed here.
save_with_new_crc(bc);
```

Only after that write succeeds does it call `SetBootRegionSlot(slot)`.

## `markBootSuccessful()`

`0xaff0` sets, for `current_slot_`:

```cpp
successful_boot = 1;
tries_remaining = 1;
save_with_new_crc();
```

The AIDL wrapper then calls the MTK conversion-flag clearer at `0x8cf0`.

## Bootability queries

`0xb500`:

```cpp
return valid(slot) && load_bcb() &&
       bc.slot_info[slot].tries_remaining != 0;
```

`0xb5a0`:

```cpp
return valid(slot) && load_bcb() &&
       bc.slot_info[slot].successful_boot != 0 &&
       bc.slot_info[slot].tries_remaining != 0;
```

`0xafe0` returns cached `num_slots_`; the captured BCB contains `nb_slot = 2`.

# Slot Selection Mechanism

## Logical Android slot

The logical slot state is standard BCB metadata in misc:

- current running slot comes from `ro.boot.slot_suffix`;
- next active slot is derived from BCB priorities;
- bootability is `tries_remaining != 0`;
- success is `successful_boot && tries_remaining`;
- setters rewrite the 32-byte record and CRC at misc offset `0x800`.

This metadata is what LK/Android bootloader code is expected to consume to choose suffixed GPT/logical partitions. Fastboot not exposing `current-slot` does not mean the device lacks Android A/B metadata; it means this MediaTek fastboot implementation does not expose the normal userspace-facing variable.

## Physical boot region

`0x9840` maps logical slots as follows:

```text
slot 0 (_a) -> boot-region value 1
slot 1 (_b) -> boot-region value 2
```

It first attempts the UFS path:

```cpp
ioctrl_w_attr("/dev/ufs-bsg0", 0, 0, 0, slot + 1);
```

Attribute index zero in `libmtk_bsg.so` is `bBootLunEn`, so this selects UFS boot LUN A or B. If that call returns a negative result, the function falls back to eMMC.

The device evidence elsewhere in the repository identifies UFS 3.10 storage, so `/dev/ufs-bsg0` is the applicable path on this Ulefone. The eMMC code is a compatibility fallback compiled into the same service.

### eMMC fallback

The fallback opens `/dev/block/mmcblk0` read/write and sends `MMC_IOC_CMD` (`0xc048b300`):

1. Read the 512-byte EXT_CSD using MMC command 8.
2. Inspect `EXT_CSD[179]` (`PARTITION_CONFIG`), bits 5:3 (`BOOT_PARTITION_ENABLE`).
3. If needed, replace those bits with `1` for slot A or `2` for slot B.
4. Issue MMC command 6 (`MMC_SWITCH`) to write the updated byte.

This is the code producing:

- `ioctl error, mmc_read_extcsd fail`
- `ioctl error, mmc_switch_bootpart fail`
- `Could not read EXT_CSD`
- `Could not switch boot part`

## Interpretation

The slot number is not merely a physical eMMC/UFS boot-region number. It is an Android logical slot index with a coupled physical boot-region operation:

```text
setActiveBootSlot(0 or 1)
        |
        +-- update misc BCB priority/tries/CRC
        |
        +-- set UFS bBootLunEn to 1 or 2
              (or eMMC EXT_CSD PARTITION_CONFIG fallback)
```

The physical UFS boot LUN supplies the early bootloader/preloader stage. LK then performs the Android slot-aware selection of `boot_a/b`, `vendor_a/b`, `vbmeta_a/b`, and the slot-specific logical partitions. The service binary proves the two state changes are intentionally coupled; it does not by itself expose the exact LK decision tree.

The repository also records that the two captured UFS preloader LUs are byte-identical. Thus switching UFS boot LUNs currently changes the physical boot source/redundancy copy, not the Android payload contents by itself. The BCB/LK path remains necessary to choose A versus B Android partitions.

# Evidence

## String XREFs

| String | String VA | Code XREF | Containing function |
|---|---:|---:|---|
| `setActiveBootSlot SetBootRegionSlot ` | `0x47a6` | `0x98d0` | `0x9840–0x9cb4` |
| `/dev/ufs-bsg0` | `0x457e` | `0x9908` | `SetBootRegionSlot` |
| `/dev/block/mmcblk0` | `0x405b` | `0x9928` | `SetBootRegionSlot` |
| `ioctl error, mmc_switch_bootpart fail` | `0x43f7` | `0x9c94` | `SetBootRegionSlot` |
| `ro.boot.slot_suffix` | `0x4724` | `0xa8b0` | `BootControl::Init` |
| `Failed to load bootloader control block` | `0x4694` | `0xabf4` | `BootControl::Init` |
| `Invalid boot control found...` | `0x4a94` | `0xad94` | `BootControl::Init` |
| `/misc` | `0x4ae2` | `0xbb54` | default-fstab lookup |
| `slotselect_other` | `0x408c` | `0xd7a4` | generic fstab parser, not a BootControl method |

There are additional XREFs to `Could not find bootloader message block device` and `Failed to load bootloader control block` in the MediaTek conversion-flag helper at `0x8cf0`.

## Call-chain evidence

The decisive `setActiveBootSlot` call chain is:

```text
0x9330 AIDL setActiveBootSlot
  -> 0xb640 validate slot
  -> 0xb200 update standard BCB in misc
  -> 0x9840 SetBootRegionSlot
       -> ioctrl_w_attr("/dev/ufs-bsg0", ..., slot + 1)
       -> on failure only: open("/dev/block/mmcblk0", O_RDWR)
          and MMC_IOC_CMD read/switch operations
```

The decisive BCB I/O evidence is:

- `0x9f88`: seek to `0x800`;
- `0x9fa4`: read `0x20` bytes;
- `0xa1c8`: seek to `0x800`;
- `0xa1e4`: write `0x20` bytes;
- `0xa180`: calculate CRC, stored at BCB offset `0x1c`.

## Captured misc evidence

`/tmp/misc.img` matches the hash recorded in `misc-partition-dump.txt` and contains the valid BCB shown in the Summary. Its first non-zero byte is at `0x800`, exactly where the disassembled service seeks.

The stock fstab confirms that `/misc` resolves to `/dev/block/by-name/misc`, so on this image the service and the captured dump refer to the same partition.

# Remaining Unknowns

1. **Exact LK implementation:** this service proves what state Android writes, but LK/preloader binaries must be analyzed separately to prove their exact precedence rules when BCB and boot-LUN state disagree.
2. **Boot-LUN failure handling:** the service writes BCB first and switches the boot region second. If boot-region switching fails, it returns a command failure but does not roll back the already-written BCB.
3. **Meaning of MTK BCB byte `0x14`:** behavior and log text identify it as an `avb boot control convert flag`, but the vendor structure declaration is not present.
4. **Why fastboot hides standard A/B variables:** this is a bootloader/fastboot policy issue, not evidence against A/B. It requires LK/fastboot analysis.
5. **Live UFS `bBootLunEn` value:** the binary shows how it is changed, but no live attribute read was captured here.
6. **Physical-region usefulness on this unit:** the captured UFS preloader LUs are reported byte-identical, so the practical distinction between LUN 1 and LUN 2 may currently be redundancy only.
