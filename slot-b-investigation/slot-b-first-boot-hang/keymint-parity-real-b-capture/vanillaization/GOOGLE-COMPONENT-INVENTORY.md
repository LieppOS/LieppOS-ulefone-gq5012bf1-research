# Google component and partition inventory

The source images were extracted read-only with host `fsck.erofs --extract`.
`erofsfuse` was not used. APK manifests and RRO targets were inspected with
`aapt2`; selected APEX payloads were decompressed with `deapexer` to identify
embedded APK package names.

The complete path/package/target/hash inventory is in
[`PARTITION-COMPOSITION-INVENTORY.tsv`](PARTITION-COMPOSITION-INVENTORY.tsv).

## Partition sources and counts

| Runtime role | Source | APK | APEX/CAPEX | JAR | permission XML | sysconfig XML |
|---|---|---:|---:|---:|---:|---:|
| current debug `system_b` | `system-b-adb-debug.img` | 61 | 33 | 41 | 18 | 11 |
| current split-fixed `product_b` | `product-b-no-gms-split-debug.img` | 108 | 0 | 0 | 18 | 29 |
| physical `system_ext_b` | `current-b-logical-dumps/system_ext_b.img` | 29 | 5 | 13 | 25 | 4 |
| physical `vendor_b` | `current-b-logical-dumps/vendor_b.img` | 0 | 1 | 0 | 22 | 0 |
| `vendor_a` used by the B control | factory V15 `vendor_a.img` | 13 | 1 | 1 | 52 | 0 |
| `system_dlkm_b` | current B dump | 0 | 0 | 0 | 0 | 0 |
| `vendor_dlkm_b` | current B dump | 0 | 0 | 0 | 0 | 0 |
| `odm_dlkm_b` | current B dump | 0 | 0 | 0 | 0 | 0 |

The DLKM images contain kernel modules/properties only and no Android APK,
APEX, permission, or sysconfig material relevant to this investigation.
`vendor_a` and physical `vendor_b` are deliberately distinguished throughout.
Neither was modified.

## System B

`system_b` is already the intended vanilla Lineage system composition. Its
APEX payloads provide AOSP package identities, including:

- ExtServices: `android.ext.services`
- PermissionController: `com.android.permissioncontroller`
- Wi-Fi resources: `com.android.wifi.resources`
- tethering: `com.android.networkstack.tethering`
- Cell Broadcast module: `com.android.cellbroadcastreceiver.module`

No real `com.google.*` APK is installed by `system_b`. Google strings found in
framework or AOSP APK code are compatibility actions, optional integrations,
or comments. The standard property
`ro.com.google.clientidbase=android-google` is not a package dependency.

**SYSTEM_MODIFICATION_REQUIRED=0**

The exact debug system is preserved:

`68b4639959dd189fcc6e6603742a4b4ef57f6106d444da48ef884031a69d1a99`

## Product B

The current product contains 85 overlay APK paths. The incompatible group is
not identified by filename alone: manifests prove that the removable RROs
target `android` or absent `com.google.*` module packages and install stock-GMS
framework values.

Verified GApps-only groups include:

- GMS framework configuration overlays (`GmsConfigOverlay*`)
- Google ExtServices, PermissionController, DocumentsUI, HealthFitness, and
  ModuleMetadata overlays
- a Google-target Wi-Fi resource overlay for
  `com.google.android.wifi.resources` while an AOSP-target counterpart for
  `com.android.wifi.resources` is also present
- permission grants and shared-library declarations for absent Google apps
- sysconfig feature declarations/component overrides for absent GApps

### Google-looking content retained intentionally

- `ApertureLensLauncher.apk` has package
  `com.google.android.apps.googlecamera.fishfood`, but source provenance is
  `packages/apps/Aperture`. Lineage Aperture uses it to expose auxiliary camera
  lenses. It is not GApps and is retained.
- `product-permissions-mediatek.xml` contains `okgoogle`/`xgoogle` hotword
  package names but also MTK/Ulefone platform grants. It is retained.
- `apns-conf.xml` can contain Google Fi carrier text; it is required telephony
  data.
- the 88-resource auto-generated Ulefone product RRO is retained because it
  supplies VoLTE/WFC, fingerprint, display-cutout, telephony, camera,
  brightness, volume, smart-key, and other device resources.

That required Ulefone RRO also contains two stale stock-Google package values.
They are not grounds to delete the overlay. A new vanilla corrective RRO with
priority 999 supersedes only those values with their AOSP package names.

## System-ext B

There is no real Google APK in `system_ext_b`.

`etc/permissions/privapp-permissions-google-system_ext.xml` is a mixed file:
it contains stale grants for absent GSF, Google Feedback, and Google
SetupWizard, but also required privileged permissions for the installed
`com.android.emergency` package. Missing-package grants are non-fatal, and
removing or editing the file would require an unnecessary system-ext rebuild.

`etc/sysconfig/com.mediatek.ims.config.xml` mentions GMS in a comment but grants
an ignore-location-settings exemption to installed `com.mediatek.ims`; it is
required IMS compatibility.

**SYSTEM_EXT_MODIFICATION_REQUIRED=0**

## Vendor and ODM material

The active `vendor_a` contains paired Google-target and AOSP-target MTK RROs
for NetworkStack, tethering, and Wi-Fi. On B, absent Google targets are ignored
while the AOSP-target variants apply. These files remain part of the proven
vendor control and are not product-GApps requirements.

Other Google text that must remain includes:

- `OMX.google.*` AOSP software media codec names;
- Google-hosted SUPL endpoints in GNSS profiles;
- CA certificates;
- vendor SELinux compatibility identifiers;
- the non-updatable Widevine APEX.

Physical `vendor_b` has no APK and no GApps package composition. Nested ODM
content was included in the vendor inventory; no relevant Google package
requirement was found.

## Reference Slot A

Factory A images were inspected only to answer package-presence questions. They
contain the complete stock Google composition, including Google ExtServices,
PermissionController, Wi-Fi resources, Cell Broadcast, NetworkStack,
DocumentsUI, ModuleMetadata, Dialer, SetupWizard, Restore, ConfigUpdater,
PartnerSetup, Feedback, Play Store, and GmsCore. This explains why stock-Google
RROs are satisfiable on A but not on vanilla B. Stock A is not used as the
vanilla product target.
