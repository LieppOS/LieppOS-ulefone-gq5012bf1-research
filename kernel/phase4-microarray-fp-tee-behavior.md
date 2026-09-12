# MicroArray fingerprint TEE — recovered behavioural contract

Everything below is read out of the frozen stock oracle
`8e1449cea5d07ef663d368ce5eea27e8c879a9cd70d39f8fc2b5b25445c2cf33`
by relocation-aware disassembly plus the frozen `.data`/`.rodata` images, the
frozen device tree, and the stock userspace binaries. Nothing about the secure
world is invented.

## Identity

| property | value |
|---|---|
| bus | SPI (`spi_bus_type`) |
| `spi_device_id` | `madev` |
| compatible | `mediatek,madev_finger` |
| char device | `/dev/madev0`, class `madev`, dynamic major |
| DT node | `/soc/spi1@11011000/fingerprint@0`, `reg = <0>`, `spi-max-frequency = <8000000>`, `vfp-supply`, parent controller `tee-only`, CS = GPIO 61 |
| IRQ source | `of_find_compatible_node("mediatek,yft_finger")` → `irq_of_parse_and_map(np, 0)` |
| driver version | `MA_DRV_VERSION = 0x4006` |

## Provider edges

| provider | symbol | use |
|---|---|---|
| `fingerprint.ko` | `yft_waite_for_finger_dts_paser` | first call in `mas_probe` |
| `fingerprint.ko` | `yft_finger_set_reset(1)` | in `mas_finger_set_gpio_info`, return ignored |
| `fingerprint.ko` | `yft_finger_set_spi_mode(1)` | in `mas_finger_set_gpio_info` and on every `mas_sync` |
| `fingerprint.ko` | `yft_finger_set_irq(1)` | in `mas_finger_set_gpio_info`, return ignored |
| `spi-mt65xx.ko` | `mt_spi_enable_master_clk` | `mas_enable_spi_clock` |
| `spi-mt65xx.ko` | `mt_spi_disable_master_clk` | `mas_disable_spi_clock` |
| `tkcore.ko` | `tee_spi_transfer` | 5 call sites, all inside `init_connect` |

`mas_enable_spi_clock` / `mas_disable_spi_clock` are defined and exported as
global symbols but are not referenced from any other function in the module;
they exist for the vendor's own external callers.

## Data path is hybrid, and the split is exact

| path | transport |
|---|---|
| probe-time chip identification (`init_connect`) | TrustKernel `tee_spi_transfer` only |
| all runtime `read()` / `write()` traffic (`mas_sync`) | normal-world `spi_sync` under `dev_lock` |

There is no `tee_spi_transfer` call outside `init_connect`, and no `spi_sync`
call inside it. The two never substitute for one another.

## `tee_spi_transfer` ABI (read out of stock `tkcore.ko`)

```c
int tee_spi_transfer(void *conf, int conf_size,
                     const char *txbuf, char *rxbuf, int len);
```

Provider behaviour, decoded from `tkcore.ko` `.text+0x9218`:

1. returns `-EINVAL` if `conf`, `txbuf` or `rxbuf` is NULL, or `len == 0`
2. `memset` a 0x108-byte `TEEC_Context` and a 0x118-byte `TEEC_Operation`
3. `memcpy(rxbuf, txbuf, len)` — the rx buffer carries the request in
4. `TEEC_InitializeContext(NULL, &ctx)`
5. `TEEC_OpenSession(&ctx, &sess, &uuid, /*login*/ 0, NULL, NULL, &origin)`
   with UUID **`966d3f7c-04ef-1beb-08b7-57f37a6d87f9`** (stock `tkcore` `.data+0x1f8`)
6. `TEEC_InvokeCommand(&sess, /*cmd*/ 0, &op, &origin)` with
   `op.paramTypes = 0x75` =
   `TEEC_PARAM_TYPES(MEMREF_TEMP_INPUT, MEMREF_TEMP_INOUT, NONE, NONE)`,
   `params[0] = {conf, conf_size}`, `params[1] = {rxbuf, len}`
7. `TEEC_CloseSession`, `TEEC_FinalizeContext`, return the TEEC result

The `TEEC_Parameter` union is 24 bytes in this implementation (it carries
`TEEC_RegisteredMemoryReference`), which is why `params[1]` starts at `op+0x38`.

### The 80-byte configuration blob

`init_connect.smt_conf` at stock `.data+0x158`, passed as `MEMREF_TEMP_INPUT`
with `conf_size = 0x50`:

```
u32[20] = { 10, 10, 10, 10, 10,  0, 0, 0, 0, 0,
             1,  1,  0,  0,  0,  1, 0, 0, 0, 0 }
```

The reconstruction reproduces this byte image exactly. **The field semantics
live in the secure world and are classified UNPROVABLE** — no Linux-side or
userspace artefact names them. Do not attribute MediaTek `mt_chip_conf` field
names to it; the size does not match any known `mt_chip_conf` layout.

## `init_connect()` chip identification sequence

| step | tx bytes | len | rx | accept condition | result |
|---|---|---|---|---|---|
| 1 | `8C FF FF FF` | 4 | same buffer | transfer must succeed | else log `TEE RESET SPI transfer failed` and return `-1` |
| — | `msleep(100)` | | | | |
| 2 | `00 FF FF FF` | 4 | `outid[4]` | `(outid[3] & ~0x04) == 0x41` | `[MAFP] chip is ok1`, `chip_id = outid[3]` |
| 3 | `70 00 00 00 00` | 5 | `inid[5]` | — | |
| — | `msleep(3)` | | | | |
| 4 | `90 08 00 00 00` | 5 | `inid[5]` | `inid[3] == 0x20 \|\| inid[3] == 0x1a` | `[MAFP] chip is ok2`, `chip_id = inid[3]` |
| 5 | `90 0B 00 00 00` | 5 | `inid[5]` | `inid[3] == 0x4a` | `[MAFP] chip is ok3`, `chip_id = inid[3]` |

Step 2 also logs `[MAFP] outid[3]=[0x%x, 0x%x,0x%x,0x%x]`. If nothing matches,
it logs `[init_connect], chip_id is 0x%x` and returns the current `chip_id`.
Any failing transfer after step 1 logs `TEE SPI transfer failed` and returns
`-1`. `mas_probe` calls `init_connect()` and **ignores its return value**.

`deinit_connect()` returns 0 and does nothing.

## Character device ABI

`struct file_operations` contains exactly six members: `owner`, `read`,
`write`, `unlocked_ioctl`, `compat_ioctl`, `mmap`. There is **no** `open`,
`release` or `poll`, so `/dev/madev0` has no per-open state.

### `read(fd, buf, count)`

```
count > 0xc000            -> log "data too long",        return -1
mas_sync(stxb, srxb, count) != 0 -> log "mas_sync failed.",    return -2
copy_to_user(buf, srxb, count)   -> log "copy_to_user failed.", return -3
otherwise                                                       return count
```

`stxb` and `srxb` are two persistent 0xc000-byte kmalloc buffers. A read
therefore transmits whatever the previous `write()` left in `stxb`.

### `write(fd, buf, count)`

```
count == 6      -> copy_from_user into a 6-byte stack buffer, discard, return 0
count > 0xc000  -> log "write data too long", return -1
otherwise       -> memset(stxb, 0, 0xc000); copy_from_user(stxb, buf, count)
                   on partial copy: zero the tail, log "copy form user failed",
                   return -2; else return count
```

The `count == 6` case is a genuine stock quirk: the data is copied into a local
buffer and thrown away.

### `mmap`

Allocates one shared `kmalloc(0x11000, GFP_KERNEL)` buffer on first use
(`kernel_memaddr`), sets `vma->vm_page_prot = pgprot_noncached(...)`
(AttrIndx = 3, plus `PTE_PXN|PTE_UXN`), then `remap_pfn_range()` over
`vm_end - vm_start`. Returns `0` on success and `-1` on any failure.

### `compat_ioctl`

```c
return filp->f_op->unlocked_ioctl(filp, cmd, arg);
```

The argument is passed through unchanged — there is no `compat_ptr()`
translation, so 32-bit callers must already pass a 64-bit-safe pointer.

## ioctl table

Magic `'M'` (0x4d). All payloads are `u32`. Accepted commands only; every other
value in `0x4d01..0x4d2d` and every value outside the three switch ranges logs
`mas_ioctl no such cmd` and returns `-EINVAL`.

| request | encoding | behaviour |
|---|---|---|
| `0x4d01` | `_IO('M',0x01)` | `__pm_wakeup_event(gProcessWakeLock, 5000)` |
| `0x4d02` | `_IO('M',0x02)` | `flag_int = 0; wait_event_interruptible(gWaitq, flag_int)` |
| `0x4d03` | `_IO('M',0x03)` | `flag_int = 1; wake_up_interruptible(&gWaitq)` |
| `0x4d04` | `_IO('M',0x04)` | accepted no-op, returns 0 |
| `0x4d05` | `_IO('M',0x05)` | accepted no-op, returns 0 |
| `0x4d06` | `_IO('M',0x06)` | `enable_irq(irq)` |
| `0x4d07` | `_IO('M',0x07)` | `disable_irq(irq)` |
| `0x4d08` | `_IO('M',0x08)` | key 249 press + `EV_SYN` |
| `0x4d09` | `_IO('M',0x09)` | key 249 release + `EV_SYN` |
| `0x4d0b` | `_IO('M',0x0b)` | key 249 press + release, each with `EV_SYN` |
| `0x4d0d` | `_IO('M',0x0d)` | accepted no-op, returns 0 |
| `0x4d24` | `_IO('M',0x24)` | `mas_switch_power(0)` |
| `0x4d25` | `_IO('M',0x25)` | `mas_switch_power(1)` |
| `0x4d27` | `_IO('M',0x27)` | `flag_u2 = 0; wait_event_interruptible(U2_Waitq, flag_u2)` |
| `0x4d28` | `_IO('M',0x28)` | `flag_u2 = 1; wake_up_interruptible(&U2_Waitq)` |
| `0x4d2d` | `_IO('M',0x2d)` | `mas_switch_power(0); msleep(5); mas_switch_power(1)` |
| `0x40044d21` | `_IOW('M',0x21,u32)` | `ioctl_lock`; `copy_from_user(&ma_drv_reg, arg, 4)` |
| `0x40044d26` | `_IOW('M',0x26,u32)` | `copy_from_user(&ma_speed, arg, 4)` then `ma_spi_change(spi, ma_speed, 0)` — **no mutex** |
| `0x40044d2a` | `_IOW('M',0x2a,u32)` | `ioctl_lock`; read `ma_drv_reg`; unlock; `msleep(4)`; `flag_u1 = 1`; `wake_up_interruptible(&U1_Waitq)` |
| `0x80044d22` | `_IOR('M',0x22,u32)` | `ioctl_lock`; `copy_to_user(arg, &ma_drv_reg, 4)` |
| `0x80044d23` | `_IOR('M',0x23,u32)` | `ioctl_lock`; `copy_to_user(arg, &MA_DRV_VERSION, 4)` → `0x4006` |
| `0x80044d29` | `_IOR('M',0x29,u32)` | `flag_u1 = 0`; wait on `U1_Waitq`; then locked `copy_to_user(arg, &ma_drv_reg, 4)` |
| `0x80044d2b` | `_IOR('M',0x2b,u32)` | `ioctl_lock`; `copy_to_user(arg, &is_screen_on, 4)` |

Rejected inside the scanned range: `0x4d0a`, `0x4d0c`, `0x4d0e`–`0x4d23`,
`0x4d26`, `0x4d29`–`0x4d2c`, and `0x80044d24`–`0x80044d28`, `0x80044d2a`.

Return-value quirk preserved from stock: on `access_ok` failure the handler
returns the **residue 4**, not `-EFAULT`, and the `copy_from_user` paths zero
the destination.

`ma_spi_change()` and `mas_select_transfer()` are empty in stock; they are
retained so the reconstructed call graph matches.

## Input device

`input_allocate_device()`; `EV_KEY`; key codes **249** and **116
(`KEY_POWER`)**; `id.bustype = BUS_SPI (0x1c)`; `name = "madev"`. On
`input_register_device()` failure the device is freed and `smas->input` is left
NULL; probe still succeeds.

## IRQ and work

```
request_threaded_irq(irq, mas_interrupt, NULL, IRQF_TRIGGER_RISING,
                     "mediatek,finger_print-eint", NULL);
irq_set_irq_wake(irq, 1);
```

`mas_interrupt()` does `queue_work(gWorkq, &gWork)` and returns `IRQ_HANDLED`.
`mas_work()` sets `flag_int = 1` and `wake_up_interruptible(&gWaitq)`. The
workqueue is `create_singlethread_workqueue("mas_workqueue")`
(`__WQ_LEGACY|__WQ_ORDERED|__WQ_ORDERED_EXPLICIT|WQ_UNBOUND|WQ_MEM_RECLAIM`,
flags `0x000E000A`).

## Power

`mas_finger_set_gpio_info(dev, on)` **ignores `on`**: it always
`regulator_get(dev, "vfp")`, `regulator_set_voltage(2800000, 2800000)`,
`regulator_enable()`, then drives the three YFT setters with `1`.
`mas_switch_power(on)` enables/disables the same regulator and returns `-1` on
failure. The MT6377/MT6373 naming in the log strings is stock text; the actual
supply is DT property `vfp-supply`.

## probe / remove

`mas_probe()` order: log start → `spi->mode = 0` → `yft_waite_for_finger_dts_paser()`
→ `mas_finger_set_gpio_info(&spi->dev, 1)` → four allocations
(`sdev` 0x28, `smas` 0x248, `srxb` 0xc000, `stxb` 0xc000) →
`wakeup_source_register(NULL, "microarray_process_wakelock")` → `INIT_WORK` →
workqueue → IRQ → `smas->spi = spi`, `spi->max_speed_hz = 6000000`,
`spi_setup()` → `INIT_LIST_HEAD` → `init_connect()` (return ignored) →
`alloc_chrdev_region("madev")` → `cdev_alloc`/`cdev_add` →
`class_create("madev")` → `device_create("madev0")` →
`sysfs_create_group(&spi->dev.kobj, &madev_attrs_group)` → `mas_set_input()` →
log end → `is_screen_on = 1` → return 0.

`mas_remove()` (void, 6.1 signature): `cdev_del`, `disable_irq`, `free_irq`,
`destroy_workqueue`.

`module_init` logs, sets the internal `compatible` flag, and calls
`spi_register_driver(&sdrv)`. `module_exit` is empty — the stock module never
unregisters its SPI driver. `mas_remove_platform()` exists and would call
`driver_unregister(&sdrv.driver)` but is never invoked.

## sysfs

One attribute, `chip_id`, mode read-only, on the SPI device:
`snprintf(buf, PAGE_SIZE, "chip_id:0x%04x\n", chip_id)`.

## Userspace consumers (static evidence only)

- `/vendor/lib64/libfprint-x64.so` — `ma_tac_*` and
  `Java_com_microarray_fingerprint_FingerprintTest_native*` entry points
  (`nativeSPICommunicate`, `nativeSet2FactoryMode`, `nativeGetBkg`,
  `nativeDirtyFinger`, `ma_tac_big_data_spi_test`, `ma_tac_factory_get_chipid`, …)
- `/vendor/lib64/hw/microarray.fingerprint.default.so`
- `/vendor/bin/hw/android.hardware.biometrics.fingerprint-service.example`
- `init.fingerprint.rc`: `/dev/madev0` → `0666 system system` on boot,
  `0777` post-fs-data
- TA `vendor/app/t6/edcf9395-3518-9067-614cafae2909775b.ta` is the MicroArray
  application TA; `966d3f7c-04ef-1beb-08b7-57f37a6d87f9` is the TrustKernel SPI
  proxy TA invoked by `tee_spi_transfer`

## Explicitly unprovable

| item | status |
|---|---|
| field semantics of the 80-byte `smt_conf` blob | UNPROVABLE from Linux/userspace artefacts |
| meaning of opcodes `0x8C`, `0x00`, `0x70`, `0x9008`, `0x900B` inside the sensor | UNPROVABLE; only the byte sequences and accept conditions are known |
| everything behind the TA boundary | UNPROVABLE; not reimplemented |
| why key code 249 was chosen | not recorded in any artefact |
