# Device-tree provider/consumer contract

Operand: stock merged base DT + overlay
`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb`, decoded losslessly
(every `clocks` list walked with each provider's `#clock-cells`; 0 undecodable lists).
Full consumer ledger: `evidence/dt/dt-consumers.tsv`.

## Providers registered by the six modules

| DT node | compatible | phandle | registered by | `#clock-cells` | consumer refs |
|---|---|---|---|---:|---:|
| `syscon@10000000` | mediatek,mt6878-topckgen | 0x41 | clk-mt6878 | 1 | 216 |
| `syscon@1000c000` | mediatek,mt6878-apmixedsys | 0x43 | clk-mt6878 | 1 | 10 |
| `syscon@1c012000` | mediatek,mt6878-vlp_cksys | 0x42 | clk-mt6878 | 1 | 2 |
| `syscon@13fa0000` | mediatek,mt6878-mfgpll_pll_ctrl | 0x184 | clk-mt6878 | 1 | 0 in decoded lists |
| `syscon@13fa0c00` | mediatek,mt6878-mfgscpll_pll_ctrl | 0x185 | clk-mt6878 | 1 | 0 in decoded lists |
| `syscon@10001000` | mediatek,mt6878-infra_ao_reg | 0x40 | clk-mt6878-bus | 1 | 25 |
| `syscon@11036000` | mediatek,mt6878-pericfg_ao | 0x3f | clk-mt6878-peri | 1 | 80 |
| `syscon@112b8000` | mediatek,mt6878-ufscfg_ao | 0x3c | clk-mt6878-peri | 1 | 12 |
| `syscon@112bb000` | mediatek,mt6878-ufscfg_pdn | 0x3b | clk-mt6878-peri | 1 | 8 |
| `syscon@11281000` | mediatek,mt6878-imp_iic_wrap_cen_s | 0x3d | clk-mt6878-peri | 1 | 3 |
| `syscon@11c25000` | mediatek,mt6878-imp_iic_wrap_e_s | 0x3a | clk-mt6878-peri | 1 | 11 |
| `syscon@11d73000` | mediatek,mt6878-imp_iic_wrap_es_s | 0x39 | clk-mt6878-peri | 1 | 7 |
| `syscon@11e04000` | mediatek,mt6878-imp_iic_wrap_w_s | 0x38 | clk-mt6878-peri | 1 | 9 |
| `syscon@1cb21000` | mediatek,mt6878-scp | 0x2c | clk-mt6878-vlp | 1 | 4 |

Total: **67 consumer nodes, 387 clock references** into these providers; every consumer is
`okay` (explicit or implicit). *Correction (PRESERVE:STORAGE, 2026-10-09):* this is the static image DT;
in the live DT the bootloader sets `mmc@11230000` (MSDC0/eMMC) to `disabled`, so one of the 67 is
inactive at runtime. Provider and ID conclusions are unaffected. Highest provider IDs referenced: topckgen 282 and pericfg_ao 32 —
both exist only because of patch 0002 (`NR_CLK` 283 / 33). With the unpatched public source,
those three DT references would resolve to an out-of-range ID.

## Consumers by subsystem (DT references only — not proof of runtime use)

| subsystem | nodes |
|---|---|
| storage | `ufshci@112b0000`, `mmc@11230000`, `mmc@11240000` (+ UFS disable-unused helpers) |
| I²C / SPI / UART / PWM | 13 I²C controllers, 8 SPI, 3 UART, `pwm@11008000` |
| display backlight | `disp-pwm0@1100e000`, `disp-pwm1@1100f000` |
| camera | cam-raw-a/b, camsv1/2/5, mraw1, `seninf-top`, `ccu_rproc`, image sensors 0/1/2/4 (mclk) |
| modem | `ccifdriver`, `dpmaif`, `ccci-scp` |
| low power / SCP | `scp-dvfs`, `power-controller@1c001000` (SCPSYS power domains), disable-unused (scp, vlp_cksys) |
| USB / audio / DMA | `usb0@11201000`, `mt6878-afe-pcm@11050000`, `cq-dma`, `dma-controller@11300b00` |
| other | `interconnect`, `mmdvfs`, `vcp@1ea00000` |

Display (mmsys), GPU, APUSYS, video codec, MDP and IOMMU/SMI blocks get their clocks from their
own subsystem clock providers (`clk-mt6878-{mmsys,mdpsys,vcodec,img,cam,ccu,adsp}` — outside this
scope) or via SCPSYS power domains, which themselves reference topckgen muxes.

## Binding vs ABI

ELF-level compatibility (identical CRCs/KCFI) is necessary but not sufficient: a provider
must also probe from its DT node with a valid `reg` syscon/regmap, and every consumer resolves
`clocks` at its own probe (deferred probe if the provider is absent). Neither layer was executed here.
