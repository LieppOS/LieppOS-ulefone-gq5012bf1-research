# GQ5012BF1 tkcore Phase 3E — init/exit acceptance

## Module entry/exit

- `init_module`: 64/64 bytes, raw-byte identical to stock.
- Exact order: initialize `tee_idr_lock`; initialize `tee_idr`; call `plat_tee_init`; discard result; return 0.
- `cleanup_module`: 4/4 bytes, raw-byte identical stock `ret`.

## Closed provider lifecycle remains separate

- supplicant state is initialized from `tee_core_alloc` and released by provider teardown;
- the three misc nodes, proc/log, sysfs, and peripheral/clock registration remain in `tee_core_add` ordering;
- peripheral, sysfs, misc, and supplicant teardown remain in `tee_core_del`;
- `plat_tee_init` performs only possible-CPU topology maximum discovery and logging;
- no proc/sysfs/misc/supplicant/clock/SPI operation was duplicated in module init;
- no affinity callback is called and no affinity state is mutated during init/exit.

`large_cluster_id` and the candidate cache require no cleanup: they hold integer topology indices only. The const operations/affinity objects require none. No missing cleanup edge was introduced.

Result: **STATIC INIT/EXIT PASS**. Runtime validation remains unperformed.
