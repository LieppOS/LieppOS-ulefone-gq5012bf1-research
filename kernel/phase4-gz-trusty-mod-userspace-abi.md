# `gz_trusty_mod` userspace ABI audit

## Result

The module has one custom userspace-visible interface: a per-bound-device sysfs attribute named **`trusty_version`**. It does not create a character device.

| Surface | Result | Proof |
|---|---|---|
| `/dev` | none | no cdev/misc/chrdev objects or imports |
| `/proc` | none | no procfs objects/imports |
| `/sys` | `trusty_version` | `dev_attr_trusty_version`, `DEVICE_ATTR_RW`, `device_create_file/remove_file` |
| debugfs | none in stock | `CONFIG_MT_GZ_TRUSTY_DEBUGFS` off; object/import set absent |
| ioctl | none | no file-operations/ioctl handler |
| read/write | sysfs only | show/store callbacks below |
| mmap | none | no mmap handler/import |
| poll | none for userspace | internal `trusty_poll_*` kthread is not a file poll operation |
| custom uevent | none | ordinary platform-device lifecycle only |
| module parameters | none | no `parm=` metadata or parameter object |

## `trusty_version`

`DEVICE_ATTR_RW` gives normal root-writable sysfs mode. The attribute is created only after the version string length and every character are retrieved successfully during probe.

- read: `scnprintf(buf, PAGE_SIZE, "%s\n", s->version_str)`;
- write: consumes no setting and returns the input byte count unchanged;
- remove/probe-unwind: removes the file when `version_str` exists.

The two stock platform instances may each expose the attribute beneath their device path (Trusty `tee-id=0`, Nebula `tee-id=1`) if version retrieval succeeds. There is no stable top-level `/sys` path asserted because platform enumeration paths are runtime-dependent.
