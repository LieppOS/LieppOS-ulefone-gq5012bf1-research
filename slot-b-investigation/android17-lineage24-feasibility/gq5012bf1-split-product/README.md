# GQ5012BF1 LineageOS 24 split product

## Result

A real `lineage_gq5012bf1 cp2a userdebug` product was configured and built from
the official LineageOS 24 / Android 17 tree at manifest
`f16772cb8c33a15e970abe42d7bb120e2dc84f33`.

It emits physically separate EROFS images for `system`, `system_ext`, and
`product`; it is not a folded GSI. All three fit the existing Slot-B extents
without resizing super:

| Partition | EROFS bytes in AVB descriptor | Minimum AVB/FEC bytes | B extent | Headroom | Result |
|---|---:|---:|---:|---:|---|
| system | 625823744 | 635940864 | 665391104 | 29450240 (4.426%) | FIT |
| system_ext | 235327488 | 239185920 | 366891008 | 127705088 (34.807%) | FIT |
| product | 291459072 | 296214528 | 337686528 | 41472000 (12.281%) | FIT |
| **Total** | **1152610304** | **1171341312** | **1369968640** | **198627328 (14.499%)** | **FIT** |

The files themselves are padded to their exact partition extents by AVB. The
headroom calculation therefore inverts `avbtool --calc_max_image_size` around
the descriptor's original EROFS byte count; it is not `extent - stat(image)`.
System misses the preferred 5% target by 3,819,315 bytes, but 4.426% is useful
headroom and all three images fit. Per the success condition, optimization
stopped without deleting additional normal Lineage functionality.

## What made it fit

- the physical product selects VNDK 34 only; VNDK 31/32/33 remove exactly
  131,538,944 installed bytes;
- the generic full AVF/Microdroid APEX (65,519,616 bytes) is replaced by the
  standard 1,400,832-byte AVF-disabled API APEX because pKVM support is not
  proven;
- compliance-GSI policy, GSI init/overlays, USB-debug test app, and old-HIDL
  compatibility payload are not inherited;
- EROFS uses `lz4hc,9` with a 262144-byte pcluster. On the identical frozen GSI
  split payload this reduced the three EROFS files by 200,896,512 bytes versus
  the default-pcluster measurement;
- **no optional Lineage application was removed** (`OPTIONAL_BYTES_REMOVED=0`).

## Validation

- full build completed successfully (three iterations, see
  `BUILD-ITERATIONS.tsv`);
- final `checkvintf` result: `COMPATIBLE` against the captured stock V15 vendor
  and DSDS ODM manifest, with API 35/vendor API 34 properties;
- the launch API level is declared once: `PRODUCT_SHIPPING_API_LEVEL := 35`
  makes the build system generate `ro.product.first_api_level=35` into the
  vendor-side property set, and the untouched stock `vendor/build.prop` already
  provides that value plus `ro.board.first_api_level=34` at runtime, so no
  framework-image property override is needed;
- initial 90 undeclared device-specific HAL instances were fixed using a
  required, non-optional device framework matrix; every item is recorded in
  `VINTF-INCOMPATIBILITIES.tsv`;
- `avbtool verify_image --follow_chain_partitions` passes for the generated
  root vbmeta, child vbmeta, and three hashtrees with flags 0;
- final keys are AOSP host test keys only and are **not phone acceptance keys**;
- the final payload equals the iteration-2 payload file-for-file except the four
  regenerated `build.prop` files (`/system/build.prop` is 30 bytes smaller — the
  deleted override line), so no application, library, font, media, or APEX
  changed between iterations;
- the frozen GSI SHA-256 remained
  `bae4ace2108d50bf431b9b49ccc3767e2867cb90e8290921c142d3df0c396eda`
  before and after every split build.

## Navigation

- `device-tree/` — exact buildable source snapshot
- `DEVICE-TREE-STRUCTURE.md` — file-by-file provenance
- `PRODUCT-INHERITANCE.md` — split product architecture
- `VNDK-REQUIREMENTS.tsv` / `VENDOR-ELF-DEPENDENCIES.tsv` — ABI proof
- `PARTITION-PACKAGE-MAP.tsv` — final logical ownership and size accounting
- `GENERIC-PAYLOAD-REMOVAL.tsv` — evidence-backed GSI differences
- `OPTIONAL-PACKAGES.tsv` — retained optional Lineage inventory
- `FONTS-MEDIA-WEBVIEW.md` — non-random content review
- `EROFS-COMPARISON.md` — measured compression decision
- `VINTF-CHECK.md` — failed-first/pass-final host checks
- `AVB-STRUCTURE.md` — generated and eventual phone descriptor ownership
- `SEPOLICY-STRATEGY.md` — platform 202604/vendor 34.0 split policy
- `scripts/` — the exact configure/build/verify commands used for each iteration
- `BUILD-ITERATIONS.tsv` / `FINAL-IMAGE-SIZES.tsv` — measured outcomes
- `NEXT-FIRST-BOOT-PLAN.md` — isolated-data next milestone
- `REFERENCE-GSI-*.tsv` — frozen generic package/APEX/VNDK inventories

## Artifact archive

Per-iteration host artifacts (images, `installed-files*`, build/configure logs,
`checkvintf` and `avbtool` output) are frozen under
`/mnt/WDBlue/TIER3-phase5-android17/split-iterations/`; the final iteration is
`i3-generated-properties/`.

No phone partition or phone state was accessed or changed by this build task.
