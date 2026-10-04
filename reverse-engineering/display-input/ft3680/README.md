# FocalTech FT3680 main touchscreen

**Status: PARTIAL — static hardware/ABI/behavior reconstruction is advanced, but not byte/source exact.**

This component is the main 1080×2400 touchscreen for GQ5012BF1. VTDR6115 panel work is separate and already DONE.

## Stock artifact identity

| item | value |
|---|---|
| path | `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/focaltech_touch_spi_ft3680.ko` |
| SHA-256 | `6629ec6148ac361a5f0085b8b19efa9d591426679f58262c4998345f41931162` |
| size | 400,936 bytes |
| build ID | `35c87682241ccdef19a9b1b24c3240fac26caa5a` |
| banner | `FocalTech V4.2 20240407` |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| depends | `yft_tpd_gesture,mtk_disp_notify,yft_devinfo` |
| OF aliases | `focaltech,fts` and wildcard form |
| functions / data objects | 166 / 85 |
| imports / exports | 105 / 0 |
| KCFI | none |
| RELA entries | 5,438 |
| embedded source-path strings | none |

Key stock section sizes: `.text` 62,408; `.data` 121,608; `.rodata` 1,052; `.rodata.str1.1` 25,084; `.bss` 154; `.init.text` 160; `.exit.text` 40; `__versions` 6,720 bytes.

## Proven hardware contract

- `/soc/spi3@11013000/focaltech@39`, `compatible="focaltech,fts"`
- MediaTek SPI3, CS0, mode 0, 8 bits, 6 MHz
- IRQ/reset/VDDI = GPIO 7 / GPIO 6 / GPIO 183
- falling-edge, oneshot threaded IRQ; gesture wake uses IRQ-wake
- VDD = fixed 3.3 V `mt6369_vtp`; optional `iovcc` is absent
- ten MT-B slots, coordinates 0..1080 × 0..2400
- display notifier source `Touch_fts`; no functional DT panel phandle
- side-mounted fingerprint means donor FOD paths are absent

See `dt-contract.md` and `hardware-topology.md`.

## Source lineage

Closest public donor: NothingOSS MT6878 FT3519 V4.1 at commit `957dac185efe46cbf6336b0fff9516d84c8cd78f`, path `drivers/input/touchscreen/FT3519/`. No exact V4.2/FT3680 source was found.

The reconstructed publishable source is in:

`/home/armol/androido_dalykai/LieppOS custom ROM/Reverse Engineer - PARTIAL/FT3680-TOUCH/source/`

The private parity harness is `lieppos/disp/ft3680` in the GKI workspace. See `source-delta.md`.

## Current parity

| axis | result |
|---|---|
| function set | **166/166**, zero one-sided |
| size-identical | **126/166** |
| raw byte-identical | **67/166** |
| normalized identical | 69 |
| normalized order-only | 29 |
| import modversions | **105/105 exact** |
| data objects | 85/85 total; 82 shared, **all shared section/size pairs exact** |
| exports | 0/0 |

The import closure includes stock CRCs for `tpgesture_value` (`0x02f3ea4c`) and `yft_spitouchpanel_device_add` (`0xea3d7f0d`). Detailed results and the honest residual boundary are in `parity-report.md`.

## Firmware boundary

`fw_file` is a non-const 118,972-byte `.data` object, SHA-256 `2269a91f6c07421749f48db31651cf59d63c66da7db92ac767e10cc95ff910bf`. It is proprietary and is not redistributed in the research/source bundle. No hardware command was executed. See `firmware-boundary.md`.

## Evidence map

- `dt-contract.md` — exact DT/SPI/GPIO/regulator/IRQ contract
- `hardware-topology.md` — power, notifier, suspend/resume and gesture sequence
- `source-delta.md` — donor provenance and recovered V4.2/Ulefone changes
- `firmware-boundary.md` — opaque blob and safety boundary
- `parity-report.md` — final comparison and PARTIAL decision
- `parity/functions.tsv` — all 166 functions
- `parity/data.tsv` — all named data objects
- `parity/focaltech_touch_spi_ft3680.parity.txt` — raw verifier output
- `workspace/phase4-focaltech-ft3680/` — detailed historical disassembly notes, FHP/FWDBG/flash protocols and source search

## Why this is not DONE

The function set, hardware contract, ABI and principal behavior are closed, but 40 functions remain size-different and 68 functions remain outside normalized-identical/order-only classes. Several are real call/opcode deltas. Without an exact V4.2 source or further instruction-level reconstruction, claiming source-exact completion would be unjustified.
