# Default fstab and late-fs import audit

The previous host scan did not locate the boot-time default fstab. It found
only fstab.postinstall, which is not sufficient to identify what
`mount_all --late` processes during normal boot.

Also, finding factory/meta rc files in the filesystem does not prove their
late-fs actions are parsed in normal boot.

This audit therefore records:

- the fstab visible on the working Slot A runtime;
- Android's `ReadDefaultFstab()` lookup behavior;
- source/output references to the MT6878 fstab;
- the actual import chain for normal MT6878, META, and factory init scripts;
- the currently mounted /data, /metadata and MediaTek persistent partitions.

No V7 instrumentation should be designed until the actual late-mount fstab
entries and normal-boot init action set are established.

PHONE_MODIFIED=0
