# VENDOR-PROPERTIES — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | "stock vendor property set is inventoried at path level, not per-key" | **RESOLVED** | 747-key ledger with value, consumers and verdict (`evidence/vendor-property-ledger.tsv`). |
| 2 | Shipped surface = `device.mk` `PRODUCT_VENDOR_PROPERTIES += ro.vndk.version=34` (README, `source/device.mk`) | **STALE** | The current device tree (`android_device_ulefone_gq5012bf1`) defines no vendor properties. 343 consumed stock keys are missing (`evidence/lieppos-vendor-missing.prop`). |
| 3 | "Runtime effect … untested" as a blocker | **RECLASSIFIED** | ROM integration. Consumers are identified statically per key. |
| 5 | `lieppos-vendor-missing.prop` values (first definition wins) | **CORRECTED** | `init` lets the *last* definition win ("Overriding previous property"). Stock `vendor/build.prop` repeats keys, so 3 values were wrong: `ro.board.platform` common→mt6878, `debug.sf.late.sf.duration` 27600000→15600000, `ro.surface_flinger.max_frame_buffer_acquired_buffers` 3→4. The script now uses last-wins; the ledger and the .prop were regenerated. |
| 6 | the .prop is installable verbatim | **REFINED** | The device-tree copy is built by `scripts/make_device_vendor_prop.py`: 327 kept and 16 dropped (build-generated or another partition, unshipped gamedriver package, OEM identity/region, privapp policy). `ro.hardware.egl` meow→mali, because `libGLES_meow.so` is not shipped. |
