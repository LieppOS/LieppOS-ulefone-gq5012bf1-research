# System-ext B vanillaization assessment

`SYSTEM_EXT_MODIFICATION_REQUIRED=0`

## Image inspected

`slot-b-investigation/current-b-logical-dumps/system_ext_b.img`

- SHA-256: `a63bd6e22cc8a451a7ffb0d8c9f026957c9ea03f89f032fd408134805865af4a`
- APKs: 29
- APEX files: 5
- framework JARs: 13
- permission XML files: 25
- sysconfig XML files: 4

No actual `com.google.*` APK package is present.

## Google-named permission file

`etc/permissions/privapp-permissions-google-system_ext.xml` contains grants for:

- absent `com.google.android.gsf`
- absent `com.google.android.feedback`
- absent `com.google.android.setupwizard`
- installed `com.android.emergency`

The `com.android.emergency` section grants privileged telephony and emergency
permissions required by the B package. Removing the file wholesale would break
that installed package. Editing out only stale grants would force a new
system-ext image and matching root-vbmeta descriptor for no demonstrated boot
benefit: PackageManager treats absent-package grants as warnings, not package
requirements.

Therefore the complete file is retained and system-ext remains byte-identical.

## MTK IMS sysconfig

`etc/sysconfig/com.mediatek.ims.config.xml` says in a comment that the setting
exists on GMS devices, but the operative entry grants
`allow-ignore-location-settings` to installed `com.mediatek.ims`. This is MTK
IMS compatibility and must remain.

## Other Google strings

Google identifiers in system-ext SELinux policy, updater/init material, or
build provenance are compatibility identifiers and do not install or require a
Google package. No framework resource in system-ext was found to impose the
known `com.google.android.ext.services` or GmsCore boot requirements.

## Decision

- no `system_ext_b` candidate built
- no new `vbmeta_system_b` built
- root `vbmeta_b` retains the existing `system_ext` descriptor byte-for-byte
- current debug `system_b` and `vbmeta_system_b` remain unchanged
