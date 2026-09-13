# Phase 4 — `tkcore_drv.ko` reverse engineering & source reconstruction

**Target device:** Ulefone Armor 29 Pro Thermal, GQ5012BF1, MediaTek MT6878/MT6878T
**Baseline:** Linux 6.1.115-android14-11, Android CI `ab/12901745`, common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
**Exact-GKI workspace:** `/home/armol/kernel-work/gki-12901745-workspace`

---

## 1. Result

| | |
|---|---|
| **Classification** | `RECONSTRUCTED` / `PROVIDER_ABI_PARTIAL` |
| **Stock import ABI reproduced** | **66 / 67** `__versions` entries, **0 CRC mismatches, 0 extra imports** |
| **Exports** | 0 (stock) = 0 (recon) — `tkcore_drv` is a pure consumer |
| **Natural provider edges** | 6 / 13 (`NATURAL`) |
| **Stock-witness provider edges** | 7 / 13 (`STOCK_PROVIDER_WITNESS`) |
| **Unreproduced** | 1 import: `alt_cb_patch_nops` (arm64 `ALTERNATIVE_CB` codegen artefact) |
| **Function inventory** | **50 / 50** defined functions — identical name set, no extra helpers, none missing |
| **Verifier** | `kernel/scripts/phase4_tkcore_drv_verify.py` — 35 checks, 0 failures |

The module is reconstructed as real, readable, buildable C that compiles in a
kleaf build against the exact GKI tree — not as a byte-patched clone. Nothing
about the secure world behind the SMC/FF-A call ids is modelled or invented.

### Stock oracles (frozen)

| Module | sha256 | size |
|---|---|---|
| `tkcore_drv.ko` | `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` | 63480 |
| `tkcore.ko` (provider) | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| `ffa_v10.ko` (provider) | `2f8341d3f920418f3d9f4b8f64299acf97e591ad232a6bbbf6298b63231eebde` | 38688 |

`vermagic=6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64`,
`srcversion=0A6E96ED7F723D4F0883C3D`, `depends=tkcore,ffa_v10`,
build path `../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tee_tz_drv.c`.

---

## 2. What the module is

`tkcore.ko` is the Linux-side TrustKernel TEE **core** (char devices, contexts,
sessions, shared memory, supplicant). `tkcore_drv.ko` is the **backend** that
carries those requests into the TrustKernel secure OS. It registers two
transports and whichever the platform provides wins:

* **FF-A** — `ffa_driver` matching partition UUID `8bf0ccc3-42a3-5271-860d-66580469479c`,
  one `sync_send_receive()` direct request per secure call.
* **SMC** — `platform_driver` on DT `compatible = "trustkernel,tzdrv"`,
  raw `arm_smccc_smc()`.

Both share one implementation; only the `->invoke_tee()` /
`->build_mem_share_handle()` function pair differs.

Load order is unchanged by this work: `P:97 ffa_v10 → P:98 teeperf →
P:99 tkcore → P:100 tkcore_drv` (recovery `R:95…R:98`).

### Recovered call identifiers

| id | meaning | evidence |
|---|---|---|
| `0xf2000001` | get secure-OS revision | `tee_tz_new()` `mov w1,#1; movk w1,#0xf200,lsl#16` |
| `0xf2005704` | register shared-memory window | `tz_start()` |
| `0xf2005705` | set up secure log ring | `tee_tz_new()` |
| `0x72000003` | return from RPC (32/64 bit preserved) | `do_smc()` `(a0 & 0x80000000) \| 0x72000003` |
| `0xffff0004` | preempted by foreign interrupt | `do_smc()` resume loop |
| `0xffff5702`, ret `6` | secure world requests a specific CPU | `run_tee_task()` |
| ret `1` | busy — park on the global completion | `run_tee_task()` |

RPC selectors (low 16 bits of `a0`): `0` alloc, `1` free-arg, `2` free,
`3` IRQ, `5` command, `0x5700`/`0x5701` supplicant alloc/free.
RPC command ids inside the message: `0x20000001`/`0x20000002` wait-queue
sleep/wakeup, `0x80000001` clock manager, `0x1000000a` supplicant invoke.
Supplicant ids: `0x1001` allocate, `0x1002` free, `0x1003` invoke.

Other constants read out of the binary: secure log ring
`__get_free_pages(order 5)` = 128 KiB, fallback shared pool
`__get_free_pages(order 10)` = 4 MiB, long-call warning threshold
1,000,000 µs, `NR_CPUS` cap 32, CPU-bind retry window ~2 ms.

---

## 3. Source layout

Single source of truth in `//lieppos/tkcore-drv-recon` (the `-stockabi`
package contains only symlinks, so both targets compile identical bytes):

| file | contents |
|---|---|
| `tkcore_drv_main.c` | transports, `struct tee_ops` backend (`tz_start/stop/open/close/invoke/cancel/alloc/free/shm_inc_ref`), `call_tee()` RPC loop, `tee_tz_new()`, FF-A + platform drivers, module init/exit |
| `tee_task.c` | per-CPU secure-call kthreads, global queue + mutex, `do_smc()`, CPU-affinity policy tables, hotplug listener |
| `tee_mem.c` | shared-memory pool (first-fit ordered chunk list with refcounts) |
| `handle.c` | pointer↔handle DB for supplicant-allocated SHM |
| `tkcore_abi.h` | tkcore's private `struct tee` / `tee_shm` / `tee_session` / `tee_cmd` layouts + the 11 consumed tkcore prototypes |
| `tkcore_drv.h` | call ids, `struct tee_tz`, dispatcher types |

### How the private layouts were recovered

TrustKernel never published the tkcore headers, so every offset is asserted
from instruction evidence, e.g.

```
tee_core_alloc():  devm_kmalloc(dev, priv_len + 0x138)   -> sizeof(struct tee)
                   snprintf(tee + 0x20, 64, "%s", name)  -> name[64] @ 0x20
                   str x8,[x20,#0x88] (x8 = tee + 0x138) -> priv @ 0x88
                   stp x22,x19,[x20,#0x90]               -> ops @0x90, dev @0x98
tz_start():        ldrb w8,[x0,#0x130]; tbnz w8,#0       -> conf @0x130, bit 0
tz_alloc():        devm_kmalloc(dev, 0x68) + stores      -> struct tee_shm
handle_get():      ldr w9,[db,#0x8]                      -> u32 max_ptrs @ 0x8
```

Member **names** are ours; only the layouts are stock. None of these types is
exported by this module, so genksyms never hashes them — the reconstruction
cannot "launder" an unknown provider ABI through them.

The `handle_get()` growth policy was read back literally from
`.text 0x35fc`: start at 4 entries, then double
(`w22 = max ? max*2 : 4`, `krealloc(ptrs, w22*8, GFP_KERNEL)`,
`memset(ptrs + max, 0, (w22-max)*8)`).

---

## 4. Provider ABI — three classes, never conflated

`tkcore_drv` exports nothing, so stock-provider ABI witnesses are permitted by
project rule. They are nevertheless labelled per symbol.

### `NATURAL` — 6 edges

Regenerated from C by exact-GKI genksyms in `//lieppos/tkcore-recon`, and the
regenerated CRC equals the stock CRC:

| symbol | CRC |
|---|---|
| `tee_map_cached_shm` | `0x6a4e508b` |
| `tee_clkmgr_handle` | `0x6913f6b2` |
| `tee_wait_queue_init` | `0x03c4c343` |
| `tee_wait_queue_exit` | `0xe773ba45` |
| `tee_wait_queue_sleep` | `0xcca24950` |
| `tee_wait_queue_wakeup` | `0xe2de5bad` |

### `STOCK_PROVIDER_WITNESS` — 7 edges

Only obtainable by reading the stock provider ELF's own
`__kcrctab`/`__kcrctab_gpl`. **These are not natural regeneration.**

| symbol | CRC | provider | why blocked |
|---|---|---|---|
| `tee_core_alloc` | `0x68aaf1dc` | tkcore | takes `struct tee *` / `struct tee_ops *` — CRC hashes TrustKernel's private member *names* |
| `tee_core_add` | `0x74f0ee2b` | tkcore | ditto |
| `tee_core_del` | `0xf53dbff2` | tkcore | ditto |
| `__tee_get` | `0xa4df7b8a` | tkcore | ditto |
| `tee_supp_cmd` | `0x6f7dfbee` | tkcore | takes `struct tee *` |
| `ffa_driver_register` | `0x0d53cde9` | ffa_v10 | vendor FF-A stack GKI does not build |
| `ffa_driver_unregister` | `0x3c660e4c` | ffa_v10 | ditto |

Extraction is read-only and reproducible:

```
tools/phase4-extract-stock-provider-symvers.py \
  --elf .../tkcore.ko --sym tee_core_alloc ... \
  --elf .../ffa_v10.ko --sym ffa_driver_register ... \
  --out stock-provider.symvers --manifest stock-provider.provenance.json
```

(The tool gained `__kcrctab_gpl` support in this task; `ffa_v10` exports are
GPL-only.) The verifier re-runs the extraction and fails if any line in
`stock-provider.symvers` does not byte-match the stock ELF record.

### `PROVIDER_ABI_GAP` — natural-evidence build

`//lieppos/tkcore-drv-recon` links **only** against the natural provider
record, so modpost reports exactly those same 7 edges as undefined
(`KBUILD_MODPOST_WARN=1`, by design). This target is the honest
"what can exact GKI regenerate?" answer; it is not loadable.

---

## 5. Build targets

| target | provider record | modpost | purpose |
|---|---|---|---|
| `//lieppos/tkcore-drv-recon` | `tkcore-recon/Module.symvers` (natural only) | warns on the 7 gaps | natural evidence |
| `//lieppos/tkcore-drv-recon-stockabi` | `stock-provider.symvers` (13 stock edges) | **fail-closed, clean** | stock-compatible, loadable |

```
tools/bazel build //lieppos/tkcore-drv-recon:tkcore_drv_recon
tools/bazel build //lieppos/tkcore-drv-recon-stockabi:tkcore_drv_recon_stockabi
```

Both compile with zero warnings under the GKI `-Werror` flag set.
`-DCONFIG_ARM_FFA_TRANSPORT_MODULE=1` is required so GKI's `arm_ffa.h` exposes
the real `ffa_driver_register()` prototypes instead of its `!IS_REACHABLE()`
stubs — without it the module would silently stop importing them (this is how
MediaTek's own out-of-tree build sees the header, since `ffa_v10` is a module).

The stock-ABI target reports `depends=ffa_v10,tkcore` (stock:
`tkcore,ffa_v10` — same set, modpost orders by first use).

---

## 6. Import-set parity

Aligning the reconstruction to the stock import set drove four
evidence-backed corrections, each one visible in the ELF:

| stock evidence | consequence |
|---|---|
| imports `_printk`, not `_dev_err/_dev_info/_dev_warn` | `tee_mem.c` logs via `pr_*` |
| imports `devm_kmalloc`/`devm_kfree`, and `__kmalloc` only for the non-constant `kmalloc_array()` | pool and chunks are `devm_kzalloc()`, not `kzalloc()` |
| imports `_raw_spin_lock`/`_raw_spin_unlock`, no irqsave variants | pool lock is plain `spin_lock()` |
| imports `usleep_range_state` | the CPU-bind retry loop sleeps rather than spins |
| out-of-line `memset` call at `.text 0x3690` inside `handle_get` | growth is doubling (variable-size zeroing), not a fixed 4-slot step |

Remaining difference: `alt_cb_patch_nops`, referenced twice from stock
`.altinstructions`. It is an arm64 `ALTERNATIVE_CB` patch callback emitted by
some inline helper; no C-level construct is recoverable from the stripped
binary, so it is declared a **codegen artefact** and allowlisted explicitly in
the verifier (it can never silently grow).

---

## 7. Verification

```
python3 kernel/scripts/phase4_tkcore_drv_verify.py
```

35 checks, 0 failures. It asserts: frozen oracle hashes; that
`stock-provider.symvers` re-extracts identically from the stock ELFs; that the
6 `NATURAL` CRCs really are regenerated from C; that no witness-only edge is
ever published by the natural provider build; zero CRC mismatches and zero
extra imports in the stock-ABI build; that the natural build's gap set is
exactly the 7 witness edges; that both builds export nothing; that the rebuilt
module defines exactly the same 50 functions as stock; and that the
`-stockabi` package holds only symlinks.

---

## 8. Stock ELF inventory (frozen)

`tkcore_drv.ko`: 50 defined functions, **0 exports**, 67 `__versions` entries
(54 kernel + 13 provider imports), 717 relocations, `.text` 0x3734 B,
`.init.text` 0x84 B, `.exit.text` 0x58 B, `.rodata` 0x2a8 B, `.bss` 0xac B,
2 `.altinstructions` entries, `__bug_table` 0x204 B.

The 50 functions, all of which the reconstruction reproduces by name:

```
init_module cleanup_module
tkcore_ffa_probe tkcore_ffa_remove tkcore_smc_probe tkcore_smc_remove
tee_tz_new
invoke_tee_ffa invoke_tee_smc
build_mem_share_handle_ffa build_mem_share_handle_smc
tz_start tz_stop tz_open tz_close tz_invoke tz_cancel
tz_alloc tz_free tz_shm_inc_ref set_params call_tee
tee_init_task tee_exit_task run_tee_task tkcore_smc_task do_smc
tee_cpu_online tee_cpu_prepare_down
default_affinity_need_bind_cpu default_affinity_match_cpu
default_affinity_get_candidate_cpu
tee_bind_cpu_request_need_bind_cpu tee_bind_cpu_request_match_cpu
tee_bind_cpu_request_get_candidate_cpu
tee_shm_pool_create tee_shm_pool_destroy tee_shm_pool_reset
tee_shm_pool_dump tee_shm_pool_is_cached tee_shm_pool_set_cached
tee_shm_pool_p2v tee_shm_pool_v2p tee_shm_pool_incref
tkcore_shm_pool_alloc tkcore_shm_pool_free
handle_db_destroy handle_get handle_put handle_lookup
```

Two stock behaviours are preserved deliberately rather than "fixed":

* `init_module()` returns **1** (not a negative errno) when *both* transport
  registrations fail.
* `cleanup_module()` guards the unregister calls with the *failed* (non-zero)
  registration return codes, so a successfully registered driver is never
  unregistered. The stock module is never unloaded on this device, so the
  asymmetry is unobservable; it is reproduced and documented, not silently
  corrected.

## 9. Scope discipline

Not touched, per charter: `tkcore` (`NO_PUBLIC_SOURCE_FOUND` /
`PROVIDER_ABI_PARTIAL`, 14/25 natural, 11/25 blocked — unchanged and not
reopened), `microarray_fp_tee`, fingerprint, connectivity, panel/provider
work, `yft_devinfo`, `uSmart`. No tkcore CRC was brute-forced, and tkcore is
still **not** marked source-pure.
