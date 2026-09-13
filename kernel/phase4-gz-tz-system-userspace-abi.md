# `gz_tz_system.ko` — userspace ABI

**Result: NONE. Proven, not assumed.**

The task brief warned against concluding "no userspace ABI" merely because the
module is a provider. So this is established by four independent negative
proofs plus one positive attribution of where the userspace interface actually
lives.

## 1. Negative proof from the import set

If the module exposed any userspace interface it would have to import at least
one registration symbol. The complete 50-symbol import list contains **none**
of them:

| symbol that would be required | present in stock imports? |
|---|---|
| `misc_register` | **absent** |
| `proc_create` (+ `proc_create_data`, `remove_proc_entry`) | **absent** |
| `debugfs_create_file` (+ `debugfs_create_dir`) | **absent** |
| `device_create` | **absent** |
| `class_create` | **absent** |
| `__register_chrdev` | **absent** |
| `cdev_add` (+ `cdev_init`) | **absent** |
| `register_chrdev_region` / `alloc_chrdev_region` | **absent** |
| `sysfs_create_group` / `sysfs_create_file` | **absent** |
| `device_create_file` | **absent** |
| `kobject_uevent` | **absent** |

## 2. Negative proof from the source

A repo-wide grep across all three translation units for
`misc_register|proc_create|debugfs_create|device_create_file|sysfs_create|file_operations|.unlocked_ioctl|cdev_add|class_create|register_chrdev`
returns **zero hits**.

There is no `struct file_operations`, no `.open`/`.release`/`.read`/`.write`/
`.mmap`/`.unlocked_ioctl`/`.compat_ioctl` anywhere in `tz_system.c`,
`mtee-kree/kree_mem.c` or `mtee-kree/tz_mmap.c`.

## 3. Negative proof from the object table

The 35 stock objects contain no `file_operations`, no `miscdevice`, no
`class`, no `cdev`, no `attribute_group`, no `kobject`. The only driver object
is `tz_system_driver` (`struct platform_driver`, 248 B) plus its
`tz_system_of_match` table — a pure in-kernel platform binding.

## 4. Negative proof from module metadata

Stock `.modinfo` declares **no parameters** (`parm=` / `parmtype=` absent), so
there is not even a `/sys/module/gz_tz_system/parameters/` surface. The only
`/sys` presence is the unavoidable generic
`/sys/module/gz_tz_system/{coresize,initstate,refcnt,…}` that the module loader
creates for every module — not an ABI this driver defines.

## 5. Where the userspace interface actually is

`gz_tz_system` is deliberately a **kernel-only KREE provider**. The GenieZone
userspace ABI belongs to its *consumer* `gz_main_mod.ko` (V:150), which is the
module that implements `tz_client_open_session()` and friends behind a
character device. `gz_main_mod` is the largest consumer of this module
(15 of the 27 exports) — it converts the in-kernel KREE API into the userspace
one.

That split is why `gz_tz_system` imports `get_user_pages_remote`,
`find_vma_intersection`, `follow_pfn`, `down_read`/`up_read`, `__folio_put`,
`__page_pinner_put_page` and `page_pinner_inited`: `_map_user_pages()` (the
one exported non-KREE function, `0x6e8b0474`) pins **user pages on behalf of
its kernel caller**, taking `mm->mmap_lock` for read. It operates on a
userspace address range, but it is invoked from kernel context by
`gz_main_mod` — it is not itself a userspace entry point.

## 6. Conclusion

| question | answer |
|---|---|
| `/dev` node | none |
| `/proc` entry | none |
| `/sys` attributes | none (beyond the generic loader-created module directory) |
| debugfs | none |
| ioctl | none |
| read / write / mmap | none |
| uevents | none |
| module parameters | none |

`gz_tz_system.ko` exposes **no direct userspace ABI whatsoever**. Its entire
interface is the 27 `EXPORT_SYMBOL` entries documented in
`kernel/phase4-gz-tz-system-kree-api.md`.
