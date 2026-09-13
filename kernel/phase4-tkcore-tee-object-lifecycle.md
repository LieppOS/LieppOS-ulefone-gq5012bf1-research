# GQ5012BF1 Phase-3A `struct tee` lifecycle map

Stock object size is **0x138 (312)**. This map records only fields visible to the Phase-3A core lifecycle plus direct-callee evidence needed to disambiguate them. Names marked `island spelling` are not claims about TrustKernel's private source spelling.

| Offset | Width | Meaning | Initial writer/value | Phase-3A readers/writers | Protection/lifetime |
|---:|---:|---|---|---|---|
| `0x000` | 0x20 | `klist_node` region | zeroed allocation | not used by five target bodies | device lifetime |
| `0x020` | 0x40 | name | `snprintf(...,64,"optee%s%02d",name,id)` | logging; device/provider lookup paths | immutable after alloc |
| `0x060` | 4 | provider id | `tee_core_alloc`: argument `id` | registration log | immutable |
| `0x064..0x087` | 0x24 | out-of-scope platform/log configuration | zeroed, then provider-private users may set | `tee_init_procfs` reads `0x70`, `0x78`, `0x80` | Phase 3F; do not assign speculative member names |
| `0x088` | 8 | provider-private tail | `tee + 0x138` | `tee_init_procfs` non-null guard and backend consumers | provider object lifetime |
| `0x090` | 8 | `const struct tee_ops *` | allocation argument | `__tee_get` owner and start; all backend dispatch | immutable |
| `0x098` | 8 | parent `struct device *` | allocation argument | managed allocation/free, misc parent, module/device references | immutable |
| `0x0a0` | 0x10 | misc-record list head | self-linked by `tee_core_alloc` | `tee_core_add` append/unwind; `tee_core_del` drain | registration/removal serialized by provider lifecycle |
| `0x0b0` | 8 | supplicant/RPC state pointer (island `rpc`) | `tee_supp_init` stores allocated 0x1d8-byte object | `tee_supp_deinit` and RPC functions | RPC-internal mutexes; object lifetime |
| `0x0b8` | 4 | atomic provider refcount | 0 by `tee_core_alloc` | `__tee_get`, `tee_get`, `tee_put` | atomic acquire/release operations |
| `0x0bc` | 4 | maximum observed refcount | zeroed allocation | `tee_get` compare/update | diagnostic; no lock visible in stock `tee_get` |
| `0x0c0` | 0x18 | three `{count,max}` statistic entries | zeroed allocation | context/session/shm stats helpers | helper-specific locking/atomicity |
| `0x0d8` | 0x10 | context list | self-linked by `tee_core_alloc` | context create/release | `tee->lock@0xf8` in context helpers |
| `0x0e8` | 0x10 | RPC-shm list | self-linked by `tee_core_alloc` | not otherwise in Phase 3A | RPC subsystem deferred |
| `0x0f8` | 0x30 | `struct mutex lock` | `__mutex_init` by alloc | context/session/list helpers | protects TEE-owned collections |
| `0x128` | 4 | state | 0 by combined 64-bit store | backend lifecycle | backend/provider lifecycle |
| `0x12c` | 4 | shm flags/capabilities | `0x00040003` by same 64-bit store | shared-memory subsystem deferred | immutable/capability state |
| `0x130..0x137` | 8 | fields not read by five target bodies | zeroed allocation | none in direct five-function stock bodies | do not rename without evidence |

## Corrected anchors discovered in Phase 3A

The Phase-2 island header placed synthetic statistics/refcount members in the earlier `0x064` gap. Stock disassembly proves that placement is wrong:

- `refcount @0xb8`: independent accesses in `__tee_get`, `tee_get`, `tee_put`, and zero store in `tee_core_alloc`.
- `max_refcount @0xbc`: load/store in `tee_get`.
- `stats[3] @0xc0`: direct context/session/shm stats call sites; 3 × 8 bytes ends exactly at `list_ctx@0xd8`.
- supplicant/RPC pointer `@0xb0`: `tee_supp_init` stores its allocation there.

These corrections were compiler-checked successfully in an exploratory layout probe, but were **not retained in the workspace source** after Phase 3A was blocked. The authoritative build tree was restored to the frozen Phase-2 source to avoid leaving a half-migrated common ABI graph.

## Misc-device record

Stock `tee_core_add` proves a separate 0x68-byte record:

| Offset | Width | Meaning |
|---:|---:|---|
| `0x00` | 0x50 | embedded Linux `struct miscdevice` |
| `0x50` | 8 | pointer to its 0x28-byte static descriptor |
| `0x58` | 0x10 | list node linked into `tee+0xa0` |

There is no `struct tee *` in the record. Stock `tee_ctx_open` reaches the owner through `record->miscdev.parent->driver_data`, validates the inode minor, creates the context, stores `usr_client=1@context+0x8c`, stores the descriptor pointer at `context+0xc8`, and replaces `file->private_data` with the context.

## Lifetime

1. `tee_core_alloc`: validate backend, allocate/zero 0x138+private bytes, initialize fixed fields/lists/lock, allocate RPC state.
2. `tee_core_add`: register three misc records, then procfs, sysfs and peripheral clocks.
3. `__tee_get`: establish the initial provider/module/device/backend-start reference.
4. Context/session lifetimes take and drop additional references through their helpers.
5. `tee_core_del`: peripheral → sysfs → misc records → RPC → managed TEE object.
6. `tee_core_free`: pre-registration failure path only; RPC → managed TEE object.

No runtime execution was performed.
