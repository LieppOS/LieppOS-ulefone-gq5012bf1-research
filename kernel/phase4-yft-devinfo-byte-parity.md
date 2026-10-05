# Phase 4 — `yft_devinfo.ko`: byte-level parity pass

Earlier work proved the reconstruction *builds* and reproduces the ABI
(40/40 import CRCs, 17/27 export CRCs). This pass measured it at the level
the other DONE kernel components are held to — per-function byte identity
against the stock object — and closed most of the gap.

| metric | before | after |
|---|---|---|
| functions byte-identical | 34 / 72 | **54 / 72** |
| functions size-equal | 37 / 72 | 57 / 72 |
| KCFI type ids equal | 59 / 72 | **61 / 72** |
| relocations equal (per function) | 39 / 72 | 57 / 72 |
| import CRCs | 40 / 40 | 40 / 40 |
| export CRCs | 17 / 27 | 17 / 27 |
| data objects byte-equal | 40 / 42 | 40 / 42 |
| modinfo fields | 6 / 6 | 6 / 6 |

Harness: `workspace/phase4-yft-devinfo/scripts/yft-build-parity.sh` (ignored workspace)
(isolated `M=` build against exact Google GKI 12901745 + `llvm-strip` +
`ko-parity-tsv.py`). Full output in
`workspace/phase4-yft-devinfo/yft-devinfo-{parity-SUMMARY.txt,function-parity.tsv}`.

---

## Corrections found and applied

### 1. `find_device_type_info()` must not survive as a NULL-returning helper

The stock `*_set_used`, `*_info_print` and `*_device_add` functions all search
`yft_devices->list` inline and branch straight out of the loop. The
reconstruction called a `static inline` helper that returns `NULL`, which left
clang with a phi it could not fold, emitting one redundant `cbz x21` per
function (+4 bytes each):

```c
/* reconstructed (wrong shape) */           /* stock shape */
pdevice = find_device_type_info(TYPE);      list_for_each_entry(pdevice, &yft_devices->list, list) {
if (pdevice == NULL)                                if (pdevice->type != TYPE)
        return -1;                                          continue;
                                                    goto found;
                                            }
                                            return -1;
                                    found:
```

Fixed 17 functions (9 × `set_used`, 7 × `info_print`, and the `cbz` in all
10 × `device_add`).

### 2. Two functions return `void`, not `int`

`yft_add_display_info` and `yft_display_info_dump` — proven by KCFI type id
and by the absence of a `w0` write before `ret`. See
[`phase4-yft-devinfo-kcfi-typeid.md`](phase4-yft-devinfo-kcfi-typeid.md).

### 3. `init_device_type_info()` takes `used` separately, and always stores both callbacks

Stock emits two nested `cbz` (`used`, then `name`) and stores the
`info_print`/`set_used` pair unconditionally on both paths — not the
`used ? name : NULL` argument (which compiles to `csel`) and not an
`if/else` that stores either `used_name` or the callbacks:

```c
static inline struct yft_device_type_info *init_device_type_info(int type,
                char *used_name, int used,
                int (*info_print)(struct seq_file *m),
                int (*set_used)(char *name, int used))
{
        ...
        pdevice->type = type;
        if (used_name && used)
                pdevice->used_name = used_name;
        pdevice->info_print = info_print;
        pdevice->set_used = set_used;
        mutex_init(&pdevice->info_mutex);
        list_add(&pdevice->list, &yft_devices->list);
}
```

### 4. The allocation is zeroed only from `info_print` onwards

Stock zeroes `0x20..0x6f` (five `stp xzr, xzr`) and then initialises the two
`list_head`s with *unpaired* stores — the signature of `INIT_LIST_HEAD()`'s
`WRITE_ONCE()`. A whole-struct `memset()` followed by `INIT_LIST_HEAD()` does
not reproduce this: the volatile stores block dead-store elimination of the
first `0x20` bytes, while plain assignments reproduce the elimination but get
paired into `stp`. Only zeroing the tail reproduces both properties.

Struct layout confirmed by this (`sizeof` = `0x70`):

| offset | field |
|---|---|
| `0x00` | `struct list_head list` |
| `0x10` | `struct list_head info_list` |
| `0x20` | `int (*info_print)(struct seq_file *)` |
| `0x28` | `int (*set_used)(char *, int)` |
| `0x30` | `int type` |
| `0x38` | `char *used_name` |
| `0x40` | `struct mutex info_mutex` (`0x30` bytes) |

## What is still not byte-identical (18 functions)

| function | stock | recon | note |
|---|---|---|---|
| `yft_camera_device_add` | 664 | 620 | blocked: unknown enum tag + residual `init_device_type_info` shape |
| `yft_touchpanel_device_add` | 664 | 632 | same |
| `yft_fuelgauge_device_add` | 664 | 632 | same |
| `yft_spitouchpanel_device_add` | 664 | 632 | same |
| `yft_tinylcd_device_add` | 664 | 632 | same |
| `yft_touchpanel_spi_device_add` | 660 | 628 | same |
| `yft_{acc,m,alsps,sar,baro}sensor_device_add` | 684 | 660 | same (5 functions) |
| `yft_devices_probe` | 576 | 740 | probe-time DT/sysfs sequence not yet reduced |
| `init_yft_class_sysfs` | 216 | 164 | stock registers more attributes than recovered |
| `c_cts_show` | 32 | 64 | stock is a thin tail-call wrapper |
| `yft_get_lcm_for_lk` | 340 | 332 | bootargs parse detail |
| `mt_ufs_lifetime_show`, `proc_yftinfo_init`, `yft_device_dump` | = | = | size-equal, immediate/ordering only |

The ten `*_device_add` functions cannot become byte-identical while the enum
tag is unknown: their KCFI prologue constant is derived from it.

<!-- component: YFT-DEVINFO -->
