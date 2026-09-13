# ffa_v10 module init/exit

Byte-identical to stock (`init_module`/`cleanup_module` are 2 of the 34
byte-identical functions). Both are `subsys_initcall(ffa_init)` /
`module_exit(ffa_exit)`, which resolve to plain `module_init`/`module_exit`
when built as a module (see build-contract.md), so `init_module` really is
`ffa_init` and `cleanup_module` really is `ffa_exit` - no special module
wrapper.

## `ffa_init()` (`init_module`)

```
1. ffa_transport_init(&invoke_ffa_fn)     -- pick SMC vs HVC conduit; fail closed
2. arm_ffa_bus_init()                     -- bus_register(&ffa_bus_type)
3. drv_info = kzalloc(sizeof(*drv_info))
4. ffa_version_check(&drv_info->version)  -- FFA_VERSION handshake, v1.0 clamp
5. ffa_id_get(&drv_info->vm_id)           -- FFA_ID_GET, "failed to obtain VM id for self" on error
6. rx_buffer = alloc_pages_exact(RXTX_BUFFER_SIZE)   -- PAGE_SIZE = 4 KiB
7. tx_buffer = alloc_pages_exact(RXTX_BUFFER_SIZE)
8. ffa_rxtx_map(tx_phys, rx_phys, RXTX_BUFFER_SIZE/FFA_PAGE_SIZE)  -- "failed to register FFA RxTx buffers" on error
9. mutex_init(&drv_info->rx_lock); mutex_init(&drv_info->tx_lock)
10. ffa_setup_partitions()                -- FFA_PARTITION_INFO_GET, ffa_device_register() per partition
11. ffa_set_up_mem_ops_native_flag()      -- FFA_FEATURES probe for SMC64 mem-ops
    return 0
```

### Error paths (preserved exactly)

Every `goto` unwinds only what was actually allocated:
`free_pages:` frees `tx_buffer` (if allocated) then `rx_buffer`;
`free_drv_info:` frees `drv_info`; `ffa_bus_exit:` unregisters the bus. A
failure in step 1 or 2 returns directly with nothing to unwind yet.

## `ffa_exit()` (`cleanup_module`)

```
1. ffa_rxtx_unmap(drv_info->vm_id)     -- FFA_RXTX_UNMAP
2. free_pages_exact(tx_buffer, RXTX_BUFFER_SIZE)
3. free_pages_exact(rx_buffer, RXTX_BUFFER_SIZE)
4. kfree(drv_info)
5. arm_ffa_bus_exit()                  -- unregisters all ffa_device children, then the bus
```

No quirks to preserve here (unlike tkcore_drv's inverted-unregister-guard
quirk) - the teardown is the clean, symmetric inverse of init. `ffa_v10` is
never unloaded on this device in practice (it is the first module in the
platform load list and has three live consumers), but the path is exact
either way.
