# ffa_v10 build/config contract

## Kconfig

```kconfig
config ARM_FFA_TRANSPORT
	tristate "Arm Firmware Framework for Armv8-A"
	depends on OF
	depends on ARM64
	default n

config ARM_FFA_SMCCC
	bool
	default ARM_FFA_TRANSPORT
	depends on ARM64 && HAVE_ARM_SMCCC_DISCOVERY
```
(byte-identical between the pinned vendor `Kconfig` and GKI's own
`common/drivers/firmware/arm_ffa/Kconfig` - MediaTek did not fork the config
symbol, only relocated the source it gates.)

`ARM_FFA_TRANSPORT` is **not set** in GKI's `gki_defconfig` on this baseline
(confirmed by grep - zero hits), which is exactly why the module ships from
the vendor tree as `ffa_v10.ko` instead of shipping in `system_dlkm` as a GKI
module, and why the reconstruction must build it out-of-tree.

## Kbuild target (vendor, verbatim)

```make
# device_modules/drivers/misc/mediatek/trusted_mem/Makefile
ifeq ($(CONFIG_ARM_FFA_TRANSPORT),...)
obj-m += ffa_v10.o
ffa_v10-y += ffa_v10/bus.o
ffa_v10-y += ffa_v10/driver.o
ffa_v10-y += ffa_v10/smccc.o
endif
```
kleaf packaging entry: `device_modules/kernel/kleaf/mgk_64_k61.bzl:467`,
`"drivers/misc/mediatek/trusted_mem/ffa_v10.ko"`.

## Required defines (proven necessary, not guessed)

| define | why | evidence |
|---|---|---|
| `CONFIG_ARM_FFA_TRANSPORT_MODULE=1` | `include/linux/arm_ffa.h` gates the real `ffa_driver_register`/`ffa_device_register`/`ffa_driver_unregister` prototypes behind `#if IS_REACHABLE(CONFIG_ARM_FFA_TRANSPORT)`; unset, the header substitutes `static inline` stubs that return `-EINVAL`/`NULL`/nothing, which would silently change every export CRC and produce a load-incompatible module | first observed in the tkcore_drv closure (`phase4-tkcore-drv-reconstruction.md` §"Exact-GKI build"), re-confirmed here since ffa_v10 itself does not include its own header guarded that way, but its *build system* (an out-of-tree module) needs `_MODULE` for consistency with every consumer sharing this GKI tree |
| `CONFIG_ARM_FFA_SMCCC=1` | selects `smccc.o` and the real (non-stub) `ffa_transport_init()` in `common.h`; unset, `ffa_transport_init` is a `static inline` returning `-EOPNOTSUPP` and the module could never invoke the secure world at all | stock ELF contains real `__arm_ffa_fn_smc`/`__arm_ffa_fn_hvc` bodies and a real `ffa_transport_init` (34/34 function parity) |

No other generated headers, vendor include paths, or namespace
imports/exports are required: `common.h` includes only public
`<linux/arm_ffa.h>` and `<linux/arm-smccc.h>`, and the module declares no
`MODULE_IMPORT_NS`/`MODULE_EXPORT_NS`.

## Dependencies

`depends=` is empty in stock `.modinfo` - ffa_v10 is a genuine provider leaf,
consistent with its position first in the platform load list (`P:97`,
`R:95`).

## Namespace imports/exports

None (`import_ns=` absent from `.modinfo`; no `MODULE_IMPORT_NS` in source).
