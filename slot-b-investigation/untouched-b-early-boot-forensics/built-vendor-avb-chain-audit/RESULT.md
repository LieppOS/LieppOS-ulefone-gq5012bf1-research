# Fixed vendor Slot-B AVB-chain audit

## Vendor runtime-candidate prerequisite

Previous research closed the vendor-content differential as:

`NARROW_RUNTIME_CANDIDATE=1`

`RUNTIME_DIFFERENCE_CLASS=ONLY_REQUIRED_CFG_IS_FUNCTIONALLY_BOOT_RELEVANT`

This audit therefore focuses only on the AVB chain required to test that
vendor image safely on Slot B.

## Image identities

Current Slot-B/TIER3 vendor SHA256:

`9f3dfe3fe5ef025b667b8181bddfedaf6b08dace4b7cd6c4e05a4fde0d16aa98`

Fixed built vendor SHA256:

`850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

## Descriptor graph

```text
IMAGE=vbmeta.img
  ALGORITHM=None
  PUBLIC_KEY_SHA1=None
  ROLLBACK_INDEX=None
  ROLLBACK_INDEX_LOCATION=None
  FLAGS=None
  DESCRIPTOR_COUNT=11
    Chain Partition descriptor -> boot
    Chain Partition descriptor -> vbmeta_system
    Chain Partition descriptor -> vbmeta_vendor
    Hash descriptor -> dtbo
    Hash descriptor -> init_boot
    Hash descriptor -> vendor_boot
    Hashtree descriptor -> odm_dlkm
    Hashtree descriptor -> product
    Hashtree descriptor -> system_dlkm
    Hashtree descriptor -> system_ext
    Hashtree descriptor -> vendor_dlkm

IMAGE=vbmeta_system.img
  ALGORITHM=None
  PUBLIC_KEY_SHA1=None
  ROLLBACK_INDEX=None
  ROLLBACK_INDEX_LOCATION=None
  FLAGS=None
  DESCRIPTOR_COUNT=1
    Hashtree descriptor -> system

IMAGE=vbmeta_vendor.img
  ALGORITHM=None
  PUBLIC_KEY_SHA1=None
  ROLLBACK_INDEX=None
  ROLLBACK_INDEX_LOCATION=None
  FLAGS=None
  DESCRIPTOR_COUNT=1
    Hashtree descriptor -> vendor

VENDOR_DESCRIPTOR_OWNER_COUNT=1
VENDOR_OWNER=vbmeta_vendor.img TYPE=Hashtree descriptor

CHAIN=vbmeta.img -> boot
CHAIN=vbmeta.img -> vbmeta_system
CHAIN=vbmeta.img -> vbmeta_vendor
```

## Owner of vendor descriptor

Owner:

`vbmeta_vendor.img`

Descriptor type:

`Hashtree descriptor`

## Parent chain

Parent vbmeta:

`vbmeta.img`

Child partition name:

`vbmeta_vendor`

Chain model:

`CHAIN_PARTITION_PUBLIC_KEY_TRUST`

## Signing identity

Vendor-child vbmeta algorithm:

``

Public-key SHA1:

``

Rollback index:

``

Rollback-index location:

``

Flags:

``

Matching private-key count discovered under TIER3:

`0`

No private-key contents are stored in this research repository.

The local private-key file itself was not copied.

## Descriptor inventory

```text
OWNER=vbmeta_vendor.img
DESCRIPTOR_COUNT=1
1. TYPE=Hashtree descriptor
   Data Block Size=4096 bytes
   FEC num roots=2
   FEC offset=807288832
   FEC size=6389760 bytes
   Flags=0
   Hash Algorithm=sha1
   Hash Block Size=4096 bytes
   Image Size=800976896 bytes
   Partition Name=vendor
   Root Digest=8740ffe9618882f976a71da4f743b19b3b9a01d4
   Salt=b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6
   Tree Offset=800976896
   Tree Size=6311936 bytes
   Version of dm-verity=1
```

## Descriptor source mapping

```text
PARTITION=vendor
  TYPE=Hashtree descriptor
  ROLE=REPLACED_FIXED_IMAGE
  SOURCE=/mnt/SamsungSSD/android/lineage-22.2/out/target/product/armol/vendor.img
  SHA256=850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50
  SIZE=816353280
```

## Root-vbmeta consequence

`ROOT_VBMETA_CONTENT_REWRITE_REQUIRED=0`

The parent relationship is an AVB chain-partition relationship.

In this model the parent authenticates the child vbmeta signing public key and
rollback location rather than storing a digest of the child vbmeta image.

Therefore, if the regenerated child vbmeta is signed with the exact same key
and preserves its rollback semantics, changing the vendor descriptor inside
that child does not by itself require changing the parent/root vbmeta content.

## Regeneration readiness

`READY_FOR_VBMETA_VENDOR_REGEN=0`

`AVB_CLASS=AVB_CHAIN_REGEN_PREREQUISITES_INCOMPLETE`

## Safety

This audit was fully host-side.

No ADB command was issued.

No fastboot command was issued.

No partition was written.

No slot metadata was changed.

No private-key material was committed.

## Next phase

If regeneration readiness is 1, the next phase is to generate a candidate
replacement for the vendor-owning vbmeta image using:

- the fixed vendor image;
- unchanged staged images for every other descriptor owned by the same child;
- the exact existing signing key;
- the existing algorithm;
- existing rollback index and rollback-index location;
- existing flags.

The regenerated vbmeta candidate must then be inspected and descriptor-diffed
against current B before any phone write is considered.
