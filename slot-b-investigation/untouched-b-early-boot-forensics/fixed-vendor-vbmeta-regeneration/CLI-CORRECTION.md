# Vendor AVB key discovery and avbtool CLI correction

The targeted signing-key audit reduced the previous broad 26,405-file search to
12 relevant AVB/key candidates.

It established:

- targeted key candidate count: 12
- matching key path count: 1
- unique matching private-key hash count: 1

The dedicated Phase-4 AVB bring-up keys were then tested directly.

Their AVB public-key SHA1 values were:

- root.pem: `d6b1afef32b1fce5c47f537df3d7ec167ae2b469`
- system.pem: `579a140d204d847f0c74332c73996baf1ed6a5fc`
- vendor.pem: `664998c1c258771293715a829bd8caeae5d5626b`

The root vbmeta chain descriptor for `vbmeta_vendor` trusts:

`664998c1c258771293715a829bd8caeae5d5626b`

Therefore the exact matching private signing key is:

`vendor.pem`

Private-key SHA256:

`18b4ad1fe3e1f7abed037bdd15f25afc76ca815d72a1347dab0108ae39df5008`

The private-key file and its contents are not stored in this repository.

## Previous candidate-generation failure

Candidate generation did not start because the locally installed avbtool
rejected:

`--release_string avbtool 1.3.0`

with:

`unrecognized arguments: --release_string`

Classification:

`AVBTOOL_RELEASE_STRING_OPTION_UNSUPPORTED=1`

This is an avbtool command-line compatibility issue, not an AVB trust-chain,
key, descriptor, or image failure.

The existing `vbmeta_vendor.img` release string is the normal avbtool release
string. The corrected generation procedure omits the unsupported argument and
strictly verifies the candidate release string against the current child after
generation.

No phone operation occurred.
