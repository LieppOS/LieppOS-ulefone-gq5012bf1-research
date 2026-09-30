
## Historical LieppOS build-output search

The current `/mnt/SamsungSSD/LieppOS/out/target/product` contains only:

- `generic_arm64`
- `tdgsi_arm64_ab`

There is no current `armol` product output.

The historical `armol` target-files metadata therefore cannot be recovered from
the present product output directory.

The `Builds/` directory contains GSI-style `lineage_arm64_bvNE` images, not an
obvious historical `armol` full-ROM target-files package.

A broad recursive exact-fingerprint grep across the whole Android source tree
proved impractical and was terminated. Future provenance searches are restricted
to targeted source/config files, shell history, signing-key candidates, and
date-constrained artifacts.

Current unresolved requirement:
recover the provenance and signing identity of the existing B installation,
especially the AVB root key with public-key SHA1
`d6b1afef32b1fce5c47f537df3d7ec167ae2b469`.
