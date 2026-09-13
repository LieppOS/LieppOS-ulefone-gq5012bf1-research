# gz_main_mod — struct / type contract

Classification key:

* **PROVEN_EXACT** — size and offsets are forced by stock evidence (an `_IOC`
  size field baked into the stock binary, or a byte-identical rebuild).
* **PROVEN_SEMANTICS_OFFSETS_ONLY** — layout derived from the pinned source
  and confirmed by byte-identical codegen, but not independently encoded in
  stock metadata.
* **UNKNOWN** — not recoverable; not invented.

A note on why the userspace structs are **PROVEN_EXACT**: the stock
`_gz_ioctl` disassembly contains the literal comparands `0xc010`, `0xc020`,
`0xc008`, `0x4008` and `0x4004`. The `_IOC` size field is bits 16-29, so the
stock binary itself asserts the argument size of every command. Any layout
disagreement would change those constants.

---

## 1. Userspace ioctl structures (`kree/tz_mod.h`)

### `struct kree_session_cmd_param` — 16 bytes — PROVEN_EXACT (`_IOC` size 16)

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 4 | `ret` | `int32_t` | TZ result code, written back by the kernel |
| 4 | 4 | `handle` | `int32_t` | `KREE_SESSION_HANDLE`; out for OPEN, in for CLOSE |
| 8 | 8 | `data` | `uint64_t` | user pointer to the TA name string (OPEN only) |

### `struct kree_tee_service_cmd_param` — 32 bytes — PROVEN_EXACT (`_IOC` size 32)

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 4 | `ret` | `int32_t` | TZ result code |
| 4 | 4 | `handle` | `int32_t` | session handle |
| 8 | 4 | `command` | `uint32_t` | TA command id |
| 12 | 4 | `paramTypes` | `uint32_t` | 4 packed slots, one byte each (`TZ_PARAM_TYPES`) |
| 16 | 8 | `param` | `uint64_t` | user pointer to the GP parameter array |
| 24 | 4 | `cpumask` | `int32_t` | affinity hint passed to `KREE_TeeServiceCallPlus` |
| 28 | 4 | — | padding | trailing pad to 8-byte alignment |

### `struct user_chm_fd_to_hd_param` — 8 bytes — PROVEN_EXACT (`_IOC` size 8)

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 4 | `secm_handle` | `uint32_t` | out: secure chunk-memory handle |
| 4 | 4 | `buf_fd` | `int` | in: dma-buf file descriptor |

### `struct user_adjust_nop_pri` — 4 bytes — PROVEN_EXACT (`_IOC` size 4)

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 4 | `policy` | `uint32_t` | scheduling policy for the Trusty NOP switch |

### `MTEE_CMD_ADJUST_WQ_ATTR` argument — 8 bytes — PROVEN_EXACT (`_IOC` size 8)

Declared as `_IOW('T', 21, char *)`, so the encoded size is that of a pointer.
The handler ignores the encoding and instead `copy_from_user`s a **fixed
32-byte `char str[32]` buffer**, then force-terminates `str[31] = '\0'` and
parses it with `sscanf`. This mismatch between the encoded size and the bytes
actually read is stock behaviour and is reproduced exactly.

### `struct args` (FF-A) — 40 bytes — PROVEN_SEMANTICS_OFFSETS_ONLY

```c
struct args { uint64_t arg[5]; };
```

Copied wholesale by `ff_a_gz_ioctl` when the argument pointer is non-NULL.
The FF-A commands are plain integers with no `_IOC` size field, so there is no
stock-encoded size assertion — hence the weaker classification.

---

## 2. Kernel-internal structures

### `struct session_info` — PROVEN_SEMANTICS_OFFSETS_ONLY

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 4 | `handle_num` | `int` | current capacity (starts at 32, doubles) |
| 4 | 4 | — | padding | |
| 8 | 8 | `handles` | `KREE_SESSION_HANDLE *` | array; empty slots are `0xffffffff` |
| 16 | — | `mux` | `struct mutex` | protects both fields above |

Ownership: allocated in `gz_dev_open`, stored in `file::private_data`, freed in
`gz_dev_release`. Lifetime is exactly the lifetime of one open file
description. The static lockdep key `_init_session_info.__key` is visible as a
stock object, confirming the `mutex_init` site.

### `struct MTIOMMU_PIN_RANGE_T` — PROVEN_SEMANTICS_OFFSETS_ONLY

| offset | size | field | type | semantics |
|---:|---:|---|---|---|
| 0 | 8 | `start` | `void *` | start of the pinned user range |
| 8 | 8 | `pageArray` | `void *` | `struct page **` when `isPage`, else `unsigned long *` pfn array |
| 16 | 4 | `size` | `uint32_t` | byte length |
| 20 | 4 | `nrPages` | `uint32_t` | element count of `pageArray` |
| 24 | 4 | `isPage` | `uint32_t` | selects the `pageArray` interpretation |
| 28 | 4 | — | padding | |

Ownership is split and this is the subtle part: the **struct** is allocated by
`gz_main_mod` (`kvmalloc`) but `pageArray` is allocated and filled by
`gz_tz_system::_map_user_pages`. `gz_main_mod` is responsible for releasing
both — `put_page()` per page when `isPage`, then `kfree(pageArray)`, then
`kvfree(pin)`.

### PA table passed to `KREE_RegisterSharedmem` — PROVEN_EXACT (from source + byte-identical codegen)

A length-prefixed `uint64_t` array of `nrPages + 1` elements:

| index | content |
|---|---|
| 0 | `nrPages` |
| 1 .. nrPages | physical address of each page (`PFN_PHYS(...)`) |

Passed as `shm_param.mapAry`, with `shm_param.buffer = NULL` and
`shm_param.size = 0`. Freed by the caller immediately after registration.

### `struct ffa_mem_record_table` — PROVEN_SEMANTICS_OFFSETS_ONLY

| field | type | semantics |
|---|---|---|
| `handle` | `unsigned long` | FF-A memory handle |
| `origin_mem_region` | `void *` | raw `kmalloc` pointer, used for `kfree` |
| `mem_region` | `void *` | page-aligned pointer actually handed to FF-A |
| `mem_size` | `uint32_t` | region size |
| `meta_data` | `void *` | FF-A descriptor metadata |
| `list` | `struct ffa_mem_list_head` | intrusive circular list node |

`struct ffa_mem_list_head { prev; next; }` is a hand-rolled circular list, not
`struct list_head`. Protected by `ffa_mem_lock` (spinlock).

---

## 3. Deliberately not reconstructed

| item | why |
|---|---|
| `KREE_SHAREDMEM_PARAM` internals beyond the three fields written | only `buffer`, `size`, `mapAry`, `region_id` are set here; the rest belongs to `gz_tz_system` |
| secure-world session id layout | never crosses into Linux |
| TA parameter semantics beyond `TZ_PARAM_TYPES` dispatch | secure-world contract, out of scope |
| historical private member names not present in the pinned source | **not invented** |
