# RT5133 (Richtek camera LDO PMIC) on GQ5012BF1

**Result:** RT5133 is an **inactive MTK platform capability**. Its DT node is
inherited unchanged from the MT6878 base DTB and its driver loads at first
stage, but no RT5133 answers at `5-0018`: the probe aborts at the first
register read, no regulator or GPO is registered, and nothing on the board
consumes its rails. The camera LDO role is filled by the WL2864C/WL2868C at
`11-0029`, which reuses RT5133's HWEN line (GPIO1) as its reset GPIO.

Both kernel modules in the RT5133 closure rebuild **byte-identical to stock
except the build-id** from unmodified ALPS `5e415e059253`.

| module | functions | data | imports (CRC, order) | exports (CRC) | KCFI | modinfo |
|---|---|---|---|---|---|---|
| `rt5133-regulator.ko` | 13/13 | 34/34 | 39/39, order equal | 0 | 13/13 | 11/11 (srcversion `3A1F23BBC7D40274DE38CDD`) |
| `extdev_io_class.ko` | 10/10 | 19/19 | 39/39, order equal | 4/4 | 10/10 | 6/6 |

`extdev_io_class.ko` is included because `rt5133-regulator.ko` is its **only**
stock importer (`kernel/stock-module-imports.tsv`).

## Contents

| path | |
|---|---|
| [`STATUS.md`](STATUS.md) | one-table closure summary |
| [`hardware/topology.md`](hardware/topology.md) | bus, address, IRQ, GPIO, DT provenance, binding proof, GPIO1 coupling with WL2864C |
| [`hardware/consumer-map.tsv`](hardware/consumer-map.tsv) | every output (BASE, LDO1–8, GPO1–3, HWEN, IRQ): voltage, register, consumers, role class |
| [`hardware/dt-source-vs-live.tsv`](hardware/dt-source-vs-live.tsv) | 68/68 properties: ALPS `mt6878.dts` vs stock live FDT |
| [`hardware/stock-live-dt-rt5133-node.dts`](hardware/stock-live-dt-rt5133-node.dts) | the node as shipped |
| [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) | sha256, size, vermagic, depends, srcversion, build-id, counts, sections |
| [`register-map.tsv`](register-map.tsv) | every register the stock binary can touch, and what it touches on this board (one failed read of 0x00) |
| [`power-sequence.md`](power-sequence.md) | probe/runtime/remove, with the board-actual path |
| [`fault-handling.md`](fault-handling.md) | OC/PGB events → regulator notifiers; inactive here |
| [`yft-rt5133-deltas.md`](yft-rt5133-deltas.md) | DIRECT_SOURCE_MATCH + board-level deltas |
| [`source/`](source/) | exact ALPS sources, git-blob verified (`source/SOURCES.tsv`) |
| [`parity/`](parity/) | function/data/abi/relocation/string/section parity TSVs per module |
| [`scripts/`](scripts/) | inventory + string/section parity generators, rebuild harness |

## Parity operands

* **A** (stock): `vendor_boot` `vendor_ramdisk00` `lib/modules/{rt5133-regulator,extdev_io_class}.ko`,
  sha256 `467dcf89b5d807c2735c22c3023edc1137d135302f14d236fc841d110b07bc03`,
  `60f520e3b7f2a0dda95b8844ead106430ec63ebf350b591a0da5db01fce3d2b4`.
* **B** (rebuild): `scripts/sb.sh` isolated `M=` build of pristine ALPS
  `5e415e059253` against exact Google GKI 12901745, `llvm-strip --strip-debug`.
* `llvm-objcopy --remove-section=.note.gnu.build-id` on A and B → `cmp` equal
  for both modules; two independent rebuilds are byte-identical.

## Build-provenance residuals

Only `.note.gnu.build-id`. `__FILE__`/source paths: none embedded. DWARF:
stripped in stock. `.llvm_addrsig`, symbol indices, vermagic, srcversion: equal.

## Firmware / calibration

None. Neither module imports any firmware, NVMEM, OTP or EFUSE interface
(full import lists in `kernel/module-inventory.tsv` / parity ABI TSVs). The
part is configured purely by register writes derived from DT; the only
"persistent" state is the chip's own power-on register defaults, which a SW
reset (`0x06 = 0xB1`) restores. No firmware boundary exists.

## Audio cross-check

MT6369 (codec), AW88394 (amp), headset, earpiece and mic-bias nodes: none
reference any of the 13 RT5133 phandles (exhaustive scan of offline and live
FDT). **RT5133 IS NOT PART OF THE ACTIVE AUDIO SIGNAL PATH** — and it provides
no rail to anything else either.

## Corrections to earlier records

* "live `buses.txt`: 5-0018 → driver `rt5133` (bound)" — **wrong**; the
  `rt5133` line is the client *name*. The client is unbound (topology §3).
* "no standalone module ships / built-in driver" — **wrong**;
  `rt5133-regulator.ko` ships in `vendor_boot` and is in `modules.load` (#123).
* "camera-sensor LDO actively used" — the reference board uses it so; GQ5012BF1 does not.

## Safety

Everything here is offline static analysis of shipped images and existing
read-only captures. No register of `5-0018` was accessed.
