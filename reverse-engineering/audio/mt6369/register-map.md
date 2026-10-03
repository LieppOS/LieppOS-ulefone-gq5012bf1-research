# MT6369 audio register map

The complete resolved list is [`registers.tsv`](registers.tsv) (397 distinct
source/macro rows). It is generated from the exact header and every register
reference in `mt6369.c` and `mt6369-accdet.c`.

| range / named block | function |
|---|---|
| `AUD_TOP_*` | audio clocks, reset and top interrupt mask/status |
| `AFE_*`, `AFUNC_AUD_*` | MTKAIF digital interface, sine generator, NLE and monitor/status |
| `AFE_VOW_*` | VOW front end, VAD, timing and high-pass filtering |
| `AUDNCP_CLKDIV_*` | negative charge-pump clocks for headphone analog path |
| `AUDLDO_NVREG_*` | codec analog rail sequencing |
| `AUDDEC_ANA_CON*` around `0x2588–0x25a0` | headphone/receiver/DAC output analog controls, depop and DC trim |
| `ZCD_CON*` | zero-cross/gain controls for HP/lineout/receiver |
| `AUDENC_ANA_CON*` around `0x2500–0x2527` | AIN/PGA/ADC/microphone-bias and EINT analog controls |
| `ACCDET_CON*`, `0x2680+` | jack comparator/FSM/PWM, AUXADC switching, IRQ and debounce |
| AUXADC request/data | headset key voltage and impedance/offset calibration |

Key board-facing controls:

- `RG_AUDMICBIAS0*`: 1.9 V built-in microphone bias.
- `RG_AUDMICBIAS1VREF`: headset microphone bias; DT code 7.
- `RG_EINT0CONFIGACCDET` / `RG_EINT0HIRENB`: EINT0 jack detector and YFT
  internal-resistor selection.
- `AUDACCDETAUXADCSWCTRL_SW`: route ACCDET voltage into AUXADC.
- `ACCDET_DEBOUNCE*`: per-state plug/button debounce values from DT.
- headphone/receiver ZCD and analog controls: click-safe gain and power
  sequencing.

Raw register programming is unsafe on hardware and was not performed.
