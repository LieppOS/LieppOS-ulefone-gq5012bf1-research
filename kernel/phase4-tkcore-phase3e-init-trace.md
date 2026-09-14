# GQ5012BF1 tkcore Phase 3E — initialization trace

## Stock module entry

```text
init_module (.init.text)
  1. spin_lock_init(&tee_idr_lock)       [inlined]
  2. idr_init(&tee_idr)                  [inlined; xa_flags = IDR_RT_MARKER]
  3. plat_tee_init()
       - max cluster_id across possible CPUs
       - store large_cluster_id
       - info log
  4. discard return from plat_tee_init
  5. return 0
```

The rebuilt `init_module` is raw-byte identical to this 64-byte stock body. Stock `cleanup_module` is an empty 4-byte `ret`; the reconstruction is also raw-byte identical.

## Relationship to already-closed setup

None of the major provider setup is folded into `plat_tee_init`. It occurs later when a provider consumer invokes exported core APIs:

```text
tkcore_drv provider init / tee_tz_new
  -> tee_core_alloc
       -> tee_supp_init                  [supplicant state]
  -> tee_core_add
       -> register tkcore_admin misc node
       -> register tkcore_client misc node
       -> register tkcore_fp misc node
       -> tee_init_procfs                [proc/log lifecycle]
       -> tee_init_sysfs                 [sysfs]
       -> tee_peridev_init
            -> plat_register_spi_clk     [DT clock scan/registration]
```

Module dependency ordering means tkcore's module entry, including `plat_tee_init`, completes before a dependent provider uses its exports. No misc/proc/sysfs/supplicant/clock operation is duplicated.

Teardown remains through the already-closed provider lifecycle (`tee_core_del`, including peripheral/sysfs/misc/supplicant teardown). Stock module exit itself is empty. No affinity callback or mutation occurs in init or exit.
