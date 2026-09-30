# Userdata-only DSU feasibility audit

Android 17 has already been staged and byte-for-byte verified on inactive
Slot B:

- system_b
- system_ext_b
- product_b

The remaining bring-up blocker is A/B shared userdata.

## Proposed isolation mechanism

Use Android's DSU infrastructure only for an isolated `userdata_gsi` backing
image while continuing to boot the actual physical Slot-B Android 17 logical
partitions.

Modern AOSP supports individually creating DSU partitions. During first-stage
mount, DSU fstab transformation redirects `/data` to `userdata_gsi` when that
partition exists. Other physical partitions are replaced only when matching
DSU images are present.

A userdata-only DSU could therefore provide:

- physical Slot-B system/system_ext/product/vendor
- isolated DSU-backed /data
- no Android 17 mount of Slot A's normal userdata filesystem as /data

This file records device-side capability only. No DSU partition was allocated
or enabled by this audit.

## Additional AVB result

The current vendor_boot_b authenticated image region exactly matches the
vendor_boot hash descriptor in current vbmeta_b:

    2dd35dbc5697256c8379f1e3ebb7c99ef209b4022cfc8b62736204f76b20cd53

The differing full-partition SHA256 therefore comes from bytes outside the
authenticated vendor_boot image region and is not an authenticated-region
mismatch.
