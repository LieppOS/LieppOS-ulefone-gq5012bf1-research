# Camera module EEPROMs — GQ5012BF1

**Result:** one shipped EEPROM driver, `camera_eeprom_v4l2.ko`, which
rebuilds **byte-identical to stock except the build-id**. The source is
NothingOSS mtkcam `5f75a3b` plus GQ5012BF1/YFT deltas (mtkcam `133c6c1`):
126/126 functions, 141/141 data objects, 38/38 versioned imports, KCFI,
relocations, strings and modinfo all exact, and B1 == B2.

Four module EEPROMs, read-only, no checksums:

| camera | sensor | EEPROM (wire) | `/dev` | stock-parsed content |
|---|---|---|---|---|
| 0 | imx989 | i2c-7 **0x50** | `camera_eeprom0` | LSC, AWB, AF, PDAF (+ QSC via imgsensor) |
| 1 | s5kjn1 front | i2c-4 **0x50** | `camera_eeprom1` | LSC, AWB (+ 4-cell via imgsensor) |
| 2 | s5kjn1main2 | i2c-2 **0x50** | `camera_eeprom2` | LSC, AWB, AF, PDAF (+ 4-cell) |
| 3 | ov64b | i2c-4 **0x53** | `camera_eeprom4` | AF only |

## Contents

| path | |
|---|---|
| [`STATUS.md`](STATUS.md) | closure table |
| [`hardware/`](hardware/) | topology TSV and association proof (sensor-ID-keyed config, imgsensor's own EEPROM reads on the sensor's bus, HAL index, live binding) |
| [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) | stock inventory, including RETRACTED names |
| [`kernel/object-map.tsv`](kernel/object-map.tsv) | 43 linked objects: address ranges, counts, provenance |
| [`kernel/function-inventory.tsv`](kernel/function-inventory.tsv) | 126 functions: address, size, KCFI, callers/callees, strings, data refs, object, status |
| [`kernel/read-write-path.md`](kernel/read-write-path.md) | ioctls, preload/cache, locking, retry, raw read, **write path: READ-ONLY** |
| [`parity/`](parity/) | function / data / ABI / relocation / string / section parity, data inventory, KCFI prototypes |
| [`binary-analysis/`](binary-analysis/) | stock-decoded `g_camCalList`, 37 configs, 37 layout tables |
| [`calibration/`](calibration/) | per-module layouts, parser map, checksum map, AF and OIS boundaries |
| [`userspace/hal-map.md`](userspace/hal-map.md) | HAL libraries, ioctl usage, consumers |
| [`yft-camera-eeprom-deltas.md`](yft-camera-eeprom-deltas.md) | donor vs stock deltas |
| [`source/`](source/) | exact sources (blob-verified `SOURCES.tsv`), donor→stock patches |
| [`scripts/`](scripts/) | build harness, decoders, inventory generator |

## Retractions / corrections

* `rt6421_eeprom.ko`, `dw9828s_eeprom.ko`, `lars2_eeprom.ko` (old CAMERA-EEPROMS
  README) do not exist. There is no file and no string in any of the 471 stock modules.
* "camera_eeprom_v4l2 63/113 functions" was a name-coverage snapshot against
  the unmodified Nothing donor, not parity. Stock has 126 function symbols.
* Master inventory: CAM2 EEPROM was listed as `4-0050` (that is the front
  camera's) and CAM3 as `2-0050, 4-0051`. Correct: CAM2 `2-0050` and CAM3
  `4-0053`. The DT `reg` values 0x51 are placeholders; wire addresses come
  from the stock layout config.
* The reconstruction's local variable names `AFMacro`/`AFInf` in the imx989,
  s5kjn1main2 and ov64b parsers are opposite to the HAL's slot labels. Only
  offset → slot is a binary fact (see `calibration/af-boundary.md`).

## Safety

Offline static analysis of stock images and existing read-only captures.
No EEPROM was read or written; no lens or OIS was driven.
