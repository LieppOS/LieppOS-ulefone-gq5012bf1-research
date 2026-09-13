# Phase 4 — `tkcore.ko` stock inventory (GQ5012BF1 / MT6878T)

Static, offline analysis of the frozen oracle
`workspace/phase4-tkcore/oracle/tkcore.ko`
(`sha256 03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`,
221352 bytes). The module was never loaded and no TrustKernel interface was
invoked on-device.

Machine-readable inventories (authoritative):

| File | Rows |
|---|---|
| `kernel/phase4-tkcore-functions.tsv` | 122 |
| `kernel/phase4-tkcore-objects.tsv` | 214 |
| `kernel/phase4-tkcore-imports.tsv` | 101 |
| `kernel/phase4-tkcore-modversions.tsv` | 101 |
| `kernel/phase4-tkcore-exports.tsv` | 25 |
| `kernel/phase4-tkcore-relocations.tsv` | 3098 |
| `kernel/phase4-tkcore-strings.tsv` | 378 |

## 1. Packaging and load position

* Present **only** in `vendor-ramdisks/platform` (`lib/modules/tkcore.ko`).
  Not in the recovery ramdisk, `vendor_dlkm`, or `system_dlkm`.
* `modules.load`: entry **100 of 184**; `modules.load.recovery`: **98 of 189**;
  `tkcore_drv.ko` is loaded immediately after in both lists.
* `modules.dep`: `/lib/modules/tkcore.ko:` — **no dependencies**. Consumers
  declare it: `tkcore_drv.ko: ffa_v10.ko tkcore.ko`, and
  `microarray_fp_tee.ko: tkcore.ko spi-mt65xx.ko fingerprint.ko`.
* `.modinfo`: author `TrustKernel`, description `TrustKernel TKCore TEEC v1.0`,
  version `6:1.1-k6.6`, license `GPL`, `import_ns=DMA_BUF`, name `tkcore`,
  `srcversion 604D4583E310DBFAC768366`, build id
  `6b6663820488959123f26a85dded547e305c56d6`, Clang 17.0.2 (`r487747c`,
  build 10087095).

## 2. Lifecycle

```c
int init_module(void)        /* zeroes the .bss driver state, then: */
{
        …
        plat_tee_init();     /* return value deliberately ignored */
        return 0;            /* module load never fails */
}
void cleanup_module(void) { }   /* single `ret` — nothing is torn down */
```

`plat_tee_init()` walks the CPU topology bitmap (`_find_next_bit` over 56-byte
`cpu_topology` entries), takes the maximum cluster id, stores it in
`large_cluster_id` and prints `tkcore: big cluster_id = %d`. It always returns
0. The device model itself is created later by `tkcore_drv.ko`, which calls
`tee_core_alloc(dev, name, id, ops, 0xa0)` → `tee_core_add()`.

Consequently `tkcore.ko` alone registers nothing: no char device, no procfs
entry, no sysfs group exists until the backend driver calls in.

## 3. Device model created on `tee_core_add()`

`tee_device_configs[3]` (`.data`, 3 × 40 bytes):

| Entry | Device name | `file_operations` |
|---|---|---|
| 0 | `tkcore_admin` | `tee_admin_fops` (supplicant: `tee_supp_read`/`tee_supp_write`) |
| 1 | `tkcore_client` | `tee_client_fops` (`tee_ioctl`, `tee_compat_ioctl`, `tee_ctx_open`, `tee_ctx_release`) |
| 2 | `tkcore_fp` | `tee_client_fops` (plus a per-entry flag word) |

For each entry `tee_core_add()` allocates a 0x68-byte misc-device record with
`devm_kmalloc()`, sets `minor = 0xff` (`MISC_DYNAMIC_MINOR`), links it into the
`struct tee` misc list at `+0xa0` and calls `misc_register()`; failures log
`TEE core: misc_register() failed …` and unwind by `misc_deregister()` + `kfree()`.
`tee_session_fops` backs anonymous per-session file descriptors created by
`tee_session_create_fd()`.

Stock `ueventd.rc` permissions: `/dev/tkcore_admin 0600 system system`,
`/dev/tkcore_client 0660 root system`, `/dev/tkcore_fp 0660 root system`.

## 4. procfs

`tee_init_procfs()` creates `proc_mkdir("tkcore")` and the entries:

| Path | Backing ops | Note |
|---|---|---|
| `/proc/tkcore/tkcore_log` | `log_tee_ops` (0x60-byte `proc_ops`) | secure-world log ring; read by `/vendor/bin/teed` |
| `/proc/tkcore/tkcore_teed_version` | `teed_version_ops` | writable; `.data teed_version` starts as `"unknown\n"` |
| `/proc/tkcore/tkcore_drv_version` | `drv_version_ops` | reports `6:1.1-k6.6` |
| `/proc/tkcore/tkcore_os_version` | `tee_version_ops` | secure-OS version |

`tee_init_procfs()` additionally resolves the `tee-log` DT/IRQ resource,
`request_threaded_irq(…, "tee_log_irq", …)` and starts the `logd` kthread
(`kthread_create_on_node` + `wake_up_process`); `tee_exit_procfs()` does
`free_irq()` + `kthread_stop()` + `proc_remove()`. `tee_log_read()` waits with
`schedule_timeout()` and copies the klog ring to user space.

Userspace confirmation: `/vendor/bin/teed` opens `/proc/tkcore/tkcore_log`,
writes the `[yyyy-mm-dd hh:mm:ss] TKCORE_LOG_START` banner and reads
`/proc/tkcore/tkcore_teed_version`.

## 5. sysfs

`device_attrs[8]` (`.data`, 8 × 32-byte `struct device_attribute`), registered
by `tee_init_sysfs()` and removed by `tee_cleanup_sysfs()`:
`dump`, `stat`, `info`, `state`, `name`, `refcount`, `type`, `conf`
(each with a distinct `show` handler; no `store`).

`tee_state_string` maps the state word to
`offline`, `online`, `suspended`, `running`, `crashed`, `invalid`.

## 6. UAPI (ioctl surface)

`tee_internal_ioctl()` (shared by `tee_ioctl`/`tee_compat_ioctl`, magic `0x74`
= `'t'`):

| Request | Payload | Handler |
|---|---|---|
| `0xc03074a1` | 48 B `tee_cmd_io` | open session → `tee_session_create_fd()` |
| `0xc03074a3` | 48 B | invoke command |
| `0xc03074a4` | 48 B | cancel command |
| `0xc01874a5` | 24 B `tee_shm_io` | `tee_shm_alloc_io()` |
| `0xc01874a6` | 24 B | shm alloc variant |
| `0xc01874a7` | 24 B | `tee_shm_fd_for_rpc()` |
| `0xc01874ad` | 24 B | SPTA install (`convert_compat_tee_spta_inst`) |
| `0xc01874ae` | 24 B | SPTA variant |
| `0x800474b7` | 4 B out | copies `nsdrv_feature_flags` to user |

32-bit callers are normalised by `convert_compat_tee_cmd()`,
`convert_compat_tee_shm_io()` and `convert_compat_tee_spta_inst()` before the
common path. Shared memory is exported to user space through DMA-BUF
(`tee_static_shm_dma_buf_ops`, namespace `DMA_BUF`), with
`sg_alloc_table_from_pages()` and IOMMU mapping on the secure path.

## 7. Recovered structure sizes (from instruction evidence)

| Type | Size | Evidence |
|---|---|---|
| `struct tee` | 312 (`0x138`) | `devm_kmalloc(dev, priv_len + 0x138)` in `tee_core_alloc()` |
| `struct tee_context` | 208 (`0xd0`) | `devm_kmalloc(dev, 0xd0)` in `tee_context_create()` |
| `TEEC_Context` | 264 (`0x108`) | `memset(ctx, 0, 0x108)` in `tee_spi_cfg_padsel()` |
| `TEEC_Operation` | 280 (`0x118`) | `memset(op, 0, 0x118)` |
| `TEEC_SharedMemory` | 40 (`0x28`) | member offsets in `TEEC_AllocateSharedMemory()` |
| `tee_wait_queue_private` | 64 (`0x40`) | `__mutex_init(priv)` + `list_head` at `+0x30` |
| `tkcore_drv` private area | 160 (`0xa0`) | `tee_core_alloc(…, 0xa0)` in `tee_tz_new()` |
| misc-device record | 104 (`0x68`) | `devm_kmalloc(dev, 0x68)` per `tee_device_configs` entry |

Field-level layouts are tabulated in `kernel/phase4-tkcore-provider-abi.md` §4.

## 8. Secure peripheral services

* **SPI proxy.** `tee_spi_transfer()`, `tee_spi_transfer_disable()` and
  `tee_spi_cfg_padsel()` open a TEEC session to
  `SENSOR_DETECTOR_TA_UUID = 966d3f7c-04ef-1beb-08b7-57f37a6d87f9`
  (`.data` bytes `7c3f6d96 ef04 eb1b 08b7 57f37a6d87f9`) and invoke command
  **0** (transfer, `paramTypes 0x75` = MEMREF_TEMP_INPUT(conf) +
  MEMREF_TEMP_INOUT(rx)), command **1** (disable) or command **2** (padsel, a
  value parameter). Debug strings confirm the argument roles:
  `conf=%p conf_size=%u inbuf=%p outbuf=%p size=%u` and `padsel=0x%x`.
  `microarray_fp_tee.ko` is the only consumer.
* **Clock manager.** `tee_clkmgr_register()` accepts clock class names
  `spi` (id base 0), `i2c` (`0x10000`) and `i2c-dma` (`0x20000`), allocating
  0x48-byte entries on a mutex-protected list (`clk_list`, `clk_list_lock`);
  `tee_clkmgr_handle()` looks an entry up by id and dispatches its callback
  with 0–3 stored arguments, returning `-ENOENT`-style TEE errors otherwise.
  `plat_register_spi_clk()` (`tee_peridev_init()`, called from
  `tee_core_add()`) registers the platform SPI clock; `tee_peridev_exit()`
  drains and frees the list.
* **Cached SHM.** `tee_map_cached_shm()` returns the linear-map address for
  kernel RAM (`pfn_is_map_memory()`) and otherwise `ioremap_prot()`s with a
  cached/normal-memory attribute; `tee_unmap_cached_shm()` is `iounmap()`.

## 9. Exports and consumers

25 plain `EXPORT_SYMBOL` entries (no `__ksymtab_gpl`), consumed by
`tkcore_drv.ko` (11), `tmem_ffa.ko` (7) and `microarray_fp_tee.ko` (1). All
consumer `__versions` CRCs equal the provider CRCs. Full table, prototype
recovery and the 14/11 natural-vs-blocked split:
`kernel/phase4-tkcore-provider-abi.md`.

## 10. Userspace / platform context (read-only evidence)

* `/vendor/bin/teed` (`u:object_r:tee_exec:s0`) runs from `trustkernel.rc` as
  `--tzdev /dev/tkcoredrv`, prepares `/data/vendor/t6`,
  `/mnt/vendor/persist/t6` and `/mnt/vendor/protect_f/tee`, drives RPMB
  (eMMC/proprietary/SD variants) and pumps `/proc/tkcore/tkcore_log`.
* TrustKernel HALs present: gatekeeper
  (`android.hardware.gatekeeper-service.trustkernel`, TA `tkcore_gatekeeper`),
  KeyMint 3.0 (`…security.keymint@3.0-service.trustkernel`, also serving
  SecureClock/SharedSecret/RemotelyProvisionedComponent), plus
  `libwv_trustkernel.so` for Widevine provisioning and
  `/vendor/bin/tee_check_keybox` driving `vendor.trustkernel.*` properties.
  All of them reach the TEE through the `TEEC_*` API this module exports.
* Fingerprint (`microarray_fp_tee.ko`) uses only the secure-SPI proxy, which is
  why its single provider edge is fully covered by the reconstruction.
