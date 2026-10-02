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

## First real Android 17 Slot-B boot result

The first fully gated Android 17 Slot-B boot did not complete.

Observed physical behavior:

1. Slot B displayed the boot logo.
2. The display briefly went black.
3. The device rebooted.
4. Slot B was attempted again.
5. After the bootloader retry budget was exhausted, the device automatically
   fell back to the known-good Slot A.

The fallback confirms that B remained unsuccessful and that the A/B retry
mechanism protected the working Slot A as intended.

No additional Slot-B activation should be performed until the retained
pstore/ramoops, boot-reason and MediaTek crash evidence from this attempt has
been analyzed.

## First failed Android 17 boot — ramoops deep analysis

The automatic Slot-A fallback preserved a `console-ramoops-0` record from the
failed Slot-B attempt.

Initial inspection showed that the failed boot reached Android first-stage
init and loaded the expected MediaTek early kernel modules. No kernel
panic/oops was visible in the initial filtered forensic output.

A second host-side analysis therefore captured the complete late-console
region and explicitly searched for:

- first-stage and second-stage init transitions
- fs_mgr and logical-partition mounting
- AVB / dm-verity
- SELinux policy loading
- snapuserd / snapshot setup
- watchdog and reboot paths
- kernel panic/oops/call-trace signatures

No additional Slot-B boot was attempted during this analysis.

## Android 17 failed boot — first-stage mount contract analysis

The first Android 17 Slot-B attempt was narrowed to an orderly init fatal
reboot immediately after the first observed EROFS logical-partition mount.

A read-only follow-up therefore captured:

- the exact factory vendor_boot first-stage fstab and mount order,
- live Slot-B logical device-mapper mappings,
- read-only mountability of system/system_ext/product/vendor,
- current Slot-B vbmeta descriptors,
- AVB metadata from the Android 17 system images and archived Phase-4 vendor.

This step did not reactivate Slot B and performed no partition or boot-control
writes.

## Android 17 metadata mountpoint fix completed

The initial metadata-root repair script successfully modified BoardConfig.mk
but aborted before rebuilding because the device directory was not itself a
Git repository.

The continuation verified the effective build configuration:

    BOARD_USES_METADATA_PARTITION := true

The Android build configuration resolves that variable as true.

An incremental systemimage build was then completed and the generated root
contains the required /metadata directory.

Previous Android 17 system image:

    8a3d844f35c6d4f5039878a7e72a65c664ded243b9e749d49390bc4118bc2030

Corrected Android 17 system image:

    d8bcd2ea2d842c02c23572cf60a55b81f5403e15cf20b3f53a208769d700d3f0

Image size remains exactly:

    665391104 bytes

which matches the existing system_b logical-partition capacity.

No phone partition or boot-control write was performed.

## Android 17 /metadata fix installed for isolated Slot-B retest

The rebuilt Android 17 system image containing the required root /metadata
mountpoint was installed to system_b as the only changed Slot-B partition.

Previous system_b SHA-256:

    8a3d844f35c6d4f5039878a7e72a65c664ded243b9e749d49390bc4118bc2030

Corrected system_b SHA-256:

    d8bcd2ea2d842c02c23572cf60a55b81f5403e15cf20b3f53a208769d700d3f0

The corrected image was verified through the canonical read-only system_b
mapping and mounted read-only after installation. The flashed root contains
both /metadata and /system/bin/init.

All other physical and logical Slot-B partition hashes remained unchanged.

Slot B's exhausted retry state was cleared and B was selected for the next
boot while remaining unsuccessful. Slot A remained active and successful
before reboot, and the metadata-encryption key invariant remained unchanged.

This retest therefore isolates BOARD_USES_METADATA_PARTITION /
root-/metadata creation as the experimental variable.

## Android 17 /metadata fix boot result

The isolated Slot-B retest with only the corrected system_b changed produced
materially different behavior.

Before the fix, Slot B reached first-stage system mounting and immediately
entered init's fatal reboot-to-bootloader path.

After adding the required root /metadata mountpoint, Slot B no longer performed
that immediate reboot. Instead, it remained at the boot logo until manually
rebooted back to the known-good Slot A.

This behavioral change strongly supports the missing root /metadata mountpoint
as the first-stage blocker. The next investigation therefore moves later in
the Android boot sequence rather than reverting that fix.

## Android 17 reached recovery userspace after metadata fix

The corrected system_b eliminated the previous first-stage fatal reboot.

The subsequent Slot-B attempt reached:

- SELinux policy loading and enforcing mode
- Android init second stage
- servicemanager
- USB gadget initialization

The boot was not a normal Android userspace boot, however. MediaTek runtime
evidence reported bootmode 0x2 / boottype 0x2, corresponding to RECOVERY_BOOT.
Recovery userspace then started and later entered fastbootd.

The later fastboot set_active:a and reboot commands were the manual rescue and
occurred after recovery/fastbootd had already started.

A read-only investigation of misc/BCB, MediaTek para state, current normal-A
boot mode, chosen DT boot tags, and retained LK logging was therefore captured
before any further Slot-B attempt.

## Normal-A versus recovery-B boot-mode distinction

Further analysis established that the post-/metadata-fix Slot-B attempt was
not merely interpreted as recovery by Android userspace.

The failed B boot exposed MediaTek bootmode 2 / boottype 2, while the
known-good Slot-A LK log reports boot mode 0. MediaTek boot-mode definitions
identify value 0 as NORMAL_BOOT and value 2 as RECOVERY_BOOT.

The current Slot-A `/chosen/atag,boot` data was therefore decoded explicitly,
and the complete `/proc/bootconfig` was captured to determine whether LK adds
`androidboot.force_normal_boot=1` during a known-good normal boot.

The misc BCB was also captured before any new Slot-B activation. A BCB observed
after recovery cannot by itself establish its pre-boot value because Android
recovery can clear the bootloader message while returning to normal boot.

No Slot-B boot was attempted in this step.

## Instrumented Slot-B boot rescue

The first live boot-mode capture did not observe a usable ADB transport within
its bounded capture window and therefore aborted before executing its automatic
Slot-A recovery stage.

A follow-up transport-aware rescue recorded the currently exposed USB mode.
When an ADB environment was available it captured bootconfig, MTK atag boot
data, LK logs and the live BCB before recovery. When fastboot was available it
captured bootloader slot state before selecting the known-good Slot A.

The phone was returned to Slot A without modifying Android 17 partitions.
Retained pstore evidence from the B attempt was copied after recovery.

## Static LK investigation after repeated recovery-mode Slot-B boots

The live Slot-B capture attempt missed the short B transport window and the
device automatically returned to known-good Slot A.

The preboot BCB had been empty and the corrected Android 17 system_b was still
installed. After fallback, Slot A again reported normal MediaTek boot mode 0,
force_normal_boot=1 and an empty BCB.

Because the recovery classification is therefore being made before normal
Android userspace, the next investigation moved offline into the exact
factory V15 LK image.

The factory LK and live LK-like partitions were identified read-only and the
bootloader binary was searched for MediaTek recovery selectors, RTC recovery
handling, interrupted-recovery detection, key detection, A/B retry logic and
force_normal_boot handling.

No new Slot-B boot was attempted.

## Static LK investigation after repeated recovery-mode Slot-B boots

The live Slot-B capture attempt missed the short B transport window and the
device automatically returned to known-good Slot A.

The preboot BCB had been empty and the corrected Android 17 system_b was still
installed. After fallback, Slot A again reported normal MediaTek boot mode 0,
force_normal_boot=1 and an empty BCB.

Because the recovery classification is therefore being made before normal
Android userspace, the next investigation moved offline into the exact
factory V15 LK image.

The factory LK and live LK-like partitions were identified read-only and the
bootloader binary was searched for MediaTek recovery selectors, RTC recovery
handling, interrupted-recovery detection, key detection, A/B retry logic and
force_normal_boot handling.

No new Slot-B boot was attempted.

## LK recovery-mode control-flow localization

The factory V15 LK image is an ARM64 MediaTek bootloader container rather than
a directly analyzable ELF image.

Static string analysis established that it contains:

- androidboot.force_normal_boot=1
- boot-recovery / reboot-recovery
- recovery_check misc handling
- recovery image loading
- hardware recovery-key handling
- MediaTek boot-mode DT propagation
- A/B slot retry handling

The next offline step parsed the MTK 0x58881688 container, extracted the main
LK payload, and searched ARM64 ADR / ADRP+ADD references to the key recovery
and normal-boot strings.

This localizes the actual code regions responsible for deciding recovery mode
without consuming another Slot-B boot attempt.

The live LK partition identities were also recorded read-only to establish
whether the factory V15 LK being reversed matches the currently installed
bootloader.

## LK RECOVERY_BOOT predicates localized

Static ARM64 analysis recovered the MediaTek LK boot-mode global:

    g_boot_mode = 0xe0ad0

The boot-mode initializer beginning near 0xca18 contains two explicit paths
which assign RECOVERY_BOOT (value 2):

1. function 0x3dc80 returns value 2
2. function 0x18924 returns a value with bit 0 set

Both converge on:

    mov w0, 2
    strb w0, [g_boot_mode]

The second predicate is located in the same region as the LK recovery_check
misc/BCB handling and is therefore expected to represent the BCB recovery
request path. The controlled Slot-B experiment had an empty BCB immediately
before boot, making the first predicate at 0x3dc80 the higher-priority target.

The force_normal_boot omission and recovery-image selection previously
observed are downstream consumers of this already-selected boot mode.

No device or boot-control write was performed.

## LK recovery mode traced to MTK_WDT_NONRST_REG2

The V15 LK recovery path has now been traced below the generic boot-mode
initializer.

Function `0x3dc80` accesses physical address `0x1c00a024`, which is
`MTK_WDT_NONRST_REG2` at TOPRGU/WDT base `0x1c00a000 + 0x24`.

On first invocation, LK:

1. reads `MTK_WDT_NONRST_REG2`;
2. extracts bits `[3:0]`;
3. caches that nibble;
4. clears bits `[3:0]` in the hardware register; and
5. returns the cached value.

The boot-mode initializer subsequently treats value `2` as `RECOVERY_BOOT`.

Consequently, an earlier writer which leaves:

    MTK_WDT_NONRST_REG2[3:0] = 2

can force recovery independently of the misc/BCB recovery command.

This is consistent with the controlled Slot-B observation in which the BCB was
empty but LK still selected recovery.

The next static target is the family of adjacent WDT helper routines beginning
at `0x3dcb8` and `0x3dcdc`, followed by their call sites and the corresponding
kernel/restart writer.

No phone partition or boot-control state was modified by this investigation.
