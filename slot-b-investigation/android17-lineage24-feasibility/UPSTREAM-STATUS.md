# Official upstream status

## Manifest

**PROVEN** from the live official repository and initialized checkout:

```text
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs
manifest commit: f16772cb8c33a15e970abe42d7bb120e2dc84f33
commit date:     2026-09-18T23:12:12Z
subject:         manifest: Forks for android-security-17.0.0_r1
AOSP default:    refs/tags/android-17.0.0_r1
projects:        1238
```

Manifest commit before and after sync is identical. The base is official
LineageOS; no RisingOS or other ROM source was added.

## Release identity

**PROVEN** by `lunch lineage_gsi_arm64 cp2a userdebug`:

| Field | Value |
|---|---|
| platform release | Android 17 (`REL`) |
| SDK/API | 37 |
| release config | `cp2a` |
| platform security patch | `2026-09-01` |
| Lineage branch/version | `lineage-24.0`; configured version `24.0-20260927-UNOFFICIAL-gsi_arm64` |
| board/vendor API level for new builds | `202604` |
| platform sepolicy | `202604` |
| shipping API of the generic product | 37 |

The patch override is source-backed at
`vendor/lineage/release/flag_values/cp2a/RELEASE_PLATFORM_SECURITY_PATCH.textproto`.
Relevant exact project revisions:

```text
build/make          92a87b9506e5d1c961292cc8138036ccbe190ada
build/release       c85f4aebe46714235599a9bd6430a0fe30c6e8d5
build/soong         5ea236479501d50a4a0eafb568f4f35d1bdda3cb
hardware/interfaces 1b92b77fe1f2f2c820c51b0b1e366c17d6b9911b
kernel/configs      200b3987b78fc25015bf826b281f0c3851daf146
system/libvintf     df89ad736e14ac375f61d50fa543ae7cd746a140
system/sepolicy     20ee50b20ec3005f91a6f96a9118544774551993
vendor/lineage      1ac40c54abeeb0a6b540e8503eb15d4bf41e1c7b
```

## Kernel and vendor baseline expectations

**PROVEN:** the new-launch Android-C kernel configuration in this source is
6.18 (`kernel/configs/c/android-6.18`). This does not automatically invalidate
upgrade devices. Framework FCM level 8 (Android U/14), sepolicy 34.0 mappings and
VNDK 34 snapshots are retained. Details are in the kernel/VINTF reports.

## Development readiness

- **PROVEN:** manifest init and sync succeeded; product discovery and lunch
  succeeded; the complete Soong/Make graph completed `m nothing`.
- **UNKNOWN:** a full image build was deliberately not started because storage
  fell below the build allowance.
- **INFERRED:** the branch is buildable enough for development; only full
  compilation and packaging remain to prove artifact production.
