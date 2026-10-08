# VINTF-HAL-MANIFEST — status

**DONE (static, 2026-10-07).** 199 stock HAL instances reconciled: 145 present, 48 non-DSDS SKU, 5 source-built, 1 dropped (bluetooth.audio fragment); 12 absent payload refs classified.

## Workspace move (2026-10-07)

Moved PARTIAL -> DONE via `reverse-engineering/scripts/promote-to-done.py`; component manifest rows rebuilt, 0 drift / 0 unregistered. Totals after this batch: 94 DONE / 36 PARTIAL / 3 BLOCKED / 0 TODO.

## Integration fix applied (2026-10-07)

Device tree `24afa6b` drops `;EXTRACT_ONLY` from `bluetooth_audio.xml` in
`proprietary-files.txt`. The vendor tree's `Android.bp`/`gq5012bf1-vendor.mk`
gained the matching `prebuilt_etc_xml` module; these were hand-applied because
extract-utils is not available offline, and they match the setup-makefiles
output format.

Re-running the reconciliation gives 146 PRESENT, 48 SKU-only, 5 source-built,
**0 dropped**.
