# `tkcore_drv.ko` — authoritative reconstruction report

> **Provenance update (2026-09-13, ffa_v10 closure):** `ffa_v10.ko` has since
> been source-closed (`DIRECT_SOURCE_MATCH`, all 5 export CRCs natural — see
> `kernel/phase4-ffa-v10-reconstruction.md`). `tkcore_drv`'s stock-ABI target
> was rebuilt against the real `//lieppos/ffa-v10` `Module.symvers` in place
> of the two `ffa_driver_*` stock witnesses. **The rebuilt `.ko` is
> byte-identical to the pre-closure build** — no behavior was reopened, only
> ABI provenance improved. Every count below that says "6 NATURAL / 7
> STOCK_PROVIDER_WITNESS" is superseded by **8 NATURAL / 5
> STOCK_PROVIDER_WITNESS**: `ffa_driver_register` and `ffa_driver_unregister`
> moved from `STOCK_PROVIDER_WITNESS` to `NATURAL_FFA` (a source-built
> provider, not a stock witness). The verifier now runs 43/43 (was 37/37).
> The remaining 5 witnesses are unchanged: `tee_core_alloc/add/del`,
> `__tee_get`, `tee_supp_cmd` — all blocked on TrustKernel's private
> `struct tee` member names. `tkcore` itself is untouched.

**Device:** Ulefone Armor 29 Pro Thermal, GQ5012BF1, MediaTek MT6878/MT6878T
**Baseline:** Linux 6.1.115-android14-11, Android CI `ab/12901745`, common commit
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
**Exact-GKI workspace:** `/home/armol/kernel-work/gki-12901745-workspace`
**Verifier:** `kernel/scripts/phase4_tkcore_drv_verify.py` — **37 checks, 0 failures**

---

# Final classification

**`SOURCE_RECONSTRUCTED` / `SOURCE_NOW_WITH_PROVIDER_WITNESSES` / `PROVIDER_ABI_PARTIAL`**

Every Linux-visible behaviour of the module is reconstructed as real, readable,
buildable C against the exact GKI tree. The reconstruction is not a byte-clone
and contains no patched CRCs, no copied `__versions`, and no fabricated symvers.

7 of its 13 provider ABI edges are `STOCK_PROVIDER_WITNESS` (read read-only out
of the stock providers' own `__kcrctab`/`__kcrctab_gpl`), which is permitted by
project rule because **`tkcore_drv` exports zero symbols** — it can never
launder an unproven ABI onward to another consumer.

# FROZEN status

**FROZEN FOR RE: YES**

Measured against the frozen standard:

| criterion | status |
|---|---|
| complete stock function set accounted | ✅ 50/50 by name, 0 extra, 0 missing |
| exact Linux-visible backend behaviour | ✅ all transports, ops, RPC, log, DT |
| exact 54 kernel ABI | ⚠️ **53/54** — `alt_cb_patch_nops` declared codegen residual |
| exact 13 provider ABI in stock-compatible target | ✅ 13/13, zero CRC mismatches |
| exact tkcore call semantics | ✅ 11/11 edges, prototypes KCFI-confirmed where address-taken |
| exact ffa_v10 call semantics | ✅ 2/2 edges, `sync_send_receive()` direct request |
| exact backend ops | ✅ 9/9 `tee_ops` slots, all 9 KCFI type ids match stock |
| exact thread model | ✅ per-CPU kthreads, naming, affinity, hotplug, queue |
| exact shared-memory contract | ✅ reserved-mem + fallback pool, chunk list, refcounts |
| exact SMC/FF-A request construction | ✅ all ids and argument slots |
| exact IRQ/log/version behaviour | ✅ DT IRQ, 128 KiB ring, `tkcoreos-rev` handshake |
| exact lifecycle | ✅ including both stock quirks (`return 1`, inverted unregister) |
| build clean | ✅ 0 compiler warnings, 0 modpost warnings in stock-ABI target |
| no Linux-visible unexplained residual | ✅ the two residuals are both explained and bounded |
| verifier | ✅ **PASS_WITH_DECLARED_PROVIDER_WITNESSES** |

Secure-world internals remain opaque by design and are not required.

# Stock oracle

| | |
|---|---|
| file | `workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko` |
| sha256 | `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` |
| size | 63480 B |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| srcversion | `0A6E96ED7F723D4F0883C3D` |
| depends | `tkcore,ffa_v10` |
| license / author | `GPL` / TrustKernel |
| build path | `../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tee_tz_drv.c` |
| placement | `vendor_boot` platform ramdisk, load slot **P:100** (recovery **R:98**) |

Providers, also frozen:

| module | sha256 | size |
|---|---|---|
| `tkcore.ko` | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| `ffa_v10.ko` | `2f8341d3f920418f3d9f4b8f64299acf97e591ad232a6bbbf6298b63231eebde` | 38688 |

# Source provenance

| | |
|---|---|
| donor search | **`NO_PUBLIC_SOURCE_FOUND`** — no TrustKernel `tee_tz_drv.c` for this generation exists publicly; upstream OP-TEE `armtz` is a distant ancestor only (it has no FF-A transport, no per-CPU dispatcher, no affinity policy tables, no `build_mem_share_handle`) |
| reconstruction basis | 100 % instruction-level evidence from the stock ELF: 717 relocations, `.text` disassembly, `.rodata` function-pointer tables, string table, `__versions`, and Clang kCFI type ids |
| copied code | none |
| copied ABI metadata | only the 7 declared `STOCK_PROVIDER_WITNESS` CRCs, extracted read-only and reproducibly |

# RED

No **RED** (empty-source / no-useful-source) condition applies to the driver
itself: the Linux-visible contract is fully recovered.

The RED-equivalent boundary lives one level down and is **not** part of this
module: the secure OS behind the SMC/FF-A interface is a signed binary whose
implementation is neither available nor required.

# Function inventory

50 defined functions in stock; the reconstruction defines exactly the same 50
(verifier check 7).

```
init_module cleanup_module
tkcore_ffa_probe tkcore_ffa_remove tkcore_smc_probe tkcore_smc_remove
tee_tz_new
invoke_tee_ffa invoke_tee_smc build_mem_share_handle_ffa build_mem_share_handle_smc
tz_start tz_stop tz_open tz_close tz_invoke tz_cancel tz_alloc tz_free tz_shm_inc_ref
set_params call_tee
tee_init_task tee_exit_task run_tee_task tkcore_smc_task do_smc
tee_cpu_online tee_cpu_prepare_down
default_affinity_need_bind_cpu default_affinity_match_cpu default_affinity_get_candidate_cpu
tee_bind_cpu_request_need_bind_cpu tee_bind_cpu_request_match_cpu
tee_bind_cpu_request_get_candidate_cpu
tee_shm_pool_create tee_shm_pool_destroy tee_shm_pool_reset tee_shm_pool_dump
tee_shm_pool_is_cached tee_shm_pool_set_cached tee_shm_pool_p2v tee_shm_pool_v2p
tee_shm_pool_incref tkcore_shm_pool_alloc tkcore_shm_pool_free
handle_db_destroy handle_get handle_put handle_lookup
```

Full per-symbol table: `kernel/phase4-tkcore-drv-functions.tsv`.

# Kernel ABI

**54 kernel imports**, of which the reconstruction reproduces **53** with
identical CRCs and imports nothing extra.

Import-set parity drove four evidence-backed corrections, each visible in the
stock ELF:

| stock evidence | consequence |
|---|---|
| imports `_printk`, not `_dev_err`/`_dev_info`/`_dev_warn` | all logging is `pr_*` |
| imports `devm_kmalloc`/`devm_kfree`; `__kmalloc` only for the non-constant `kmalloc_array()` | pool and chunks are `devm_kzalloc()` |
| imports `_raw_spin_lock`/`_raw_spin_unlock`, no irqsave variants | pool lock is plain `spin_lock()` |
| imports `usleep_range_state` | CPU-bind retry sleeps, does not spin |
| out-of-line `memset` at `.text 0x3690` inside `handle_get` | handle DB grows by doubling, not by a fixed step |

Full table: `kernel/phase4-tkcore-drv-imports.tsv`,
`kernel/phase4-tkcore-drv-modversions.tsv`.

# Provider ABI

**13 provider imports, 0 exports.** In the stock-compatible target all 13 CRCs
equal stock exactly; in the natural-evidence target 6 resolve and 7 are
declared gaps.

# tkcore provider edges

All **11** tkcore edges, with provenance:

| # | symbol | CRC | provenance |
|---|---|---|---|
| 1 | `tee_map_cached_shm` | `0x6a4e508b` | **NATURAL** |
| 2 | `tee_clkmgr_handle` | `0x6913f6b2` | **NATURAL** |
| 3 | `tee_wait_queue_init` | `0x03c4c343` | **NATURAL** |
| 4 | `tee_wait_queue_exit` | `0xe773ba45` | **NATURAL** |
| 5 | `tee_wait_queue_sleep` | `0xcca24950` | **NATURAL** |
| 6 | `tee_wait_queue_wakeup` | `0xe2de5bad` | **NATURAL** |
| 7 | `tee_core_alloc` | `0x68aaf1dc` | `STOCK_PROVIDER_WITNESS` |
| 8 | `tee_core_add` | `0x74f0ee2b` | `STOCK_PROVIDER_WITNESS` |
| 9 | `tee_core_del` | `0xf53dbff2` | `STOCK_PROVIDER_WITNESS` |
| 10 | `__tee_get` | `0xa4df7b8a` | `STOCK_PROVIDER_WITNESS` |
| 11 | `tee_supp_cmd` | `0x6f7dfbee` | `STOCK_PROVIDER_WITNESS` |

Edges 7–11 all take `struct tee *` / `struct tee_context *` / `struct tee_ops *`,
whose genksyms expansion hashes TrustKernel's private member *names*. Those
names exist in no shipped binary and no public source
(`kernel/phase4-tkcore-provider-abi.md`). They are **not** brute-forced here and
tkcore is **not** reopened.

**tkcore natural vs witnessed split: 6 NATURAL / 5 STOCK_PROVIDER_WITNESS.**

# ffa_v10 provider edges

Both **2** edges:

| # | symbol | CRC | provenance |
|---|---|---|---|
| 1 | `ffa_driver_register` | `0x0d53cde9` | `STOCK_PROVIDER_WITNESS` (GPL-only export) |
| 2 | `ffa_driver_unregister` | `0x3c660e4c` | `STOCK_PROVIDER_WITNESS` (GPL-only export) |

GKI 12901745 does not build the vendor FF-A stack that publishes these, so
exact-GKI cannot regenerate them. `ffa_v10` itself was **not** analysed beyond
reading these two published CRCs, and is **not** claimed reconstructed.

**ffa natural vs witnessed split: 0 NATURAL / 2 STOCK_PROVIDER_WITNESS.**

# ABI provenance split

| class | count | meaning |
|---|---|---|
| `NATURAL` | **6** | regenerated from C by exact-GKI genksyms in `//lieppos/tkcore-recon`; regenerated CRC equals stock CRC |
| `STOCK_PROVIDER_WITNESS` | **7** | obtainable only by reading the stock provider ELF's own `__kcrctab`/`__kcrctab_gpl`; never described as natural |
| `PROVIDER_ABI_GAP` | **7** | the same 7 edges, unresolved in the natural-evidence target, where modpost reports them undefined on purpose |

Witness extraction is read-only and reproducible:

```
tools/phase4-extract-stock-provider-symvers.py \
  --elf .../tkcore.ko   --sym tee_core_alloc ... \
  --elf .../ffa_v10.ko  --sym ffa_driver_register ... \
  --out stock-provider.symvers --manifest stock-provider.provenance.json
```

(The tool gained `__kcrctab_gpl` support in this task.) Verifier check 2
re-extracts every record and fails if any line does not byte-match the stock
ELF, so a hand-edited or invented CRC cannot survive.

Artefacts: `kernel/phase4-tkcore-drv-stock-provider.symvers`,
`kernel/phase4-tkcore-drv-stock-provider.provenance.json`.

# Backend registration

`tee_tz_new(dev, id, invoke_tee, build_mem_share_handle, &tee)` is the single
entry both transports use:

1. `tee_core_alloc(dev, "tkcore", id, &tee_fops, sizeof(struct tee_tz))` —
   `devm_kmalloc(dev, priv_len + 0x138)`, name copied with
   `snprintf(tee + 0x20, 64, "%s", name)`, `priv` at `+0x88`, `ops` at `+0x90`,
   `dev` at `+0x98`.
2. transport function pointers stored into the private area
   (`invoke_tee` `+0x40`, `build_mem_share_handle` `+0x48`).
3. `invoke_tee(0xf2000001)` — secure OS revision handshake.
4. `tee_wait_queue_init(&ptee->wait_queue)`.
5. secure log ring setup (below).
6. `tee_core_add(tee)` publishes the char devices owned by tkcore.

Teardown (`tee_tz_destroy`, inlined into both `*_remove` in stock) is the exact
inverse: `tee_core_del()`, `tee_wait_queue_exit()`, free log pages.

# tee_ops

All 9 slots, in stock `.rodata+0x80 … +0xc0` order. Every one of the 9 Clang
kCFI type ids matches stock exactly, which proves the prototypes — including
the struct *tag names* — are spelled as TrustKernel spelled them:

| slot | .rodata | function | prototype | kCFI |
|---|---|---|---|---|
| `.start` | +0x80 | `tz_start` | `int (struct tee *)` | `0xa1200a70` |
| `.stop` | +0x88 | `tz_stop` | `int (struct tee *)` | `0xa1200a70` |
| `.open` | +0x90 | `tz_open` | `int (struct tee_session *, struct tee_cmd *)` | `0x48c6e9cf` |
| `.close` | +0x98 | `tz_close` | `int (struct tee_session *)` | `0x5ffcff8b` |
| `.invoke` | +0xa0 | `tz_invoke` | `int (struct tee_session *, struct tee_cmd *)` | `0x48c6e9cf` |
| `.cancel` | +0xa8 | `tz_cancel` | `int (struct tee_session *, struct tee_cmd *)` | `0x48c6e9cf` |
| `.alloc` | +0xb0 | `tz_alloc` | `struct tee_shm *(struct tee *, size_t, u32)` | `0x45b20ce9` |
| `.free` | +0xb8 | `tz_free` | `void (struct tee_shm *)` | `0xa7e6969f` |
| `.shm_inc_ref` | +0xc0 | `tz_shm_inc_ref` | `int (struct tee_shm *)` | `0x4c262249` |

`.rodata+0x70` is `__this_module` (the `owner` slot) and `+0x78` is the
`"tkcore"` name string, so the stock `struct tee_ops` begins
`{ owner, name, start, stop, open, close, invoke, cancel, alloc, free,
shm_inc_ref }`.

# Transport architecture

Two drivers registered unconditionally; whichever bus the platform provides
wins. They differ **only** in the `invoke_tee`/`build_mem_share_handle` pair
stored at private `+0x40`/`+0x48`; every other code path is shared.

```
        tkcore.ko (char devs, contexts, sessions, supplicant)
                        |  struct tee_ops
        +---------------+----------------+
        |  tkcore_drv.ko backend (this)  |
        +----+----------------------+----+
             | invoke_tee_ffa       | invoke_tee_smc
       ffa_v10.ko                arm_smccc_smc()
   sync_send_receive()          (no bus provider)
```

# Thread model

* `tee_init_task()` creates **one kthread per possible CPU**,
  `kthread_create_on_node(tkcore_smc_task, ..., cpu_to_node(cpu), "tkcore_smc_task.%u", cpu)`,
  then `kthread_bind(task, cpu)` and `wake_up_process()`; `NR_CPUS` is capped
  at **32** (the idle mask is a `u32`).
* Thread body `tkcore_smc_task` is `int (void *)` — kCFI `0x89fb613d`, matching
  stock.
* Every secure call is serialised by a single global `mutex` (`ctl->g_lock`);
  `waiters`/`wait_done` implement the busy (`ret == 1`) back-off.
* `run_tee_task()` consults the affinity policy: if no CPU binding is needed the
  call runs inline on the caller; otherwise the request is queued
  (`list_head` + `spinlock_t q_lock` + `struct completion`) to the thread bound
  to the requested CPU, with a ~2 ms (`usleep_range_state`) retry window before
  giving up.
* Two policy tables (`struct tee_affinity_ops`, three slots each):
  `default_affinity_operations` (`.rodata+0xc8`: never bind) and
  `tee_bind_cpu_request_operations` (`.rodata+0x290`: bind to the CPU the secure
  world named). All six callbacks take `void *arg` — proven by kCFI
  (`0x98d3ad02` / `0x7850c00b` / `0x89fb613d`, all matching stock).
* CPU hotplug: `tee_cpu_online` / `tee_cpu_prepare_down` via
  `__cpuhp_setup_state`, so a bound call never targets a departing CPU.
* Calls longer than **1,000,000 µs** emit
  `WARNING SMC[0x%x] %sDURATION %lld us`.

# Shared memory

* Preferred: DT reserved region `trustkernel,shared_mem`, looked up with
  `of_find_compatible_node()` + `of_reserved_mem_lookup()`; on failure the stock
  string `tkcore_drv: cannot lookup reserved memory` is printed and the driver
  falls back to `__get_free_pages(order 10)` = **4 MiB**.
* The window is handed to the secure world with fast call `0xf2005704`
  (`REGISTER_SHM`), then wrapped in a pool by `tee_shm_pool_create()`.
* Pool: ordered first-fit chunk list with per-chunk refcounts,
  `tkcore_shm_pool_alloc(dev, pool, size, align)` /
  `tkcore_shm_pool_free()`, `tee_shm_pool_p2v()` / `v2p()` for translation,
  `tee_shm_pool_incref()`, `tee_shm_pool_reset()`, and a debug dumper
  `tee_shm_pool_dump()` printing `| [0x%p] 0x%p 0x%p 0x%p %08zu %d`.
* Cacheability is tracked (`tee_shm_pool_is_cached` / `set_cached`) and cached
  windows are mapped through tkcore's `tee_map_cached_shm()`.
* Diagnostics preserved verbatim: `< %s() WARNING, paddr=0x%p already released`,
  `%s() FAILED, pAddr=%p is not a valid @`, `Free lost chunkH=0x%p`.
* Supplicant-allocated buffers are tracked by the handle DB
  (`handle_get`/`handle_put`/`handle_lookup`/`handle_db_destroy`), whose growth
  policy — start at 4 slots, then double, `krealloc` + `memset` of the new tail —
  is read literally from `handle_get()` at `.text 0x35fc`.

# FF-A contract

* `struct ffa_device_id` UUID **`8bf0ccc3-42a3-5271-860d-66580469479c`**.
* `ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE, KBUILD_MODNAME)`;
  `.name`, `.probe`, `.remove`, `.id_table`.
* One `ffa_dev->ops->msg_ops->sync_send_receive(ffa_dev, &data)` per secure
  call; the `struct ffa_send_direct_data` args carry the same
  `(func_id, a1, a2, a3)` payload the SMC path puts in `x0..x3`.
* `ffa_dev` is recovered from the `struct tee`'s `dev` by
  `container_of(dev, struct ffa_device, dev)`.
* Probe logs `tkcore_drv: ffa: initialized driver`.
* `-DCONFIG_ARM_FFA_TRANSPORT_MODULE=1` is mandatory at build time: otherwise
  GKI's `arm_ffa.h` substitutes its `!IS_REACHABLE()` stubs and the module
  silently stops importing the two FF-A symbols. This is how MediaTek's own
  out-of-tree build sees the header, since `ffa_v10` is a module.

# SMC contract

* `platform_driver` on DT `compatible = "trustkernel,tzdrv"`, driver name
  `tzdrv`, `MODULE_DEVICE_TABLE(of, ...)`.
* `arm_smccc_smc(a0, a1, a2, a3, 0, 0, 0, 0, &res)` with the results read back
  into the `smc_param` block.
* `do_smc()` absorbs preemption: while the return is an RPC code
  (`(a0 & 0xffff0000) == 0xffff0000`) it re-enters with
  `(first_a0 & 0x80000000) | 0x72000003`, preserving the caller's 32/64-bit
  calling convention.

# Exact SMC/FFA IDs

| id | meaning | evidence |
|---|---|---|
| `0xf2000001` | get secure-OS revision | `tee_tz_new()` `mov w1,#1; movk w1,#0xf200,lsl#16` |
| `0xf2005704` | register shared-memory window | `tz_start()` |
| `0xf2005705` | set up secure log ring | `tee_tz_new()` |
| `0x72000003` | return from RPC (32/64-bit bit preserved) | `do_smc()` `(a0 & 0x80000000) \| 0x72000003` |
| `0xffff0004` | preempted by foreign interrupt | `do_smc()` resume loop |
| `0xffff5702` | secure world requests a specific CPU | `run_tee_task()` |
| ret `1` | busy — park on the global completion | `run_tee_task()` |
| ret `6` | rebind to the requested CPU, then resume | `run_tee_task()` |

Prefixes: `0xf2000000` fast call, `0x72000000` standard call, `0x80000000`
selects the 64-bit convention.

# RPC/supplicant

RPC selector = low 16 bits of the returned `a0`:

| selector | action |
|---|---|
| `0` | allocate from the shared pool |
| `1` | free the argument block |
| `2` | free a buffer |
| `3` | foreign IRQ — just resume |
| `5` | execute an RPC command |
| `0x5700` / `0x5701` | supplicant allocate / free (handle DB) |

RPC command ids inside the message block: `0x20000001` / `0x20000002`
wait-queue sleep / wakeup (dispatched to tkcore's
`tee_wait_queue_sleep()`/`_wakeup()`), `0x80000001` clock manager
(`tee_clkmgr_handle()`), `0x1000000a` supplicant invoke (`tee_supp_cmd()`).
Supplicant ids: `0x1001` allocate, `0x1002` free, `0x1003` invoke.
The RPC argument block is a `0x88`-byte, 8-aligned allocation from the pool.

# Logging path

* IRQ number from DT node `trustkernel,tkcore` via `irq_of_parse_and_map(np, 0)`.
* Ring buffer `__get_free_pages(GFP_KERNEL | __GFP_ZERO, order 5)` = **128 KiB**.
* Registered with `build_mem_share_handle()` then fast call `0xf2005705`;
  failure paths print `tkcore_drv: alloc log buffer failed` and
  `tkcore_drv: setup tee log buffer failed with 0x%x` and are non-fatal.
* Buffer, size and IRQ are stored back into the `struct tee` so tkcore's own
  `tee_log_irq` handler and `logd` kthread can drain it into
  `/proc/tkcore/tkcore_log`. **The consumer side of the log lives in `tkcore`,
  not here** — this module only provides the ring.

# Device tree

| node / property | use |
|---|---|
| `compatible = "trustkernel,tzdrv"` | platform (SMC) transport match |
| `compatible = "trustkernel,tkcore"` | source of the secure-log IRQ (`interrupts`, index 0) |
| `compatible = "trustkernel,shared_mem"` | reserved-memory phandle for the shared window |

No other DT property is read. The FF-A transport needs no DT node — it matches
on the partition UUID.

# Reserved memory

One region: `trustkernel,shared_mem`, resolved with `of_reserved_mem_lookup()`,
used verbatim as the non-secure half of the shared window and registered with
`0xf2005704`. If the node or the lookup fails the driver logs and falls back to
a 4 MiB `__get_free_pages(order 10)` allocation, so a device without the node
still works. The 128 KiB log ring is always page-allocator memory, never
reserved memory.

# Private state

`struct tee_tz` — 0xa0 B, `devm`-allocated as tkcore's `priv` tail:

```
0x00 bool   started
0x08 struct tee *tee
0x10 unsigned long shm_paddr
0x18 void *shm_vaddr
0x20 bool   shm_cached
0x28 struct shm_pool *shm_pool
0x30 / 0x38 reserved (zeroed by tee_tz_new)
0x40 int (*invoke_tee)(ptee, func_id, a1, a2, a3, struct smc_param *)
0x48 int (*build_mem_share_handle)(ptee, vaddr, size, flags, &handle, &out_flags)
0x50 struct tee_wait_queue_private wait_queue   /* { mutex mu; list_head db; } */
0x90 struct handle_db handle_db                 /* { void **ptrs; u32 max_ptrs; } */
```

Consumed tkcore layouts (names are ours, offsets are stock):
`struct tee` 0x138 B (`name[64]` @0x20, `priv` @0x88, `ops` @0x90, `dev` @0x98,
`conf` bit 0 @0x130), `struct tee_shm` 0x68 B, plus `tee_session` / `tee_cmd` /
`tee_context`. The *type tag names* of `tee`, `tee_session`, `tee_cmd` and
`tee_shm` are not guesses — they are proven by kCFI type-id equality on the nine
`tee_ops` callbacks.

# Locking

| lock | scope |
|---|---|
| `struct mutex g_lock` | serialises every secure-world entry; the whole driver is single-threaded with respect to the TEE |
| `spinlock_t q_lock` (plain `spin_lock`, no irqsave — proven by the import set) | the CPU-bound request queue and the idle mask |
| `struct completion wait_done` | busy (`ret == 1`) back-off |
| per-request `struct completion done` | hand-off to the bound CPU thread |
| `cpus_read_lock()` | held across CPU selection so hotplug cannot race the binding |
| tkcore's `tee_wait_queue_private.mu` | secure-world wait-queue objects (owned by the provider) |
| pool `spin_lock` | shared-memory chunk list |

# IRQs

The module registers **no interrupt handler of its own**. It reads exactly one
IRQ number (`trustkernel,tkcore`, index 0) and hands it to tkcore, which owns
`tee_log_irq`. Foreign interrupts that preempt a secure call arrive as RPC
return `0xffff0004` and are handled purely by resuming the call — no handler,
no threaded IRQ, no tasklet.

# Probe/init

```
init_module
 └ pr_info("TrustKernel TEE Driver initialization")
 ├ ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE, KBUILD_MODNAME) -> ffa_abi_rc
 ├ __platform_driver_register(&tkcore_smc_driver, THIS_MODULE)          -> smc_abi_rc
 └ return (ffa_abi_rc && smc_abi_rc) ? 1 : 0

tkcore_ffa_probe(ffa_dev)            tkcore_smc_probe(pdev)
 └ tee_tz_new(&ffa_dev->dev,          └ tee_tz_new(&pdev->dev, pdev->id,
        ffa_dev->id, invoke_tee_ffa,        invoke_tee_smc,
        build_mem_share_handle_ffa)         build_mem_share_handle_smc)
 ├ dev_set_drvdata()                  └ platform_set_drvdata()
 └ pr_info("ffa: initialized driver")
```

`tz_start()` (first real use) registers the shared window, and
`tee_init_task()` brings up the per-CPU threads.

**Status: exact.** Both probe/remove pairs carry stock-matching kCFI type ids
(`0xd353e493`, `0xa30d19cc`, `0x63df1691`, `0x63df1691`).

# Lifecycle

Two stock quirks are **preserved deliberately, not "fixed"**, and both are
documented in the source:

1. `init_module()` returns **`1`** — not a negative errno — when *both*
   registrations fail.
2. `cleanup_module()` guards each unregister with the **failed** (non-zero)
   registration return code, so a driver that registered successfully is never
   unregistered. The stock module is never unloaded on this device (no
   dependents; it is the last entry in the ramdisk load list), so the asymmetry
   is unobservable.

`cleanup_module` is one of the 17 byte-identical functions, which is itself
evidence the quirk is reproduced exactly.

# Secure OS version

`tee_tz_new()` issues fast call `0xf2000001` and formats the reply as
`tkcore_drv: tkcoreos-rev: %d.%d.%d-gp`. The version is passed up to tkcore,
which publishes it at `/proc/tkcore/os_version`; `teed_version` and
`drv_version` are tkcore's own. A failed handshake aborts `tee_tz_new()` with
`tkcore_drv: Unexpected error %d`.

# Userspace/init

The module exposes **no** device node, sysfs attribute, procfs entry, ioctl or
uevent of its own. All userspace surface (`/dev/tkcore_admin`,
`/dev/tkcore_client`, `/dev/tkcore_fp`, `/proc/tkcore/*`, 8 sysfs attrs,
9 ioctls with compat converters) belongs to `tkcore.ko`.

Init/ramdisk requirements are therefore unchanged: keep the stock load order

```
P:97 ffa_v10   P:98 teeperf   P:99 tkcore   P:100 tkcore_drv
R:95 ffa_v10   R:96 teeperf   R:97 tkcore   R:98 tkcore_drv
```

# Security boundary

* This module is **non-secure world only**. It marshals requests and shared
  memory; it implements no policy, no crypto and no attestation.
* The trust boundary is the SMC/FF-A call itself. Everything the secure OS does
  with `0xf2xxxxxx` calls is out of scope and stays opaque.
* Secure-SPI/TA routing (`966d3f7c-04ef-1beb-08b7-57f37a6d87f9`) and fingerprint
  paths are `tkcore`'s, not this module's.
* No new attack surface is introduced relative to stock: identical import set,
  identical call ids, zero exports.

# Exact-GKI build

| target | provider record | modpost | purpose |
|---|---|---|---|
| `//lieppos/tkcore-drv-recon` | `tkcore-recon/Module.symvers` (natural only) | warns on the 7 gaps (`KBUILD_MODPOST_WARN=1`, by design) | natural evidence; not loadable |
| `//lieppos/tkcore-drv-recon-stockabi` | `stock-provider.symvers` (13 stock edges) | **fail-closed, clean** | stock-compatible, loadable |

```
tools/bazel build //lieppos/tkcore-drv-recon:tkcore_drv_recon
tools/bazel build //lieppos/tkcore-drv-recon-stockabi:tkcore_drv_recon_stockabi
```

One source of truth: the `-stockabi` package contains only symlinks to the
8 real files (verifier check 9). Sources are archived at
`kernel/phase4-tkcore-drv-recon/`.

# Function parity

| metric | value |
|---|---|
| stock functions | 50 |
| rebuilt functions | 50 |
| name-set identical | **yes** (0 missing, 0 extra) |
| size-identical | **24 / 50** |
| byte-identical | **17 / 50** |
| total function bytes | stock 14168 → rebuilt 10656 (75.2 %) |

Byte-identical set (17): `build_mem_share_handle_ffa`,
`build_mem_share_handle_smc`, `cleanup_module`, the three
`default_affinity_*`, `handle_db_destroy`, `handle_lookup`, `handle_put`,
`init_module`, `invoke_tee_ffa`, `invoke_tee_smc`,
`tee_bind_cpu_request_match_cpu`, `tee_bind_cpu_request_need_bind_cpu`,
`tee_cpu_online`, `tee_shm_pool_is_cached`, `tee_shm_pool_set_cached`.

The rebuilt module is *smaller* than stock, concentrated in `call_tee`
(−1300 B), `tz_open` (−832 B) and `tz_invoke` (−404 B). That is an inlining and
error-string-duplication difference, not a behavioural one: the import set,
the call-id set and the control flow all match. No stock function is missing
and none is oversized in a way that implies extra work.

# Object parity

| section | stock | note |
|---|---|---|
| `.text` | 0x3734 B | rebuilt smaller (see above) |
| `.init.text` | 0x84 B | `init_module` byte-identical |
| `.exit.text` | 0x58 B | `cleanup_module` byte-identical |
| `.rodata` | 0x2a8 B | both `tee_ops` and both affinity tables reproduced, same slot order |
| `.rodata.str1.1` | 0x839 B | every stock format string reproduced |
| `.bss` | 0xac B | |
| `__bug_table` | 0x204 B | |
| `.altinstructions` | 2 entries | the single residual (below) |
| relocations | 717 | |
| `__versions` | 67 entries | 66 reproduced |
| `__ksymtab*` | absent | 0 exports, matched |

Per-object detail: `kernel/phase4-tkcore-drv-objects.tsv`,
`kernel/phase4-tkcore-drv-relocations.tsv`,
`kernel/phase4-tkcore-drv-strings.tsv`.

# Behavioral verifier

`python3 kernel/scripts/phase4_tkcore_drv_verify.py` → **37 checks, 0 failures**,
`RESULT: tkcore_drv reconstruction verified (PROVIDER_ABI_PARTIAL / stock-ABI
complete)`.

1. frozen oracle hashes/sizes + vermagic + srcversion + depends
2. `stock-provider.symvers` re-extracts byte-identically from the stock ELFs
3. the 6 `NATURAL` CRCs really are regenerated from C
4. no witness-only edge is ever published by the natural provider build
5. stock-ABI build: 0 CRC mismatches, 0 extra imports, allowlist exact,
   `depends` correct, 0 exports
6. natural build: `PROVIDER_ABI_GAP` set is exactly the 7 witness edges, and
   every CRC it *does* carry matches stock
7. function inventory parity (50/50)
8. **kCFI prototype identity**: 20 type ids equal stock, and the one declared
   unresolved id is still exactly unresolved
9. one source of truth (symlink-only `-stockabi` package)

Verdict class: **`PASS_WITH_DECLARED_PROVIDER_WITNESSES`**.

# Secure-world opaque items

Permitted to remain opaque; none is required for a faithful Linux-side driver:

* the secure OS implementation behind every `0xf2xxxxxx` / `0x72xxxxxx` call
* the meaning of the secure-OS revision triple beyond its printed form
* the internal format of the 128 KiB secure log ring (the driver only supplies
  and registers it; tkcore drains it)
* the secure-side layout of the shared-memory window
* secure-side TA identities, session semantics and the secure-SPI TA
* the secure scheduler policy that produces `0xffff5702` CPU-bind requests

# Residuals

Exactly two, both bounded and explained:

1. **`alt_cb_patch_nops`** — one unreproduced kernel import, referenced twice
   from stock `.altinstructions`. It is an arm64 `ALTERNATIVE_CB` patch
   callback emitted by some inline helper; no C-level construct is recoverable
   from the stripped binary. Declared a **codegen artefact** and explicitly
   allowlisted in the verifier, so the allowlist can never silently grow.
   It is not a behavioural difference: patch sites are runtime nop-patching
   hooks, not control flow the driver depends on.
2. **`run_tee_task` kCFI type id** — stock `0xc2052128`, reconstruction
   `0xef18cf2f`. Arity and argument roles **are** proven from the two stock call
   sites (`call_tee+0x74`, `call_tee+0x120`: `x0 = ptee`, `x1 = &param`,
   `x2 = &affinity`, return unused), so behaviour is exact. What differs is the
   *tag names* of its two private parameter structs; **3,690 candidate
   spellings were compiled and hashed** (`tools/phase4-kcfi-probe/`) with zero
   hits, so the names are declared unrecoverable — the same class of block as
   tkcore's private member names, and equally not brute-forceable further.

Neither residual is Linux-visible behaviour.

# Runtime-validation status

**NOT RUNTIME-VALIDATED.** Nothing in this task was flashed or loaded on the
device; every claim is static and reproducible from the frozen oracles plus the
exact-GKI build. The stock-ABI target is *load-compatible* by construction
(identical import set, identical CRCs, identical `depends`, correct vermagic),
but "loads and serves TEE traffic on hardware" remains unproven and is the
obvious next validation step.

# Safety

* Load order must stay `ffa_v10 → teeperf → tkcore → tkcore_drv` (P:97–P:100,
  R:95–R:98). `tkcore_drv` probes nothing until its provider is present.
* Only the `-stockabi` target may ever be shipped; the natural-evidence target
  has 7 unresolved symbols and must never be flashed.
* Replacing this module does **not** make `tkcore` or `ffa_v10` replaceable —
  both remain stock vendor binaries and both remain required at runtime.
* Fingerprint, secure-SPI and all TA paths are unaffected: they live in
  `tkcore`/`microarray_fp_tee`, which this task did not touch.
* The two preserved stock quirks (init `return 1`, inverted unregister) mean
  module unload behaves exactly as stock — including not being a supported
  operation.

# Evidence index

| artefact | contents |
|---|---|
| `kernel/phase4-tkcore-drv-reconstruction.md` | this report |
| `kernel/scripts/phase4_tkcore_drv_verify.py` | fail-closed verifier (37 checks) |
| `kernel/phase4-tkcore-drv-recon/` | the reconstruction sources (4 `.c`, 4 `.h`, 2 Makefiles, 2 BUILD files) |
| `kernel/phase4-tkcore-drv-stock-provider.symvers` | the 13 provider CRCs, with class labels |
| `kernel/phase4-tkcore-drv-stock-provider.provenance.json` | extraction manifest (source ELF, section, offset per CRC) |
| `kernel/phase4-tkcore-drv-functions.tsv` | 50 stock functions with sizes/offsets |
| `kernel/phase4-tkcore-drv-imports.tsv` | 67 imports |
| `kernel/phase4-tkcore-drv-modversions.tsv` | 67 `__versions` records |
| `kernel/phase4-tkcore-drv-exports.tsv` | empty (0 exports) — the point being that it *is* empty |
| `kernel/phase4-tkcore-drv-objects.tsv` | section/object inventory |
| `kernel/phase4-tkcore-drv-relocations.tsv` | 717 relocations |
| `kernel/phase4-tkcore-drv-strings.tsv` | 178 strings |
| `tools/phase4-kcfi-probe/` | the kCFI prototype solver (probe generator + harness) |
| `tools/phase4-extract-stock-provider-symvers.py` | read-only witness extractor (now `__kcrctab_gpl`-aware) |
| `workspace/phase4-tkcore-drv/oracle/` | frozen stock oracles |
| `workspace/phase4-tkcore-drv/build/` | both rebuilt modules, for diffing |
| `workspace/phase4-tkcore-drv/raw/` | stock disassembly and symtab dumps |
| `kernel/phase4-tkcore-provider-abi.md` | why the 5 tkcore witness edges cannot be regenerated |

# Final verdict

`tkcore_drv.ko` is **SOURCE_RECONSTRUCTED**, **SOURCE_NOW_WITH_PROVIDER_WITNESSES**
and **FROZEN FOR RE**.

The Linux-visible driver is fully recovered as source: same 50 functions, same
call ids, same thread and memory models, same DT and log contracts, same
lifecycle including its quirks, 53/54 kernel imports, 13/13 provider imports in
the shippable target, 20/21 kCFI prototype identities, 17 functions
byte-identical to stock, clean exact-GKI build, and 37/37 verifier checks.

Its honesty boundary is stated per symbol: 6 provider edges are `NATURAL`, 7 are
`STOCK_PROVIDER_WITNESS`, and the same 7 appear as `PROVIDER_ABI_GAP` in the
natural-evidence build. **`tkcore` and `ffa_v10` are not source-pure, not
reconstructed and remain stock runtime providers.**
