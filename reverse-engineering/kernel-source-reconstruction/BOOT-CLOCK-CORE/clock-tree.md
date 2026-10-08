# MT6878 clock hierarchy as compiled into the GQ5012BF1 stock modules

Entry counts are measured from the **stock** data objects (entry stride from relocation
pattern; verified identical in the rebuild). Source names are from the reconstructed C.

## Functional split

| module | provider role | compatible strings it binds | content |
|---|---|---|---|
| clk-common | framework library, no own DT node | — | PLL ops (`clk-pll.c`, incl. HW-voter/fhctl hooks), mux ops (clr/set/upd, gate, HWV, IPI-synchronised), gate ops (setclr, setclr_inv, no_setclr, HWV), cpumux, apmixed helpers, reset controller, `mtk_clk_simple_probe`, clk registration/`mtk_alloc_clk_data`, clkchk/pd-chk framework (PM notifier, `/proc` reporting, AEE warnings), fmeter dispatch (`fmeter_set_ops`), clkdbg core; 64 exported functions + 23 exported ops objects |
| clk-mt6878 | core SoC clock generators | `mt6878-apmixedsys`, `mt6878-topckgen`, `mt6878-vlp_cksys`, `mt6878-mfgpll_pll_ctrl`, `mt6878-mfgscpll_pll_ctrl` | 10 apmixed PLLs, 1 + 1 GPU PLLs, 189 top fixed factors, 72 top muxes (incl. restored `top_disp_pwm_sel`), 15 top composites, 7 top gates, 20 VLP factors, 18 VLP muxes; export `mt6878_pll_force_off` |
| clk-mt6878-bus | infra bus gates | `mt6878-infra_ao_reg` | 13 gates (`ifrao_clks`) |
| clk-mt6878-peri | peripheral gates | `mt6878-pericfg_ao`, `mt6878-ufscfg_ao`, `mt6878-ufscfg_pdn`, `mt6878-imp_iic_wrap_{cen_s,e_s,es_s,w_s}` | 33 PERICFG_AO (UART×3, PWM×6, **DISP_PWM×2**, SPI×8, DMA, USB frmcnt, MSDC0/1, audio), 6 UFS-AO, 4 UFS-PDN, 2+6+4+5 I2C-wrapper gates |
| clk-mt6878-vlp | SCP-side low-power gates | `mt6878-scp` | 4 gates (`scp_clks`) — despite the module name, the VLP *mux/PLL* clocks live in clk-mt6878 |
| clk-fmeter-mt6878 | frequency-meter tables | — (registers via `fmeter_set_ops`) | MT6878 fmeter clock-ID tables and register access for topckgen/apmixed/VLP measurement |

Mux register model (from the restored entry): `CLK_CFG_n` with `_SET`/`_CLR` shadows; field
`lsb/width`; optional power-down bit (`pdn`); update bit in `CLK_CFG_UPDATE{,1,2}`. Muxes with
`mtk_hwv_mux_ops` are hardware-voter controlled (disp0, mminfra, venc); `mtk_ipi_mux_ops` muxes
(vdec, img1, ipe, cam) synchronise through an IPI.

## Display PWM path (the GQ5012BF1 delta)

```
top_tck_26m_mx9_ck | univpll_d6_d4 | osc_d2 | osc_d4 | osc_d16 | univpll_d5_d4 | mainpll_d4_d4
                      └─ top_disp_pwm_sel  (topckgen ID 282; CLK_CFG_7[26:24], pdn bit 31, UPDATE1 bit 0)
                           └─ top_disp_pwm_ck (factor 1/1, ID 227)
                                ├─ peraop_disp_pwm0 (pericfg_ao ID 31, gate bit 10) → disp-pwm0@1100e000 "main"
                                └─ peraop_disp_pwm1 (pericfg_ao ID 32, gate bit 11) → disp-pwm1@1100f000 "main"
```

Both disp-pwm nodes additionally request `<&topckgen 282>` ("mm") and `<&topckgen 184>` ("pwm_src").

## Not inferred

Only names, IDs, register fields and parent lists encoded in the shipped tables are stated.
Actual PLL rates, which parent each mux selects at boot, which gates are on, and HW-voter state
are runtime facts not established offline.
