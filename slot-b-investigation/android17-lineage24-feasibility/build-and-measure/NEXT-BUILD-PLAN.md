# Next build plan

## Decision

```text
RECOMMENDED_NEXT_BUILD=B_PROPER_SPLIT_GQ5012BF1_PRODUCT
```

The folded generic GSI is complete and useful for a future isolated DSU proof,
but it cannot answer final partition ownership or fit. Actual measurements now
justify moving immediately to a split device product.

## Required product shape

Create `lineage_gq5012bf1` with:

```text
system_b extent     665391104
system_ext_b extent 366891008
product_b extent    337686528
filesystem          EROFS lz4hc,9
AVB                  SHA256_RSA2048 hashtree/FEC, flags 0
shipping API         35
vendor contract      FCM/VNDK 34 (level 8)
```

Set real `TARGET_COPY_OUT_SYSTEM_EXT=system_ext` and
`TARGET_COPY_OUT_PRODUCT=product`, enable both images, and put all three in the
device dynamic-partition group. Use fixed current extents while proving fit; do
not resize super.

## First split-build package policy

1. Preserve all core API37 APEX/framework/providers and native LineageSettings
   DB24 implementation.
2. Keep only the VNDK 34 snapshot after VINTF and ELF closure prove the Ulefone
   vendor has no older snapshot dependency.
3. Exclude compliance-GSI debug policy, virtual test HALs and universal GSI
   payload not selected by Ulefone's manifest.
4. Remove Vim/runtime, Updater and measured optional apps/media through product
   makefiles. Do not modify the completed image by hand.
5. Investigate omitting AVF (`com.android.virt`) only after checking current
   kernel capabilities, manifest features and dependencies.
6. Keep 32-bit support until MTK process/ELF closure proves otherwise.
7. Build `userdebug` for first host validation, then produce a `user` size and
   security comparison.

## Fit gates

Do not accept a build that merely reaches the exact extent. Recommended first
headroom targets:

| Partition | Maximum final AVB image target | Desired headroom |
|---|---:|---:|
| system | 648613888 | 16 MiB |
| system_ext | 350113792 | 16 MiB |
| product | 320909312 | 16 MiB |

For each image record payload, EROFS blocks, exact final bytes, hash, AVB footer,
hashtree/FEC and descriptor owner. Run `checkvintf`, SELinux policy tests,
installed-file ownership and vendor ELF closure before any hardware proposal.

## DSU role

Keep the current folded system image unchanged as the reference DSU candidate.
DSU remains the safest framework/vendor test only after DSU capability is
separately validated and only with a separate guest userdata image. This build
does not authorize installing it.

## AVB and phone safety

The eventual split build must produce a coherent flags-0 B chain and resolve the
known init_boot descriptor mismatch before any write. No flash, slot activation,
userdata access, metadata write or super change is part of the next host build.
