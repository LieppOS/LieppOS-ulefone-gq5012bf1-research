# TrustKernel common header contract (ABI island)

Header root:

```
/home/armol/kernel-work/gki-12901745-workspace/lieppos/trustkernel/include/trustkernel/
    tee_client_api.h    GlobalPlatform client types + all 8 TEEC prototypes
    tee_core.h          struct tee, tee_context, tee_session, tee_shm,
                        tee_cmd, tee_data, tee_ops
    tee_wait_queue.h    tee_wait_queue_private + 4 exported entry points
    tee_shm.h           tee_map_cached_shm / tee_unmap_cached_shm + helpers
    tee_supp.h          supplicant/RPC structures + tee_supp_cmd
    tee_clkmgr.h        tee_clkmgr_handle / tee_clkmgr_register
    tee_spi.h           tee_spi_cfg_padsel / transfer / transfer_disable
    layout-assert.h     machine-checked layout assertions
```

Bazel filegroup: `//lieppos/trustkernel:trustkernel_headers`.

Every source-built island module consumes **this one header set**, which is
what makes the island's genksyms CRCs mutually consistent without any CRC
injection, witness record or ELF patching.

## 1. Layout assertions are machine-checked, not asserted in prose

`layout-assert.h` encodes every recovered stock anchor as a `static_assert`.
It is compiled by the analysis-only target
`//lieppos/trustkernel-layout:tk_layout_probe` against the real exact-GKI
headers, so a wrong offset breaks the build.

**Status: the probe builds successfully — all assertions below hold.**

| type | assertion | class |
|---|---|---|
| `TEEC_Context` | `sizeof == 0x108` | PROVEN_EXACT |
| `TEEC_Session` | `sizeof == 8` | PROVEN_EXACT |
| `TEEC_SharedMemory` | `sizeof == 0x28`, `size@8`, `flags@0x10` | PROVEN_EXACT |
| `TEEC_Operation` | `sizeof == 0x118`, `paramTypes@4`, `params@8` | PROVEN_EXACT |
| `TEEC_UUID` | `sizeof == 16` | PROVEN_EXACT |
| `struct tee` | `sizeof == 0x138` + 12 offset anchors | PROVEN_EXACT anchors |
| `struct tee_context` | `sizeof == 0xd0` + 7 offset anchors | PROVEN_EXACT anchors |
| `struct tee_wait_queue_private` | `sizeof == 0x40`, `db@0x30` | PROVEN_EXACT |

## 2. Measured kernel type sizes (exact GKI ab/12901745)

These were **measured**, not assumed, by emitting them as symbol sizes from a
probe module compiled with the real toolchain:

| kernel type | size |
|---|---:|
| `struct mutex` | **48 (0x30)** |
| `struct klist_node` | 32 |
| `struct completion` | 32 |
| `struct list_head` | 16 |
| `struct sg_table` | 16 |
| `struct kref` | 4 |
| `atomic_t` | 4 |

This measurement produced an important corroboration. `struct mutex` on this
kernel is 0x30, not the 0x20 one would assume from a generic arm64
configuration. That makes `struct tee_wait_queue_private` fit its proven
0x40 size as exactly `mutex@0x00 + list_head@0x30` **with no padding at all**,
and it makes `struct tee`'s proven `lock@0xf8` land exactly on the proven
`state@0x128`. Two independent proven anchors are explained by one measured
fact, which is strong evidence the recovered layout is correct.

## 3. Classification of every definition

### PROVEN_EXACT — name and layout both certain

* All GlobalPlatform constants (`TEEC_PARAM_TYPES`, `TEEC_MEMREF_*`,
  `TEEC_MEM_*`, `TEEC_LOGIN_*`, `TEEC_ORIGIN_*`, `TEEC_ERROR_*`).
* `TEEC_UUID`, `TEEC_Value`, `TEEC_TempMemoryReference`,
  `TEEC_RegisteredMemoryReference`, `TEEC_Parameter` layouts.
* All 8 `TEEC_*` prototypes — proven twice over, by `tmem_ffa`'s call sites
  and by `gz_tz_system`'s five weak GlobalPlatform fallback stubs.
* `tee_wait_queue_private` layout and all 4 wait-queue prototypes.
* `tee_map_cached_shm` / `tee_unmap_cached_shm` prototypes.
* `tee_clkmgr_handle` / `tee_clkmgr_register` prototypes.
* `tee_spi_cfg_padsel` / `tee_spi_transfer` / `tee_spi_transfer_disable`
  prototypes — `tee_spi_transfer` additionally matches stock KCFI
  `0xffeb18b3` and stock CRC `0x184ce7da`.
* Struct **tags** `tee`, `tee_context`, `tee_session`, `tee_cmd`, `tee_shm`
  (recovered from `tkcore_drv`).

### PROVEN_EXACT_LAYOUT / SYNTHETIC_ISLAND_NAME — offset certain, spelling invented

Every member of `struct tee` and `struct tee_context` sitting on a proven
anchor. The offsets are proven; the spellings are not recoverable and are
chosen once here:

`struct tee`: `node@0x00`, `name@0x20`, `id@0x60`, `priv@0x88`, `ops@0x90`,
`dev@0x98`, `list_misc@0xa0`, `list_ctx@0xd8`, `list_rpc_shm@0xe8`,
`lock@0xf8`, `state@0x128`, `shm_flags@0x12c`.

`struct tee_context`: `tee@0x00`, `name@0x08`, `tgid@0x88`, `usr_client@0x8c`,
`entry@0x90`, `list_sess@0xa0`, `list_shm@0xb0`, `refcount@0xc0`,
`ctx_priv@0xc8`.

Note `list_misc@0xa0`: TrustKernel replaced the OP-TEE donor's **inline
`struct miscdevice`** with a **list of misc devices**, which is why one
`struct tee` can back `/dev/tkcore_admin`, `/dev/tkcore_client` and
`/dev/tkcore_fp`. This is a real structural divergence from the donor and is
recorded as such.

### SYNTHETIC_ISLAND_NAME — gap fillers

Members placed between proven anchors so the anchors land correctly. Their
presence and role are inferred from stock call sites (statistics, refcount,
rpc channel, debugfs, log state); their spellings and exact ordering within a
gap are **not** proven:

`struct tee`: `max_refcount@0x64`, `refcount@0x68`, `stats[3]@0x6c`,
`pad_stats@0x84`, `rpc@0xb0`, `dbg_dir@0xb8`, `log_state@0xc0`,
`plat_priv@0xc8`, `reserved0@0xd0`, `conf@0x130`, `test@0x134`.

`struct tee_context`: `pad_refcount@0xc4`.

`struct tee_rpc` in `tee_supp.h` is entirely PROVEN_SEMANTICS: the read/write
pairing, single-in-flight handshake and completion model are proven from the
stock supplicant functions, but no member spelling is recoverable.

### UNKNOWN — deliberately not invented

The historical TrustKernel spellings of every synthetic name above. They are
not guessed, and no claim of historical source identity is made anywhere.

## 4. The deliberate CRC consequence

Because member spellings feed genksyms, the 11 historically
`PROVIDER_ABI_BLOCKED` exports will receive island CRCs that differ from the
historical Ulefone CRCs. This is accepted by design and is the entire reason
the island strategy exists. It is recorded in
`kernel/phase4-tkcore-historical-vs-island-crc.md`, and a differing island CRC
is **never** described as a stock ABI match.

The 14 historically natural exports are unaffected: none of their prototypes
reference a private struct, so this header set keeps reproducing their
historical CRCs exactly.
