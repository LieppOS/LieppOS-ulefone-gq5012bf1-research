# V11 experiment: bypass only KeyMint earlyBootEnded propagation

V10 proved init blocks while executing:

    /system/bin/vdc keymaster earlyBootEnded

Source tracing shows Keystore2 performs:

    permission check
    SuperKeyManager::set_up_boot_level_cache(...)
    Maintenance::call_on_all_security_levels(
        "earlyBootEnded",
        |dev| dev.earlyBootEnded(),
        None
    )

Working Slot A proves the actual hardware backend is the TrustKernel KeyMint
3.0 service. The TrustKernel HAL binary, RC, and VINTF declaration are
byte-identical between A and the B build.

The system-side vdc, vold, and keystore2 binaries differ between working A and
the Lineage B build.

V11 preserves:
- permission checking;
- boot-level-cache setup;
- vold/vdc behavior;
- existing V9/V10 init markers.

V11 temporarily replaces only the KeyMint propagation call with `Ok(())`.

Interpretation:

- If v10-after-keymaster becomes 1, the immediate blocker is in the KeyMint
  propagation path after boot-level-cache setup.
- If v10-after-keymaster remains 0, the blocker occurs before the skipped
  propagation, most importantly in Keystore2 boot-level-cache setup or an
  earlier part of the Binder path.

This is diagnostic only. Skipping earlyBootEnded is not suitable for a
production ROM because it changes the intended EARLY_BOOT_ONLY key lifecycle.

PHONE_MODIFIED=0
