# GQ5012BF1 GenieZone transport lineage

## Frozen lineage

Both modules are exact outputs of the same pinned source island already used by `ffa_v10`, `tmem_ffa`, and `gz_tz_system`:

- repository: `NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878`
- revision: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- vendor directory: `drivers/misc/mediatek/geniezone/gz-trusty/`
- headers: `drivers/misc/mediatek/geniezone/public/gz-trusty/`

| Module | Kconfig | Objects | Source classification | Source delta |
|---|---|---|---|---|
| `gz_trusty_mod.ko` | `MTK_ENABLE_GENIEZONE=m` | `trusty.o smcnr-table.o` | `EXACT_SOURCE` | none |
| `gz_ipc_mod.ko` | `MTK_GZ_VIRTIO_IPC=m` | `trusty-ipc.o` | `EXACT_SOURCE` | none |

`trusty-debugfs.o` is a separate conditional object and is stock-proven off.

## Final build layout

Final exact-GKI target:

`//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`

It emits both modules in one invocation, as the vendor Kbuild does. This has two useful proof properties:

1. clang sees the same `../kernel_device_modules-6.1/...` source/header spelling embedded by stock;
2. `gz_ipc_mod` resolves its three Trusty imports from the real `gz_trusty_mod` generated in the same `Module.symvers`.

The package contains no stock provider witness, fake object, injected CRC, copied `__versions`, or patched ELF.

## Build chain

```text
exact GKI 6b18f0b574ab
  └─ gz_trusty_mod  (59 GKI imports; no intermodule dependency)
       └─ gz_ipc_mod (78 GKI imports + 3 natural Trusty imports)
            └─ gz_tz_system (5 natural IPC + 2 natural Trusty imports)
                 └─ tmem_ffa
```

`tkcore` is independent and remains stock runtime. `gz_main_mod` is not reconstructed here.

See `phase4-gz-transport-source-hashes.tsv` for the immutable source inventory.
