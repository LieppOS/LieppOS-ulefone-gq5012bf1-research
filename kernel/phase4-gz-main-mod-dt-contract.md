# gz_main_mod — device-tree / platform binding contract

No DT or DTBO file was modified. Everything below is read from the stock
module, the stock `modules.alias`, and the pinned source.

## 1. The `mediatek,trusty-mtee-v1` question — answered

Earlier notes said the `mtee` node **may** belong to `gz_main_mod` and that
this must not be assumed. It is now proven from three independent sources:

1. **Stock `modules.alias`** (`vendor_dlkm/lib/modules/modules.alias:177-178`):
   ```
   alias of:N*T*Cmediatek,trusty-mtee-v1     gz_main_mod
   alias of:N*T*Cmediatek,trusty-mtee-v1C*   gz_main_mod
   ```
2. **Stock `.modinfo`** carries the same two `alias=` entries and no others.
3. **Stock OF table object** `gz_main_of_match` plus
   `__mod_of__gz_main_of_match_device_table`, matching the source:
   ```c
   static const struct of_device_id gz_main_of_match[] = {
           { .compatible = "mediatek,trusty-mtee-v1", },
           {},
   };
   MODULE_DEVICE_TABLE(of, gz_main_of_match);
   ```

**`gz_main_mod` is the driver that binds `mediatek,trusty-mtee-v1`.** It is
the only compatible string it claims.

## 2. Platform driver

```c
struct platform_driver gz_main_driver = {
        .probe  = gz_main_probe,
        .remove = gz_main_remove,
        .driver = {
                .name           = "gz_main",
                .owner          = THIS_MODULE,
                .of_match_table = gz_main_of_match,
        },
};
```

| property | value |
|---|---|
| driver name | `gz_main` |
| compatible | `mediatek,trusty-mtee-v1` |
| probe | `gz_main_probe` (164 B) |
| remove | `gz_main_remove` (88 B) |
| registration | `platform_driver_register` in `gz_main_init` |
| unregistration | `platform_driver_unregister` in `gz_main_exit` |

`gz_main_driver` is a **global** (non-static) object in stock, with 4
relocations.

## 3. Position in the stock DT hierarchy

```
trusty {                        compatible = "android,trusty-smc-v1"
    tee-id   = <0>;             tee-name = "trusty"
    |
    +-- trusty-virtio {         "android,trusty-virtio-v1"   -> gz_virtio_mod
    +-- trusty-irq {            "android,trusty-irq-v1"      -> gz_irq_mod
    +-- tz-system {             "mediatek,trusty-tz"         -> gz_tz_system
    |       virtio-supply = <&trusty_virtio>;
    |       irq-supply    = <&trusty_irq>;
    +-- mtee {                  "mediatek,trusty-mtee-v1"    -> gz_main_mod  <== THIS
            tz-supply = <&tz_system>;
}

nebula {                        compatible = "android,nebula-smc-v1"
    tee-id = <1>;               tee-name = "nebula"
    ... (no mtee child matched by this driver)
}
```

| relationship | value |
|---|---|
| node | `mtee` |
| parent | `trusty` (the SMC root, `tee-id = <0>`) |
| phandle supply | `tz-supply = <&tz_system>` |
| TEE id | 0 (Trusty). No Nebula binding exists for this driver. |

## 4. How the supply relationship is actually used

`gz_main_mod` does **not** call `of_parse_phandle` or any regulator/supply
API — it imports none. The `tz-supply` phandle expresses load/probe ordering
declaratively; at runtime the module reaches `gz_tz_system` through the
exported `tz_system_dev` pointer instead:

```c
if (IS_ERR_OR_NULL(tz_system_dev))
        return -EINVAL;                 /* "GZ KREE is still not initialized!" */
trusty_adjust_task_attr(tz_system_dev->dev.parent, manual_task_attr);
```

`tz_system_dev->dev.parent` is the **Trusty root device**, which is how the
module issues SMCs against the correct TEE without ever parsing `tee-id`
itself.

## 5. Probe / remove behaviour

`gz_main_probe`:
1. `create_files()` → `misc_register(&gz_device)` then
   `device_create_file(gz_device.this_device, &dev_attr_gz_test)`.
2. Returns the result. **A sysfs-creation failure is logged but the probe
   still returns that non-zero value**, so probe fails if misc registration
   fails.

`gz_main_remove`:
1. `remove_files()` → `device_remove_file()` then `misc_deregister()`.
2. Returns 0.

The DEVAPC violation-callback registration is inside `#if enable_code` with
`enable_code == 0`, so it is absent from stock and from the rebuild.

## 6. Ordering

| stage | order |
|---|---|
| module load | `vendor_dlkm` `modules.load` index 150 (one-based) / 149 (zero-based) |
| load dependencies | `gz_tz_system`, `gz_trusty_mod`, `gz_ipc_mod`, `ffa_v10`, `mtk_sec_heap`, `tmem_ffa` — all loaded earlier |
| bind | when the `mtee` node probes, after its `tz-supply` provider |
| FF-A char device | created lazily on the **first FF-A probe**, not at module init |

No DT node, overlay or DTBO was read for modification, and none was changed.
