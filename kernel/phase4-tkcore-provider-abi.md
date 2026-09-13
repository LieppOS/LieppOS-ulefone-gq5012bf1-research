# Phase 4 — `tkcore.ko` provider ABI (GQ5012BF1 / MT6878T)

**Status: `NO_PUBLIC_SOURCE_FOUND` / `PROVIDER_ABI_PARTIAL` —
14/25 exports naturally regenerated against the exact GKI,
11/25 classified `PROVIDER_ABI_BLOCKED`.**

Stock oracle: `workspace/phase4-tkcore/oracle/tkcore.ko`
(`sha256 03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`,
221352 bytes, `vermagic 6.1.115-android14-11-g945dff7bc1bf SMP preempt
mod_unload modversions aarch64`, `srcversion 604D4583E310DBFAC768366`,
`TrustKernel TKCore TEEC v1.0`, `version 6:1.1-k6.6`, license `GPL`,
imports namespace `DMA_BUF`, 101 MODVERSION imports, 25 plain
`EXPORT_SYMBOL` exports, no `__ksymtab_gpl`).

Rebuilt artefact:
`workspace/phase4-tkcore/build/tkcore-abi-witness.ko` +
`workspace/phase4-tkcore/build/Module.symvers`, built by
`//lieppos/tkcore-recon:tkcore_recon` in
`/home/armol/kernel-work/gki-12901745-workspace` (exact GKI CI build
`12901745`, `kernel/common 6b18f0b574ab`, Clang `r487747c`).

Verifier: `kernel/scripts/phase4_tkcore_verify.py` → `kernel/phase4-tkcore-verify.txt`
(**36/36 PASS**, fail-closed).

---

## 1. Method — how the CRCs were derived, not copied

No CRC was patched, copied, hand-written into `__versions`, or taken from a
fabricated symvers file. Every CRC below is produced by `genksyms` from plain C
in a real kleaf module build against the exact stock GKI.

Two independent oracles were used to recover the *exact* stock prototypes
before any CRC was accepted:

1. **KCFI type hashes.** The stock module is built with `-fsanitize=kcfi`, so
   every function carries a 32-bit Clang type hash in the word preceding its
   entry point. Candidate prototypes were compiled with the same
   `clang-r487747c` and their prologue hash compared against the stock hash.
   This pins the full function type (return + every parameter) independent of
   genksyms.
2. **genksyms expansion CRC.** `scripts/genksyms` emits the expanded type
   string; its MODVERSION CRC is `crc32(expansion_string)` (standard CRC-32,
   each token followed by a space). Reproducing this offline turned the search
   for struct spellings into a fast, checkable experiment rather than guesswork.
   The final numbers in this document come from the real kleaf build, not from
   the offline model.

Layout evidence came from the stock disassembly: `memset`/`snprintf`/`strncpy`
sizes and instruction offsets gave `sizeof(TEEC_Context) = 0x108`,
`sizeof(TEEC_Operation) = 0x118`, `sizeof(TEEC_SharedMemory) = 0x28`,
`sizeof(struct tee) = 0x138`, `sizeof(struct tee_context) = 0xd0`, and
`tee_wait_queue_private = mutex@0x00 + list_head@0x30`.

## 2. Naturally regenerated exports (14/25)

All 14 match stock on **both** the MODVERSION CRC and the KCFI type id, i.e.
the reconstructed prototype is the stock prototype.

| Export | Stock CRC | Rebuilt CRC | KCFI (stock = rebuilt) | Recovered prototype |
|---|---|---|---|---|
| `tee_map_cached_shm` | `0x6a4e508b` | `0x6a4e508b` | `0x455697f2` | `void *tee_map_cached_shm(unsigned long paddr, size_t size)` |
| `tee_unmap_cached_shm` | `0xd793261b` | `0xd793261b` | `0xa488ebfc` | `void tee_unmap_cached_shm(void *vaddr)` |
| `tee_wait_queue_init` | `0x03c4c343` | `0x03c4c343` | `0x8d9819cd` | `void tee_wait_queue_init(struct tee_wait_queue_private *priv)` |
| `tee_wait_queue_exit` | `0xe773ba45` | `0xe773ba45` | `0x8d9819cd` | `void tee_wait_queue_exit(struct tee_wait_queue_private *priv)` |
| `tee_wait_queue_sleep` | `0xcca24950` | `0xcca24950` | `0x52d2dfc8` | `void tee_wait_queue_sleep(struct device *dev, struct tee_wait_queue_private *priv, u32 key)` |
| `tee_wait_queue_wakeup` | `0xe2de5bad` | `0xe2de5bad` | `0x52d2dfc8` | `void tee_wait_queue_wakeup(struct device *dev, struct tee_wait_queue_private *priv, u32 key)` |
| `tee_clkmgr_handle` | `0x6913f6b2` | `0x6913f6b2` | `0x06da45e1` | `int tee_clkmgr_handle(uint32_t id, uint32_t command)` |
| `tee_clkmgr_register` | `0x7a827d74` | `0x7a827d74` | `0xe70e59df` | `int tee_clkmgr_register(const char *name, int id, void *enable, void *disable, void *arg1, void *arg2, void *arg3, size_t num_args)` |
| `tee_spi_cfg_padsel` | `0x56729869` | `0x56729869` | `0xab53c5c9` | `int tee_spi_cfg_padsel(uint32_t padsel)` |
| `tee_spi_transfer` | `0x184ce7da` | `0x184ce7da` | `0xffeb18b3` | `int tee_spi_transfer(void *conf, uint32_t conf_size, void *txbuf, void *rxbuf, uint32_t len)` |
| `tee_spi_transfer_disable` | `0xadb9b21c` | `0xadb9b21c` | `0x36b1c5a6` | `int tee_spi_transfer_disable(void)` |
| `TEEC_CloseSession` | `0xcb193c37` | `0xcb193c37` | `0x31bed4ef` | `void TEEC_CloseSession(struct TEEC_Session *session)` |
| `TEEC_InvokeCommand` | `0x202b681e` | `0x202b681e` | `0x593c5866` | `TEEC_Result TEEC_InvokeCommand(struct TEEC_Session *, uint32_t commandID, struct TEEC_Operation *, uint32_t *returnOrigin)` |
| `TEEC_ReleaseSharedMemory` | `0xc4d15e1c` | `0xc4d15e1c` | `0x0dc79758` | `void TEEC_ReleaseSharedMemory(struct TEEC_SharedMemory *)` |

Notable exactness findings:

* `tee_spi_transfer`'s stock prototype is **not** the
  `(void *, int, const char *, char *, int)` shape previously assumed by the
  `microarray_fp_tee` witness; KCFI `0xffeb18b3` and CRC `0x184ce7da` are both
  only reproduced by `(void *, uint32_t, void *, void *, uint32_t)`.
  `kernel/phase4-microarray-fp-tee-tkcore-abi-witness.c` and
  `lieppos/tkcore-provider-abi/tkcore-abi.c` still carry the older spelling,
  which reaches the same CRC through a different declaration; the spelling in
  this reconstruction is the KCFI-confirmed one.
* `tee_clkmgr_register` takes 8 parameters: a clock class name (`"spi"`,
  `"i2c"`, `"i2c-dma"` are recognised), an id, an enable/disable callback pair,
  three callback arguments and an argument count (0–3 are dispatched by
  `tee_clkmgr_handle`).
* `tee_wait_queue_private` is exactly the OP-TEE donor shape —
  `struct mutex mu; struct list_head db;` — proven by CRC, which means
  TrustKernel kept the donor's *member names*, not just its layout.
* The GlobalPlatform value types (`TEEC_Session`, `TEEC_SharedMemory`,
  `TEEC_Operation`, `TEEC_Parameter`, `TEEC_UUID`, `TEEC_TempMemoryReference`,
  `TEEC_RegisteredMemoryReference`, `TEEC_Value`) are byte-for-byte and
  name-for-name the OP-TEE `optee_linuxdriver` definitions, with tagged structs
  (`typedef struct TEEC_Session { … } TEEC_Session;`) and prototypes written in
  `struct X *` form — three CRCs (`TEEC_CloseSession`, `TEEC_InvokeCommand`,
  `TEEC_ReleaseSharedMemory`) triangulate that whole type graph.

## 3. `PROVIDER_ABI_BLOCKED` exports (11/25)

| Export | Stock CRC | Blocking type edge |
|---|---|---|
| `TEEC_InitializeContext` | `0x89b94f9a` | `TEEC_Context` → `struct tee_context *` |
| `TEEC_FinalizeContext` | `0x7b3bc43f` | `TEEC_Context` |
| `TEEC_OpenSession` | `0xe821e2a3` | `TEEC_Context` |
| `TEEC_RegisterSharedMemory` | `0xa7bb0a46` | `TEEC_Context` |
| `TEEC_AllocateSharedMemory` | `0x4c2f8738` | `TEEC_Context` |
| `tee_core_alloc` | `0x68aaf1dc` | `const struct tee_ops *` → `struct tee` |
| `tee_core_add` | `0x74f0ee2b` | `struct tee *` |
| `tee_core_del` | `0xf53dbff2` | `struct tee *` |
| `tee_core_free` | `0x9f63c2f9` | `struct tee *` |
| `__tee_get` | `0xa4df7b8a` | `struct tee *` |
| `tee_supp_cmd` | `0x6f7dfbee` | `struct tee *` |

Why this is a hard block, not an unfinished search:

1. `genksyms` expands **pointed-to struct definitions in full**. A CRC over
   `struct tee *` therefore hashes every member *name*, *order* and *type* of
   TrustKernel's private `struct tee` (312 bytes) and, transitively,
   `struct tee_context` (208 bytes) plus TrustKernel's `struct tee_ops`.
2. Member names do not exist in a stripped `.ko`. Layout is recoverable
   (see §4), names are not.
3. The CRC is a hash of the whole expansion: there is no partial feedback, so
   no incremental search can converge. Confirmed empirically — 5.8M + 0.9M
   candidate spellings of `TEEC_Context` alone (tags, field names, array sizes,
   union shapes, scalar typedef chains) produced **zero** hits for
   `TEEC_FinalizeContext 0x7b3bc43f`, which is exactly what a blocked-on-a-
   nested-private-struct CRC looks like.
4. The OP-TEE donor's `struct tee` does not fit: donor prototypes give
   `tee_core_add 0x05670103`, `tee_core_del 0x34a19f52`,
   `tee_core_free 0x7557cfc4`, `__tee_get 0xbe5d9101` — all wrong, because
   TrustKernel reworked `struct tee` (no inline `struct miscdevice`, an added
   misc-device list, extra fields; see §4).

Per the project rule "natural genksyms CRC closure is mandatory, otherwise
classify `PROVIDER_ABI_BLOCKED`", these 11 symbols are **declared blocked**.
The witness module deliberately does not export them, and the verifier fails
closed if it ever does.

## 4. Recovered private layouts (evidence for §3, not usable as names)

`struct tee` — 312 (`0x138`) bytes, allocated by
`tee_core_alloc()` as `devm_kmalloc(dev, priv_len + 0x138, GFP_KERNEL)`:

| Offset | Size | Evidence |
|---|---|---|
| `0x00` | 32 | `klist_node` (donor-compatible prefix) |
| `0x20` | 64 | `char name[64]` — `snprintf(tee+0x20, 64, "%s", name)` |
| `0x60` | 4 | `int id` — 3rd argument stored |
| `0x64`–`0x87` | 36 | unknown TrustKernel additions |
| `0x88` | 8 | `void *priv` = `tee + 0x138` (private area follows the struct) |
| `0x90` | 8 | `const struct tee_ops *ops` (4th argument) |
| `0x98` | 8 | `struct device *dev` (1st argument) |
| `0xa0` | 16 | `list_head` of dynamically allocated misc devices (self-init) |
| `0xb8` | 4 | int, zeroed at alloc |
| `0xd8` | 16 | `list_head` (contexts) self-init |
| `0xe8` | 16 | `list_head` (RPC shm) self-init |
| `0xf8` | 48 | `struct mutex lock` (`__mutex_init(&tee->lock)`) |
| `0x128` | 4 | state (`0` = offline at alloc) |
| `0x12c` | 4 | shm flags, initialised to `0x00040003` |
| `0x130` | 8 | conf/test tail |

`struct tee_context` — 208 (`0xd0`) bytes, `devm_kmalloc(dev, 0xd0, …)`:
`struct tee *` @`0x00`, `char name[128]` @`0x08`, `tgid` @`0x88`,
`usr_client` @`0x8c`, `list_head entry` @`0x90`, `list_head list_sess` @`0xa0`,
`list_head list_shm` @`0xb0`, `kref refcount` @`0xc0` (init 1), and one extra
TrustKernel pointer @`0xc8` (`NULL`-ed by `TEEC_InitializeContext`, set by
`tee_ctx_open`/`tee_supp_open`, consumed by `tee_internal_ioctl` and
`_release_tee_cmd`).

`TEEC_Context` — 264 (`0x108`) bytes: `char devname[256]` @`0x00` (written by
`strncpy(context, name, 256)`) and a 8-byte union at `0x100` whose `int` arm is
the TEE context handle allocated by `tee_core_alloc_uuid()` and resolved by
`tee_core_uuid2ptr()`. The pointer arm is what drags `struct tee_context` into
the CRC.

## 5. Stock consumer edges

| Consumer | tkcore edges | Natural | Blocked |
|---|---|---|---|
| `tkcore_drv.ko` | 11 | 6 (`tee_map_cached_shm`, `tee_clkmgr_handle`, `tee_wait_queue_{init,exit,sleep,wakeup}`) | 5 (`__tee_get`, `tee_core_alloc`, `tee_core_add`, `tee_core_del`, `tee_supp_cmd`) |
| `tmem_ffa.ko` | 7 | 3 (`TEEC_CloseSession`, `TEEC_InvokeCommand`, `TEEC_ReleaseSharedMemory`) | 4 (`TEEC_InitializeContext`, `TEEC_FinalizeContext`, `TEEC_OpenSession`, `TEEC_RegisterSharedMemory`) |
| `microarray_fp_tee.ko` | 1 | 1 (`tee_spi_transfer`) | 0 |

Every consumer `__versions` CRC equals the stock provider CRC (verified), so
the stock link graph is fully characterised. But because 9 of the 19 distinct
consumed symbols are blocked, **a from-source tkcore replacement cannot
currently satisfy `tkcore_drv` or `tmem_ffa`**; `microarray_fp_tee`'s single
edge is fully covered.

## 6. Consequences

* `tkcore` stays a **stock vendor binary** on this device. It is not
  reconstructed, and this document does not claim source purity for it.
* The rebuilt `tkcore-abi-witness.ko` is a **build-only ABI witness**. It fails
  every call closed, must never be installed in `modules.load`, loaded, or
  shipped as a TEE provider, and exists only so downstream consumer builds can
  link against naturally derived CRCs instead of fabricated ones.
* Unblocking requires the original TrustKernel headers
  (`drivers/tee/tkcore/core/*.h` under a `kernel_device_modules-6.1` tree) —
  not more binary analysis.
