# Fixed vendor AVB pair finalized

## Vendor signing key

Targeted key discovery proved a unique matching vendor signing key.

Exact key:

`vendor.pem`

Private-key SHA256:

`18b4ad1fe3e1f7abed037bdd15f25afc76ca815d72a1347dab0108ae39df5008`

Derived public-key SHA1:

`664998c1c258771293715a829bd8caeae5d5626b`

Root vbmeta's `vbmeta_vendor` chain descriptor trusts the same public key.

No private-key contents are stored in this repository.

## AVB topology

```text
CHILD_ALGORITHM=SHA256_RSA2048
CHILD_PUBLIC_KEY_SHA1=664998c1c258771293715a829bd8caeae5d5626b
CHILD_ROLLBACK_INDEX=0
CHILD_ROLLBACK_INDEX_LOCATION=0
CHILD_FLAGS=0
CHILD_RELEASE_STRING='avbtool 1.3.0'

PARENT_CHAIN_PUBLIC_KEY_SHA1=664998c1c258771293715a829bd8caeae5d5626b
PARENT_CHAIN_ROLLBACK_LOCATION=4
PARENT_CHAIN_FLAGS=0
```

`PARENT_CHAIN_KEY_MATCH=1`

`ROOT_TRUSTS_VENDOR_KEY=1`

## avbtool CLI correction

The locally installed avbtool does not accept the attempted
`--release_string` argument for `make_vbmeta_image`.

The corrected invocation omitted that argument.

The generated candidate's release string was then compared directly against
the current Slot-B `vbmeta_vendor`.

`RELEASE_STRING_EQUAL=1`

Therefore the CLI workaround does not alter the child release metadata.

## Candidate

Path:

`vbmeta_vendor.fixed.img`

Size:

`4096`

SHA256:

`1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

Algorithm:

`SHA256_RSA2048`

Public-key SHA1:

`664998c1c258771293715a829bd8caeae5d5626b`

## Strict semantic comparison

```text
TOP_LEVEL_METADATA_EQUAL=1
RELEASE_STRING_EQUAL=1
CURRENT_CANDIDATE_PROPS_EQUAL=1
CANDIDATE_FIXED_VENDOR_PROPS_EQUAL=1
CANDIDATE_TREE_MATCHES_FIXED_VENDOR=1
ONLY_EXPECTED_TREE_FIELDS_CHANGED=1
CRITICAL_TREE_STRUCTURE_SAME=1

OLD_RELEASE_STRING='avbtool 1.3.0'
CANDIDATE_RELEASE_STRING='avbtool 1.3.0'

TREE_CHANGES:
FEC offset: '807288832' -> '807292928'
Image Size: '800976896 bytes' -> '800980992 bytes'
Root Digest: '8740ffe9618882f976a71da4f743b19b3b9a01d4' -> '4e290de2ea57b86baf081f1d248b8ad5ce568e9c'
Tree Offset: '800976896' -> '800980992'
```

Self-signature verification:

`CRYPTO_VERIFY=0`

## Root vbmeta

`ROOT_VBMETA_CONTENT_REWRITE_REQUIRED=0`

`ROOT_VBMETA_CAN_REMAIN_BYTE_IDENTICAL=1`

The root chain descriptor authenticates the `vbmeta_vendor` signing public
key and rollback-index location.

The candidate is signed by the same trusted vendor key.

## Narrow pair

`CANDIDATE_READY=0`

`AVB_CLASS=VBMETA_VENDOR_CANDIDATE_FAILED_STRICT_GATE`

When readiness is 1, the complete AVB-consistent Slot-B experiment requires
only:

1. fixed vendor:
   `850a58b16357597e0fa93f7d5ab9443c85e1b49df33b0e86fa1d2d393044ca50`

2. regenerated vbmeta_vendor:
   `1ac2a85791813b70f7a901c73d43a19d1358ba0c4158a7e20688f32a2ffe783f`

The existing root vbmeta remains byte-identical:

`bb2c7cb52dd15ee636cdb27b60f3fa5ed8fd6f774fe4acfc0a77301cbb4b17fb`

## Safety

- phone operations: none
- flash operations: none
- slot operations: none
- Slot A untouched
- root vbmeta untouched
- private-key contents not stored
