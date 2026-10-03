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

## Recovery reboot-mode kernel bridge

A follow-up to the LK WDT helper investigation corrected the earlier static
target classification:

- `0x3dcdc` is a getter for `MTK_WDT_NONRST_REG2[10:4]`.
- `0x3dcb8` is the corresponding writer for bits `[10:4]`.
- the adjacent function at `0x3dc5c` is the low-nibble writer candidate and
  directly accesses `0x1c00a024` while preserving the upper 28 bits.

Independent DT evidence from the GQ5012BF1 vendor device tree shows an enabled
`syscon-reboot-mode` description with `mode-recovery = <0x02>`, exactly equal
to the recovery value consumed by LK.

The vendor module set contains both `reboot-mode.ko` and
`syscon-reboot-mode.ko`.

The remaining proof requirement is to bind the DT node's exact offset, mask,
and parent syscon physical base to `0x1c00a024`.

No phone state was modified during this investigation.

## Recovery reboot-mode path — proven end to end

The GQ5012BF1 recovery reboot-mode mechanism is now statically and live-DT
validated end to end.

Confirmed contract:

- watchdog/syscon base: `0x1c00a000`
- reboot-mode register offset: `0x24`
- resulting physical register: `0x1c00a024`
- field mask: `0x0f`
- recovery magic: `0x02`
- bootloader magic: `0x03`

The generic Linux reboot-mode framework resolves the reboot command to its
`mode-*` DT value. `syscon-reboot-mode` then calls `regmap_update_bits()` with
the parent watchdog syscon, DT offset and DT mask.

LK function `0x3dc5c` accesses the same physical register and writes the
reboot-mode value after preserving the upper register bits. LK's recovery
consumer subsequently reads the same low-nibble field.

This establishes the Linux -> MTK WDT NONRST register -> LK recovery-mode
handoff.

This does not by itself establish which component caused the failed
experimental Slot-B boot to request recovery. That causal question remains
separate and is the next investigation target.

## LK reboot-mode dispatcher follow-up

After proving the Linux -> WDT NONRST -> LK recovery-mode contract, the next
target is LK function `0x8938`.

This function contains direct calls to the low reboot-mode writer `0x3dc5c`
using both:

- `3`, matching the DT `mode-bootloader` value
- `2`, matching the DT `mode-recovery` value

A dedicated host-only investigation now captures the complete function,
control flow, referenced strings, call graph, and post-write reset path in
order to identify the exact LK-side conditions that select these modes.

No phone state is modified by this investigation.

## Slot-B first-boot recovery-cause audit

Further LK analysis showed that the previously oversized `0x8938` function
was partially an analysis-boundary artifact.

Adjacent code implements explicit reboot command paths:

- normal reboot,
- reboot to bootloader using reboot-mode value 3,
- fastbootd via `boot-fastboot` in misc followed by recovery-mode value 2,
- recovery using reboot-mode value 2 with a `boot-recovery` fallback.

The low `MTK_WDT_NONRST_REG2` writer at `0x3dc5c` has only three direct static
call sites in the analyzed LK payload. The third call supplies zero.

This substantially weakens the hypothesis that ordinary LK boot selection
spontaneously writes recovery value 2. The leading causal question is now
whether an earlier Slot-B Android boot requested a recovery reboot, causing
Linux `syscon-reboot-mode` to persist value 2 before the next LK invocation.

A host-only audit therefore searched all retained Slot-B runtime evidence for
normal-boot, recovery-boot, reboot-command, sys.powerctl, BCB, init-failure and
reboot_on_failure markers. Generated Android 17 init/RC configuration was also
scanned for recovery-producing failure actions.

No phone state was modified and Slot B was not booted.

## Recovery-mode 0 -> 2 transition: stale reboot-mode investigation

The retained runtime evidence now proves two distinct Slot-B boot states:

1. the original failed Android 17 Slot-B attempt reached Linux with MediaTek
   boot mode 0;
2. the later metadata-fixed attempt reached Linux with MediaTek boot mode 2
   and entered recovery userspace.

The retained runtime evidence did not contain a direct Android
`sys.powerctl=reboot,recovery` or kernel
`Restarting system with command 'recovery'` line connecting those boots.
Previous automated recovery-request hits were dominated by static LK strings
and research prose and therefore did not prove causality.

A new host-only investigation checks an important generic reboot-mode edge
case: commandless reboot resolves to the `normal` reboot mode, while generic
Linux reboot-mode implementations may skip the hardware write when the
resolved magic value is zero. The device DT is therefore checked explicitly
for `mode-normal`, the exact local reboot-mode implementation is inspected,
all known LK accesses to the WDT NONRST reboot-mode register are re-audited,
and retained command history is searched for recovery/fastboot mode writes.

No phone state was modified and Slot B was not booted.

## Slot-B mode-2 origin timeline continuation

The mode-2 origin audit was resumed after correcting a host-side Python parser
error.

The original mode-0 Slot-B boot explicitly ends with kernel restart target
`bootloader`, while the later metadata-fixed boot begins with MediaTek mode 2.
Since LK clears the reboot-mode nibble after consuming it, a new value-2 write
is required between those states.

Generated init `reboot_on_failure` bootloader rules and multiline zsh command
history were therefore correlated against the retained experiment timeline.

No phone state was modified and Slot B was not booted.

## Slot-B mode-2 command reconstruction

Disk zsh history contains a large gap across the relevant Slot-B experiments
and therefore cannot by itself exclude an explicit recovery/fastboot
transition.

The stronger evidence source is the experiment transcript sequence immediately
preceding the metadata-fixed mode-2 boot:

- metadata root fix;
- metadata root-fix continuation;
- corrected system_b metadata-fix install.

Those artifacts and all other research files created during the critical
19:30-20:00 UTC interval were audited for adb, fastboot, bootctl, reboot,
BCB, fastbootd and recovery commands.

The first mode-0 Slot-B reboot-to-bootloader cause was also checked for an
explicit `bootstrap-apexd-failed` marker.

No phone state was modified.

## Pre-LK NONRST_REG2 address users found

A targeted raw machine-code scan found direct AArch64 constructions of
`0x1c00a024` in firmware stages outside the main LK payload.

Candidates were found in:

- `bl2_ext`;
- AEE;
- `preloader_k6878v1_64.bin`.

This is significant because the preloader executes before LK and can in
principle alter the reboot-mode field before LK reads it.

Focused disassembly was generated only around those candidate offsets to
distinguish reads from writes and identify any value-2 recovery assignment.

No phone state was modified and Slot B was not booted.

## AEE has a direct NONRST_REG2 reboot-mode writer

Focused static analysis corrected the earlier broad pre-LK classification.

`bl2_ext` and the directly observed preloader helper modify higher
`MTK_WDT_NONRST_REG2` fields, notably bits `[10:4]`.

In contrast, `06-aee.bin` contains an exact low-field writer at `0x2eaa0`.
It clears `NONRST_REG2[3:0]`, ORs in its argument, and writes the register
back.

This is the exact field whose value `2` causes main LK recovery boot.

A dedicated direct-call scan now traces all callers of the AEE writer and
their arguments to determine whether AEE contains an executable path that
sets recovery value 2 before the observed LK mode-2 boot.

No phone state was modified and Slot B was not booted.

## AEE contains an explicit recovery-magic writer invocation

The AEE low-nibble writer has three direct callers.

One caller immediately supplies value `3`, one immediately supplies value
`2`, and one supplies zero.

The recovery path is explicit:

    mov w0, 2
    bl 0x2eaa0

where `0x2eaa0` writes `MTK_WDT_NONRST_REG2[3:0]`.

The same path is associated with the retained AEE `boot-recovery` string.

A follow-up maps AEE fastboot/reboot command strings directly to these
handler regions to identify the exact command capable of creating the
mode-2 handoff observed on the failed Slot-B experiment.

No phone state was modified and Slot B was not booted.

## AEE fastboot callback table resolution

The AEE fastboot command-registration block uses four distinct callback slots
for `reboot`, `reboot-bootloader`, `reboot-fastboot`, and
`reboot-recovery`.

A previous callback-resolution attempt stopped before analysis because of a
host-side Python/heredoc pipe error.

The continuation directly dumps and resolves the callback slots and
disassembles only the resulting function addresses. It does not assume that
the recovery callback begins at `0xef24`; the table itself determines the
true entry point.

No phone state was modified and Slot B was not booted.

## AEE recovery/fastboot reboot-mode path — final static proof

The AEE fastboot callback table has been resolved after accounting for its
runtime virtual-address base.

Confirmed command callbacks:

- `reboot` -> `0xedd0`
- `reboot-bootloader` -> `0xedfc`
- `reboot-fastboot` -> `0xee30`
- `reboot-recovery` -> `0xef24`

The recovery callback loads `boot-recovery` and the fastboot callback loads
`boot-fastboot`; both enter the shared BCB engine at `0xee3c`.

After a successful BCB write, that shared engine executes:

    mov w0, 2
    bl 0x2eaa0

where `0x2eaa0` writes the low reboot-mode nibble of physical register
`0x1c00a024`.

Thus AEE's recovery/fastboot reboot handlers provide a complete firmware path
for creating the value `2` later consumed by main LK as `RECOVERY_BOOT`.

This establishes command semantics and register provenance. Historical
causality for the specific failed Slot-B experiment remains a separate
question.

No phone state was modified and Slot B was not booted.

## AEE recovery mode-2 proof classifier correction

The final AEE static-proof checker initially produced false FAIL results for
the `0x2eaa0` register-writer instructions because it assumed a fixed textual
radare2 address padding width.

The corrected checker parses radare2 addresses numerically.

The resulting proof covers the complete static chain:

    reboot-recovery
        -> callback 0xef24
        -> boot-recovery
        -> shared BCB engine 0xee3c
        -> successful BCB write
        -> mov w0, 2
        -> AEE writer 0x2eaa0
        -> MTK_WDT_NONRST_REG2[3:0] = 2
        -> reset

`reboot-fastboot` enters the same shared recovery-mode-2 transport while using
`boot-fastboot` as the BCB command.

No phone state was modified.

## Slot-B mode-2 historical-trigger audit

With the AEE recovery/fastboot mode-2 mechanism proven, investigation moved
to the final unresolved historical question: what command actually invoked
that mechanism during the failed Slot-B workflow.

The on-disk zsh history is known to be incomplete across the experiment
window. Live shell history, git history, install-transcript provenance and
retained scripts were therefore searched for explicit:

- `adb reboot fastboot`
- `adb reboot recovery`
- `fastboot reboot fastboot`
- `fastboot reboot recovery`

No phone state was modified and Slot B was not booted.

## Slot-B mode-2 historical-trigger audit

With the AEE recovery/fastboot mode-2 mechanism proven, investigation moved
to the final unresolved historical question: what command actually invoked
that mechanism during the failed Slot-B workflow.

The on-disk zsh history is known to be incomplete across the experiment
window. Live shell history, git history, install-transcript provenance and
retained scripts were therefore searched for explicit:

- `adb reboot fastboot`
- `adb reboot recovery`
- `fastboot reboot fastboot`
- `fastboot reboot recovery`

No phone state was modified and Slot B was not booted.

## Controlled plain Slot-B reboot produced logo hang

A controlled plain A -> B transition was performed with an empty BCB and no
targeted recovery/fastboot reboot command.

The resulting B attempt remained at the boot logo and exposed neither ADB nor
fastboot during the 120-second observation period.

Because no B-side log was captured before rescue, the B-side LK boot mode
remains unknown for this attempt.

This distinguishes the experiment from the earlier immediately observable
fastbootd/recovery path, but does not by itself prove which LK mode was used.

## Controlled Slot-B logo-hang pstore classification

Pstore captured after manually returning to Slot A was analyzed to classify
the failed plain-reboot Slot-B attempt.

Result:

SLOT_B_MARKER=NO
SLOT_A_MARKER=NO
MODE0_MARKER=NO
MODE2_MARKER=NO
FORCE_NORMAL_BOOT=NO
RECOVERY_OR_FASTBOOTD=NO
LINUX_STARTED=NO
FIRST_STAGE_INIT=NO
SECOND_STAGE_INIT=NO
SERVICEMANAGER_SEEN=NO
APEXD_SEEN=NO
ZYGOTE_SEEN=NO
SYSTEM_SERVER_SEEN=NO
BOOT_COMPLETED_SEEN=NO
KERNEL_PANIC=NO
EXPLICIT_REBOOT_SEEN=NO
B_BOOTMODE_VERDICT=B_BOOTMODE_NOT_PROVEN_FROM_PSTORE
DEEPEST_BOOT_STAGE=NO_LINUX_PROGRESS_PROVEN

This analysis is host-only and does not perform another Slot-B boot.

## Correction: controlled Slot-B logo-hang pstore was non-diagnostic

The three pstore files recovered after the controlled plain-reboot Slot-B
logo hang were only approximately 62-65 bytes each and did not contain the
failed kernel console.

The initial marker extraction also contained malformed grep quoting.

Therefore the earlier `NO_LINUX_PROGRESS_PROVEN` label described an absence
of evidence, not proof that Linux never started.

Post-rescue investigation remained on safe Slot A and examined previous-boot
logcat, last_kmsg, MediaTek AEE/mtklog, Android DropBox/logd and boot-reason
history for surviving evidence of the failed B attempt.

No additional Slot-B boot was performed.

## October 3 Slot-B logo hang: stale DropBox data excluded

Review of the post-rescue DropBox extraction showed that the available
`SYSTEM_LAST_KMSG` records are historical October 2 logs.

Those records include explicit recovery, OrangeFox and fastbootd activity and
must not be attributed to the controlled October 3 plain-reboot Slot-B logo
hang.

No current failed-B kernel console survived in pstore or DropBox.

Investigation therefore moved to a static audit of the exact Android 17
system payload, including init/adbd, APEX, VINTF, VNDK/linker and SELinux
contracts against the live stock vendor environment.

No Slot-B boot was performed.

## Android 17 ↔ stock vendor contract reconciliation

The prior static audit's claim that `com.android.vndk` was missing was a
classifier false positive: Android 17 supplies a versioned
`com.android.vndk.v*.apex`.

The exact version was reconciled against the stock vendor
`ro.vndk.version`.

The stock vendor/ODM VINTF trees were then captured read-only from healthy
Slot A and reconciled with the exact Android 17 system/product/system_ext
output.

Result:

OLD_UNVERSIONED_VNDK_MISSING_RESULT=FALSE_POSITIVE
VERSIONED_VNDK_APEX_PRESENT=YES
VNDK_APEX_MATCHES_VENDOR=YES
LIVE_DEVICE_TARGET_LEVEL=8
MATCHING_FRAMEWORK_MATRIX=YES
CHECKVINTF_RC=70
FRAMEWORK_VENDOR_VINTF_COMPATIBILITY=NOT_PROVEN
STATIC_CONTRACT_BLOCKER_FOUND=UNRESOLVED

No Slot-B boot was performed.

## Android 17 Slot-B logo hang — VINTF/VNDK/kernel FCM cleared

The Android 17 framework and the stock Ulefone vendor contract were
reconciled again after the controlled Slot-B graphical-logo hang.

The earlier exact checker result remains authoritative:

- device target FCM level 8;
- Android 17 has matching FCM level 8;
- kernel 6.1 is accepted by that selected matrix;
- stock kernel 6.1.115 and the captured kernel configuration pass;
- versioned VNDK compatibility APEX v34 is present;
- stock vendor VNDK level is 34;
- exact framework/vendor checkvintf result is COMPATIBLE.

The later checkvintf status 70 was caused only by a missing host-side `/apex`
directory mapping.

VINTF, VNDK and kernel FCM are therefore removed from the primary blocker
list.

The active investigation target is now the second-stage boot chain:
userdata/FBE, APEX activation, zygote, system_server and display/framework
bring-up.

No Slot-B boot was performed during this pass.

## Android 17 critical-service path correction

The previous second-stage audit's fixed `/system/bin` presence test was
revisited because modern Android may place legacy HIDL service binaries in
system_ext and adbd in the com.android.adbd APEX.

The zygote property/import chain was also resolved explicitly because the
earlier audit printed an empty `ro.zygote` result while zygote rc variants
were present.

Result:

STATIC_RO_ZYGOTE_FOUND=NO
LIVE_A_RO_ZYGOTE_FOUND=YES
ZYGOTE_DYNAMIC_IMPORT_PRESENT=YES
ZYGOTE_SELECTED_RC_RESOLVES=YES
ZYGOTE_CHAIN_STATUS=PROPERTY_SOURCE_OUTSIDE_SCANNED_SYSTEM_PROPS
HWSERVICEMANAGER_BINARY_FOUND=YES
HWSERVICEMANAGER_SERVICE_RESOLVES=NO
VNDSERVICEMANAGER_SERVICE_DEFINED=NO
VNDSERVICEMANAGER_BINARY_FOUND=NO
ADBD_APEX_PRESENT=YES
ADBD_MODULE_CONTRACT_FOUND=YES
OLD_SYSTEM_BIN_MISSING_CLASSIFIER=NOT_FULLY_CLEARED
NEXT_FOCUS=RESOLVE_CRITICAL_SERVICE_EXEC_PATH

This pass is host/static plus read-only Slot-A inspection. Slot B was not
booted.
