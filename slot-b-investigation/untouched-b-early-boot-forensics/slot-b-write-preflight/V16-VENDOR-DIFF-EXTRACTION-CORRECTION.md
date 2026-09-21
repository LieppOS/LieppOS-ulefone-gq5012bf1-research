# V16 vendor-tree diff extraction correction

The previous V15-vs-V16 vendor-tree audit used an incorrect host-tool path:

    $OUT/host/linux-x86/bin/fsck.erofs

where OUT was the product directory.

Both extraction commands therefore returned:

    RC=127

and the resulting zero-entry tree diff was invalid.

The correct host tool is:

    /mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/fsck.erofs

The replacement report in:

    v15-vs-v16-vendor-tree-diff.txt

was generated only after both EROFS extraction commands succeeded.

PHONE_MODIFIED=0
