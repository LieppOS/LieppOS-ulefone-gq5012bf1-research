# gz_main_mod — FF-A contract

## 1. Imported ffa_v10 symbols — exactly one

The stock ELF was scanned exhaustively against the 5-symbol `ffa_v10` export
table. Only one edge exists; the earlier note that gz_main_mod imports "at
least `ffa_driver_register`" is now closed as **exactly one**.

| symbol | stock CRC | source-built ffa_v10 CRC | call sites | status |
|---|---|---|---:|---|
| `ffa_driver_register` | `0x0d53cde9` | `0x0d53cde9` | 1 | NATURAL_OK |

`ffa_driver_unregister` is **not** imported. The module registers an FF-A
driver at `init` and never unregisters it — `gz_main_exit` only calls
`platform_driver_unregister`. This is an asymmetry in the vendor source, not
an analysis gap, and it is reproduced exactly by the source build.

Provider: the REAL source-built `//lieppos/ffa-v10:ffa_v10`
(`DIRECT_SOURCE_MATCH / FROZEN FOR RE`). No witness.

## 2. Registration object

```c
static const struct ffa_device_id gz_ffa_device_id[] = {
        /* Echo server UUID  SP UUID - BE Format */
        { UUID_INIT(0x11001100, 0x1100, 0x3322,
                    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77) },
        { }
};

struct ffa_driver gz_ffa_driver = {
        .name      = "gz_ffa_dev",
        .probe     = gz_ffa_driver_probe,
        .id_table  = gz_ffa_device_id,
};
```

Both `gz_ffa_device_id` and `gz_ffa_driver` are present as stock objects.

| property | value |
|---|---|
| partition UUID matched | `11001100-1100-3322-0011-223344556677` (big-endian form, as commented "Echo server UUID / SP UUID") |
| id table entries | 1 real + 1 terminator |
| `.remove` | **not provided** |
| driver name | `gz_ffa_dev` |

## 3. Registration call

```c
get_ffa_drv = gz_get_ffa_dev();              /* returns &gz_ffa_driver */
if (!get_ffa_drv)
        KREE_ERR("get_ffa_drv is null\n");
ret = ffa_driver_register(get_ffa_drv, THIS_MODULE, KBUILD_MODNAME);
if (ret)
        KREE_ERR("%s gz_ffa_dev driver register fail, ret=%d\n", __func__, ret);
return 0;
```

Two behaviours worth recording, both reproduced byte-exactly:

* `gz_get_ffa_dev()` returns the address of a static object, so the NULL check
  can never fire; it is dead but compiled (12-byte function, one relocation).
* **FF-A registration failure is non-fatal**: `gz_main_init` logs and still
  returns 0. A device without the matching secure partition still gets a
  working `/dev/gz_kree`; only the FF-A surface is inert.

## 4. Probe lifecycle — `gz_ffa_driver_probe`

1. Logs the partition `vm_id`.
2. Caches `g_ffa_dev = ffa_dev` and `g_ffa_ops = ffa_dev->ops`; if `ops` is
   `IS_ERR_OR_NULL`, returns `-1`.
3. **Creates the character device on first probe only**, guarded by the global
   `device_driver_initalized`. This is why `/dev/gz_ffa_dev` exists only when a
   matching FF-A partition is present.
4. Initialises the memory-record list as an empty circular list
   (`ffa_drv_manager->next = ffa_drv_manager->prev = ffa_drv_manager`).
5. `spin_lock_init(&ffa_mem_lock)`.
6. Sets `ffa_enabled = true` — the value returned by the
   `GZ_FFA_IS_ENABLED` (200) ioctl.

There is no `.remove` callback, so none of this is torn down.

## 5. Memory and message operations

All performed through `g_ffa_ops` function pointers obtained from the FF-A
device, not through exported symbols:

| operation | ioctl | notes |
|---|---|---|
| memory share/lend | `GZ_FF_A_MEMORY_SEND` (250) → `gz_ffa_memory_share` → `memory_send` | builds a constituent buffer (`CONSTITUENT_BUFFER` = 4 KB), uses `sg_alloc_table_from_pages_segment`/`sg_next`, records the handle in the `ffa_mem_record_table` list |
| reclaim | `GZ_FF_A_MEM_RECLAIM` (251) | frees the record and the region |
| partition info | `GZ_FF_A_PARTITION_INFO_GET` (252) | returns the partition id |
| direct request | `GZ_FF_A_MESSAGE_SEND` (253) → `ffa_send_to_ha` | retries on a "DIR_REQ: Busy" response |
| dma-buf → chunk handle | `GZ_FF_A_GET_CHM_HANDLE` (254) | `dma_buf_get` → `dmabuf_to_secure_handle` → `dma_buf_put` |

MediaTek-specific flag, defined locally:

```c
#define FFA_MEMORY_REGION_FLAG_MTK_RETRIEVE  (1 << 31)
```

documented in-source as: for `FFA_MEM_LEND`, perform the memory retrieve at
the same time.

Partition-id helpers:

```c
#define IS_LOGICAL_SP_ID(x)  (((x) >> 14) & 0x11)
#define IS_PHYSICAL_SP_ID(x) (((x) >> 15) & 0x1)
#define VM_NUMBER_MAX 10
```

## 6. Safety

No FF-A call was issued, no partition was contacted, no memory was shared.
Everything above is read from the compiled stock module and the pinned source.
