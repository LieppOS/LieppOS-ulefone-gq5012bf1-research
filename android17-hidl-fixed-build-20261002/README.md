# Android 17 HIDL-fixed userspace build

Build result: SUCCESS

Command:
`m -j48 systemimage systemextimage productimage`

Ninja completed 46040 steps successfully.

8a3d844f35c6d4f5039878a7e72a65c664ded243b9e749d49390bc4118bc2030  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/system.img
4187b58a47ad36cd5b4e58f87c642ac4a73c617d241d796cdff53f451d41d84b  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/system_ext.img
e2130d8fda18ffe2cb2b94a16659acd28b160127175547afee4a876539b6135a  /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/product.img

## Slot-B capacity verification

Exact image sizes match the already-established Slot-B logical partition sizes byte-for-byte:

- system.img: 665391104 / system_b: 665391104
- system_ext.img: 366891008 / system_ext_b: 366891008
- product.img: 337686528 / product_b: 337686528

Result:

- SYSTEM_FITS=1
- SYSTEM_EXT_FITS=1
- PRODUCT_FITS=1
- no super resize required

## Post-HIDL offline validation

- Android 17 checkvintf: COMPATIBLE (exit 0)
- Tested exact newly built system/system_ext/product images
- Stock Ulefone vendor/ODM inputs retained
- HIDL allocator manifest successfully parsed from system_ext
- secilc exit: 255

## Corrected split-SELinux verification

- stock vendor hash gate: PASS
- stock plat_pub_versioned.cil: bd4c019a2f2faeaf7b682be718e416f83ca22c6ff5e0754280693ae212bcd352
- stock vendor_sepolicy.cil: 282b405b13cdb830999a9f932dbbd78cf6adbe7c15a11c769f548c8d65fb04fd
- vendor policy mapping version: 34.0
- secilc exit: 0
- SELinux split-policy result: PASS

## HIDL-fixed Android 17 Slot-B write completed

The HIDL-fixed Android 17 userspace image set was successfully written to
the existing inactive Slot-B logical extents through temporary writable
device-mapper aliases.

Verified final hashes:

- system_b: 8a3d844f35c6d4f5039878a7e72a65c664ded243b9e749d49390bc4118bc2030
- system_ext_b: 4187b58a47ad36cd5b4e58f87c642ac4a73c617d241d796cdff53f451d41d84b
- product_b: e2130d8fda18ffe2cb2b94a16659acd28b160127175547afee4a876539b6135a

The first system_b verification raced the still-running remote dd process.
A later read after dd completion matched the expected system_b hash exactly.
The completion procedure therefore waits for remote dd termination before
syncing and hashing subsequent partitions.

Slot A remained active throughout and the metadata-encryption key invariant
remained unchanged.

## Android 17 generic init_boot correction

The first successfully generated Android 17 init_boot image had a valid
8 MiB header-v4 generic ramdisk but lacked snapuserd.

Root cause: the GQ5012BF1 product enabled init_boot generation but did not
inherit AOSP target/product/generic_ramdisk.mk. Merely setting
BOARD_USES_GENERIC_KERNEL_IMAGE does not populate the generic ramdisk.

The product now inherits generic_ramdisk.mk, which supplies the canonical
first-stage ramdisk package set including snapuserd_ramdisk.

Corrected init_boot:

- path: /mnt/SamsungSSD/android/lineage-24.0/out/target/product/gq5012bf1/init_boot.img
- size: 8388608
- SHA-256: a205b1e432194e2ef077801974296a367b7a165e4ac2028b2ba9a6d75ec1c13f
- header: v4
- kernel: absent
- snapuserd: present
- KernelSU/Magisk contamination: absent

## Android 17 init_boot_b replacement

The contaminated KernelSU init_boot_b image:

- 23560214615cdff7b890bcf62eb43ba913dc352d1004d41c25281164e49a45b5

was replaced while Slot A remained active with the validated Android 17
generic init_boot:

- a205b1e432194e2ef077801974296a367b7a165e4ac2028b2ba9a6d75ec1c13f

Only the physical init_boot_b partition was written. The metadata-encryption
key invariant remained unchanged.

## Slot B vendor_boot provenance and factory restoration

The unexpected Slot B vendor_boot hash:

- fb748f23058c5189ca1a6ec7954d30e4174a3b15c2054c52385f48bf863d3a03

was identified exactly as the previously generated
`slot-b-investigation/boot-chain-compare/vendor-a-on-b-control/vendor_boot_b.vendor-a.fixed.img`.

It was therefore a leftover vendor-A-on-B control image, not unexplained
partition corruption.

A verified V15 factory vendor_boot was located in the original firmware set:

- size: 67,108,864 bytes
- SHA-256: c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756

Slot B vendor_boot was restored to that factory-exact image while Slot A
remained active. vendor_boot_a was hash-checked before and after and remained
unchanged. The metadata-encryption key invariant also remained unchanged.
No boot-control state was modified and no reboot was performed.

## Restore compact Phase-4 vendor_b for Android 17 bring-up

The V21 userdebug experimental vendor image:

- SHA-256: e76e5c2e7076d900155d1f80f01565dcfec6e602a655e697a774edd977220c2a

was replaced with the archived compact Phase-4 Lineage vendor baseline:

- size: 816349184 bytes
- SHA-256: 9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98

The restore did not modify super metadata. A temporary writable device-mapper
alias was created over the exact existing vendor_b physical extent:

- underlying block device: /dev/block/sdc75 (259:59)
- physical start sector: 17098384
- sector count: 1594432

The alias was verified byte-identical to vendor_b before writing. After the
write, the target hash was verified through both the writable alias and the
original read-only vendor_b mapping.

vendor_dlkm_b, system_dlkm_b and odm_dlkm_b retained their expected hashes.
Slot A remained active, the metadata-encryption key invariant remained
unchanged, and the temporary alias was deleted after verification.

## Android 17 Slot-B first real boot armed

After restoring vendor_b to the archived compact Phase-4 baseline, the entire
experimental Slot-B stack passed a final hash gate.

The final first-boot stack is:

- factory boot_b
- clean branch-generated Android 17 init_boot_b
- factory V15 vendor_boot_b
- preserved factory-compatible DTBO
- preserved vbmeta stack
- Android 17 system_b
- Android 17 system_ext_b
- Android 17 product_b
- restored compact Phase-4 vendor_b
- preserved vendor_dlkm_b
- preserved system_dlkm_b
- preserved odm_dlkm_b

Any remaining known temporary LieppOS writable DM aliases were first verified
against their canonical read-only mappings and then removed.

Slot A remained bootable and successful. Slot B's historical success state was
cleared, B was re-enabled as bootable and selected for the next boot while
remaining unsuccessful, preserving the retry/fallback mechanism.

The metadata-encryption key invariant remained unchanged immediately before
the reboot.
