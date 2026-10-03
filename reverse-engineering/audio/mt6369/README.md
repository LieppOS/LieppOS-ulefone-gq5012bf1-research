# MT6369 codec / ACCDET: DONE

## Source closure

| module | functions | data | ABI |
|---|---:|---:|---|
| `snd-soc-mt6369` | 83/83 | 105/105 | exact |
| `mt6369-accdet` | 49/49 | 24/24 | exact |
| `mtk-spmi-pmic` | 10/10 | 39/39 | exact |
| `mt6369-regulator` | 14/14 | 16/16 | exact |
| `mtk-spmi-pmic-adc` | 7/7 | 18/18 | exact |

Sources are in [`source/`](source/) and reports in [`parity/`](parity/).

## Ownership/addressing

MT6369 is `second_pmic@5` on the MediaTek SPMI controller (USID 5), interrupt
5. The SPMI MFD owns the regmap/IRQ controller; its `mediatek,mt6369-sound`
child binds `snd-soc-mt6369`, and its ACCDET child binds `mt6369-accdet`.

## Codec contract

- Playback: MTKAIF RX -> DAC L/R -> HPL/HPR or RCV mux/output.
- Capture: AIN0/AIN1/AIN2 muxes -> PGA L/R -> ADC L/R -> MTKAIF TX.
- Built-in mics use AIN0/AIN2 and MIC_BIAS_0.
- Headset mic uses AIN1 and MIC_BIAS_1.
- DAPM sequencing covers DC compensation, headphone depop, NCP, DAC/ADC,
  receiver and microphone-bias power.
- ALSA controls expose headphone/lineout/receiver gains, input muxes/PGA gains,
  MTKAIF protocol calibration and impedance/offset calibration.
- VANT18 is bypassed for this board's codec path.

[`register-map.md`](register-map.md) summarizes blocks; [`registers.tsv`](registers.tsv)
contains every resolved register macro referenced by the exact codec/ACCDET
sources.

## GQ5012BF1 changes

1. ACCDET adds an FM-antenna GPIO, initializes it and makes it follow jack state.
2. EINT0 analog setup forces `RG_EINT0HIRENB` (internal 500 kΩ selection).
3. Stock is built without the donor's Nothing-specific HL5280 wrapper.
4. The MT6369 PMIC header uses VPA_OC IRQ index 1, matching the stock resource
   table (not the later ALPS index 6).

These deltas are reconstructed, built and byte-exact.
