# Kernel audio dependency graph

Load-order numbers are from stock `modules.load`.

```text
platform ramdisk
 53 mtk-spmi-pmic
 54 mtk-spmi-pmic-adc
 55 mt6369-regulator
 72 clk-mt6878-adsp
 75 audio_ipi
 76 adsp
 95 mt6685-audclk
104 mtk-vow
105 mtk-sp-spk-amp ───────────────┐
                                  │ calls exported probe/remove
vendor_dlkm                       ▼
 51 snd-soc-tfa98xx (dormant)   aw883xx_driver (AW88394 library module)
 69 mtk-soc-offload-common
 70 mtk-scp-vow
 71 mtk-scp-ultra
 72 snd-soc-mt6369
 73 mtk-afe-external
 74 snd-soc-audiodsp-common
 75 snd-soc-mtk-common
 76 snd-soc-mtk-scp-ultra
 77 snd-soc-mt6878-afe
 78 mtk-scp-audiocommon
 79 mt6878-mt6369
133 mt6369-accdet
```

ASoC binding:

```text
mt6878-mt6369 machine card
  -> snd-soc-mt6878-afe platform/CPU DAIs
  -> snd-soc-mt6369 codec DAIs
  -> mtk-sp-spk-amp external-codec BE
       -> aw883xx_driver exported probe/remove
  -> audiodsp/offload/SCP/VOW/ultrasound front ends where configured
```

All modules listed in [`module-inventory.tsv`](module-inventory.tsv) are ABI
exact against stock. `snd-soc-tfa98xx` is loaded compatibility code but no TFA
node is fitted and speaker type 5 selects AW883XX.
