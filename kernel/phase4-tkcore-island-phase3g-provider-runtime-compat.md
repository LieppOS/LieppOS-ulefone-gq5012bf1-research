# TrustKernel Phase 3G — installed-provider runtime compatibility

Result: **PASS — retain every non-tkcore provider as stock for the first boot**.

Runtime-selection update: the final minimized image also retains stock `tkcore_drv`; only source `tkcore` and source `tmem_ffa` are staged. The broader source-`tkcore_drv` checks below remain a conservative compatibility proof, not an instruction to deploy it.

Authoritative machine-readable matrix:

`workspace/phase4-tkcore-island/phase3g/provider-runtime-compat.tsv`

All CRCs were independently read from the installed-stock provider ELF export sections and the exact Phase-3F/3G consumer `__versions` sections. No `Module.symvers` witness was used for an installed-stock result.

## Conservative broader static candidate

| Provider retained | Consumer replaced | Edges | Compatible |
|---|---|---:|---|
| stock `ffa_v10.ko` | source `tkcore_drv.ko` | `ffa_driver_register`, `ffa_driver_unregister` | **2/2 YES** (`0x0d53cde9`, `0x3c660e4c`) |
| stock `ffa_v10.ko` | source `tmem_ffa.ko` | `ffa_driver_register` | **1/1 YES** (`0x0d53cde9`) |
| stock `gz_tz_system.ko` | source `tmem_ffa.ko` | 9 KREE exports | **9/9 YES** |

The nine exact GenieZone values are:

- `KREE_AppendSecureMultichunkmem=0x9a19c31a`
- `KREE_CloseSession=0x5878d629`
- `KREE_ConfigSecureMultiChunkMemInfo=0xbdb6a34b`
- `KREE_CreateSession=0x552d4efc`
- `KREE_ION_AllocChunkmem=0x3d5d5254`
- `KREE_ION_UnreferenceChunkmem=0x8dceb484`
- `KREE_ION_ZallocChunkmem=0x0175c8da`
- `KREE_ReleaseSecureMultichunkmem=0x44781e48`
- `KREE_TeeServiceCall=0xec19e146`

Required first-boot non-tkcore provider edges: **12/12 compatible**.

## Stock MicroArray consumer retained

The installed stock `microarray_fp_tee.ko` imports `tee_spi_transfer=0x184ce7da`; the frozen Phase-3G source `tkcore.ko` exports exactly `0x184ce7da`. Result: **YES**, so stock MicroArray is retained and no fingerprint-stack module is added to the changed set.

## Deferred source-MicroArray cross-check

Although source MicroArray is explicitly **not** part of the first boot, its provider compatibility was checked to prevent ambiguity in a later separately controlled delta:

- installed stock `fingerprint.ko`: 4/4 edges compatible;
- installed stock `spi-mt65xx.ko`: 2/2 edges compatible.

Thus stock `fingerprint` and `spi-mt65xx` also remain installed.

## Complete-population proof

A second audit assembled all 471 modules from the authoritative extracted normal-boot population (196 vendor-boot platform, 215 vendor_dlkm, 60 system_dlkm), replaced exactly the three island files, and resolved every `__versions` entry against exact-GKI `Module.symvers` plus the assembled module exports:

- ELF parse errors: **0**
- unresolved imports: **0**
- version disagreements: **0**
- duplicate conflicting provider symbols: **0**

Conclusion: no extra provider replacement is required; silently expanding the deployment unit would be unjustified.
