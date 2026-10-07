# MT6375-CHARGER — stale / wrong claims corrected (2026-10-07)

| # | claim (where) | verdict | correction / evidence |
|---|---|---|---|
| 1 | "Still required: full charger source parity" (status row/README) | **RESOLVED** | All five MT6375 charger-side modules are identical to stock except the build-id, with B1==B2 (`parity/`). |
| 2 | "`source/mt6375-charger.c` is a build-only ABI witness, not a driver" (README) | **SUPERSEDED** | The full GQ5012BF1 `mt6375-charger.c` is now the source of record (KDM f8e3f87; delta in `source/*.patch`). The witness is kept only as a historical file. |
| 3 | `mt6375-battery` "332/332 … exact" (power-charging README, 2026-10-03) | **INCOMPLETE** | That count covered functions only. Three `__bug_table` WARN line numbers differed (1154/3357/3370 vs stock 1343/3544/3557). Fixed by a declared line-layout reconstruction, so the file is now identical except the build-id. |
| 4 | `tcpc_class` "not CRC-exact on its exports … all 21 export CRCs that tcpc_mt6375 consumes differ" (README) | **SUPERSEDED** | TCPC-CLASS has been DONE since 2026-09-25 with an ABI-exact 707-function reconstruction. Every `tcpc_class` import of the rebuilt `mt6375-charger` has the stock provider CRC. |
| 5 | (implicit) `mt6375`/`mt6375-adc`/`mt6375-auxadc` are covered elsewhere | **WRONG** | They were in no DONE pack. They are now closed here: two are unmodified ALPS, and the MFD core carries a reconstructed IRQ-ack delta. |
| 6 | "Live charging-protocol validation" as a blocker | **RECLASSIFIED** | Runtime/physical integration work; it does not affect the module contract. The live capture already shows binding, both psys and periodic charger register dumps. |
