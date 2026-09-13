# gz_main_mod — source search and candidate classification

## 1. Search method

The search started in the pinned MediaTek/Nothing tree and only ever needed to
stay there. Exact stock identifiers recovered from the frozen oracle were used
as the search keys, not filename guesses:

| search key | origin |
|---|---|
| `tz_client_open_session` | stock defined function |
| `gz_compat_ioctl` | stock defined function |
| `mtee_sdsp_enable` | stock defined function |
| `gz_ffa_driver_probe` | stock defined function |
| `mediatek,trusty-mtee-v1` | stock `modules.alias` + OF table |
| `tipc_set_default_cpumask` | stock import |
| `ffa_driver_register` | stock import |
| `gz_kree`, `gz_ffa_dev` | stock `.rodata` device-name strings |

## 2. Result

All keys resolve inside one pinned revision:

```
NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878
957dac185efe46cbf6336b0fff9516d84c8cd78f
drivers/misc/mediatek/geniezone/
```

`git rev-parse HEAD` in the donor checkout returns that exact revision and
`git status` reports the geniezone subtree clean, so the donor is the pinned
revision itself, not a derivative.

## 3. Object membership — proven, not assumed

Filename similarity was explicitly **not** trusted. Membership was read out of
the vendor build files:

`drivers/misc/mediatek/geniezone/Makefile` lines 51-56:

```make
obj-$(CONFIG_MTK_GZ_MAIN) += gz_main_mod.o
gz_main_mod-objs += gz_main.o \
                    mtee_ut/gz_ut.o \
                    mtee_ut/gz_chmem_ut.o mtee_ut/gz_shmem_ut.o \
                    mtee_ut/gz_vreg_ut.o \
                    gz_ffa.o
```

`drivers/misc/mediatek/geniezone/Kconfig` line 26 defines `MTK_GZ_MAIN` as
`tristate`, matching a stock loadable module.

This confirms the earlier gz_tz_system finding: `gz_main.c` belongs to
`gz_main_mod`, and `gz_tz_system` is a *different* module built from
`tz_system.o mtee-kree/tz_mmap.o mtee-kree/kree_mem.o` in the same directory.

The six-object list is independently corroborated by the stock ELF: every one
of the 42 stock functions maps onto exactly one of those six translation
units, with no function left over and none missing.

| object | stock functions it accounts for |
|---|---|
| `gz_main.o` | `gz_test_show`, `gz_test_store`, `mtee_sdsp_enable`, `gz_adjust_task_attr`, `gz_manual_adjust_trusty_wq_attr`, `gz_main_probe`, `gz_main_remove`, `get_gz_version`, `gz_ioctl`, `gz_compat_ioctl`, `gz_dev_open`, `gz_dev_release`, `_gz_ioctl`, `_reg_shmem_from_userspace`, `tz_client_open_session`, `tz_client_close_session`, `tz_client_tee_service`, `DMAFd2MemHandle`, `access_ok`, `_register_session_info`, `check_gp_inout_mem`, `init_module`, `cleanup_module` |
| `mtee_ut/gz_ut.o` | `test_gz_syscall`, `simple_ut`, `test_all_funs`, `test_saturation` |
| `mtee_ut/gz_chmem_ut.o` | `gz_test_chm_main`, `gz_test_chm` |
| `mtee_ut/gz_shmem_ut.o` | `verify_data`, `upt_data_in_GZ`, `shmem_test_continuous`, `shmem_test_discontinuous`, `gz_test_shm` |
| `mtee_ut/gz_vreg_ut.o` | `gz_test_vreg_main`, `gz_test_vreg` |
| `gz_ffa.o` | `ffa_send_to_ha`, `kmalloc_aligned`, `ff_a_gz_ioctl`, `gz_ffa_driver_probe`, `gz_get_ffa_dev`, `memory_send` |

## 4. Path parity evidence

The stock module embeds exactly one vendor path string:

```
../kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz_ffa.c
```

This is a `__FILE__` expansion from `gz_ffa.c`. It pins the build location to
the vendor directory layout, which is why this module is built in-tree at
`kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/` rather than under
`lieppos/`. No other vendor source path appears in the stock strings, so no
other include path text is byte-constrained.

## 5. Classification

**EXACT_SOURCE.**

The pinned revision supplies every object, every header and the exact build
recipe. No forward-port, no revision substitution and no donor variant was
required. Because the subsequent RED build reproduced the stock module with
zero functional delta, the final module classification is
`DIRECT_SOURCE_MATCH`.

No internet search was performed: the exact pinned source was found first.
