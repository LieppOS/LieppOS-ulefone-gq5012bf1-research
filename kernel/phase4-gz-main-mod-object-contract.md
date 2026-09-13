# gz_main_mod — object and callback-table contract

All 45 stock objects are present in the rebuild; 44 are size-identical and the
single difference is the `vermagic` string length
(`kernel/phase4-gz-main-mod-object-parity.tsv`).

## 1. Callback tables

### `fops` (gz_main.c) — `struct file_operations` for `/dev/gz_kree`

| slot | stock target | rebuilt target | KCFI id | parity |
|---|---|---|---|---|
| `.owner` | `THIS_MODULE` | same | — | EXACT |
| `.open` | `gz_dev_open` | same | `0x8f07ca55` | EXACT |
| `.release` | `gz_dev_release` | same | `0x8f07ca55` | EXACT |
| `.unlocked_ioctl` | `gz_ioctl` | same | `0xe01408cd` | EXACT |
| `.compat_ioctl` | `gz_compat_ioctl` | same | `0xe01408cd` | EXACT |

`gz_dev_open` and `gz_dev_release` share one KCFI id because both are
`int (*)(struct inode *, struct file *)`. `gz_ioctl`, `gz_compat_ioctl` and
`ff_a_gz_ioctl` share `0xe01408cd`, the
`long (*)(struct file *, unsigned int, unsigned long)` signature.

### `fops` (gz_ffa.c) — `struct file_operations` for `/dev/gz_ffa_dev`

| slot | stock target | KCFI id | parity |
|---|---|---|---|
| `.unlocked_ioctl` | `ff_a_gz_ioctl` | `0xe01408cd` | EXACT |

All other slots NULL, including `.owner` and `.compat_ioctl`.

Both translation units define a file-scope symbol named `fops`, which is why
the object table lists `fops` twice.

### `gz_main_driver` — `struct platform_driver`

| slot | target | KCFI id | parity |
|---|---|---|---|
| `.probe` | `gz_main_probe` | `0x63df1691` | EXACT |
| `.remove` | `gz_main_remove` | `0x63df1691` | EXACT |
| `.driver.name` | `"gz_main"` | — | EXACT |
| `.driver.owner` | `THIS_MODULE` | — | EXACT |
| `.driver.of_match_table` | `gz_main_of_match` | — | EXACT |

### `gz_ffa_driver` — `struct ffa_driver`

| slot | target | KCFI id | parity |
|---|---|---|---|
| `.name` | `"gz_ffa_dev"` | — | EXACT |
| `.probe` | `gz_ffa_driver_probe` | `0xd353e493` | EXACT |
| `.id_table` | `gz_ffa_device_id` | — | EXACT |
| `.remove` | **NULL** | — | EXACT |

### `dev_attr_gz_test` — `struct device_attribute`

| slot | target | KCFI id | parity |
|---|---|---|---|
| `.show` | `gz_test_show` | `0xdf43c25c` | EXACT |
| `.store` | `gz_test_store` | `0x95a8ba07` | EXACT |

### kthread entry points (indirect calls from `gz_test_store`)

Five functions share KCFI id `0x89fb613d` (`int (*)(void *)`), matching the
five `__kcfi_typeid_*` weak symbols in stock:

`get_gz_version`, `simple_ut`, `test_gz_syscall`, `gz_test_shm`,
`gz_test_chm`, `gz_test_vreg` — of which `simple_ut`, `test_gz_syscall`,
`gz_test_shm`, `gz_test_chm`, `gz_test_vreg` carry emitted
`__kcfi_typeid_` symbols because they are address-taken across translation
units.

## 2. Device / registration objects

| object | type | role |
|---|---|---|
| `gz_device` | `struct miscdevice` | `MISC_DYNAMIC_MINOR`, name `gz_kree`, `&fops` |
| `gz_main_of_match` | `struct of_device_id[]` | one entry: `mediatek,trusty-mtee-v1` |
| `__mod_of__gz_main_of_match_device_table` | alias | emitted by `MODULE_DEVICE_TABLE(of, …)` |
| `gz_ffa_device_id` | `struct ffa_device_id[]` | one UUID + terminator |

## 3. Global state

| object | type | protected by | role |
|---|---|---|---|
| `g_ffa_dev` | `struct ffa_device *` | — | cached FF-A device from probe |
| `g_ffa_ops` | `const struct ffa_ops *` | — | cached FF-A operation table |
| `ffa_enabled` | `bool` | — | returned by ioctl 200 |
| `device_driver_initalized` | `bool` | — | one-shot guard for FF-A chardev creation (vendor spelling preserved) |
| `fm_head` | `struct ffa_mem_list_head` | `ffa_mem_lock` | list head storage |
| `ffa_drv_manager` | `struct ffa_mem_list_head *` | `ffa_mem_lock` | circular list anchor |
| `_uts_total`, `_uts_failed` | counters | per-test mutex | unit-test tallies; **three separate pairs**, one per UT translation unit |
| `buf1`, `buf2` | static buffers | `shmem_ut_mutex` | shared-memory UT scratch |

## 4. Synchronisation objects

| object | type | scope |
|---|---|---|
| `ut_mutex` | mutex | general UT serialisation |
| `simple_ut_mutex` | mutex | `simple_ut` |
| `chmem_ut_mutex` | mutex | `gz_test_chm` |
| `shmem_ut_mutex` | mutex | `gz_test_shm` |
| `vreg_ut_mutex` | mutex | `gz_test_vreg` |
| `ffa_mem_lock` | spinlock | FF-A memory record list |
| `session_info::mux` | mutex (per open) | session handle table |
| `_init_session_info.__key`, `device_driver_init.__key` | lockdep keys | static keys for the two dynamically initialised locks |

## 5. Absent object classes

| class | state |
|---|---|
| workqueues | none — the module uses `kthread_run`, not workqueues |
| notifiers | none |
| completions | none |
| timers | none |
| `struct list_head` lists | none — FF-A uses its own `ffa_mem_list_head` |
| PM ops | none (`.driver.pm` unset, no `dev_pm_ops` object) |
