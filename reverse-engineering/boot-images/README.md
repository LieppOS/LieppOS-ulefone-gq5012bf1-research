# BOOT-IMAGES — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/BOOT-IMAGES` → **DONE**.

## Scope

This covers the image *containers*: `boot`, `init_boot` and `vendor_boot`
(header v4, GKI split), their fragment layout, and the AVB hash footers and
`vbmeta` descriptors that bind them.

Not in scope (integration or other components):
* Building and booting a custom kernel through this container. That is
  integration (LieppOS kernel bring-up).
* Release signing keys (AVB-SIGNING-CHAIN, DONE).
* The recovery payload (RECOVERY-ORANGEFOX).

## Result

**Every stock image is reproduced byte-for-byte by AOSP `mkbootimg`.**
`scripts/boot_roundtrip.py` unpacks each image with `unpack_bootimg.py
--format=mkbootimg` and repacks it with `mkbootimg.py`, using the GKI
workspace `tools/mkbootimg`. Output is in `evidence/roundtrip.txt`.

| image | repacked body | AVB hash descriptor | in vbmeta of its slot |
|---|---|---|---|
| boot_a / boot_b | identical (16 506 880 B) | footer digest **matches** (signed footer, chained `boot`, rollback location 3) | chain descriptor |
| init_boot_b | identical (2 351 104 B; `--os_version 15.0.0 --os_patch_level 2026-07`) | matches | vbmeta_b hash **matches** |
| vendor_boot_b | identical (33 828 864 B; 2 fragments: PLATFORM `''` + RECOVERY `recovery`; `bootopt=64S3,32N2,64N2`) | matches | vbmeta_b hash **matches** |
| dtbo_a / dtbo_b | — | — | vbmeta hash **matches** (48 320 B) |
| init_boot_a | identical repack | **does not match vbmeta_a** | modified: KernelSU LKM patch (`init` → KernelSU loader, `init.real`, `kernelsu.ko`) |
| vendor_boot_a | identical repack (62 697 472 B) | **does not match vbmeta_a** | modified: OrangeFox recovery fragment (447 fox/twres entries) |

So slot **B** is the verified stock baseline, while slot **A** carries our
test modifications. The packing rules are exact in both cases, so any custom
image built with the recorded argument sets is structurally stock-identical.

The vbmeta chain is the same in both slots:
* `vbmeta_{a,b}` (alg 1) holds hash descriptors for `dtbo`, `init_boot` and
  `vendor_boot`;
* it chains to `boot` (rollback location 3), `vbmeta_system` (2) and
  `vbmeta_vendor` (4).

## Packing contract (for LieppOS)

* `boot`: `--header_version 4 --kernel <Image.gz-class> --ramdisk <empty>`.
  The footer is a signed chained partition, so a custom kernel needs the
  `boot` chain key (AVB-SIGNING-CHAIN).
* `init_boot`: `--header_version 4 --os_version 15.0.0 --os_patch_level
  2026-07 --ramdisk <GKI ramdisk>`. Its hash lives in the top-level
  `vbmeta`.
* `vendor_boot`: the args recorded in `evidence/roundtrip.txt` (page 0x1000,
  offsets, cmdline, DTB, bootconfig). It has exactly two fragments,
  type 1 `''` and type 2 `recovery`, and its hash lives in `vbmeta`.
* Use the existing `vbunpack.py`/`vbrepack.py` for recovery-only swaps.

## Boundaries

On-device boot of a custom kernel/ramdisk and release signing are
integration work. Container format, chain and digests are fully determined.
