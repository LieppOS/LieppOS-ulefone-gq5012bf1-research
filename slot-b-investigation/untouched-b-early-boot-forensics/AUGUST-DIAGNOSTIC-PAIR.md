# August Slot-B diagnostic pair — exact delta

## Conclusion

The August post-firmware diagnostic pair did not contain an Android boot fix.

The diagnostic `vendor_boot` differs from the Phase-4/current-B baseline only
in the vendor kernel command line:

Baseline:

`bootopt=64S3,32N2,64N2`

Diagnostic:

`bootopt=64S3,32N2,64N2 printk.always_kmsg_dump=Y`

The following are byte-identical between baseline and diagnostic vendor_boot:

- vendor_ramdisk00
- vendor_ramdisk01
- DTB
- bootconfig (empty in both)
- vendor ramdisk fragment order/type/name/board IDs
- header topology and load-address parameters

Extracted-file SHA256 manifests are identical.

The root vbmeta semantic diff contains exactly one descriptor change: the
SHA-256 digest covering `vendor_boot`. Chain keys, flags, rollback fields,
init_boot coverage, and every other descriptor remain unchanged.

Therefore the August observation of MediaTek USB PID `0e8d:201c` cannot
currently be attributed to a repaired boot path introduced by the diagnostic
images. The diagnostic change was kmsg-persistence instrumentation.

A later test that only waits for stable ADB cannot rule out the same brief
kernel/Android-init USB enumeration, because `0e8d:201c` may occur while ADB
remains offline and never reaches `adb device`.

## Consequence

The leading boundary remains early kernel/Android userspace after the repaired
MediaTek B firmware chain, not vendor_boot payload drift or AVB topology.
