# Complete vendor / vbmeta_vendor pair verification

## Previous path-guard false stop

The previous verification continuation stopped before executing the complete
AVB verification because it compared a canonicalized symlink path against a
literal source pathname.

That comparison was invalid.

Correct identity checks prove:

`VERIFY_VENDOR_SAME_FILE_OBJECT=1`

Staged vendor SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

Expected fixed vendor SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

Staged child SHA256:

`1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

Expected child SHA256:

`1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

Thus the verification directory contained the exact intended pair.

## Complete AVB verification

Embedded-key verification:

`FULL_PAIR_VERIFY_RC=0`

`FULL_PAIR_VERIFY=1`

Explicit expected-key verification:

`EXPECTED_KEY_VERIFY_RC=0`

`EXPECTED_KEY_VERIFY=1`

Vendor descriptor result:

`VENDOR_DESCRIPTOR_VALID=1`

Final cryptographic result:

`CRYPTO_VERIFY=1`

## Existing strict semantic gates

Previously proven and reconfirmed:

- top-level metadata identical
- release string identical
- current/candidate properties identical
- candidate properties equal fixed vendor properties
- candidate hashtree descriptor exactly matches fixed vendor
- only Image Size, Tree Offset, FEC offset and Root Digest changed
- all critical hashtree structure fields remain unchanged

## Root trust

Root vbmeta chain public-key SHA1:

`664998c1c258771293715a829bd8caeae5d5626b`

Candidate public-key SHA1:

`664998c1c258771293715a829bd8caeae5d5626b`

Rollback-index location:

`4`

Flags:

`0`

`ROOT_TRUSTS_CANDIDATE_KEY=1`

No root vbmeta regeneration is required.

## Final offline classification

`ROOT_VBMETA_CONTENT_REWRITE_REQUIRED=0`

`ROOT_VBMETA_CAN_REMAIN_BYTE_IDENTICAL=1`

`CANDIDATE_READY=1`

`AVB_CLASS=FIXED_VENDOR_AND_VBMETA_VENDOR_FORM_STRICT_CHAIN_CONSISTENT_PAIR`

The complete validated Slot-B candidate pair is:

Fixed vendor:

`/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.img`

SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

Regenerated vbmeta_vendor:

`/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/untouched-b-early-boot-forensics/fixed-vendor-vbmeta-regeneration/vbmeta_vendor.fixed.img`

SHA256:

`1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

No phone operation occurred.
