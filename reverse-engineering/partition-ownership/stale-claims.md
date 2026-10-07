# PARTITION-OWNERSHIP — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | `para`, `boot_para`, `expdb`, `proinfo`, `seccfg`, `otp`: "UNDOCUMENTED purpose" | **RESOLVED** | Each has evidence-backed Android-side owners, or none (bootloader-owned). See README table and ledger. |
| 2 | "AVB rollback indexes … Unknown persistent scope" | **RESOLVED (static)** | Locations 0/2/3/4 are decoded, every index is 0, and no Android consumer exists, so the store is bootloader-owned. Destructive tests remain out of scope. |
| 3 | rollback "images use zero" | **CONFIRMED + EXTENDED** | Also `vbmeta_a` flags = 3 (verification disabled, development slot). |
