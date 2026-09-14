# GQ5012BF1 tkcore island Phase 3F — common header authority

## Rule

The final source-island authority is `lieppos/trustkernel/include/trustkernel/`. The Phase-3E provider already compiles against it. Phase-3F consumer targets may use build-only source/header overlays, but retain every frozen function body byte-for-byte. They must not carry a second private type definition for a category-B edge.

| API | Return | Parameters | Private tags expanded by genksyms | Authoritative header | Provider include | Phase-3F consumer include |
|---|---|---|---|---|---|---|
| `tee_core_alloc` | `struct tee *` | `struct device *, char *, int, const struct tee_ops *, size_t` | `struct tee`, `struct tee_ops`, `struct tee_session`, `struct tee_cmd`, `struct tee_shm` | `trustkernel/tee_core.h` | `tee_core_priv.h` → authority | tkcore_drv overlay `tkcore_abi.h` → authority |
| `tee_core_add` | `int` | `struct tee *` | `struct tee` and transitive private graph | `trustkernel/tee_core.h` | `tee_core_priv.h` → authority | tkcore_drv overlay → authority |
| `tee_core_del` | `int` | `struct tee *` | `struct tee` and transitive private graph | `trustkernel/tee_core.h` | `tee_core_priv.h` → authority | tkcore_drv overlay → authority |
| `__tee_get` | `int` | `struct tee *` | `struct tee` and transitive private graph | `trustkernel/tee_core.h` | `tee_core_priv.h` → authority | tkcore_drv overlay → authority |
| `tee_supp_cmd` | `int` | `struct tee *, uint32_t, void *, size_t` | `struct tee` | `trustkernel/tee_supp.h` | `tee_supp_com.c` → authority | tkcore_drv overlay → authority |
| `tee_map_cached_shm` | `void *` | `unsigned long, size_t` | none | `trustkernel/tee_shm.h` | `tee_shm.c` → authority | tkcore_drv overlay → authority |
| `tee_clkmgr_handle` | `int` | `uint32_t, uint32_t` | none | `trustkernel/tee_clkmgr.h` | `tee_core.c` → authority | tkcore_drv overlay → authority |
| `tee_wait_queue_init` | `void` | `struct tee_wait_queue_private *` | `struct tee_wait_queue_private` | `trustkernel/tee_wait_queue.h` | `tee_wait_queue.c` → authority | tkcore_drv overlay → authority |
| `tee_wait_queue_exit` | `void` | `struct tee_wait_queue_private *` | `struct tee_wait_queue_private` | `trustkernel/tee_wait_queue.h` | `tee_wait_queue.c` → authority | tkcore_drv overlay → authority |
| `tee_wait_queue_sleep` | `void` | `struct device *, struct tee_wait_queue_private *, u32` | `struct tee_wait_queue_private`; visible `struct device` graph is include-context-sensitive | `trustkernel/tee_wait_queue.h` | `tee_wait_queue.c` → authority | tkcore_drv overlay → authority |
| `tee_wait_queue_wakeup` | `void` | `struct device *, struct tee_wait_queue_private *, u32` | same as sleep | `trustkernel/tee_wait_queue.h` | `tee_wait_queue.c` → authority | tkcore_drv overlay → authority |
| `TEEC_InitializeContext` | `TEEC_Result` | `const char *, TEEC_Context *` | `TEEC_Context` → `struct tee_context` | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_RegisterSharedMemory` | `TEEC_Result` | `TEEC_Context *, TEEC_SharedMemory *` | context and shared-memory private members | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_OpenSession` | `TEEC_Result` | `TEEC_Context *, TEEC_Session *, const TEEC_UUID *, uint32_t, const void *, TEEC_Operation *, uint32_t *` | context/session/operation/shared-memory graph | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_InvokeCommand` | `TEEC_Result` | `TEEC_Session *, uint32_t, TEEC_Operation *, uint32_t *` | session/operation/shared-memory graph | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_CloseSession` | `void` | `TEEC_Session *` | `TEEC_Session` → `struct tee_session` | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_ReleaseSharedMemory` | `void` | `TEEC_SharedMemory *` | shared-memory private members | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `TEEC_FinalizeContext` | `void` | `TEEC_Context *` | `TEEC_Context` → `struct tee_context` | `trustkernel/tee_client_api.h` | `tee_kernel_api.c` → authority | tmem Phase-3F common-first include path |
| `tee_spi_transfer` | `int` | `void *, uint32_t, void *, void *, uint32_t` | none | `trustkernel/tee_spi.h` | `tee_spi.c` → authority | MicroArray declaration-only overlay → authority |

## Authority mechanics

- **tkcore_drv:** its frozen `tkcore_abi.h` has independently proven layouts but synthetic member spellings and a local enum return for `tee_supp_cmd`. The Phase-3F overlay replaces that duplicate definition file with a compatibility wrapper over the common headers; compatibility member-name macros preserve unchanged function bodies and code generation.
- **tmem_ffa:** its pinned donor header remains frozen. The Phase-3F Makefile places the common TrustKernel directory before `inc/teec`, so the sole `#include "tee_client_api.h"` resolves to the authority. No C body changes.
- **microarray_fp_tee:** the frozen source's local declaration uses ABI-equivalent C spellings (`int` versus `uint32_t`, typed character pointers versus `void *`). The Phase-3F declaration-only overlay replaces that declaration with `#include <trustkernel/tee_spi.h>`; all 27 function bodies remain unchanged.

The resulting CRCs must come only from the frozen provider's naturally generated `Module.symvers`. Header equality is necessary but is not treated as proof by itself: Phase 3F also compares every generated consumer function body, call relocation, KCFI datum, object, and string against its frozen accepted baseline.
