# ffa_v10 consumer ABI

Full stock module population scanned (471 `.ko` files across the platform
ramdisk, `vendor_dlkm`, `system_dlkm`, `odm_dlkm`) for any `__versions` entry
naming one of ffa_v10's five exports. **Three consumers found - one more than
the two named in the task brief.**

| consumer | provider symbol | consumer CRC | provider CRC | prototype | KCFI | status |
|---|---|---|---|---|---|---|
| `tkcore_drv.ko` | `ffa_driver_register` | `0x0d53cde9` | `0x0d53cde9` | `int (struct ffa_driver *, struct module *, const char *)` | n/a (import) | **MATCH** |
| `tkcore_drv.ko` | `ffa_driver_unregister` | `0x3c660e4c` | `0x3c660e4c` | `void (struct ffa_driver *)` | n/a (import) | **MATCH** |
| `tmem_ffa.ko` | `ffa_driver_register` | `0x0d53cde9` | `0x0d53cde9` | same | n/a | **MATCH** |
| `gz_main_mod.ko` | `ffa_driver_register` | `0x0d53cde9` | `0x0d53cde9` | same | n/a | **MATCH** |

No consumer imports `ffa_bus_type`, `ffa_device_register` or
`ffa_device_unregister` on this device - only the driver-registration pair is
used, and only `tkcore_drv` uses the unregister half.

## `tmem_ffa`

Discovered in `vendor_dlkm/lib/modules/tmem_ffa.ko`,
`depends=gz_tz_system,tkcore,ffa_v10` per the task brief. Confirmed by direct
scan (not assumed): its `__versions` table imports exactly one ffa_v10 symbol,
`ffa_driver_register` at `0x0d53cde9`, matching the naturally rebuilt provider
CRC exactly. Source: `nothing-mt6878/device_modules/drivers/misc/mediatek/
trusted_mem/{dev_mgr,entry,region_mgr,...}.c` (out of scope for this task;
noted for the phase-4 queue only).

## `gz_main_mod` (new discovery, not previously catalogued)

`vendor_dlkm/lib/modules/gz_main_mod.ko` also imports
`ffa_driver_register` at `0x0d53cde9`. Source located in the same pinned tree:
`nothing-mt6878/device_modules/drivers/misc/mediatek/geniezone/gz_main.c`
(GenieZone hypervisor/TEE glue - out of scope; flagged here only as a
consumer-ABI fact so it is never silently missed by a future task).

## Acceptance result

All three consumers' required CRCs are satisfied by the naturally
source-built `//lieppos/ffa-v10` provider with **zero exceptions**. No
consumer requires a symbol this reconstruction does not naturally publish.
