# Product-B vanilla candidate build

## Inputs

Current split-permission-fixed base:

`/mnt/SamsungSSD/TIER3/phase4/controls/product-b-no-gms-split-debug/product-b-no-gms-split-debug.img`

- SHA-256: `a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d`
- exact size: `337686528` bytes
- EROFS UUID: `5f6ef6ab-aa46-5964-b0fb-7328cf61f6f5`

New work directory:

`/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/`

## Build method

`erofsfuse` was not used.

1. The base was extracted read-only with `fsck.erofs --extract`.
2. Source inode UID/GID, mode, nlink, timestamp, and xattr-size metadata were
   recorded directly from the EROFS image.
3. A complete canned Android fs-config was generated. This preserves the seven
   `root:shell` product-bin entries while all other source owners remain exact.
4. The same compiled Lineage platform file-context source used by the build was
   passed to `mkfs.erofs`, restoring the exact SELinux labels.
5. An unchanged baseline was rebuilt before changing the tree. It reproduced
   the source EROFS size, UUID, inode count, block count, owner, mode, nlink,
   timestamp, and xattr-size geometry with zero metadata differences.
6. Only manifest-approved files present in the current base were deleted.
7. A deterministic vanilla corrective RRO was added.
8. The image was rebuilt with the original LZ4HC mode, UUID, and mkfs time.
9. The EROFS payload was zero-padded to the original `331276288`-byte AVB data
   geometry before regenerating the identical hashtree/FEC/footer layout.

## Corrective framework RRO

The stock auto-generated product RRO cannot be removed: it contains 88 required
Ulefone/MTK device resources. It also sets these two stock-Google package names:

- `config_defaultCaptivePortalLoginPackageName=com.google.android.captiveportallogin`
- `config_defaultModuleMetadataProvider=com.google.android.modulemetadata`

The candidate adds:

`overlay/VanillaFrameworkPackageConfigOverlay/VanillaFrameworkPackageConfigOverlay.apk`

Manifest/resource facts:

- package: `org.lineageos.overlay.armol.vanilla.config`
- target: `android`
- static: `true`
- priority: `999`
- signing certificate: the same Lineage test-key identity used by product
  overlays in this build
- APK SHA-256:
  `83d098d91421d402e05aa42f0b42edd5027d8c37085f7915a5fa1ae4570c7b90`
- effective values:
  - `config_defaultCaptivePortalLoginPackageName=com.android.captiveportallogin`
  - `config_defaultModuleMetadataProvider=com.android.modulemetadata`

The Google ExtServices overlay itself is removed, allowing the unchanged
framework base value `android.ext.services` to apply.

## Removal counts

- cumulative approved removal entries: **32**
- already absent in the input after the proven live test: **1**
  (`etc/permissions/split-permissions-google.xml`)
- additional files removed from this build input: **31**
- added paths: **2** (one corrective-overlay directory and one APK)

The authoritative list is
[`VANILLA-REMOVAL-MANIFEST.tsv`](VANILLA-REMOVAL-MANIFEST.tsv).

## Final artifact

`/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/product-b-vanilla-debug.img`

- SHA-256: `e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b`
- exact size: `337686528` bytes
- EROFS UUID: unchanged
- AVB data image size: `331276288` bytes
- `fsck.erofs`: pass
- `avbtool verify_image`: pass

## Semantic verification

Current base paths: `706`

Candidate paths: `677`

Common paths: `675`

| Check on common paths | Differences |
|---|---:|
| regular-file content | 0 |
| type | 0 |
| UID | 0 |
| GID | 0 |
| mode | 0 |
| mtime | 0 |
| regular-file size | 0 |
| rdev | 0 |
| SELinux/xattr geometry | 0 |
| symlink target | 0 |

One common-directory nlink changes as expected: `overlay` changes from 71 to 72
because the corrective overlay adds one child directory. Nineteen directory
record sizes change solely because approved directory entries were removed or
the corrective directory was added. No unexplained change exists.

No existing common file changed content. Filesystem-prefix comparison proves
the verified final AVB image contains the exact audited EROFS payload.

## Remaining exact strings

No remaining product XML/config file requires
`com.google.android.ext.services` or `com.google.android.gms`. No remaining
product APK resource defines `config_servicesExtensionPackage` or a GMS package
requirement.

Exact residual strings are classified in
[`REMAINING-GOOGLE-STRING-HITS.tsv`](REMAINING-GOOGLE-STRING-HITS.tsv). They are
compatibility code or data, not PackageManager requirements. In particular,
the retained Ulefone RRO mentions Google ExtServices only in a process-cleaner
whitelist array, not in `config_servicesExtensionPackage`.

## Unchanged partitions

- `SYSTEM_MODIFICATION_REQUIRED=0`
- `SYSTEM_EXT_MODIFICATION_REQUIRED=0`
- no vendor or DLKM partition was rebuilt
- debug `system_b` remains
  `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`
