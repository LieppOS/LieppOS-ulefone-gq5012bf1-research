# FocalTech FT3680 main touch — progress pass

Scope opened after the VTDR6115 closure. **Not closed** — this records what
moved and what is left.

## Stock artifact (Phase 1)

| item | value |
|---|---|
| path | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/focaltech_touch_spi_ft3680.ko` |
| sha256 | `6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162` |
| size | 400 936 B |
| `name` | `focaltech_touch_spi_ft3680` |
| `author` | `FocalTech Driver Team` |
| `description` | `FocalTech Touchscreen Driver(SPI)` |
| `vermagic` | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| `depends` | **`yft_tpd_gesture,mtk_disp_notify,yft_devinfo`** |
| aliases | `of:N*T*Cfocaltech,fts`, `of:N*T*Cfocaltech,ftsC*` |
| functions | 166 |
| data objects | 85 |
| imports | 105 |
| exports | 0 |
| KCFI | none |
| `.data` | 121 608 B — dominated by the **embedded firmware** |
| `.rodata.str1.1` | 25 084 B |

## Firmware boundary

The touch firmware is **compiled into the module**, not a `/vendor/firmware`
file:

| item | value |
|---|---|
| object | `fw_file`, **118 972 B**, in `.data` at `+0x4a0` (not `.rodata` — the array is non-const in stock) |
| sha256 | `2269a91f6c07421749f48db31651cf59d63c66da7db92ac767e10cc95ff910bf` |
| selection record | `upgrade_setting_list[] = { 0, "", fw_file, sizeof(fw_file) }` |
| request_firmware path | present (`fts_get_fw_file_via_request_firmware`) but the built-in entry has an empty filename, so the built-in blob wins |

This is the **FT3680-FIRMWARE** half of the component and it is a proprietary
binary: it can be extracted and hashed but not reconstructed. Per the scope
rule it must not block the kernel-driver half.

## What moved this pass

**All 105 import modversion CRCs are now exact** (previously 103/105).

The two long-standing mismatches — `tpgesture_value` and
`yft_spitouchpanel_device_add` — were an artifact of linking against
*rebuilt* vendor providers. Harvesting the CRCs from the **stock** providers'
`__kcrctab` with `../vtdr6115/source/mk_symvers.py` resolves both:

| symbol | provider | stock CRC | now |
|---|---|---|---|
| `tpgesture_value` | `yft_tpd_gesture.ko` (**vendor ramdisk**) | `0x02f3ea4c` | match |
| `tpgesture_status` | `yft_tpd_gesture.ko` | `0x30ac810a` | match |
| `tpgesture_hander` | `yft_tpd_gesture.ko` | `0x8386526d` | match |
| `yft_spitouchpanel_device_add` | `yft_devinfo.ko` (vendor_dlkm) | `0xea3d7f0d` | match |
| `touch_fw_version` | `yft_devinfo.ko` | `0xd0815107` | match |
| `mtk_disp_notifier_register/unregister` | `mtk_disp_notify.ko` | — | match |

Note `yft_tpd_gesture.ko` lives in the **vendor ramdisk**, not `vendor_dlkm`;
looking for it only in `vendor_dlkm` is why the CRC was previously unresolved.

A second source delta was recovered: stock's `fw_file` is **non-const**
(`.data`), the reconstruction had it `const` (`.rodata`). Fixing that moved
121 kB of firmware from `.rodata` to `.data` and brought `.data` from 2 088 B
to 121 064 B against stock's 121 608 B.

## Current parity

A = stock module above. B = rebuild of
`lieppos/focaltech-ft3680-recon/recon` sources at the same GKI, isolated `M=`
build with stock-harvested `Module.symvers`.

| axis | result |
|---|---|
| functions | **166/166 present, 0 stock-only, 0 rebuild-only**, 105/166 size-identical, 23/166 byte-identical |
| imports | **105/105 names + CRCs exact** |
| exports | 0/0 both |
| `.modinfo` | identical |
| `depends=` | identical |
| `.rela.altinstructions`, `.rela__jump_table`, `.rela.eh_frame`, `.rela.exit.*`, `.rela.init.data`, `.rela.gnu.linkonce.this_module` | byte-identical |
| `.data` | 121 608 vs 121 064 |
| `.text` | 62 408 vs 63 384 |

## What is left

1. ~61 functions differ in size; the previously documented inlining/feature
   deltas (`workspace/phase4-focaltech-ft3680/ex-mode-and-inlining.md`,
   `fhp-abi.md`, `fwdbg-protocol.md`, `flash-engine-reconstruction.md`) are the
   map for closing them.
2. `.rodata`/`.rodata.str1.1` are 900 B / 470 B larger in the rebuild —
   leftover donor-only strings.
3. The hardware contract (SPI bus/CS, IRQ, reset, regulators, DT compatible)
   still needs the same DT-proof treatment the panel received.

Because **no blocker remains** (the firmware blob is extracted and hashed, all
provider CRCs resolve, and the function set converges exactly), the workspace
component is reclassified **BLOCKED → PARTIAL**.
