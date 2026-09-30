# Android 17 checkvintf / VINTF checker audit

Date: 2026-10-01T01:13:14+03:00

Input collection:
/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/slot-b-investigation/android17-lineage24-feasibility/gq5012bf1-split-product/android17-vintf-compat-collect-20261001-010627

Purpose:

Determine the exact Android 17 VINTF checker/tooling and extract the
framework/vendor/kernel requirements needed for a real Slot-B
Android 17 compatibility reconciliation.

Safety:

- Slot A remained active.
- Slot B was not booted.
- system_b/system_ext_b/product_b were mounted read-only.
- No flashing.
- No reboot.
- No slot metadata changes.
- No AVB/vbmeta changes.
- No userdata or metadata changes.

Important:

This is an audit/collection step, not yet the final compatibility result.
