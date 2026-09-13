# `gz_trusty_mod` mandatory RED

## Rules

The pinned donor was built before any C behavior change. Permitted preparation was limited to `BUILD.bazel`, an out-of-tree Makefile wrapper, include placement, config visibility, and `-faddrsig`. There was no provider witness because this is the lowest module and all 59 imports are GKI.

- source revision: `957dac185efe46cbf6336b0fff9516d84c8cd78f`
- source files: unmodified `trusty.c`, `smcnr-table.c`
- target: `//lieppos/gz-trusty-mod-red:gz_trusty_mod_red`
- exact kernel: `//common:kernel_aarch64` (`6b18f0b574ab...`)

## Result

`BUILD_RC=0`; compiler warnings `0`; modpost warnings `0`; unresolved symbols `0`.

| Check | RED result |
|---|---:|
| stock / RED functions | 33 / 33 |
| shared / missing / extra | 33 / 0 / 0 |
| size-identical functions | 33/33 |
| byte-identical functions | **33/33** |
| KCFI exact | **33/33** |
| imports | **59/59 identical** |
| MODVERSIONs | **60/60 identical** |
| exports | 14 / 14 |
| natural export CRCs | **14/14** |
| semantic relocations | **553/553** |
| string set | 59/59 unique; only package-path prefix differed |

The RED did not reveal a source delta: it immediately proved a direct source match. The only mismatch was line provenance (`../lieppos/gz-trusty-mod-red/...` versus stock `../kernel_device_modules-6.1/...`). Moving the unchanged files into the vendor directory layout closed it. This is build plumbing, not a C-source change.

**RED conclusion:** no functional or ABI delta exists; source changes required: **none**.
