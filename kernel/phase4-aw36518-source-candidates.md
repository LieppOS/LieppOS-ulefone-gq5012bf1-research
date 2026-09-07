# AW36518 source candidates

## Classification

**PARTIAL_PUBLIC_SOURCE_MATCH**

No local tree contains the GQ5012BF1 AW36518 source. The closest public source is a MediaTek V4L2/flashlight-core AW36518 driver from Motorola; it establishes the architectural base and the published register/current conversions, but it is not the stock revision and is not used as an electrical oracle where the binary differs.

## Search scope

Searched local trees and history under `kernel-research/nothing-mt6878`, all `kernel-research`, this research repository, exact-GKI workspace, and `~/kernel-work/vendor-reference` for `aw36518`, `AW36518`, `aw36515`, `aw36518_v2`, Awinic and flashlight function names. Nothing's MT6878 tree has the matching MediaTek flashlight-core/V4L2 framework and `lm3644.c` structural ancestor, but no AW36518 source. Public searches included exact function names, module metadata and unique strings.

## Accepted structural donor

| field | value |
|---|---|
| repository | `https://github.com/MotorolaMobilityLLC/kernel-mtk` |
| commit | `ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de` |
| date | 2023-03-01 |
| path | `drivers/misc/mediatek/flashlight/v4l2/aw36518.c` |
| kernel | Linux 5.10.149 tree |
| source hash | recorded in `public-source/`; file frozen verbatim in donor build |
| role | structural donor only |

The repository's five path revisions were frozen (`f10286b9`, `1f94e13e`, `c9711bca`, `a543eaa6`, `ecf0e8f4`). The last three carry the 40 ms step / 600 ms maximum timeout family. The stock binary proves the same fundamental one-channel register interface and exact V4L2/MediaTek operation architecture, but it also proves substantial deltas.

### Confirmed overlap

* one LED channel;
* V4L2 flash subdevice plus MediaTek `flashlight_operations` bridge;
* register addresses 0x01, 0x03, 0x05, 0x08, 0x0a and 0x0b;
* 2.94 mA + 5.87 mA/LSB flash conversion and 0.75 mA + 1.51 mA/LSB torch conversion (values are in uA in V4L2 controls);
* 40 ms timeout quantum in the accepted revision;
* mode/enable, brightness, strobe, ioctl, cooling, DT, probe/remove and PM structure;
* `Alec <like@awinic.com>` / GPL / AW36518 metadata family.

### Why it is not a direct match

Mandatory RED proves: stock 23 functions vs donor 22; only 20 shared names; stock adds hardware init, GPIO/HWEN, register sysfs and YFT board-selection paths; donor adds a shutdown function and a low-power-throttling call absent from stock. Stock uses four cooling levels `{150000,100000,50000,25000}` instead of donor's five `{100000,80000,60000,40000,20000}`. Many shared function sizes differ. The stock logging prefix/version strings and DT parser differ. See `RED.md`.

## Other candidates

* **NothingOSS MT6878 `v4l2/lm3644.c`** — rejected as direct donor; it is the MediaTek structural ancestor and documents the framework ABI, but targets TI LM3644, two channels, and a different register/electrical contract.
* **Stock `aw36518_v2.ko`** — accepted as a binary sibling oracle, not public source. It has the same 23 symbol names/sizes after prefix normalization except `parse_dt`; normalized string multiset is identical; its only material framework delta is omission of the YFT board hook. See `family-comparison.md`.
* **Stock `aw36515.ko`** — rejected as direct donor; dual-channel and materially different function/register behavior despite sharing the same MediaTek V4L2 bridge ancestry.
* **Awinic public datasheet/product pages** — corroborative only. They may establish product-family electrical units, but cannot override stock literal behavior.
