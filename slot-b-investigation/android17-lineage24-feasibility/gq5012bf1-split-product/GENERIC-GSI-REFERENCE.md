# Frozen generic GSI reference

```text
target   = lineage_gsi_arm64 cp2a userdebug
Android  = 17
SDK      = 37
image    = /mnt/SamsungSSD/TIER3/phase5/android17/out-lineage_gsi_arm64-erofs/target/product/generic_arm64/system.img
bytes    = 1745326080
SHA-256  = bae4ace2108d50bf431b9b49ccc3767e2867cb90e8290921c142d3df0c396eda
layout   = folded product + system_ext under system
```

Logical payload measurements were 1,152,368,951 system bytes, 627,951,987
system_ext bytes, and 500,596,070 product bytes. The original artifact was not
rebuilt. Its SHA-256 was checked before and after both split-product builds and
remained identical. A second immutable copy is stored at:

```text
/mnt/WDBlue/TIER3-phase5-android17/reference-gsi-lineage_gsi_arm64-cp2a-userdebug-erofs/system.img
```

The split build reused shared host/intermediate objects in the existing OUT_DIR
to avoid another 124 GB output tree, but writes went to the distinct
`target/product/gq5012bf1` product directory. The generic image itself was not
overwritten.

Exact inventories:

- `REFERENCE-GSI-PACKAGES.tsv`: all app/priv-app bundles and payload bytes;
- `REFERENCE-GSI-APEX.tsv`: all 44 APEX/CAPEX containers with hashes;
- `REFERENCE-GSI-VNDK-CONTENTS.tsv`: 1,126 extracted files from VNDK
  generations 31/32/33/34, each with size and hash;
- parent `build-and-measure/IMAGE-SIZE-BREAKDOWN.tsv`: top files/directories;
- the frozen `installed-files.json` remains in the host reference directory.
