# MT6878 AFE / machine stack: DONE

| module | functions | data | ABI |
|---|---:|---:|---|
| `snd-soc-mt6878-afe` | 204/204 | 932/932 | exact |
| `mt6878-mt6369` | 15/15 | 322/322 | exact |
| `snd-soc-mtk-common` | 83/83 | 32/32 | exact |
| `mtk-afe-external` | 15/15 | 5/5 | exact |
| `mtk-sp-spk-amp` | 16/16 | 11/11 | exact |
| `clk-mt6878-adsp` | 3/3 | 11/11 | exact |
| `mt6685-audclk` | 5/5 | 6/6 | exact |

The source and ABI are closed. Board-use classification is in
[`playback-routes.md`](playback-routes.md) and
[`capture-routes.md`](capture-routes.md). Exact sources are copied under
[`source/`](source/); reports are under [`parity/`](parity/).

The stock AFE node is `mediatek,mt6878-sound` at `0x11050000`, size `0x9000`,
IRQ 392. It provides DL/UL DMA memifs, IRQs, interconnection matrices, ADDA,
PCM, I2S, TDM/ETDM, SRC, HW gain, hostless and GPIO/clock management. Only the
routes proven in the board DT/HAL configs are labelled active; the rest are
platform capability.
