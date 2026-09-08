# SC851x source-candidate and provenance audit

## Result

`NO_USEFUL_SOURCE` / **no-public-source RED mode**.

No source file matching the GQ5012BF1 `sc851x_charger.ko` was found locally or
publicly. The reconstruction therefore derives from the GPL-v2 stock binary
itself, with SouthChip's public SC8510 product page used only to identify the
silicon's high-level purpose.

## Exact search keys

The search used names that are unusually specific to this translation unit:

- `sc851x_charger_probe`
- `sc851x_charger_shutdown`
- `sc851x read field %d fail: %d`
- `sc,sc851x,audio-en`
- `sc,sc851x,t-v2x2vad-lnc-max-dg`
- `sc,sc851x,v1x-oss-opp-dis`
- `SC SC851X Driver`
- `South Chip Aiden-yu sc851x`
- filenames `sc851x_charger.c`, `sc851x.c`, `sc8510.c`, `sc8517.c`

## Local search

Searched the research tree, exact GKI workspace, local vendor-reference trees,
and other local kernel workspaces for `*sc851*`, `*sc8510*`, and `*sc8517*`.
The only driver artifact was the stock binary and its frozen analysis copy.
No C/header/Kconfig/Makefile source candidate was present.

## Public search

| Candidate | Result | Decision |
|---|---|---|
| SouthChip official SC8510 page: <https://www.southchip.com/en/product/SC8510> | Identifies SC8510 as a dual-cell 10-A forward 2:1 converter / 4-A reverse 1:2 charger with load-switch; no register map or Linux source | **Identity/context only** |
| `winzkh/alps_kernel_mt6989` | MT6989 kernel tree searched by repository tree and likely power/misc/USB locations; no SC851x file | Reject |
| `winzkh/kernel_mainline_mt6989` | MT6989 mainline-derived tree; no SC851x file | Reject |
| public exact-string searches for all keys above | No exact source result | Reject / none found |
| public SouthChip SC8551/SC8561/SC8571 drivers | Different silicon, register map, DT vocabulary, callback topology, and charging-framework integration | **Reject as donor** |
| stock `sc8571_charger.ko` on GQ5012BF1 | Binary sibling from same vendor only in the broad sense; depends on `charger_class` and implements the direct-charge stack that SC851x explicitly lacks | **Reject as donor and framework template** |
| `yft_tiny2c_usb.ko` and `extcon-mtk-usb.ko` | Board USB/thermal-camera/accessory power drivers, unrelated ABI and hardware | Reject; used only as negative uSmart evidence |

Search limitation: public code-index coverage is never mathematically complete.
The bounded conclusion is that no useful source was found in the inspected local
corpus, exact-string web indexes, and candidate MT6989 repositories.

## Mandatory donor decision

There is no untouched source candidate to compile. Per the established workflow,
`kernel/phase4-sc851x-RED.md` is therefore a **no-public-source RED**: the stock
ELF, relocation, register-field, DT, and behavioral decisions were frozen before
source transcription. No candidate was silently adapted and no framework from a
different SouthChip charger was imported.

## Why SC8571/SC8551-family source is unsafe

The similar vendor prefix does not make those drivers valid donors:

1. the stock SC851x module has 30 kernel-only imports, no `charger_class`
   dependency, and no exports;
2. its regmap ends at `0x15` and its fixed table has 50 `reg_field` entries;
3. it parses 35 `sc,sc851x,*` raw encoded properties;
4. its IRQ merely reads/logs `0x0c..0x0e`;
5. it registers no charger device, power supply, regulator, extcon, Type-C or
   notifier object;
6. its only shutdown mutation is clearing `AUDIO_EN` at `0x06[2]`.

Adding a charger framework, ADC interface, charge-enable policy, OTG API, or a
register map from SC8551/SC8571 would be invention, not reconstruction.

## Licensing/provenance

- Stock metadata declares `GPL v2` and South Chip authorship.
- Reconstructed file is SPDX `GPL-2.0`, preserves the stock metadata, and names
  the exact stock SHA-256/build-id as its behavioral source.
- Public product text establishes only device purpose. No third-party driver
  source was copied.
