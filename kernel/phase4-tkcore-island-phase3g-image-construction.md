# TrustKernel Phase 3G — minimized Slot-B image construction

Classification: **CONSTRUCTION VALIDATED / DEVICE TRIAL FAILED BEFORE G1 / DO NOT RETRY AS-IS**.

The images were flashed once to Slot B under explicit authorization and verified byte-exact from A. The single B boot never reached ADB and fell back to A. All B partitions were then restored to their exact retained stock hashes under renewed authorization; A remains the known-good active slot. See `phase4-tkcore-island-phase3g-device-trial.md`.

## Minimized first-boot delta

The staged runtime test changes exactly two module payloads:

| Stock path | Staged module | SHA-256 | Bytes | Vermagic | Runtime choice |
|---|---|---|---:|---|---|
| vendor boot platform `/lib/modules/tkcore.ko` | source `tkcore` | `e156a9c0bbdcc9668ee0b59549c0544ef2c8394fb4cebbfa60887a1025bfbc9a` | 199592 | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` | replace |
| vendor boot platform `/lib/modules/tkcore_drv.ko` | stock `tkcore_drv` | unchanged | 63480 | stock | retain |
| vendor_dlkm `/lib/modules/tmem_ffa.ko` | source `tmem_ffa` | `073523e878fe97603680a6ade234ffb00e34099664ec0f4620af9baba54e1c44` | 151448 | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` | replace |
| vendor boot platform `/lib/modules/microarray_fp_tee.ko` | stock MicroArray | unchanged | unchanged | stock | retain |

Stock `ffa_v10`, `gz_tz_system`, `fingerprint`, `spi-mt65xx`, all dependency metadata and every `modules.load*` file are retained.

The two source modules are the already accepted Phase-3E/3F code rebuilt with a controlled Kleaf SCM stamp. Relative to the frozen `-maybe-dirty` acceptance files, executable/data sections are unchanged; only `.modinfo`, its derived build ID and corresponding symbol-table metadata differ. The canonical unstamped Bazel outputs were then restored and the Phase-3F verifier remained **181/181**.

## Final images

Artifact root (gitignored build workspace):

`workspace/phase4-tkcore-island/phase3g/build/`

| Partition | Final image | Bytes | SHA-256 | Current exact rollback image |
|---|---|---:|---|---|
| `vendor_boot_b` | `vendor_boot_b.phase3g.img` | 67108864 | `df684678914292c285d7c37d757a77807d7278889ca503018da97573cd47886f` | `slot-b-investigation/device-dumps/vendor_boot_b.img` (`c8953d16b7a47976362aa23b53d0a08dde451f25cab4c552fa70c43e56ee0756`) |
| `vendor_dlkm_b` | `vendor_dlkm_b.phase3g.img` | 17534976 | `7612591d67c3042a649dbd08bbd542ed7a16a18fb794303b58be962088d8833c` | `slot-b-investigation/device-dumps/vendor_dlkm_b.img` (`fce7acfb64956126a03929f085050ab1b300272333e84abf27b9e708aaa40297`) |
| `vbmeta_b` | `vbmeta_b.phase3g.img` | 8388608 | `43cd2bb0a71b1f7cdb4619a3d8969363ee36a860289a137a50c68d7372bd5a0f` | `slot-b-investigation/device-dumps/vbmeta_b.img` (`e14e11e184950d487b31def17a349f4f161e34988825bf35d85fc9bd6c3bde93`) |

`vbmeta_vendor_b` is not changed: its sole descriptor is for `vendor`; the authoritative `vendor_boot` hash and `vendor_dlkm` hashtree descriptors are both in top-level `vbmeta_b`.

## `vendor_boot_b` proof

The stock legacy-LZ4 platform ramdisk was decompressed byte-exactly. A direct `newc` CPIO transform preserved all 713 member names, headers, order and payloads except:

- `lib/modules/tkcore.ko`: stock `03837d...d226`, 221352 bytes → source `e156a9...bc9a`, 199592 bytes.

The transformed CPIO was recompressed using the stock-reproducing `lz4 -l -12` mode. Fresh unpacking of the final image proved:

- boot header and vendor ramdisk table arguments equal to stock;
- DTB, recovery ramdisk, bootconfig and every non-platform output byte-identical;
- only `vendor_ramdisk00` differs;
- decompression returns the exact transformed CPIO;
- the extracted source `tkcore` has the exact stock vermagic and no intermodule dependency.

The valid rebuilt payload was zero-padded to the stock 33828864-byte hash extent before adding the AVB hash footer. Full partition size remains 67108864. `avbtool verify_image` passes.

Evidence: `vendor_boot-phase3g.build.log`, `vendor_boot-phase3g.validation.txt`.

## `vendor_dlkm_b` proof

A read-only EROFS inspector recovered every inode's exact logical metadata, including security xattrs. The stock filesystem contains 227 inodes: all uid/gid 0, four mode-0755 directories, 223 mode-0644 files, fixed timestamp 1230768000 and one SELinux label per inode (`vendor_file`, except the five `etc`/config entries labelled `vendor_configs_file`).

An unchanged tar-source EROFS round trip proved **0/227 content mismatches** and **0/227 metadata/xattr mismatches**. The final rebuild then changed only:

- `/lib/modules/tmem_ffa.ko`: stock `707e26...f01b` → source `073523...1c44`.

All 226 other inode payloads and all 227 logical metadata/xattr records match stock. `fsck.erofs` passes. Stock UUID, timestamp, LZ4 big-pcluster configuration and feature set (`sb_csum mtime 0padding compr_cfgs big_pcluster`) are preserved. The smaller valid EROFS was zero-padded to the stock 17125376-byte dm-verity extent; AVB tree/FEC geometry and full 17534976-byte partition size therefore remain stock-identical. The generated hashtree verifies.

Evidence: `vendor_dlkm-stock-manifest.json`, `vendor_dlkm-phase3g.mkfs.log`, `vendor_dlkm-phase3g.avb.log`, `vendor_dlkm-phase3g.validation.txt`.

## `vbmeta_b` necessity and proof

Stock top-level `vbmeta_b` directly records both changed payloads. Leaving it untouched would supply a stale vendor-boot digest and stale vendor-dlkm dm-verity root.

The final image preserves the exact 27-descriptor multiset from current `vbmeta_b`, with exactly two intended descriptor field changes:

- `vendor_boot` SHA-256 digest → `0fcdd8decf0e06d4aa476007017449dddd76b4892c83ed9208e1a254a624afa6`;
- `vendor_dlkm` root digest → `760992a426d42529f77d1e71638343eeee306af53ce4f5c99fa6c9aac0d70995`.

Flags remain 0: verification and dm-verity are not disabled. Rollback index remains 0. The image is coherently signed with the local AOSP AVB RSA-2048 test key (AVB public-key SHA-1 `cdbb77177f731920bbe0a0f94f84d9038ae0617d`), not the unavailable current private key. This image therefore requires the already proven bootloader-unlocked state (`unlocked=yes`, `secure=no`) and must never be attempted after relocking.

`avbtool` verifies the new top-level signature, all three unchanged chain descriptors/keys, stock `dtbo_b`, stock `init_boot_b`, and the new `vendor_boot_b`. Complete host traversal then stops only because the unchanged dynamic `odm_dlkm_b` image was not retained locally. The full descriptor multiset for all unavailable children is copied byte-exactly from current bootable `vbmeta_b`; the new parent vendor-dlkm root equals the independently verified child footer.

Evidence: `vbmeta-phase3g.build-validation.txt`.

## Pre-flash stop gate

Before any write, reconnect the authorized serial and freshly prove:

1. serial `5012BF3010001335` only;
2. A active, bootable and successful; B bootable;
3. Fastboot still reports `unlocked=yes`, `secure=no`;
4. current `vendor_boot_b`, `vendor_dlkm_b` and `vbmeta_b` hashes still equal the rollback images above;
5. the host final-image hashes still equal this report;
6. the user explicitly authorizes the three listed B-only partition writes.

Any mismatch stops the operation. No A-slot partition, userdata, RPMB, calibration, NVRAM or persist partition is in scope.
