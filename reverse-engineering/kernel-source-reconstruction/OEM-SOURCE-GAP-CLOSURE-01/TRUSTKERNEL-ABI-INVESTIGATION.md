# TrustKernel ABI investigation (tkcore.ko C, tmem_ffa.ko C)

## Result

- **The private-declaration blocker is closed.** In stock TrustKernel 6:1.1-k6.6, `struct tee_shm` **has no
  `uint16_t shm_name` member**: the *named shared memory* feature was added later, in 7:2.2.
  - Removing that one member from the public 7:2.2 header reproduces all **25/25** stock `tkcore.ko` export CRCs
    naturally, together with H1 (the authentic, unprefixed GP `TEEC_*` names). The four `TEEC_*` CRCs imported by
    `tmem_ffa` are among them.
  - The member's absence is proven independently by stock machine code, so the result rests on more than CRC
    agreement.
- **tmem_ffa → A (proposed).** It is rebuilt with a source-built provider witness carrying this delta. Fresh
  B1/B2 builds pass strict GNU20-only whole-file acceptance; see `BATCH-PARITY.tsv` and `MERGE-INSTRUCTIONS.md`.
- **tkcore.ko stays C.** Its declarations and exports are now exact, but 19/122 function bodies differ. The 6:1.1
  implementation (platform CPU affinity, procfs logger, shm allocator) is not in any public release.

## Prior state (not repeated here)

- ALL-C-TO-A-CLOSURE tested:
  - ZTE 3.2p3: layout rejected;
  - Vivo 3.2p8: old struct blocks;
  - the UMIDIGI scopes: no hits;
  - 7:2.2 anvil-kernel `8e1a0f39478f`: 9/9 layout anchors, 11/25 CRCs;
  - H1: 14/25;
  - an H1×H2×H3 grid: 14/25.
- It localized all 11 remaining misses to the `struct tee` type closure, and its stated next step was "anvil-kernel
  history before 8e1a0f39478f".

## New evidence this session

| # | Evidence | Result |
|---|---|---|
| 1 | anvil-kernel gitiles log (read-only): `drivers/tee/tkcore` on master | Single import commit `8e1a0f39478f` (2026-01-29); **no earlier history**. The stated next step is closed |
| 2 | anvil-kernel branch `4.19`, commit `492dbcf3e728` ("mtk: modified in-tree drivers", 2026-07-06) | **New authentic release: TrustKernel `4.0p0.4.19p0`** (53 files, GPL-2.0 headers). Blob IDs and SHA256 are in `evidence/trustkernel/anvil-4.0p0/`. It has not been examined before |
| 3 | 4.0p0 vs 7:2.2, declaration diff of the closure | 4.0p0 predates stock: `struct tee` has `miscdev` where stock and 7:2.2 have `udevs`. Stock therefore lies between 4.0p0 and 7:2.2. Differences in the closure are listed below |
| 4 | Genksyms symtypes closure (`scripts/tk-genksyms.py`; control 11/25 and H1 14/25 reproduced first) | All 11 misses share one closure. Every type reached by a matching export is excluded. Candidates: `tee`, `tee_context`, `tee_cmd`, `tee_ops`, `tee_shm`, `tee_shm_static`, `tee_device_config`, `tee_rpc*`, `tee_task_cpu_affinity*` |
| 5 | Stock layout (read-only `llvm-readelf`/`llvm-objdump`; sizes from compile-only probes of both releases) | See the layout table below |
| 6 | 7:2.2 natural build vs stock, 16-bit accesses at `tee_shm+0x3c` (the `shm_name` offset) | 7:2.2 has them in `tee_shm_alloc_from_rpc` and `tee_shm_fd_for_rpc`; **stock has none** in any of its 806 functions |
| 7 | Stock `tee_shm_alloc_from_rpc` | 3 arguments `(tee, size, extra_flags)`, `orr w2, extra, #0x6000000`; its caller zeroes a 0x18-byte `tee_rpc_alloc`. This is the authentic 4.0p0 form, with no name argument and no `named_shm` |
| 8 | Genksyms variants on H1 (one declaration each, all authentic text) | S1 (4.0p0 union `resv`/`ns`): 14/25. S3 (`struct tee_shm_resv resv`): 14/25. **S2 (7:2.2 minus `uint16_t shm_name`): 25/25** |
| 9 | Compiled provider (build1: S2 plus the consistent removal of named-shm code, using authentic 4.0p0 text for `tee_shm_alloc_from_rpc` and the `tee_rpc_alloc` case; `tkcore_notify_logger` removed because absent in stock) | `Module.symvers` = the 25 stock exports, all CRCs exact. Whole-module parity 103/122 functions (`evidence/trustkernel/tkcore-build1-parity.txt`) |
| 10 | `tmem_ffa` in a fork of the secure_transport recipe with the S2 witness (`android_kernel_modules_trustkernel_abi` @ `15e7e8d8`) | provider-boundary errors `[]`; 9/9 strict PASS; fresh B1 = B2; 124 + 124 mutations; `tmem_ffa` 141/141 |

### Layout evidence (item 5)

| Field | Stock | 7:2.2 | 4.0p0 | Verdict |
|---|---|---|---|---|
| `sizeof(tee_ops)` | 88 B (`tee_tz_fops` in `tkcore_drv.ko`) | 88 | 104 (`call_tee`, `raw_call_tee`) | 4.0p0 form rejected |
| `sizeof(tee_cmd)` | `_init_tee_cmd` zeroes exactly 0x100 with 16 inline `stp xzr` | 0x100 | 0xe8 (no login fields) | 4.0p0/3.2p3 form rejected (confirms the earlier H2 rejection) |
| `tee_device_config` | stock `tee_device_configs` = 120 B | 3 × 0x28 | — | consistent with 7:2.2 |
| `tee_task_cpu_affinity_operations` | stock objects = 24 B | 0x18 | — | consistent with 7:2.2 |
| `sizeof(tee_shm)` | — | 0x68 | 0x68 | the same either way, so this field must be tested by code and CRC (items 6–8) |

## The exact declaration (provider side)

```c
struct tee_shm {                 /* include/linux/tee_tkcore.h, 6:1.1 as evidenced */
	struct list_head entry;
	struct tee_context *ctx;
	struct tee *tee;
	struct device *dev;
	size_t size_req;
	size_t size_alloc;
	uint32_t flags;
	/* 7:2.2 adds: uint16_t shm_name;  -- absent in stock 6:1.1 */
	struct tee_shm_static static_shm;
};
```

Exported signatures, which are unchanged and include `struct tee_shm` through the recursive expansion:

- `TEEC_InitializeContext(const char *, struct TEEC_Context *)`
- `TEEC_FinalizeContext(struct TEEC_Context *)`
- `TEEC_RegisterSharedMemory(struct TEEC_Context *, struct TEEC_SharedMemory *)`
- `TEEC_OpenSession(struct TEEC_Context *, struct TEEC_Session *, const struct TEEC_UUID *, uint32_t, const void *, struct TEEC_Operation *, uint32_t *)`
- `__tee_get`, `tee_core_{alloc,add,del,free}`, `tee_supp_cmd`

The recursive chain is `TEEC_Context` → `tee_context` → `tee` → `tee_rpc` / `list_rpc_shm` users → `tee_shm`.

### Classification of this delta

- It is a **reconstruction proven by stock evidence**, not verbatim TrustKernel 6:1.1 text.
- Every other byte comes from the authentic public release.
- The deleted member is proven absent by stock code (items 6–7), and the result is confirmed by 11 independent
  32-bit CRCs that the unmodified header misses.
- No CRC value, symvers line or stock byte is used as a build input.

## What remains for tkcore.ko (C)

Of the 122 functions, 19 differ:

- **Platform CPU affinity:** `plat_cpu_is_big`, `plat_tee_init`.
- **Procfs logger:** `logd`, `tee_init_procfs`, `tee_exit_procfs`, `tee_version_read`, `teed_version_read`,
  `teed_version_write`.
- **Shm allocator:** `tkcore_alloc_shm` (408 B in stock vs 104 B), `tkcore_shm_free`, `tee_shm_alloc_io`,
  `tee_shm_free_io`, `tee_shm_fd_for_rpc`, `tee_shm_free_from_rpc`, `tee_shm_alloc_from_rpc`.
- **Other:** `tee_internal_ioctl`, `tee_supp_write`, `tee_context_get`, `tee_core_alloc`.
- **Imports:** 7:2.2 adds user-page pinning (`mmap_lock` tracepoints, `down_read`/`up_read`,
  `sg_alloc_table_from_pages_segment`), which stock lacks.
- **Data:** `large_cluster_id` exists only in stock.

These are 6:1.1 implementation differences, not declarations. Writing them from disassembly would certify
reconstruction of stock bytes, so it was not done; see `TRUSTKERNEL-SOURCE-REQUEST.md`.

## Effect on other rows (handoff only; nothing of theirs modified)

- **`tkcore_drv.ko` and `microarray_fp_tee.ko`:** both are Codex G-SOURCE-RECOVERY-BATCH-02. Their provider CRC
  errors (`__tee_get`, `tee_core_add/alloc/del`, `tee_supp_cmd`) are exactly the closure fixed here; see
  `HANDOFF-TO-CODEX.md`.
- **The armtz side (`tkcore_drv`):** the 7:2.2 `tee_tz_drv.c` also uses `named_shm`. That is Codex's to evaluate.
