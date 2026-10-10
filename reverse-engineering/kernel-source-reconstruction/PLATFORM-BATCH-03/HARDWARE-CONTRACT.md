# GQ5012BF1 Batch03 hardware and runtime boundaries

Authoritative detailed ledgers: evidence/hardware/*.tsv, SAVED-RUNTIME-BOUNDARIES.json,
SOURCE-TO-HARDWARE-CONTRACTS.json (34 modules / 68 compiled C units), and PROVIDER-GRAPH.tsv.
All source calls/compatibles were extracted from actually compiled units, not a donor
search result. Every selected identity has a saved-runtime record and source contract.

## Evidence levels

- **PROVEN_RUNTIME:** only historical capture observations (e.g. a load or actual saved
  driver/module link). This work performed no runtime measurements. No selected module
  gains a new proven hardware binding or firmware transaction from compilation.
- **ENABLED_IN_STOCK_DT:** 21 stock-binary alias/node matches in the saved DT. Parent
  status was considered. This proves configuration, not successful probing.
- **STOCK_BINARY_IMPLEMENTATION:** complete source/instruction/data/ABI correspondence
  for 33 A targets; ADC's instruction implementation matches but full metadata remains C.
- **PUBLIC_SOURCE_ONLY:** declarations/type graphs for nonclosed external producers;
  candidate source interfaces not independently matched to executing hardware.
- **UNKNOWN:** actual register values, interrupts delivered, timing, temperature accuracy,
  safe voltage/current limits, firmware startup, secure-service behavior and runtime provider selection.

The saved live-stock capture is from 2026-08-31, not a new ADB interaction.
`devicetree.tar` SHA256 `c30d118138ea8df045a245b21afc888408b89ea090f6781f97c8b815211c595d`.
98 configured contextual platform nodes (including unselected clients) and 49 exact
stock load-list occurrences are retained separately from the 21 alias matches.

## Secure RNG, diagnostics, watchdog, tinysys

`sec-rng.ko` matches `/hwrng`, `arm,sec-rng`, enabled. Its exact normal-world source
interface does not reconstruct or invoke secure RNG. AEE/mrdump/hangdet modules are
whole normal-world host implementations, not evidence that crash capture was triggered.
`mtk_wdt.ko` matches `/soc/watchdog@1c00a000`: saved reg address `0x1c00a000`, size `0x100`,
MT6878/MT6589-compatible syscon/simple-mfd configuration. No reset was triggered.
`tinysys-scmi.ko` and `mtk_cm_ipi.ko` preserve SCMI/IPI host APIs. Mailbox/shared-memory
and reserved-memory configuration is retained in configured-node properties; an enabled
node or exported send API does not prove SSPM started or accepted a message.

## Thermal and cooling

- `thermal_interface.ko`: `/therm-intf@114000`, `mediatek,therm_intf`, saved `0x114000/0x400`.
- `board_temp.ko`: four MT6685 TIA-NTC configured registers: `0x1c013120`, `0x1c013130`,
  `0x1c01312c`, `0x1c013128`, each 4 bytes; each has zero thermal-sensor arguments.
- `pmic_temp.ko`: `/mt6363-temp` and `/mt6369-temp`, nvmem cells and four named IIO
  channels each (`ts1`..`ts4`, channel arguments 5..8). Node naming is not a new
  assertion of the underlying auxiliary-ADC silicon variant.
- `soc_temp_lvts.ko`: `/soc/lvts@10315000`, regions `0x10315000/0x1000`,
  `0x10316000/0x1000`, `0x13ff0000/0x1000`; decoded GIC interrupt specifiers
  `[0,218,4,0]`, `[0,219,4,0]`, `[0,277,4,0]`; four saved nvmem-cell references.
- `vtskin_temp.ko`: `/vtskin`, `mediatek,mt6878-virtual-tskin`, one sensor argument.
- `charger_cooling.ko`: `/charger-cooler`, `mediatek,mt6375-charger-cooler`, two cooling
  arguments. The source-derived cooling policy and warning locations now match stock.
  Actual charger producer boundaries are source-witnessed but whole producer modules
  are not certified by these declarations. No charging/thermal policy was applied.
- `backlight_cooling.ko`: `/backlight-cooler`, `mediatek,backlight-cooler`, two cooling
  arguments; matching host behavior does not certify measured panel luminance.
- `thermal-generic-adc.ko`: genuine common source with exact instructions/data/imports/
  relocations; no stock-compatible enabled alias match is invented. Its 21 split-BTF
  reference-byte mismatch remains C, documented in BLOCKERS.tsv.

Thermal conversion, calibration and operating temperatures were not measured. Saved
calibration/nvmem references are configuration only; no firmware or calibration changed.

## Power policy, CPU and clocks

CPU DVFS/sugov/core_ctl/QoS/PBM/PPB/CM/DCM source and exports are matched wholly for
selected A targets. `/pbm`, `mediatek,pbm`, is enabled. Full clock/power/regulator,
OPP/DCM/CM configuration is preserved in configured-node properties and genuine source
calls in SOURCE-TO-HARDWARE-CONTRACTS.json. Those APIs do not establish active CPU
transitions, firmware voltage programming, current limits or bandwidth/QoS effects.
The PPB callback removal is a real normal-world stock source difference, not a claim
of reconstructed PMIC firmware. `clkbuf.ko` source interfaces match; `/clkbuf-ctrl`
configuration is contextual, not newly proven binding.

## PMIC/MFD/ADC

`mtk-spmi-pmic.ko` matches the MT6363 `pmic@4`, MT6369 `second_pmic@5` and MT6319
`mt6319@6` children beneath `/soc/spmi@1cc04000`. Saved reg slave-address cells are
`[4,0]`, `[5,0]`, `[6,0]`; first two IRQ arguments are 4 and 5 to the SPMI parent.
Do not decode these child addresses as CPU MMIO addresses.

`mtk-spmi-pmic-adc.ko` matches MT6363 auxiliary ADC and the `mt6369-auxadc` node whose
actual compatible is **`mediatek,mt6368-auxadc`**. Preserve that distinction; node names
must not override the stock compatible/type lineage.

`mt6375.ko` matches `/soc/i2c@11280000/mt6375@34`, I2C address `0x34`; saved interrupt
provider is `/soc/pinctrl`, arguments `[15,8]`. Recovered IRQ acknowledgement source
is stock-exact, but no interrupt or charger interaction was generated.
`mt6685-core.ko` matches the enabled MT6685 MFD child, saved reg cells `[9,0]`.
The completed parent/MFD interfaces make charger/Type-C child preservation a coherent
next batch, not an automatic certification of those children.

## DMA/IOMMU, dependencies, firmware

No new selected DMA/IOMMU relationship is inferred from a generic DMA API or address.
Actual configured properties and compiled calls are preserved; UNKNOWN remains where
source/capture does not establish a relationship. 1434 import / 320 export graph rows
include provider identity, CRC/license, KCFI requirement, source lineage, and saved load
relationships. 89 noncore API boundaries agree; 31 external slots are freshly generated
from genuine source declarations/definitions. Existing accepted components are unchanged.
Multiple stock matching providers remain runtime-ambiguous where recorded by the audit.

Secure-world RNG/SiP execution, SSPM/SCMI/IPI firmware, crash firmware, physical ADC
readout, temperature calibration, DVFS/PMIC voltage/current behavior and actual hardware
binding are outside offline closure. No new firmware, phone/register transaction,
experimental module loading, calibration change or push occurred.
