# VINTF-HAL-MANIFEST — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | "no automated equality check exists yet, so manifest drift can only be caught by a full build" | **RESOLVED** | Instance-level reconciliation script and ledger. 145 present, 48 SKU-only, 5 source-built, 1 dropped. |
| 2 | "13 absent-payload service references" | **CORRECTED** | 12 references (9 binaries). 3 apparent misses are symlinks to `.mt6878` binaries. All are classified (alternate FP BOM, factory/meta, 32-bit, legacy GNSS). |
| 3 | (implicit) the authored manifests cover stock | **ONE GAP** | `bluetooth.audio@3 IBluetoothAudioProviderFactory/default` is dropped (EXTRACT_ONLY fragment, impl shipped). |
| 4 | "build-time VINTF assembly + vintf checks … is what blocks DONE" | **RECLASSIFIED** | Full-checkout build gate = integration. |
