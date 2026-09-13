# gz_main_mod → gz_tz_system provider acceptance

## 1. Method

The edge list was **re-derived independently** from the stock `gz_main_mod`
ELF, not taken from the earlier triage note. Every undefined symbol was
matched against the `gz_tz_system` export table
(`kernel/phase4-gz-tz-system-exports.tsv`, 27 exports) and then against the
CRC actually produced by the REAL source-built provider.

Provider used: `//lieppos/gz-tz-system-accept:gz_tz_system_accept` — the
**witness-free** acceptance build of gz_tz_system, in which all seven of its
own transport edges resolve against source-built `gz_trusty_mod`/`gz_ipc_mod`.
No gz_tz_system witness record exists anywhere in this build.

## 2. Result — 15/15 edges, all NATURAL

The independent scan found exactly 15 edges, confirming the previously
recorded count.

| symbol | stock CRC | source-built provider CRC | call sites | status |
|---|---|---|---:|---|
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | `0x9a19c31a` | 1 | NATURAL_OK |
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | 12 | NATURAL_OK |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | 13 | NATURAL_OK |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | `0x3d5d5254` | 3 | NATURAL_OK |
| `KREE_ION_QueryChunkmem_TEST` | `0x14085470` | `0x14085470` | 1 | NATURAL_OK |
| `KREE_ION_ReferenceChunkmem` | `0x5df7236c` | `0x5df7236c` | 1 | NATURAL_OK |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | `0x8dceb484` | 3 | NATURAL_OK |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | `0x0175c8da` | 2 | NATURAL_OK |
| `KREE_RegisterSharedmem` | `0xfbdd82be` | `0xfbdd82be` | 3 | NATURAL_OK |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | `0x44781e48` | 1 | NATURAL_OK |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | 3 | NATURAL_OK |
| `KREE_TeeServiceCallPlus` | `0xf45addc2` | `0xf45addc2` | 1 | NATURAL_OK |
| `KREE_UnregisterSharedmem` | `0xd9a6d5ea` | `0xd9a6d5ea` | 2 | NATURAL_OK |
| `_map_user_pages` | `0x6e8b0474` | `0x6e8b0474` | 1 | NATURAL_OK |
| `tz_system_dev` | `0xebab6727` | `0xebab6727` | 8 | NATURAL_OK |

**15/15 NATURAL. 0 witnesses. 0 mismatches.**

## 3. Notes on individual edges

* `tz_system_dev` is a **data** export, not a function: an exported
  `struct platform_device *`. Its 8 references are the `IS_ERR_OR_NULL()`
  guards and `->dev.parent` dereferences used to reach the Trusty parent
  device for SMC and task-attribute operations.
* `_map_user_pages` has exactly one call site, in
  `_reg_shmem_from_userspace`. This closes the open question recorded in
  `kernel/phase4-gz-tz-system-userspace-abi.md`, which stated that the export
  exists to pin user pages on behalf of a kernel caller but did not identify
  the caller. **The caller is `gz_main_mod`, and it is the only one.**
* `KREE_TeeServiceCall` (3 sites) is used by the unit-test paths; the ioctl
  service path uses `KREE_TeeServiceCallPlus` (1 site), which additionally
  carries the `cpumask` argument.

## 4. Effect on gz_tz_system

None. `gz_main_mod` is a pure consumer: it defines no symbol that
`gz_tz_system` imports, and building it does not rebuild or alter the
provider. `gz_tz_system` remains `SOURCE_DELTA_RECONSTRUCTION_EXACT /
FROZEN FOR RE` with its 27 natural exports unchanged.
