# Product-B Google split-permission diagnostic candidate

## Scope and safety

This was an **offline build and read-only analysis task**. Nothing was flashed.
Slot A was not modified. Userdata, metadata, package state, and dynamic-partition
sizes were not changed. No factory reset, format, or device-side filesystem check
was performed.

The generated images remain outside Git under:

`/mnt/SamsungSSD/TIER3/phase4/controls/product-b-no-gms-split-debug/`

## Runtime blocker

The authorized Slot-B diagnostic boot reaches a substantially working Android
userspace: `/data` and user-0 CE storage are mounted, and `vold`, `keystore2`,
SurfaceFlinger, and the boot animation are running. The current blocker is a
repeated `system_server` / zygote crash loop with this exact fatal exception:

```text
java.lang.IllegalStateException: Unknown source permission
com.google.android.gms.permission.ACTIVITY_RECOGNITION in split permissions
```

The declaration is in
`product_b/etc/permissions/split-permissions-google.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <split-permission name="com.google.android.gms.permission.ACTIVITY_RECOGNITION"
                      targetSdk="29">
        <new-permission name="android.permission.ACTIVITY_RECOGNITION" />
    </split-permission>
</permissions>
```

The source permission string was not found in `system_b`, `system_ext_b`,
`vendor_a`, or `vendor_b`. Slot-B PackageManager logs also report that
`com.google.android.gms` is missing.

## Product A/B comparison

The captures were inspected read-only.

| Image | Filesystem | Exact size | SHA-256 |
|---|---:|---:|---|
| `product_a` | EROFS | 1,855,819,776 bytes | `d1d8ae6d91ec722a012c716b8029483e2cf544cbccf111db84ec80fe8234e09c` |
| current `product_b` | EROFS | 337,686,528 bytes | `10c17f4eea7ba7d79b22d85f88672a3e0694113777ab6a49dd225f67f463e1a1` |

They are not byte-identical and do not represent the same ROM composition.

### Split permission and Google configuration

`product_a` **does contain the same**
`etc/permissions/split-permissions-google.xml`. The A and B copies are
byte-identical:

- size: 288 bytes
- SHA-256: `259cae2124ee93641d38812f0d25b62785d40ad514f78faad45473a984aad8dd`
- content: the XML shown above

For Google/GMS-related entries under `etc/permissions` and `etc/sysconfig`, A
and B have 16 common files and every common file is byte-identical. B has one
additional file:

`etc/sysconfig/lineage-component-overrides.xml`

The common configuration includes, among other files:

- `etc/permissions/privapp-permissions-google-product.xml`
- `etc/permissions/split-permissions-google.xml`
- `etc/sysconfig/google.xml`
- `etc/sysconfig/google-initial-package-stopped-states.xml`
- `etc/sysconfig/google-staged-installer-whitelist.xml`

The complete paths, sizes, and hashes are in
[`product-ab-semantic-analysis.txt`](product-ab-semantic-analysis.txt).

### Package composition explains why A tolerates the rule

Product A contains 85 APK package records and has a full Google package set,
including:

- `priv-app/GmsCore/GmsCore.apk` — package `com.google.android.gms`,
  173,178,617 bytes
- `priv-app/Phonesky/Phonesky.apk` — package `com.android.vending`,
  85,729,596 bytes

The live-A permission registry attributes
`com.google.android.gms.permission.ACTIVITY_RECOGNITION` to
`com.google.android.gms`.

Product B contains 108 APK package records but no `com.google.android.gms` and
no `com.android.vending`. Its Google-named APKs are primarily GMS configuration
or framework overlays; they do not provide the missing source permission.
Thus the same split XML is internally satisfiable on A but orphaned on the
current B composition.

## Product-B construction provenance

The current product-B image is not the stock Ulefone product and is not an
unidentified GSI artifact. Its exact size, SHA-256, EROFS UUID, and AVB-bearing
form match the recorded `product.img` from the custom LineageOS armol build
`/mnt/SamsungSSD/TIER3/phase3/inventory/builds/run-20260811T230645Z/`:

```text
out/target/product/armol/product.img
size   337686528
sha256 10c17f4eea7ba7d79b22d85f88672a3e0694113777ab6a49dd225f67f463e1a1
```

The established preservation/rebuild route was reused rather than inventing a
new filesystem format:

- `erofsfuse` 1.8.1 for a read-only source tree
- host `mkfs.erofs` with the original LZ4HC mode, UUID, and mkfs time
- a directory-entry filter shim that hides only the target XML while mkfs reads
  the otherwise unchanged FUSE tree
- host `avbtool` plus `fec` to reproduce the existing hashtree/FEC/footer layout
- tree comparison of path type, content, UID/GID, mode, mtime, nlink, rdev,
  regular-file size, symlink target, and xattrs

## Minimal diagnostic candidate

Candidate image:

`/mnt/SamsungSSD/TIER3/phase4/controls/product-b-no-gms-split-debug/product-b-no-gms-split-debug.img`

| Field | Current B | Candidate |
|---|---:|---:|
| Filesystem | EROFS | EROFS |
| Exact partition-image size | 337,686,528 | 337,686,528 bytes |
| EROFS UUID | `5f6ef6ab-aa46-5964-b0fb-7328cf61f6f5` | same |
| SHA-256 | `10c17f4eea7ba7d79b22d85f88672a3e0694113777ab6a49dd225f67f463e1a1` | `a0a7eb7692dfc27e261d17eef366cd43beff351f5e67979ae35aa1d2e17d329d` |

The final candidate passes host `fsck.erofs`. Its embedded product hashtree
verifies successfully with `avbtool` when presented under the descriptor's
exact partition name.

### Complete semantic delta

```text
old paths:                 707
new paths:                 706
common paths:              706
added paths:               0
removed paths:             1
content differences:       0
type differences:          0
mode differences:          0
owner differences:         0
mtime differences:         0
nlink differences:         0
rdev differences:          0
regular-size differences:  0
xattr differences:         0
symlink differences:       0

REMOVED: etc/permissions/split-permissions-google.xml
```

The only other reported value is the expected EROFS directory-size accounting
change for `etc/permissions`, from 835 to 795 bytes, caused by removing that
single directory entry. No other path or metadata changed semantically.

Machine-readable evidence:

- [`product-b-candidate-semantic-diff.txt`](product-b-candidate-semantic-diff.txt)
- [`product-b-candidate-artifact-manifest.txt`](product-b-candidate-artifact-manifest.txt)
- [`product-b-candidate-avb-verify.txt`](product-b-candidate-avb-verify.txt)

## AVB ownership and matching metadata

### Proven owner

The product hashtree descriptor is owned directly by **root `vbmeta_b`**, not
by `vbmeta_system_b` or `vbmeta_vendor_b`.

Current product descriptor in `vbmeta_b`:

| Field | Value |
|---|---|
| descriptor type | AVB hashtree descriptor |
| partition name | `product` |
| image size | 331,276,288 bytes |
| tree offset | 331,276,288 |
| tree size | 2,613,248 bytes |
| data/hash block size | 4,096 / 4,096 bytes |
| hash algorithm | SHA-1 |
| salt | `b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6` |
| current root digest | `82f2881b4fb4830478455dec29bab5a67274b0e1` |
| FEC roots | 2 |
| FEC offset | 333,889,536 |
| FEC size | 2,646,016 bytes |
| descriptor flags | 0 |

The product footer's embedded vbmeta has rollback index 0, rollback-index
location 0, and flags 0. Root `vbmeta_b` has algorithm `SHA256_RSA2048`,
rollback index 0, rollback-index location 0, and the already-active diagnostic
flags value 3. Those root flags were preserved exactly; AVB was not weakened
further.

The current root's embedded AVB public key and the public key extracted from
the existing bring-up signing identity both hash to:

`2540a16cdbdafe1a3fc08fbef83b5dc876099b881e174b63a895b6def8798d50`

No private key material is recorded here.

### New matching root vbmeta

Because root `vbmeta_b` directly owns `product`, a matching root image was
required. No change to `vbmeta_system_b` or `vbmeta_vendor_b` was required.

Image:

`/mnt/SamsungSSD/TIER3/phase4/controls/product-b-no-gms-split-debug/vbmeta_b.product-no-gms-split-debug.img`

- exact size: 8,192 bytes
- SHA-256: `41afac0837a1d4d6d012fe745160a2cadf8463f55e3f3ff737b7f97f99e10844`
- signature: valid
- signing public-key identity: identical to current root
- flags, rollback fields, algorithm, release string, and descriptor order:
  identical to current root
- descriptor count: 28 before and 28 after
- all non-product descriptors: byte-identical
- product descriptor: every field identical except root digest
- new product root digest:
  `2cee01617463eb37655a0913b6c695da5b7e52f7`
- candidate product's embedded descriptor and the new root product descriptor:
  byte-identical

The exact complete descriptor listings before and after are retained in:

- [`product-b-root-vbmeta-before.txt`](product-b-root-vbmeta-before.txt)
- [`product-b-root-vbmeta-after.txt`](product-b-root-vbmeta-after.txt)
- [`product-b-root-vbmeta-descriptor-audit.txt`](product-b-root-vbmeta-descriptor-audit.txt)
- [`product-b-root-vbmeta-signature-verify.txt`](product-b-root-vbmeta-signature-verify.txt)

## Why the split rule is invalid on this B composition

A split-permission declaration maps an existing source permission to one or
more newer permissions for compatibility with older target SDKs. During
PackageManager permission-policy evaluation, the source permission must exist
in the permission registry. On A, GmsCore defines the Google source permission.
On B, the configuration file remains but the package that defines its source
permission is absent, leaving an orphaned split declaration. The framework
therefore cannot resolve the source and throws the observed
`IllegalStateException`.

## Evidence classification

### PROVEN

- The exact fatal exception occurs in the authorized Slot-B capture.
- `product_b/etc/permissions/split-permissions-google.xml` declares the source
  named in the fatal.
- The source string was not found in the searched B system/system_ext and A/B
  vendor images.
- Product B has no `com.google.android.gms` package; PackageManager reports it
  missing.
- Product A has the same XML but also has GmsCore, and live A attributes the
  source permission to `com.google.android.gms`.
- Product B is the recorded custom Lineage armol product image.
- The candidate's only intentional and observed path delta is removal of the
  split XML; all compared file metadata and content for common paths match.
- The candidate image size and AVB layout match current B.
- Root `vbmeta_b` owns the product descriptor. The matching root signature is
  valid and only the product root digest changed.
- Nothing was flashed in this task.

### INFERRED

The incompatible combination of an orphaned Google split-permission rule and
an absent GmsCore permission owner is the immediate cause of the observed
PackageManager fatal. This is strongly supported by direct provenance, but the
causal claim still requires a controlled boot.

### TEST TO CONFIRM

Boot Slot B with only these paired B artifacts changed:

1. the minimal diagnostic `product_b` candidate; and
2. its matching root `vbmeta_b` image.

Success for this hypothesis is disappearance of the exact unknown-source
permission fatal and progression beyond the current `system_server` crash
loop. A later, different blocker would not invalidate this narrow result.

## Next controlled boot plan (not executed)

1. Reconfirm Slot A is booted, healthy, marked successful, and retain current
   B `product_b`/`vbmeta_b` readback hashes.
2. Obtain separate explicit authorization for a flash operation.
3. Flash only the candidate to `product_b` and its paired image to `vbmeta_b`;
   do not touch A, userdata, metadata, super size, or package state.
4. Re-read and hash both B targets before attempting a boot.
5. Attempt one controlled B boot and capture early boot, PackageManager,
   `system_server`, and boot-completion state.
6. If B loops, return to known-good A without wiping. Preserve logs before any
   separately authorized restoration of the prior B pair.

**No part of this boot plan was performed during this task.**
