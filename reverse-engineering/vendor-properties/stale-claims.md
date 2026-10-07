# VENDOR-PROPERTIES — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | "stock vendor property set is inventoried at path level, not per-key" | **RESOLVED** | 747-key ledger with value, consumers and verdict (`evidence/vendor-property-ledger.tsv`). |
| 2 | Shipped surface = `device.mk` `PRODUCT_VENDOR_PROPERTIES += ro.vndk.version=34` (README, `source/device.mk`) | **STALE** | The current device tree (`android_device_ulefone_gq5012bf1`) defines no vendor properties. 343 consumed stock keys are missing (`evidence/lieppos-vendor-missing.prop`). |
| 3 | "Runtime effect … untested" as a blocker | **RECLASSIFIED** | ROM integration. Consumers are identified statically per key. |
