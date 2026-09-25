# Purpose

Slot B's `adb unauthorized` state was traced to an A/B property difference rather than proving that `/data` failed to mount:

- Slot A: `ro.adb.secure=0`
- Slot B: `ro.adb.secure=1`

The Slot-B Lineage candidate reaches `adbd` about 30 seconds after boot, but it enforces ADB authentication. This temporary diagnostic candidate changes only Slot B's system property `ro.adb.secure` from `1` to `0`, while retaining `ro.debuggable=1`, so the next controlled Slot-B boot can provide an authorized shell for early vold, KeyMint, and system_server capture. It is not a final ROM candidate.

This was a host-only build and verification operation. Nothing was flashed.

# Input Candidate

## System

- Path: `/mnt/SamsungSSD/TIER3/phase4/controls/keymint-parity-16-20260601/parity.img`
- Expected and verified SHA256: `6fd4b633d616ec50c6fa69c6b50471c00654974e3b2e19dfc30ed8782a2289ab`
- Final image size: `665391104` bytes
- EROFS/AVB payload size: `652840960` bytes
- EROFS UUID: `bb0b1128-e988-5128-9a1e-81753d044da9`
- Existing system root digest: `d54fad2c20b6937254bbf3cdc7b730b748098e2f`

The input image was inspected through `fsck.erofs --extract` and a read-only `erofsfuse` view. Its `system/build.prop` contains:

```text
ro.adb.secure=1
ro.debuggable=1
ro.build.version.release=16
ro.build.version.sdk=35
ro.build.version.security_patch=2026-06-01
```

## Existing vbmeta_system

- Path: `/mnt/SamsungSSD/TIER3/phase4/controls/keymint-parity-16-20260601/vbmeta_system.parity.img`
- Size: `4096` bytes
- Expected and verified full/first-4096 SHA256: `4abbcf32d6d731d538a6924d5a6363df54e354d3a37a5256d007194388f36c63`

# Build Procedure

## Recovered original parity procedure

The exact final parity procedure was recovered from:

- `slot-b-investigation/boot-chain-compare/vendor-a-on-b-control/system-keymint-parity-image/fresh-baseline-parity-build.txt`
- `slot-b-investigation/boot-chain-compare/vendor-a-on-b-control/system-keymint-parity-image/avb-repair.txt`
- `slot-b-investigation/boot-chain-compare/vendor-a-on-b-control/system-keymint-parity-image/vbmeta-system-parity-build.txt`
- the retained command transcript in local clipboard history
- `/mnt/SamsungSSD/TIER3/phase4/scripts/43-generate-bringup-vbmeta.sh`

Recovered paths and constants:

```sh
ANDROID=/mnt/SamsungSSD/android/lineage-22.2
HOSTBIN="$ANDROID/out/host/linux-x86/bin"
MKFS="$HOSTBIN/mkfs.erofs"
FSCK="$HOSTBIN/fsck.erofs"
AVB="$HOSTBIN/avbtool"
export PATH="$HOSTBIN:$PATH"     # makes the matching fec binary available

RAW_SIZE=652840960
PART_SIZE=665391104
UUID=bb0b1128-e988-5128-9a1e-81753d044da9
BUILD_TS=1786490212
SALT=b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6
FP='Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys'
KEY=/mnt/SamsungSSD/TIER3/phase4/private/avb-bringup/system.pem
```

The final parity rebuild first made fresh source trees from the original staged system image:

```sh
sudo mount -t erofs -o loop,ro "$ORIG" "$MO"
sudo cp -a --preserve=all "$MO/." "$BT/"
sudo cp -a --preserve=all "$MO/." "$PT/"
sudo umount "$MO"
```

It changed only the five then-required, equal-length Android release/security-patch property strings in `parity-tree/system/build.prop`. It then built EROFS with:

```sh
sudo "$MKFS" \
  -zlz4hc \
  -U "$UUID" \
  -T"$BUILD_TS" \
  --mkfs-time \
  "$raw" "$tree" >"$log" 2>&1

[ "$(stat -c %s "$raw")" = "$RAW_SIZE" ]
cp "$raw" "$img"
```

The proven system AVB footer command was:

```sh
"$AVB" add_hashtree_footer \
  --image "$img" \
  --partition_name system \
  --partition_size 665391104 \
  --hash_algorithm sha1 \
  --salt b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6 \
  --fec_num_roots 2 \
  --prop 'com.android.build.system.os_version:16' \
  --prop 'com.android.build.system.fingerprint:Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys' \
  --prop 'com.android.build.system.security_patch:2026-06-01'
```

The proven matching child-vbmeta command was:

```sh
"$AVB" make_vbmeta_image \
  --output "$OUT" \
  --algorithm SHA256_RSA2048 \
  --key "$KEY" \
  --rollback_index 0 \
  --rollback_index_location 0 \
  --flags 0 \
  --padding_size 4096 \
  --include_descriptors_from_image "$SYSTEM_IMG"
```

As a provenance gate, running that recovered command against the unchanged parity system reproduced `vbmeta_system.parity.img` byte-for-byte, including its expected SHA256.

## ADB-debug build execution

Work directory:

```text
/mnt/SamsungSSD/TIER3/phase4/controls/keymint-parity-16-20260601-adb-debug/
```

The retained `parity.raw.img` was mounted read-only with `erofsfuse 1.8.1`. This exposes the image's original ownership, permissions, mtimes, symlink targets, and xattrs without changing the input image. A same-length copy of `system/build.prop` was made and this assertion-guarded replacement was applied exactly once:

```python
a = b"ro.adb.secure=1"
b = b"ro.adb.secure=0"
assert len(a) == len(b)
assert data.count(a) == 1
data = data.replace(a, b)
```

A small `LD_PRELOAD` open shim redirected only the `mkfs.erofs` content read for the exact path `.../fuse-parity/system/build.prop` to that modified 5872-byte copy. All `lstat`, ownership, permission, timestamp, symlink, and xattr reads continued to resolve against the read-only source image. The recovered EROFS command and constants were otherwise unchanged:

```sh
env \
  LD_PRELOAD="$WORK/open-override.so" \
  LIEPPOS_OVERRIDE_FROM="$WORK/fuse-parity/system/build.prop" \
  LIEPPOS_OVERRIDE_TO="$WORK/build.prop.adb-debug" \
  "$MKFS" \
    -zlz4hc \
    -U bb0b1128-e988-5128-9a1e-81753d044da9 \
    -T1786490212 \
    --mkfs-time \
    "$WORK/system-b-adb-debug.raw.img" \
    "$WORK/fuse-parity"
```

The raw output was exactly `652840960` bytes. It was copied to `system-b-adb-debug.img`, then the proven `add_hashtree_footer` command above was run unchanged. EROFS repacking changed physical inode/layout bytes, as expected, but the complete mounted-tree comparison below proves the semantic and filesystem-metadata result.

Tools:

- `mkfs.erofs 1.8.1`: `/mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/mkfs.erofs`
- `fsck.erofs 1.8.1`: `/mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/fsck.erofs`
- `avbtool 1.3.0`: `/mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/avbtool`
- matching `fec`: `/mnt/SamsungSSD/android/lineage-22.2/out/host/linux-x86/bin/fec`
- `erofsfuse 1.8.1`, built host-side from the matching Lineage `external/erofs-utils` source for read-only inspection

# Semantic Delta

## Required properties

```text
OLD:
ro.adb.secure=1
ro.debuggable=1
ro.build.version.release=16
ro.build.version.sdk=35
ro.build.version.security_patch=2026-06-01

NEW:
ro.adb.secure=0
ro.debuggable=1
ro.build.version.release=16
ro.build.version.sdk=35
ro.build.version.security_patch=2026-06-01
```

Unified `build.prop` diff:

```diff
@@ -130,7 +130,7 @@
 # from variable PRODUCT_SYSTEM_DEFAULT_PROPERTIES
 ####################################
 ro.com.google.clientidbase=android-google
-ro.adb.secure=1
+ro.adb.secure=0
 persist.sys.strictmode.disable=true
 ro.control_privapp_permissions=enforce
 ro.storage_manager.enabled=true
```

## Image and filesystem sizes/hashes

| Item | Old parity | New ADB-debug |
|---|---:|---:|
| Final image SHA256 | `6fd4b633d616ec50c6fa69c6b50471c00654974e3b2e19dfc30ed8782a2289ab` | `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99` |
| Final image size | `665391104` | `665391104` |
| Raw EROFS SHA256 | `16aeec4e56aadb6e11a1080f933882b1e8cf5e21cc03bd288f97294bcaa70659` | `c21c1b4f9218deb34948c99b536342a30b9c5c299736c6164d5addb6e15522e0` |
| Raw EROFS size | `652840960` | `652840960` |
| `system/build.prop` SHA256 | `aaf4cf7743cb67c216508a7aafbec194fe50f731d1ed8d46ff3cbb9c2389df51` | `d76787028d2984c801fc0ff94c743168abde9039e295678264c23e5783c68edf` |

## Complete mounted-tree comparison

Both final images were mounted read-only with `erofsfuse`. Every path was compared for type, mode, UID, GID, size, mtime, link count, device number, xattr names/values, symlink target, and regular-file SHA256.

```text
OLD_PATH_COUNT=3289
NEW_PATH_COUNT=3289
COMMON_PATH_COUNT=3289
REGULAR_FILE_COUNT=2711
ADDED_COUNT=0
REMOVED_COUNT=0
CONTENT_DIFF_COUNT=1
METADATA_DIFF_COUNT=0
XATTR_DIFF_COUNT=0
SYMLINK_DIFF_COUNT=0
TYPE_DIFF_COUNT=0
```

Files whose contents differ:

```text
system/build.prop
```

Added files: none.

Removed files: none.

There are no unexplained semantic changes. The only file-content change is the intended `ro.adb.secure=1` to `ro.adb.secure=0` edit, and there are no filesystem metadata or xattr differences.

`fsck.erofs` returned 0. Embedded system AVB self-verification also succeeded for the full `652840960`-byte payload.

# AVB

## New system image

- Path: `/mnt/SamsungSSD/TIER3/phase4/controls/keymint-parity-16-20260601-adb-debug/system-b-adb-debug.img`
- SHA256: `68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`
- Size: `665391104` bytes
- Root digest: `aa57361b018f99c0985c15b2e29934192849adeb`
- Hash algorithm: `sha1`
- Salt: `b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6`
- FEC roots: `2`
- Tree offset: `652840960`
- Tree size: `5148672`
- FEC offset: `657989632`
- FEC size: `5201920`

The three AVB properties remain:

```text
com.android.build.system.os_version=16
com.android.build.system.fingerprint=Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys
com.android.build.system.security_patch=2026-06-01
```

## New vbmeta_system

- Path: `/mnt/SamsungSSD/TIER3/phase4/controls/keymint-parity-16-20260601-adb-debug/vbmeta_system.adb-debug.img`
- Full/first-4096 SHA256: `9adb5fb2d3b2375d08884bdb1721097fa26b96f6cbb708408cec47b7862ddfc9`
- Size: `4096` bytes
- Algorithm: `SHA256_RSA2048`
- Public key SHA1 identity: `579a140d204d847f0c74332c73996baf1ed6a5fc`
- Extracted AVB public-key blob SHA256: `7ec327ef73c0452ffc116973ef347f83c3300acd51f057b61959369abe031e7b`
- Signing key file SHA256: `901233f64c8b5443bca5f6c5043adbb24455ff4641061b31e5b5597cd3245d09`
- Rollback index: `0`
- Rollback index location: `0`
- Flags: `0`
- Release string: `avbtool 1.3.0`

Descriptor structure:

```text
Prop: com.android.build.system.os_version -> '16'
Prop: com.android.build.system.fingerprint -> 'Ulefone/lineage_armol/armol:15/BP1A.250505.005/eng.armol:userdebug/test-keys'
Prop: com.android.build.system.security_patch -> '2026-06-01'
Hashtree descriptor:
  dm-verity version: 1
  image size: 652840960
  tree offset: 652840960
  tree size: 5148672
  data/hash block size: 4096/4096
  FEC roots: 2
  FEC offset: 657989632
  FEC size: 5201920
  hash algorithm: sha1
  partition: system
  salt: b6497d667c35b54999e4eee6d8c57a3e606fe5bf5d1c2e4919e201e5fb624aa6
  root digest: aa57361b018f99c0985c15b2e29934192849adeb
  flags: 0
```

Compared with `vbmeta_system.parity.img`, `avbtool info_image` differs only in the necessary system root digest:

```diff
-Root Digest: d54fad2c20b6937254bbf3cdc7b730b748098e2f
+Root Digest: aa57361b018f99c0985c15b2e29934192849adeb
```

The signing identity, algorithm, rollback fields, flags, AVB properties, hashtree geometry, hash algorithm, salt, FEC structure, and partition name are unchanged. `avbtool verify_image --key .../system.pem` successfully verified both the signed vbmeta structure and the new system hashtree. The system image's embedded root digest and the child-vbmeta descriptor root digest match exactly.

No root `vbmeta_b` image was read, modified, regenerated, or written.

# Size / Flashability

The existing `system_b` logical allocation is `665391104` bytes.

```text
new system image size: 665391104
system_b allocation:   665391104
fits:                  yes
exact size:            yes
```

No super resize or super metadata change is needed or was performed.

# Safety

- No Slot A partition was written.
- No Slot B or other device partition was written.
- No device was flashed during this task.
- No userdata or metadata operation was performed.
- No userdata or metadata filesystem was formatted, checked, repaired, or wiped.
- No shared metadata encryption key or key blob was altered.
- No super resize was performed.
- No super metadata was changed.
- No factory reset was performed.
- This was a build-only, host-side verification operation.

# Next Boot Procedure

**Not performed in this task.** The next separately authorized device test will:

1. Verify the phone currently runs Slot A.
2. Verify the metadata key blob hash.
3. Verify the current Slot-B candidate backup.
4. Write the new system image to `system_b` using the already-proven RW dm mapping technique.
5. Flash/write the new 4 KiB `vbmeta_system_b`.
6. Verify exact readback hashes.
7. Set Slot B active with `bootctl`.
8. Capture authorized ADB immediately.
9. Return to Slot A through bootloader fastboot.
10. Recheck the shared metadata key.
