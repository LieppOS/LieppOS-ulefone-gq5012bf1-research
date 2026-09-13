# gz_main_mod — complete Linux-visible userspace ABI

`gz_main_mod` owns the **higher-level GenieZone/KREE userspace ABI**. This is
distinct from `gz_ipc_mod`'s lower raw TIPC character device
(`kernel/phase4-gz-ipc-mod-userspace-abi.md`), which exposes message-level
transport rather than KREE sessions.

There are **two** device nodes, not one.

## 1. `/dev/gz_kree` — the KREE client device

| property | value | evidence |
|---|---|---|
| creation | `misc_register(&gz_device)` from `gz_main_probe()` | stock imports `misc_register`/`misc_deregister`; `gz_device` object present |
| name | `gz_kree` | stock `.rodata` string `gz_kree`; `miscdevice.name` |
| major | 10 (misc) | misc framework |
| minor | `MISC_DYNAMIC_MINOR` | `gz_device` initialiser |
| node path | `/dev/gz_kree` | committed `init.mt6878.rc` |
| owner/group | `system` / `system` | `init.mt6878.rc:564` `chown system system /dev/gz_kree` |
| mode | `0660` | `init.mt6878.rc:563` `chmod 0660 /dev/gz_kree` |
| SELinux type | `u:object_r:gz_device:s0` | `vendor_file_contexts:582` |

Header `kree/tz_mod.h` still carries the legacy `TZ_DEV_NAME "trustzone"` and
`MAJOR_DEV_NUM 197`. **Neither is used by this module** — the compiled code
registers a misc device named `gz_kree`. Recorded here so the legacy constants
are not mistaken for the live ABI.

### file_operations (`fops`, gz_main.c)

| slot | handler | stock function | size |
|---|---|---|---|
| `.owner` | `THIS_MODULE` | — | — |
| `.open` | `gz_dev_open` | present | 192 B |
| `.release` | `gz_dev_release` | present | 256 B |
| `.unlocked_ioctl` | `gz_ioctl` | present | 32 B |
| `.compat_ioctl` | `gz_compat_ioctl` | present | 36 B |

Slots **not** implemented, and therefore not part of the ABI:
`read`, `write`, `llseek`, `poll`, `mmap`, `fasync`, `flush`, `fsync`.

Consequences, all Linux-visible and all proven by absence of the slots:

* `read(2)`/`write(2)` on `/dev/gz_kree` return `-EINVAL` (no handler).
* `mmap(2)` returns `-ENODEV`. **This device is not mappable.** User memory is
  shared with the secure world by pinning, never by mapping (see
  `kernel/phase4-gz-main-mod-memory-contract.md`).
* `poll(2)`/`select(2)` report the default always-ready mask; there is no
  readiness or event surface.
* The file is not seekable in any meaningful way.

`gz_dev_open` allocates the per-open session table; `gz_dev_release` closes
every still-open KREE session and frees it. There is no global open count and
no exclusivity check, so multiple simultaneous opens are permitted and each
gets an independent session table.

### sysfs

| attribute | path | mode | handler |
|---|---|---|---|
| `gz_test` | `/sys/devices/virtual/misc/gz_kree/gz_test` | RW (`DEVICE_ATTR_RW`) | `gz_test_show` / `gz_test_store` |

`show` returns the fixed menu string
`" 0: GZ Version\n 1: TIPC\n 2.General Function\n 3: Shared Memory\n 4: GZ abort 5: Chunk Memory\n C: Secure Storage\n"`.

`store` accepts `1..50` bytes, reads **only the first character**, and spawns a
kthread:

| char | kthread | function |
|---|---|---|
| `0` | `GZ version` | `get_gz_version` |
| `1` | `Simple test` | `simple_ut` |
| `2` | `test_gz_syscall` | `test_gz_syscall` |
| `3` | `test_shm` | `gz_test_shm` |
| `4` | `test_chm` | `gz_test_chm` |
| `5` | `test_vreg` | `gz_test_vreg` |
| other | none | logs "unknown test case" |

`store` always returns `n` (the full write length), even for a rejected size
or unknown case. This is an engineering/unit-test surface that is compiled into
the production stock module; it is reachable from userspace only with write
access to the sysfs attribute, which the misc device's default root-owned
sysfs permissions restrict.

**No test was executed on hardware.** The behaviour above is read out of the
source and confirmed against stock code bytes only.

## 2. `/dev/gz_ffa_dev` — the FF-A client device

| property | value | evidence |
|---|---|---|
| creation | `class_create()` + `register_chrdev(0, …)` + `device_create()` in `device_driver_init()` | stock imports `__class_create`, `__register_chrdev`, `device_create` |
| name | `gz_ffa_dev` | stock `.rodata` string |
| major | **dynamically allocated** (`register_chrdev(0, …)`) | first argument 0 |
| minor | 0 (`MKDEV(rc, 0)`) | `device_create` call |
| class | `gz_ffa_dev` | `class_create(THIS_MODULE, GZ_FFA_DEV_NAME)` |
| node path | `/dev/gz_ffa_dev` | committed `init.mt6878.rc` |
| owner/group | `system` / `system` | `init.mt6878.rc:568` |
| mode | `0660` | `init.mt6878.rc:567` |
| SELinux type | no explicit `file_contexts` rule → inherits the default `device` type | absence in `vendor_file_contexts` |

### file_operations (`fops`, gz_ffa.c)

| slot | handler |
|---|---|
| `.unlocked_ioctl` | `ff_a_gz_ioctl` |

Every other slot is unset, including `.owner`, `.open`, `.release` and
`.compat_ioctl`.

Two Linux-visible consequences follow directly and are worth stating plainly:

* **There is no `.compat_ioctl`.** A 32-bit userspace process calling `ioctl`
  on `/dev/gz_ffa_dev` gets `-ENOTTY` from the VFS compat path. This device is
  effectively 64-bit-only.
* **`.owner` is not set**, so the module reference count is not incremented
  while the node is open.

Note the two modules each define a symbol literally named `fops`; both are
file-scope in their own translation unit (`gz_ffa.c`'s is `const`, non-static),
which is why the stock object table lists `fops` twice.

## 3. Module parameters, procfs, debugfs, uevent

| surface | state | evidence |
|---|---|---|
| module parameters | **none** | stock `.modinfo` contains no `parm=`/`parmtype=`; `/sys/module/gz_main_mod/parameters/` does not exist |
| procfs | **none** | no `proc_create`/`remove_proc_entry` import |
| debugfs | **none** | no `debugfs_*` import; `CONFIG_MT_GZ_TRUSTY_DEBUGFS` off |
| custom uevent | **none** | no `dev_uevent`/`add_uevent_var`; `device_create` is passed a NULL parent and no uevent hook |
| generic `/sys/module/gz_main_mod/` | present | created by the module loader for every module; not an ABI this driver defines |

## 4. ABI summary

| item | count |
|---|---|
| character devices | 2 (`/dev/gz_kree`, `/dev/gz_ffa_dev`) |
| implemented file_operations slots | 5 on `gz_kree`, 1 on `gz_ffa_dev` |
| ioctl commands | 9 on `gz_kree`, 8 on `gz_ffa_dev` (17 total) |
| sysfs attributes | 1 (`gz_test`) |
| module parameters | 0 |
| exported kernel symbols | 0 |

The full command tables are in
`kernel/phase4-gz-main-mod-ioctl-contract.md`.
