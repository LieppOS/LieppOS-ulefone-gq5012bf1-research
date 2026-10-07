# TrustKernel TKCore normal-world backend (`tkcore_drv.ko`): DONE (static)

`tkcore_drv.ko` is rebuilt **byte-identical in all 50 functions** from the public TrustKernel
source plus a reconstructed release delta; data, strings, imports, 67/67 modversions, KCFI,
relocations, `__bug_table` and modinfo equal stock except `srcversion`; B1 == B2.
See `STATUS.md`, `parity/residuals.md`.

## Stock module identity

| item | value |
|---|---|
| file | `vendor_boot` platform ramdisk `/lib/modules/tkcore_drv.ko` (only copy in any partition) |
| sha256 / size | `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d` / 63 480 B |
| build-id | `8e73e9f92105915fe497b6c4cfbfffaf7b3fb2d9` |
| modinfo | author TrustKernel, description "TrustKernel TKCore TZ driver", version 1.0, license GPL, depends `tkcore,ffa_v10`, srcversion `0A6E96ED7F723D4F0883C3D` |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| build paths | `../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/{tee_tz_drv,tee_smc_xfer,tee_mem,handle}.c` |
| imports / exports | 66 (+`module_layout`): 53 GKI, 11 tkcore, 2 ffa_v10 / 0 |
| functions / data / relocations | 50 / 30 / 717 |
| compiler | Android clang 17.0.2 (r487747c) |

## Load / boot relationship (from the closed module-loading research)

| seq | module | phase |
|---|---|---|
| 108 | ffa_v10 | first stage (vendor_boot) |
| 109 | teeperf | first stage |
| 110 | tkcore | first stage |
| 111 | tkcore_drv | first stage (`modules.load` line 101, `modules.load.recovery` line 99) |
| 186 | microarray_fp_tee | first stage (tkcore client) |
| 300 | tmem_ffa | vendor_dlkm (FF-A/tkcore user) |

It must be early because `tkcore_drv` probe is what makes `tkcore.ko` publish
`/dev/tkcore_{admin,client,fp}` and `/proc/tkcore` (via `tee_core_add`), which `teed`
(`class core`, started at `post-fs`) and the KeyMint/Gatekeeper HALs need before
`/data` decryption, and which the first-stage fingerprint driver uses through tkcore. Recovery
loads the same set.

## Files

| topic | file |
|---|---|
| module set | `module-set.tsv` |
| lineage, donor pin, reconstructed delta | `source-lineage.md`, `source/donor-manifest.tsv`, `patches/0001-…patch` |
| platform / DT | `hardware-contract.md` |
| interface | `normal-world-interface.md`, `ioctl-map.tsv`, `smc-map.tsv` |
| shared memory | `shared-memory.md` |
| clients / RPMB | `userspace-clients.tsv`, `rpmb-boundary.md` |
| secure boundary / firmware metadata | `secure-world-boundary.md`, `firmware-inventory.tsv` |
| deltas | `yft-tkcore-deltas.md` |
| parity | `parity/` (function, data, abi, modversions, relocation, kcfi, bug-table TSVs; shared-tool outputs; `residuals.md`) |
| source | `source/armtz/*` (final armtz files), `source/core/tee_supp_com.h`, provider symvers |
| scripts | `scripts/build_tkcore_drv.sh`, `parity.sh`, `kcfi_preamble_parity.py`, `bug_table_parity.py` |

Earlier analysis: `kernel/phase4-tkcore-drv-reconstruction.md` (behavioural rebuild, 17/50
exact) and `kernel/phase4-tkcore-island-*` — superseded for `tkcore_drv`, see corrections.

## Corrections to earlier notes

| earlier claim (`kernel/phase4-tkcore-drv-reconstruction.md`) | correction |
|---|---|
| `NO_PUBLIC_SOURCE_FOUND`; 17/50 byte-identical; `alt_cb_patch_nops` codegen residual; `run_tee_task` KCFI unrecoverable after 3,690 spellings | public TrustKernel source exists (anvil-kernel); 50/50; `alt_cb_patch_nops` comes from LSE atomics on `nr_waiting_cmds`; KCFI tags are `invoke_tee_response` / `tee_task_cpu_affinity` |
| "whichever bus the platform provides wins" | SMC driver is dormant: no `trustkernel,tzdrv` DT node; FF-A SP `8bf0ccc3-…` (id 0x8001) is in `tee.img` |
| `0x80000000` "selects the 64-bit convention"; `0x72000003` preserves 32/64-bit | bit 31 is the SMCCC **fast-call** bit, bit 30 (`0x40000000`) is SMC64; return-from-RPC keeps the caller's fast/std kind |
| RPC selectors "0 alloc, 1 free arg block, 2 free buffer, 3 foreign IRQ" | 0 ALLOC_ARG, 1 ALLOC_PAYLOAD (unsupported → a2=0), 2 FREE_ARG, 3 FREE_PAYLOAD (no-op), 4 IRQ (resumed in `do_smc`), 5 CMD |
| "`0x1000000a` supplicant invoke" | `0x1000000A` is `TEE_RPC_RPMB_CMD` (forwarded as one combined buffer); other unknown commands go to the supplicant generically; `0x30000000` = sleep |
| CPU-bind retry "sleeps (`usleep_range_state`), ~2 ms" | no sleep in the bind loop (busy retry with `add_cpu`, 2000 µs budget); `usleep_range` serves RPC `0x30000000` |
| `idle_mask` "bit set while a CPU thread runs" naming / `tee_task_ctl` member names | `cpu_mask` = busy threads; an already-busy thread is preferred and not woken |
| private struct names ours (`smc_param`, `tee_affinity`) | `invoke_tee_response` (4 words), `tee_task_cpu_affinity {ops, priv}`, `tee_task_cpu_affinity_operations` |
| `tee_core_alloc(dev, "tkcore", …)` | name `"tkcoredrv"`, ops type `"tz"`; FF-A driver name `"tkcore"` |
