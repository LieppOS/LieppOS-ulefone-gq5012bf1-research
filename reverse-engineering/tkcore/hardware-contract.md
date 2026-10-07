# tkcore_drv platform / DT contract (GQ5012BF1)

Only what `tkcore_drv.ko` itself consumes. Evidence: stock module (byte-exact rebuild), stock
merged DT (`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`), stock
`firmware/tee.img` (metadata only), earlier runtime baseline
(`kernel/phase4-tkcore-island-phase3g-stock-runtime-baseline.md`).

| item | value | evidence | confidence |
|---|---|---|---|
| transport actually used | **FF-A v1.0 direct messages** through `ffa_v10.ko` to secure partition UUID `8bf0ccc3-42a3-5271-860d-66580469479c` | `tkcore_ffa_device_id`; `tee.img` `spmc_dtb` manifest: `description="trustkernel"`, same UUID (`uuid = <0xc3ccf08b 0x7152a342 0x58660d86 0x9c476904>`), `id = <0x8001>`, `messaging-method = <1>` (direct), `execution-ctx-count = <8>`, `ffa-version = 1.1`; stock DT has **no** `trustkernel,tzdrv` node so the SMC platform driver can never bind; runtime `/dev/tkcore_admin` exists, and only `tee_core_add()` (called from `tee_tz_new()` in probe) registers it | PROVEN |
| SMC transport | `platform_driver` "tzdrv", `of_match` `trustkernel,tzdrv`; registered but **dormant** on GQ5012BF1 (no DT node) | rebuild + DT | PROVEN |
| SPMC | EL3 SPMC inside the `atf` image of `tee.img` (`services/std_svc/spm/el3_spmc/spmc_main.c`) | strings, metadata only | STRONGLY SUPPORTED |
| reserved memory | `/reserved-memory/tkcore_shared_mem`: `compatible = "trustkernel,shared_mem"`, dynamic `size = 0x2000000` (**32 MiB**), `alignment = 0x1000`, `alloc-ranges = <0 0x40000000 0 0x80000000>` (1–3 GiB), `no-map` | DT | PROVEN |
| reserved-memory consumer | `tz_start()` → `of_find_compatible_node(NULL,NULL,"trustkernel,shared_mem")` + `of_reserved_mem_lookup()`; base/size used verbatim; mapped **cacheable** through tkcore's `tee_map_cached_shm()`; fallback (node/lookup missing) `__get_free_pages(order 10)` = 4 MiB | rebuild | PROVEN |
| log IRQ | `of_find_compatible_node(NULL,NULL,"trustkernel,tkcore")` → `irq_of_parse_and_map(np,0)`; **node absent on GQ5012BF1** → `tkcore_drv: device node not found`, `tee->log.irq = 0` | rebuild + DT | PROVEN (static) |
| log ring | `__get_free_pages(GFP_KERNEL, order 5)` = 128 KiB, registered with fast call `0xf2005705`; failure non-fatal | rebuild | PROVEN |
| clocks / regulators / resets / pinctrl / GPIO | none | import set (66) | PROVEN |
| IRQ handlers | none registered by this module (foreign IRQs arrive as RPC `0xffff0004` and are simply resumed) | import set | PROVEN |
| char devices / sysfs / procfs / debugfs | **none of its own**; `/dev/tkcore_{admin,client,fp}`, `/proc/tkcore/*` belong to `tkcore.ko` | import set | PROVEN |
| CPU hotplug | `cpuhp_setup_state(CPUHP_AP_ONLINE_DYN, "tee/tkcore_tzdrv:cpu_listener", tee_cpu_online, tee_cpu_prepare_down)` | rebuild | PROVEN |
| kthreads | one per possible CPU, `tkcore_smc_task.%u`, bound with `kthread_bind`; `NR_CPUS` limit 32 | rebuild | PROVEN |
| secure-partition device regions (secure side) | GICv3 distributor `0x0c400000` (16 pages), redistributors `0x0c440000` (512 pages) granted to the SP | `spmc_dtb` manifest | PROVEN (metadata) |

Config of the stock build, proven by code present in the binary: `CONFIG_TRUSTKERNEL_TEE_SUPPORT=m`,
`CONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=y` (RPMB RPC branch), `CONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=y`
(clkmgr RPC branch + `tee_clkmgr_handle` import), `CONFIG_ARM_FFA_TRANSPORT=m` (IS_REACHABLE true),
`CONFIG_OF`, `MODULE` (runtime reserved-mem lookup instead of `RESERVEDMEM_OF_DECLARE`).
