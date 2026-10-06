# Slot-B plain-reboot logo hang (2026-10-03): post-mortem boundary from Slot A

This pass looks at the controlled plain `adb reboot` A→B attempt
(`../slot-b-plain-reboot-mode-controlled-test-20261003`, reboot at
2026-10-03 14:25:48 host time). The B attempt hung at the logo, and the phone was
manually returned to Slot A, whose rescue boot started at about 14:45.

Everything here was collected **read-only from healthy Slot A** on 2026-10-07:
no Slot-B boot, no partition or boot-control write, no reboot.
`scripts/slotb-postmortem-collect.sh` performs the whole collection and was run end-to-end;
its output is in `collection/`. Static checks are in `static/`.

## Result

**DEEPEST_PROVEN_B_STAGE = Android 17 second-stage init, `on early-init`**
(aconfigd ran at 14:26:08.964, about 20.9 s after `adb reboot`).

**B never mounted /data and never reached apexd's post-fs-data activation.**
The hang therefore sits between early-init and the /data mount, which covers
`fs` → `post-fs` → `late-fs` → `post-fs-data`.

**Primary root-cause candidate (static, exact flashed vendor_b):** the B vendor
(`vendor_b`, sha256 `9f3dfe3f…`, the "compact Phase-4" Lineage vendor) has **no
`/vendor/etc/fstab.mt6878`**. No other file on B's second-stage search path supplies
one either: odm, system, system_ext and product all lack it, and the ramdisk is gone
after switch_root. The stock vendor_a does have the file.

In Android 17 `GetFstabPath()` therefore returns `""`. Both `mount_all --early` (`on fs`)
and `mount_all --late` (`on late-fs`) fail with "Could not read default fstab", and
`queue_fs_event` is never reached. The result is that /data, nvdata, protect_f/s,
nvcfg and persist are never mounted. `ro.crypto.state` is also never set, so the
`zygote-start` triggers cannot match and post-fs-data runs against the read-only
`/data` stub of the system image. That stalls the boot with no reboot path, which is
consistent with a silent logo hang, no adbd and no fastboot.

**Secondary gate on the same window:** `vendor_b` `init.mt6878.rc:137` (`on late-fs`) does
`wait_for_prop hwservicemanager.ready "true"` before `mount_all --late`.
`wait_for_prop` has no timeout. This gate blocks forever if hwservicemanager does not
come up. The flashed system_ext_b *does* contain `hwservicemanager` + rc (see the
correction below), so this is only a contributing risk, and the retained evidence
cannot show whether it was satisfied.

## Evidence

### 1. B's second-stage init ran (lower bound)
- In `collection/04-window-sweep.txt`, the only persistent-storage change inside the B window is
  `/metadata/aconfig/boot` (directory), with mtime and ctime both `2026-10-03 14:26:08.964`.
  Every other entry is from the Slot-A rescue boot at 14:45:34 or later.
- Only `init` and `aconfigd` may write `aconfig_storage_metadata_file` (`system/sepolicy/private/aconfigd.te` neverallows).
- Android 17 `aconfigd-system early-platform-init` runs from `aconfigd.rc` `on early-init`.
  The flag `enable_earlier_aconfigd` is ENABLED in the B build (checked with `aconfig dump-cache` on `out/.../system/etc/aconfig_flags.pb`).
- A17 rewrites boot copies through `copy_file_without_fsync` (`remove_file` + `File::create`), which changes the directory's mtime.
  Slot A (Android 15) rewrote `boot/system.*` in place at 14:45:34 and on Oct 5 without touching the directory's mtime.
  The 14:26:08 directory change therefore belongs to the B (A17) aconfigd.
- A17 aconfigd creates `/metadata/aconfig/early_init_done` after early init succeeds. `/metadata/aconfig` still has its
  2026-08-30 mtime, so the marker was never created. The early platform init exited with an error after writing the
  boot files. This is non-fatal by itself (exit code only).
  The likely cause is that `apply_all_staged_overrides("vendor")` fails because vendor_b has no `/vendor/etc/aconfig`.

### 2. B never mounted /data (upper bound)
- B ships compressed APEXes at version **370399999** (`static/b-apex-versions.txt`). apexd decompresses them into
  `/data/apex/decompressed/` during post-fs-data.
- That directory still has its **2026-09-27** mtime and contains only `@361099999` files (`collection/05-stage-markers.txt`).
  Slot A has never deleted from it, so the timestamp is reliable.
- Nothing under `/data` changed in the B window (all 19 /data hits are from the A rescue at 14:45:45).
- The mainline aconfigd init (post-fs-data, after `apexd.status activated`) would have rewritten
  `/metadata/aconfig/boot/com.android.*` for the changed A17 module flags; for example, the permission flag.map is
  1582 bytes vs 1335 bytes. Those files keep their Aug-30 timestamps, and the boot directory's last change is 14:26:08.

### 3. Why no kernel log survived (the forensic-collection defect)
- The rescue Slot-A boot's preloader log (`../slot-b-plain-reboot-logo-hang-20261003/recovered-a-state.txt`) shows
  `[PMIC]POFFSTS=0x20`, `[pmic_check_rst] Cold Reset` and `RAM_CONSOLE wdt status 0x800`. The manual rescue was a PMIC
  cold reset (long-press/power-off), which drops DRAM, so ramoops/pstore came back as about 60-byte stubs.
- For comparison, the current boot (`collection/01-pl_lk-key.txt`) followed a normal reboot: `POFFSTS=0x400`,
  `AP Watchdog`, and a full 2306-line pstore survived. **Any future B attempt must end in a warm reset**
  (watchdog/`reboot`/sysrq) if pstore is to be useful. A long-press destroys it.
- A/B metadata (`collection/02-bootctrl-decoded.txt`, CRC OK): slot_b priority 6, tries_remaining 1, not successful,
  not marked unbootable. The preflight preloader saw B retry=4; the rescue boot saw B retry=1. So the preloader
  started slot B three times in total: the hang plus the manual power cycles before `set_active a`. B was never
  auto-marked unbootable, so no automatic fallback happened.

### 4. Correction to the earlier VINTF/HIDL finding
`slot-b-investigation/.../android17-vintf-real-reconciliation/README.md` said Slot B lacks `hwservicemanager`.
That claim was derived from the **Oct-1 collection images** (system_ext.img sha256 `e72441c5…`). The system_ext_b
**flashed for this test** is `4187b58a…` (the "hidl-fixed" build, live readback == `out/system_ext.img`). It contains
`/system_ext/bin/hwservicemanager`, `hwservicemanager.rc`, `android.hidl.allocator@1.0-service.rc` and
`bin/hw/android.hidl.allocator@1.0-service` (`static/system_ext_b-hidl-presence.txt`). The missing-hwservicemanager
finding therefore does **not** apply to the 2026-10-03 hang. The checkvintf run itself was also against vendor_a
files, not the vendor_b that B boots.

### 5. vendor_b vs stock vendor_a
`static/vendor_a-vs-vendor_b-critical.txt` lists what vendor_b lacks compared with stock vendor_a. Besides
`etc/fstab.*`, it lacks:
- `vndservicemanager` (binary and rc);
- the graphics allocator binaries at top level (only `bin/hw/mt6878/` copies remain);
- the health, sensors multihal, wifi, face, IR and drm services;
- `lib64/hw/mapper.mediatek.so` and `vulkan.mali.so`;
- the audio implementation libraries.

Even after /data mounts, B would still need these for display bring-up (allocator/mapper) and vndbinder.

## What is still missing
- No B-side kernel or init log exists for this attempt, because the cold reset wiped DRAM. Without one it cannot be
  proven whether init stopped at `late-fs` (`wait_for_prop hwservicemanager.ready`) or continued into post-fs-data
  with no /data. Both lie inside the proven window, and the fstab defect blocks /data regardless.
- B's pstore console from a run that ends in a **warm** reset, or a UART capture.

## Next steps (not performed; each needs explicit authorization)
1. Give B a second-stage fstab. Either restore `etc/fstab.mt6878` into vendor_b (and re-sign vbmeta_vendor),
   or install the stock fstab via the device tree into `/system/etc/fstab.mt6878` / `/odm/etc`.
   Also restore `vndservicemanager` and the allocator/mapper paths, or switch B to a vendor_b built from the stock vendor_a.
2. Instrument the next attempt the way the September runs did. Use init `write` markers to
   `/metadata/lieppos-slotb/` at early-init, fs, late-fs (before and after the hwservicemanager wait),
   post-fs-data and boot. That works through a cold reset.
3. Let B time out and reboot warmly, or use a watchdog/sysrq, instead of a long-press. Then run
   `scripts/slotb-postmortem-collect.sh OUT "<reboot time>" "<rescue boot time>"` immediately on the first Slot-A boot.
