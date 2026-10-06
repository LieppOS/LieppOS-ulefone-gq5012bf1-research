# A/B slot and AVB boundary for module loading

## Slot ownership

| artifact | partition | slot selection |
|---|---|---|
| GKI kernel `Image` | `boot_a/_b` (ramdisk empty) | LK, active slot |
| first-stage `/init` (+ libmodprobe) | `init_boot_a/_b` | LK, active slot |
| first-stage modules + `modules.load{,.recovery}`, `fstab.mt6878` | `vendor_boot_a/_b` | LK, active slot |
| `vendor_dlkm`, `system_dlkm`, `odm_dlkm`, `vendor`, `system` | logical (super), `slotselect` in fstab | first-stage init uses `androidboot.slot_suffix` (bootconfig, e.g. `"_a"`) |
| `init.insmod.sh`, cfg, `init.mtkgki.rc`, `toolbox`(modprobe) | `vendor_X` | same suffix |

All module metadata are owned by the partition that holds the modules; `modules.dep` uses
absolute paths (`/lib/modules/…`, `/vendor_dlkm/lib/modules/…`, `/system_dlkm/lib/modules/…`)
and contains no slot information. A single boot therefore always uses one slot for
everything; stock has no path that mixes `vendor_boot_a` with `vendor_dlkm_b`.

- Mixed slots are only possible by hand-editing partitions. The loader would still run;
  what decides success is the kernel: every first-stage and vendor module must match the
  running GKI kernel's KMI (modversion CRCs) and must not export GKI-protected symbols. The
  vendor modules carry `vermagic 6.1.115-android14-11-g945dff7bc1bf …`, the GKI kernel is
  `…-g6b18f0b574ab-ab12901745`; the release token is ignored under `modversions`, so the
  `vendor_boot`/`vendor_dlkm` pair loads on any kernel with the same KMI CRCs.
- `vendor_boot` and `vendor_dlkm` must come from the same build: 13 modules are shipped in
  both, the first-stage copy wins (EEXIST for the second); a vendor_dlkm module whose hard
  dep is a first-stage module of a different build would fail on CRC.
- Slot B can independently carry its own kernel + vendor_boot + vendor_dlkm + vendor; the
  previous slot-B stall was caused by a missing `/vendor/etc/init.insmod.mt6878.cfg` on
  `vendor_b` (see `INIT-INSMOD` notes), not by module/slot mixing.

## AVB / dm-verity

From `slot-b-investigation/07-avbtool-info.txt` and `phase3g-r/c0/stock-vbmeta-info.txt`:

| artifact | protection |
|---|---|
| `boot` (kernel) | chained `vbmeta` descriptor (rollback location 3) → hash |
| `init_boot`, `vendor_boot` (first-stage modules and lists) | hash descriptors in top-level `vbmeta` (sha256) |
| `vendor_dlkm`, `system_dlkm`, `odm_dlkm` | **hashtree** descriptors in top-level `vbmeta` → dm-verity at first_stage_mount |
| `vendor` (init.insmod.sh, cfg, rc, modprobe) | hashtree via chained `vbmeta_vendor` |
| individual `.ko` | system_dlkm GKI modules carry module signatures (60/60); vendor_boot/vendor_dlkm `.ko` are unsigned (0/411) — integrity comes only from AVB/dm-verity |

Stock unit runs `androidboot.verifiedbootstate=orange` (unlocked): images may be replaced,
but each changed hash/hashtree must be consistent with the vbmeta that is booted (or
verification disabled in vbmeta flags). Changing `modules.load` therefore means
re-signing/re-hashing the containing partition's descriptor.
