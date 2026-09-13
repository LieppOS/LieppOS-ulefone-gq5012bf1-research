# `gz_ipc_mod` mandatory RED

## Rules

The pinned `trusty-ipc.c` donor was built before any C behavior change. Its three lower-provider imports were resolved from the **real RED/source-built `gz_trusty_mod`**, not from stock CRC records.

- source revision: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- source file: unmodified `trusty-ipc.c`
- target: `//lieppos/gz-ipc-mod-red:gz_ipc_mod_red`
- lower dependency: `//lieppos/gz-trusty-mod:gz_trusty_mod`
- exact kernel: `//common:kernel_aarch64` (`6b18f0b574ab...`)

## Result

`BUILD_RC=0`; compiler warnings `0`; modpost warnings `0`; unresolved symbols `0`.

| Check | RED result |
|---|---:|
| stock / RED functions | 43 / 43 |
| shared / missing / extra | 43 / 0 / 0 |
| size-identical functions | 43/43 |
| byte-identical functions | **43/43** |
| KCFI exact | **43/43** |
| imports | **81/81 identical** |
| MODVERSIONs | **82/82 identical** |
| exports | 15 / 15 |
| natural export CRCs | **15/15** |
| semantic relocations | **1003/1003** |
| string set | 84/84 unique; only source/header package-path prefixes differed |

The RED immediately proved a direct source match. The only differences were line provenance for `trusty-ipc.c` and `trusty_ipc.h`. Reproducing the stock `kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/{gz-trusty,public}` layout closed both without changing source.

**RED conclusion:** no functional or ABI delta exists; source changes required: **none**.
