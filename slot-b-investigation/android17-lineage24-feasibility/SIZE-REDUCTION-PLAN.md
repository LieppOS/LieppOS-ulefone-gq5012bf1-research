# Coherent size-reduction plan

No Android 17 image was built, so reductions are source/config candidates—not
claimed byte savings. First obtain a successful baseline build on a filesystem
with adequate space, then use `installed-files*.json`, filesystem maps and
per-package sizes before removing anything.

## SAFE

| Candidate | Reason |
|---|---|
| EROFS with supported compression | kernel and current phone already support EROFS; source supports `GSI_FILE_SYSTEM_TYPE=erofs` |
| production `user` payload after diagnostic boot | removes userdebug-only binaries/policy/logging once bring-up is complete |
| exclude GSI compliance debug policy from final device product | final `gq5012bf1` is not a CTS GSI target; provide proper device sepolicy instead |
| no GApps | official Lineage base is already vanilla; do not add Google payload |
| no recovery/super artifacts in logical images | build artifacts are not partition contents; keep only required runtime files |

## LIKELY SAFE (measure and test)

- static/live wallpapers, duplicate wallpaper packs and demo media;
- excess ringtone/notification/alarm sets while retaining functional defaults;
- optional Lineage apps not needed for boot: AudioFX, Eleven, Etar, Jelly,
  Recorder, optional gallery/terminal equivalents;
- Updater in early non-OTA proof builds;
- duplicate optional fonts/locales after preserving configured languages,
  fallback glyphs, emoji, CJK needs and accessibility;
- remove generic emulator/stub payload only after confirming it is not selected
  by product dependencies.

## INVESTIGATE

- SetupWizard/Provision: can affect provisioning and permissions; use a coherent
  headless-development flow rather than deleting one package blindly.
- dexpreopt: disabling can reduce read-only images but increases first-boot time
  and `/data` usage and changes ART behavior.
- 32-bit architecture payload: current product target is arm64+arm and MTK
  vendor may require 32-bit clients; prove complete ELF/service closure first.
- product/system_ext redistribution: necessary for current extents, but obey
  partition ownership, classpath, SELinux labels and APEX availability.
- APEX variants/prebuilts: choose exactly one release-compatible variant through
  product configuration; never delete files from a built image ad hoc.
- media/camera/telephony apps: may appear optional but providers and privileged
  permission grants can be framework dependencies.

## DO NOT REMOVE

- framework-res, SystemUI, Settings, PackageInstaller/PermissionController;
- ART/runtime/linker/APEX infrastructure and release-matched module set;
- vold, keystore2, servicemanager/hwservicemanager, init, SELinux policy;
- Contacts/Telephony/Media/Settings providers needed by installed framework;
- networking, DNS resolver, tethering and Wi-Fi framework modules;
- VINTF level-8, VNDK-34, HIDL allocator/memory and legacy OMX compatibility
  content while current vendor is retained;
- Ulefone vendor HALs/configs/firmware or their transitive ELF dependencies;
- the native Lineage 24 provider/database configuration.

## Layout strategy

1. Build `lineage_gsi_arm64` once for a DSU proof and measure it.
2. Create `lineage_gq5012bf1` with independent EROFS system/system_ext/product.
3. Generate per-partition installed-file size reports.
4. Move packages only through make/Soong partition ownership, never file surgery.
5. Require each image plus AVB hashtree/FEC/footer to fit its exact current
   extent; preserve roughly 63.45 MiB free super pool.

**BLOCKER:** exact `EXTRA_SUPER_REQUIRED_BYTES` is unknown until images exist.
No super resize is proposed.
