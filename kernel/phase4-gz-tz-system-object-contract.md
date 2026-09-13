# `gz_tz_system.ko` — object, ops-table and global-state contract

35 stock objects, all reproduced. Parity table:
`kernel/phase4-gz-tz-system-object-parity.tsv` — **30/35 byte-and-offset
exact, 5 differ only in `.modinfo` offset because the `vermagic` git-describe
string is 2 bytes shorter in a local build.** No object differs in content.

## 1. Driver / ops tables

| object | section | size | contents |
|---|---|---:|---|
| `tz_system_driver` | `.data` | 248 | `struct platform_driver` |
| `tz_system_of_match` | `.rodata` | 400 | `struct of_device_id[2]` |
| `__mod_of__tz_system_of_match_device_table` | `.rodata` | 400 | alias of the above, emitted by `MODULE_DEVICE_TABLE` |

```c
struct platform_driver tz_system_driver = {
        .probe  = tz_system_probe,          /* .text, 268 B, LOCAL, kCFI 0x63df1691 */
        .remove = tz_system_remove,         /* .text,          LOCAL               */
        .driver = {
                .name           = "trusty_tz",
                .owner          = THIS_MODULE,
                .of_match_table = tz_system_of_match,
        },
};
static const struct of_device_id tz_system_of_match[] = {
        { .compatible = "mediatek,trusty-tz", },
        {},
};
```

| callback slot | stock target | rebuilt target | kCFI | parity |
|---|---|---|---|---|
| `.probe` | `tz_system_probe` | `tz_system_probe` | `0x63df1691` | **EXACT** |
| `.remove` | `tz_system_remove` | `tz_system_remove` | matches | **EXACT** |

These are the **only** two callback slots in the module. There is no
`file_operations`, no `miscdevice`, no `dev_pm_ops`, no notifier block, no
`attribute_group` — see the userspace-ABI report for the full negative proof.

## 2. Locks (`.data`, 48 bytes each — `struct mutex`)

| object | offset | protects |
|---|---:|---|
| `fd_mutex` | `0x00` | the 512-slot session handle table |
| `session_mutex` | `0x30` | session create/close lifecycle |
| `servicecall_lock` | `0x60` | global service-call serialisation (`cpumask == -1`) |
| `perf_boost_lock` | `0x90` | `perf_boost_cnt` and the wake-lock |
| `shared_mem_mutex_trusty` | `0x1c0` | shared-memory registration, Trusty TEE |
| `shared_mem_mutex_nebula` | `0x1f0` | shared-memory registration, Nebula TEE |
| `chmem_mutex` | `0x220` | multi-chunk append/release |

Seven mutexes, no spinlocks, no rwlocks, no seqlocks, no atomics.

## 3. Session table and channel state (`.bss`)

| object | offset | size | role |
|---|---:|---:|---|
| `_kree_session_handle_pool` | `0x8` | **4096** | `struct tipc_k_handle[512]` — 8 bytes/slot |
| `_kree_session_handle_idx` | `0x1008` | 4 | rotating allocation cursor |
| `_sys_service_h` | `0x1010` | 16 | `struct tipc_k_handle[TEE_ID_END]` → **`TEE_ID_END == 2`** |
| `_sys_service_Fd` | `.data 0xc0` | 8 | `int32_t[2]`, initialised to `{-1, -1}` |

The sizes are load-bearing evidence: `4096 / 512 = 8` confirms
`sizeof(struct tipc_k_handle) == 8` (a single `void *dn`), and `16 / 8 == 2`
plus `8 / 4 == 2` independently confirm exactly **two** TEE ids (Trusty and
Nebula) are compiled in.

## 4. Service-name table

| object | section | size | contents |
|---|---|---:|---|
| `gz_sys_service_name` | `.rodata` | 16 | `char *[2]` |

```c
static char *gz_sys_service_name[] = {
        "com.mediatek.geniezone.srv.sys",
        "nebula.com.mediatek.geniezone.srv.sys",
};
```

16 bytes = 2 pointers — again confirming two TEEs. Both strings are present in
the stock `.rodata.str1.1`.

## 5. Thread / completion / PM state (`.bss`)

| object | offset | size | role |
|---|---:|---:|---|
| `ree_dummy_event` | `0x1020` | 32 | `struct completion` |
| `ree_dummy_task` | `0x1060` | 8 | `struct task_struct *` |
| `TeeServiceCall_wake_lock` | `0x1068` | 8 | `struct wakeup_source *` (`CONFIG_PM_SLEEP`) |
| `perf_boost_cnt` | `0x105c` | 4 | wake-lock refcount |
| `new_param` | `0x1040` | 24 | scratch parameter block |
| `tz_system_dev` | `0x0` | 8 | `struct platform_device *` — **the only exported object** |

`tz_system_dev` (CRC `0xebab6727`) is exported so that `tz_system_std_call32`
can reach `tz_system_dev->dev.parent` for `trusty_std_call32`.

## 6. Lockdep keys

| object | size |
|---|---|
| `KREE_CreateSession.__key` | 1 |
| `init_completion.__key` | 1 |

Static lockdep keys emitted for the `mutex`/`completion` initialised inside
those functions. Their presence confirms the kernel build has lockdep key
emission on, matching exact-GKI.

## 7. Module-infrastructure objects

| object | section | size |
|---|---|---:|
| `__this_module` | `.gnu.linkonce.this_module` | 1088 |
| `____versions` | `__versions` | **3264** = 51 × 64 |
| `__UNIQUE_ID_license426` | `.modinfo` | 15 |
| `__UNIQUE_ID_vermagic333` | `.modinfo` | 87 |
| `__UNIQUE_ID_name334` | `.modinfo` | 18 |
| `__UNIQUE_ID_depends335` | `.modinfo` | 33 |
| `__UNIQUE_ID_alias336` | `.modinfo` | 33 |
| `__UNIQUE_ID_alias337` | `.modinfo` | 35 |
| `_note_9`, `_note_10` | `.note.Linux` | 24 each |
| `__UNIQUE_ID___addressable_init_module424` | `.init.data` | 8 |
| `__UNIQUE_ID___addressable_cleanup_module425` | `.exit.data` | 8 |

`____versions` at 3264 bytes is an exact cross-check of the 51 MODVERSION
records (50 imports + `module_layout`).

The five `.modinfo` objects whose *offsets* shift by 2 are the sole object
residual, caused entirely by
`vermagic=…-g945dff7bc1bf` (stock) vs `…-maybe-dirty` (local). Their `size`
fields are identical except `vermagic` itself (87 vs 85). No content
difference.

## 8. Init / exit paths

| symbol | section | note |
|---|---|---|
| `init_module` | `.init.text` | alias of the `module_init` function |
| `cleanup_module` | `.exit.text` | alias of the `module_exit` function |

Init registers `tz_system_driver` via `__platform_driver_register`
(import `0x894c433a`); exit calls `platform_driver_unregister`
(`0xe1b15563`). The real work happens in `tz_system_probe`, not in
`init_module`.

## 9. UUID / identifier tables

There are **none**. Unlike `tmem_ffa`, this module hardcodes no TA UUID: the
UUID is always supplied by the caller as the `const char *ta_uuid` argument to
`KREE_CreateSession`. The only fixed identifier strings are the three port
names (two sys services + `com.default.tee_id`).
