# Slot-B coherent vanilla userspace candidate

## Scope and safety

This directory records an offline build and read-only analysis of the Ulefone
Armor 29 Pro (`gq5012bf1`) Slot-B Android composition.

No partition was flashed. Slot B was not activated. Slot A, userdata, metadata,
super metadata, calibration partitions, and package/permission state under
`/data` were not modified.

The generated images remain outside Git under:

`/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/`

## Investigation progression

1. Slot B initially reached Android, but ADB authentication obscured runtime
   logs.
2. The diagnostic `ro.adb.secure=0` system enabled authorized live Slot-B
   capture.
3. Live B proved `/data`, user-0 CE storage, `vold`, `keystore2`,
   SurfaceFlinger, and PackageManager startup functional.
4. The first fatal was Google split-permission configuration without GmsCore:
   `Unknown source permission com.google.android.gms.permission.ACTIVITY_RECOGNITION`.
5. Removing `product/etc/permissions/split-permissions-google.xml` eliminated
   that fatal in a controlled live test.
6. B then progressed to a new fatal requiring
   `config_servicesExtensionPackage=com.google.android.ext.services`.
7. Healthy A resolves the base configuration to `android.ext.services`; the B
   system APEX also contains `android.ext.services`.
8. Offline resource analysis proves that a product RRO inherited from the stock
   Google composition changes the value to the absent Google package.
9. The strategy therefore changes from one-failure-at-a-time repair to a
   coherent **vanilla Lineage + MTK/Ulefone** product composition.

## Result

The candidate keeps the current diagnostic `system_b` byte-identical and does
not modify `system_ext_b`, vendor, or DLKM images. It removes 31 additional
verified GApps-only product files from the already split-permission-fixed base
(32 cumulative approved removals including the previously removed XML).

A required Ulefone framework RRO contains 88 device resources, including VoLTE,
WFC, fingerprint, display cutout, telephony, camera, and smart-key settings. It
was **not** removed. A new high-priority vanilla corrective RRO restores only
two stale package resources from that required overlay:

- `config_defaultCaptivePortalLoginPackageName=com.android.captiveportallogin`
- `config_defaultModuleMetadataProvider=com.android.modulemetadata`

The known ExtServices override APK is removed, so the unchanged framework base
value is again:

`config_servicesExtensionPackage=android.ext.services`

## Candidate artifacts

- Product:
  `/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/product-b-vanilla-debug.img`
- Product SHA-256:
  `e8a6b134a4f32b6f9fbdea337c8384c75ba9c4897f385be51d437be2bc46af8b`
- Product size: `337686528` bytes
- Matching root vbmeta:
  `/mnt/SamsungSSD/TIER3/phase4/controls/slot-b-vanilla-product-debug/vbmeta_b.vanilla-debug.img`
- Root vbmeta SHA-256:
  `39ab5e9e6eabc2fa33e9a8e0aec842fc650828f5f8cb505f9e2ea655fab7c917`

## Evidence classification

### PROVEN

- The split-permission removal eliminated the prior fatal during a live B test.
- The next fatal names `com.google.android.ext.services`.
- `armol_product_overlay_GoogleExtServicesConfigOverlay.apk` is a static RRO
  targeting `android`, priority 0, and defines the exact Google value.
- The B ExtServices APEX contains package `android.ext.services`, not the Google
  package.
- All 31 newly removed paths are approved by
  `VANILLA-REMOVAL-MANIFEST.tsv` and target absent Google packages or obsolete
  Google-only configuration.
- No common regular file changed content, ownership, mode, timestamp, xattr
  geometry, symlink target, or regular-file size.
- The only added APK is the documented corrective RRO.
- The new product hashtree and root vbmeta signature verify.
- All non-product root-vbmeta descriptors are byte-identical to the current
  diagnostic chain.

### INFERRED

The coherent vanilla product should remove the currently known Google
PackageManager hard requirements and avoid the sequence of failures caused by
stock-GApps configuration paired with a vanilla Lineage system. Runtime boot
success remains unproven.

### TEST TO CONFIRM

A separately authorized controlled B boot must show that:

- the ExtServices fatal is absent;
- PackageManager resolves services extension to `android.ext.services`;
- no core boot configuration requires `com.google.android.gms`;
- reconciliation with untouched shared Slot-A userdata succeeds or exposes a
  distinct next blocker.

**This report does not claim that the candidate boots.**
