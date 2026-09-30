# Android 17 VINTF debug / compatibility precheck

This run diagnoses the Android 17 Slot-B userspace against the existing
Ulefone vendor environment.

The previous diagnostic accidentally allowed adb shell to inherit the
outer bash heredoc stdin. This run explicitly redirects every adb shell
operation from /dev/null so the complete host script executes.

Checks performed:

- host ADB state
- basic ADB shell connectivity
- OrangeFox identity
- BootControl state
- root access
- SELinux context
- B logical mapper visibility
- B logical partition sizes
- read-only mounting of Android 17 system/product/system_ext
- Android release/build property discovery
- Android 17 VINTF file discovery
- current vendor VINTF inventory
- current vendor HAL inventory
- final slot/BootControl state
- metadata keymaster hash invariant

No partition writes.
No reboot.
No slot change.
No vbmeta modification.
No userdata modification.
No metadata modification.

Final state:

ADB_STATE=device
BOOTMODE=normal
SLOT=_a
BOOTCONTROL=running
