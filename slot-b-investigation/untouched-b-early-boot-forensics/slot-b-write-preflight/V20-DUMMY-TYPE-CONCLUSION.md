# V20 unused dummy-type conclusion

V20 was designed as a minimal control against V17.

V17 did not boot successfully; it is a historical policy/artifact baseline only.

V20 differs from V17's vendor SELinux policy by exactly one unused bare
SELinux type plus its automatically generated object_r roletype:

    type lieppos_v20_dummy_type;

The V17 -> V20 compact audit proved that deleting those two generated CIL
lines makes vendor_sepolicy.cil byte-identical to V17.

V20 runtime result:

- v15-mtkgki-early-init remained 0
- its mtime remained exactly the seed time:
  2026-09-24 00:47:32.952000092 +0300
- no Android-init checkpoint advanced
- V20 vendor_b remained exact
- frozen V12 system_b remained exact
- vbmeta_vendor_b, vbmeta_system_b and root vbmeta_b remained exact

Therefore an unused additional vendor SELinux type is sufficient to
reproduce the pre-early-init regression.

This rules out vendor_mtk_device_prop-specific semantics as the primary
cause of the V19 failure.

The investigation should now move to the consequences of changing the
compiled/precompiled vendor policy type layout itself: type IDs, split
policy/precompiled policy compatibility, or first-stage SELinux loading.

V20_PRE_EARLY_INIT_REPRODUCED=1
CAPTURE_PHONE_MODIFIED=0
EXPERIMENT_PHONE_MODIFIED=1
