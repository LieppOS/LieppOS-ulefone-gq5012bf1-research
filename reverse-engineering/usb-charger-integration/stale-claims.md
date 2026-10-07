# USB-CHARGER-INTEGRATION — stale claims (2026-10-07)

| # | claim | verdict | correction |
|---|---|---|---|
| 1 | power-charging "mtk_charger_framework 130/130, 70/72 data (UNIQUE_ID counter only)" | **INCOMPLETE** | Size, section order and counter also differed. The TU placement of the two YFT flags is now fixed, so the file is identical except build-id. |
| 2 | "Still required: runtime protocol traces, limits and replacement validation" | **RECLASSIFIED** | Runtime integration only. All three core modules rebuild with byte-identical code, data and ABI. |
| 3 | (implicit) charger_class/mtk_chg_type_det fully exact | **QUALIFIED** | `srcversion` differs (token-stream hash; the YFT header text is not recoverable). Declared residual. |
