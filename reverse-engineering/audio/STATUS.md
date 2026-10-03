# Audio RE status

## Phase-1 audit

| component | prior state | remaining gap at start | donor | offline-solvable | result |
|---|---|---|---|---|---|
| MT6369-AUDIO-CODEC | PARTIAL | source/parity, analog routing, ACCDET | exact MTK/Nothing MT6878 history | yes | **DONE** |
| MT6878 AFE/machine | embedded in other scopes | source/parity and active route classification | exact MTK ALPS history | yes | **DONE**, new named scope |
| AW883XX-SPEAKER-AMP | DONE | tuning/physical boundary only | Awinic v1.6 + reconstructed v1.7.1 delta | kernel yes | remains **DONE**; fitted PID is AW88394 |
| AUDIO-DSP | PARTIAL | distinguish open transport from firmware/algorithms | exact MTK ALPS source | transport yes, algorithms no | kernel scope **DONE**; parent proprietary scope remains PARTIAL |
| MICROPHONES | PARTIAL | physical/live use-case confirmation | exact codec/AFE now available | electrical/software yes | remains PARTIAL for its named physical/runtime scope |
| FM-RADIO-HEADSET | PARTIAL | exact jack/antenna/FM closure | exact ACCDET source; FM core separate | jack yes | headset/ACCDET closed; FM receiver scope remains PARTIAL |
| proprietary Audio HAL | undocumented | service, version, policy, dependencies | no public exact source | interface mapping only | PARTIAL boundary |

## Exact kernel closure

[`kernel/module-inventory.tsv`](kernel/module-inventory.tsv) is authoritative.
All 22 rows have exact imports, exports, modversions, export CRCs, modinfo,
vermagic, section sizes, functions and data objects.

Aggregate: **1,463/1,463 functions and 1,996/1,996 data objects exact** across
those 22 modules. AW88394 is separate: 235/236 byte-exact, 236/236 code/reloc/
call/string equivalent, ABI exact.

Important build configuration recovered from stock:

- `CONFIG_SND_SOC_RT5512` off;
- `CONFIG_AUDIO_SWITCH_HL5280` off;
- `CONFIG_MTK_TINYSYS_SCP_DEBUG_SUPPORT` off;
- MT6369 `VPA_OC` IRQ enum index is 1;
- user build, not debug build, for VOW code generation.

## Boundaries

### Reconstructable

- MT6878 AFE, clocks, memifs, DAI and interconnect code.
- MT6369 codec/ACCDET and PMIC support.
- MTK speaker dispatcher and AW88394 kernel module.
- ADSP/SCP/VOW/ultrasound Linux transports and ALSA PCMs.
- Device tree, mixer XML and audio policy XML contracts.

### Proprietary, mapped but not source-closed

- MediaTek V3 primary HAL (`audio.primary.mediatek.so`).
- MediaTek speech, Aurisys, DMNR/AEC/NS algorithms.
- Executable ADSP/SCP firmware and modem speech firmware.
- Awinic SKTune effect/algorithm implementation.
- AW88394 acoustic ACF and per-device calibration values.

### Physical/runtime only

- Loudspeaker grille/mechanical location.
- Acoustic port/package confirmation for microphones.
- Real impedance, excursion, thermal calibration and on-device route switching.
