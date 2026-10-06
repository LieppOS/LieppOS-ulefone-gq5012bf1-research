# Camera VCM / autofocus actuators — GQ5012BF1

**Result:** three fitted AF actuators, one protocol (DW9800W command set,
lens_id `0x9800`), each at **`0x0C` on its sensor's bus**: camera 0 imx989
`7-000c` (`main_vcm`), camera 2 s5kjn1main2 `2-000c` (`main4_vcm`), camera 3
ov64b `4-000c` (`main2_vcm`). Camera 1 (s5kjn1 front) is **fixed focus**.
All six shipped lens modules rebuild **byte-identical to stock except the
build-id** from unmodified ALPS `5e415e059253`.

| module | class | functions | data | imports (CRC, order) | KCFI | relocs | strings |
|---|---|---|---|---|---|---|---|
| `main_vcm.ko` | ACTIVE, camera 0 | 10/10 | 25/25 | 29/29 ✓ | 10/10 | 299/299 | 49/49 |
| `main2_vcm.ko` | ACTIVE, camera 3 | 10/10 | 25/25 | 29/29 ✓ | 10/10 | 291/291 | 49/49 |
| `main4_vcm.ko` | ACTIVE, camera 2 | 10/10 | 25/25 | 29/29 ✓ | 10/10 | 291/291 | 49/49 |
| `main3_vcm.ko` | PLATFORM-ONLY | 10/10 | 25/25 | 29/29 ✓ | 10/10 | 291/291 | 49/49 |
| `sub_vcm.ko` | PLATFORM-ONLY | 10/10 | 25/25 | 29/29 ✓ | 10/10 | 291/291 | 49/49 |
| `camera_af_media.ko` | ACTIVE (media aggregator) | 7/7 | 18/18 | 23/23 ✓ | 7/7 | 132/132 | 33/33 |

No exports in any module. Modinfo exact. Only differing section:
`.note.gnu.build-id` (20 bytes). Two rebuilds byte-identical.

## Contents

| path | |
|---|---|
| [`STATUS.md`](STATUS.md) | closure table |
| [`hardware/topology.md`](hardware/topology.md) | association proof (4 channels), effective vs DT address, power, fitted/shipped classes |
| [`hardware/lens-association.tsv`](hardware/lens-association.tsv) | per camera: AF yes/no, bus, address, module, rail, HAL entry |
| [`dw9800w-class/`](dw9800w-class/) | protocol, register map, park/release sequence |
| [`framework/lens-framework.md`](framework/lens-framework.md) | MTK V4L2 lens framework, ioctls, generic vs vendor parts |
| [`userspace/hal-lens-map.md`](userspace/hal-lens-map.md) | HAL → `libcameracustom.lens.so` → subdev path; OIS table empty |
| [`userspace/vcm-list-decoded.tsv`](userspace/vcm-list-decoded.tsv) | decoded stock lens table |
| [`calibration/boundary.md`](calibration/boundary.md) | AF calibration = module EEPROM (AFInf/AFMacro); no firmware |
| [`yft-vcm-deltas.md`](yft-vcm-deltas.md) | DIRECT_SOURCE_MATCH + packaging/DT/HAL deltas |
| [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) | sha256, size, vermagic, counts, sections, build-ids |
| [`kernel/source-map.tsv`](kernel/source-map.tsv) | module → source files → blob |
| [`parity/<module>/`](parity/) | function/data/abi/relocation/string/section parity |
| [`source/`](source/) | exact ALPS sources (blob-verified `SOURCES.tsv`), plus reference `dw9800w.c` |
| [`scripts/`](scripts/) | rebuild harness, inventory, parity, lens-table decoder |

## Parity operands

* **A**: `vendor_dlkm/lib/modules/{main_vcm,main2_vcm,main3_vcm,main4_vcm,sub_vcm,camera_af_media}.ko`
  (sha256 in `kernel/module-inventory.tsv`).
* **B**: `scripts/sb.sh` isolated `M=` build of pristine ALPS `5e415e059253`
  against exact GKI 12901745, `llvm-strip --strip-debug`.
* `llvm-objcopy --remove-section=.note.gnu.build-id` on A and B → `cmp` equal (all six).

## OIS relationship

AF and OIS are **separate chips on separate buses**: camera 0 AF at `7-000c`
(`main_vcm`), DW9781C OIS at `4-000e`. The HAL's OIS table is empty and all
cameras report `availableOpticalStabilization = [0]`.

## Corrections to earlier notes

* "AF actuators at `0x0a`/`0x0b`/`0x0d`" — those are DT `reg` placeholders;
  the wire address is `0x0C` (set from the HAL table at init).
* "`main2_vcm` = second main / `main4_vcm` = fourth main" — `main2_vcm` serves
  camera 3 (ov64b) and `main4_vcm` serves camera 2 (s5kjn1main2).
* "three fitted VCMs / 3 AF-capable cameras" from DT alone — now proven by
  four channels; front camera is fixed focus.
* "`sub_vcm` / `main3_vcm` possibly used" — platform-only, no DT client and no HAL entry.

## Safety

Offline static analysis of shipped images and existing read-only captures only.
No lens register was accessed and no motor was moved.
