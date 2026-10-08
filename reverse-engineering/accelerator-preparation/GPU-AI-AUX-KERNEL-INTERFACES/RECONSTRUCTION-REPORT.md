# GPU-AI-AUX-KERNEL-INTERFACES — reconstruction report

Measured 2026-10-08 on a clean checkout of
`android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1` @ `aa21b33`, built twice (B1, B2) and
compared against the three stock modules
(`partitions/vendor_dlkm/lib/modules/{gpueb,vcp}.ko`,
`vendor-ramdisks/platform-extracted/lib/modules/vcp_status.ko`).

## 1. Acceptance

| module | stock bytes | functions | data objects | imports | export CRCs | KCFI abs ids | relocations | raw differing bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpueb.ko` | 109 016 | 59 | 69 | 68 | 14 | 6 | 1 820 | 20 |
| `vcp.ko` | 268 776 | 107 | 136 | 134 | 27 | 7 | 5 889 | 20 |
| `vcp_status.ko` | 22 624 | 17 | 17 | 1 | 19 | 0 | 158 | 20 |
| **total** | **400 416** | **183** | **222** | **203** | **60** | **13** | **7 867** | **60** |

Every differing byte of every module lies inside `.note.gnu.build-id`
(`gpueb` @0xa050, `vcp` @0x16710, `vcp_status` @0x1e90; 20 bytes each).
`unresolved = 0` for all three.

Classification: **BYTE_EXACT** for all code, data, section content, relocation and ABI
axes; **BUILD_METADATA_ONLY** for the three build IDs; **UNRESOLVED: none**. No
`PROVEN_SEMANTIC_EQUIVALENT` or `COMPILER_ONLY` class was needed — nothing differed.

Machine ledgers: [`function-parity.tsv`](function-parity.tsv) (183 rows),
[`data-parity.tsv`](data-parity.tsv) (222), `evidence/reconstruction/acceptance/`
→ `sections-parity.tsv` (142 rows: 139 IDENTICAL + 3 BUILD_ID_ONLY),
`abi-parity.tsv` (294 rows), `relocations-parity.tsv.xz` (7 867 rows, raw **and**
semantic), `acceptance.json`.

## 2. What was compared

* **Functions** — every `STT_FUNC` symbol keyed by (section, offset, name, size); byte
  content compared. 183/183 byte-identical, so there is no control-flow difference to
  analyse.
* **Data** — every `STT_OBJECT` keyed the same way: the IPI channel/pin tables, the VCP
  `feature_table`, mailbox layouts, reserved-memory descriptor arrays, register maps,
  `file_operations` / `platform_driver` / `notifier_block` / `miscdevice` /
  `attribute_group` registration structures, `.bss` layout. 222/222 identical.
* **Sections** — type, flags, size, align, entsize, offset, link, info and full content for
  all 142 sections across the three modules.
* **Relocations** — raw `.rela*` bytes *and* decoded (offset, type, target symbol, addend)
  tuples per section.
* **ABI** — 203 `__versions` import CRCs, 60 export CRCs read via `__crc_<name>` (so
  exported *data* such as `vcp_ipidev`, `vcp_mboxdev`, `feature_table`, `vcp_ao`,
  `pwclkcnt` is covered, with its `__kcrctab`/`__kcrctab_gpl` licence bucket), 13 absolute
  `__kcfi_typeid_*` values, 18 `.modinfo` records, `vermagic`, `srcversion`.
* **Whole file** — sha256 of the normalized (build-ID-zeroed) image equals stock for all
  three: `723a266ccb12…` (gpueb), `79bd2cdf96c1…` (vcp), `0e2e0242280b…` (vcp_status).

`srcversion` is identical for all three modules; no normalization was needed anywhere
except the build ID.

## 3. Source

Unmodified public ALPS `5e415e059253` (tree `9c61acc3cb0d…`). See [SOURCE.md](SOURCE.md).
Two patches, **5 added files, 0 modified files, 0 C/header edits**:

* `0001-owned-module-build-scope.patch` — 2 `Kbuild` wrappers (`drivers/gpu/mediatek/gpueb`,
  `drivers/misc/mediatek/vcp/rv`) selecting only the three owned modules from the unchanged
  vendor Makefiles.
* `0002-provider-abi-witness-scope.patch` — 3 `Kbuild` files scoping a compile of only the
  sources that *define* the 16 external exports, so their CRCs are produced by genksyms.

Patched tree ids are pinned: `src/kdm` `d3a42d6e93f0…`, `src/prov` `3e04c795a4b8…`.

## 4. Determinism

B1 and B2 (each regenerating source trees, kernel output tree and provider ABI from
scratch) are identical for: all 3 raw `.ko`, all 3 stripped `.ko`, all **22** target object
files (including composite and `.mod.o`), both per-directory `Module.symvers`, the provider
symvers, the CRC witness table, the kout `.config` sha256 and both source tree ids.

## 5. External ABI

16 externally provided exports are consumed; **16/16 CRCs were regenerated from public
source by genksyms and equal the CRCs the stock modules record in `__versions`**. No
symvers file was copied. The 8 cross-module imports of `vcp.ko` that come from
`vcp_status.ko` are satisfied inside this component's own modpost run. See
[abi-parity.md](abi-parity.md).

## 6. Relationship to already-DONE components

The rebuilt exports were checked against every other stock module's `__versions`:
**67 cross-component ABI edges, 67 MATCH, 0 mismatch** — 26 from MTK-VCODEC-KERNEL
(DONE), 15 from MALI-GPU-KERNEL (DONE), 1 from MEDIATEK-DRM (DONE), and 25 from
MMQoS/MMDVFS/CMDQ/MMINFRA/camera consumers owned elsewhere. Ledger:
[cross-component-abi.tsv](cross-component-abi.tsv). No DONE component was rebuilt,
modified or re-owned.

## 7. Scope retained

GPUEB and VCP **firmware images** (`gpueb.img`, `vcp.img`), their signing, secure boot
chain and on-core algorithms are separate proprietary components and were not touched,
loaded or analysed. The TinySys IPI / MTK mailbox transport modules keep their existing
DONE owners; SCP and ADSP host code was not duplicated. See
[firmware-boundary.md](firmware-boundary.md).

## 8. Not established

Nothing was executed on hardware. No probe, firmware boot, IPI exchange, interrupt,
watchdog, exception dump, suspend/resume or reset was observed. See
[source-to-userspace-contract.md](source-to-userspace-contract.md) §4 for the runtime
acceptance list.
