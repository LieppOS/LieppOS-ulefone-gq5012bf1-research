# Static radio feature map (GQ5012BF1)

Classification is deliberately conservative: **platform capability** means code/config exists;
**SKU enabled** means the stock GQ5012BF1 configuration enables it; **runtime proven** would require
an existing authorized trace (none was collected in this offline pass).

| feature | evidence | conclusion |
|---|---|---|
| modem | DT MD1 gen 6299, MT6878_S00 CHECK_HEADER | one integrated MT6878 MD1; SKU proven |
| RAT family | CHECK_HEADER `image_type=14`; build `TK_MD NLWCG_6878`; `ro.vendor.mtk_protocol1_rat_config=N/C/Lf/Lt/W/G` | NR + CDMA2000 + LTE FDD/TDD + WCDMA + GSM compiled/configured; no TD-SCDMA |
| NR | NLWCG firmware; default network 33; PS1 RAT includes N | SKU enabled. **NSA versus SA and exact NR bands are not proven** by readable config |
| LTE | `ro.vendor.mtk_lte_support=1`; Lf/Lt in PS1; DPMAIF | SKU enabled |
| WCDMA/GSM | W/G in image/config | SKU enabled |
| CDMA2000 | C in image/config; `ro.vendor.mtk_c2k_support=1`, `mtk_eccci_c2k=1`, C2K USB debug functions | software capability enabled; operator/network use unproven |
| dual SIM | `sim.count=2`, three DSDS properties, two AIDL slot instances | **DSDS proven**, not DSDA |
| VoLTE | IMS/VoLTE properties and ImsService/IRadioIms | SKU enabled; registration/call not tested |
| VoWiFi | WFC properties, AP-assisted IWLAN, ipsec helper | SKU enabled; registration not tested |
| ViLTE/ViWiFi | ViLTE properties, vtservice, VT HAL | SKU enabled |
| SMS over IMS | IMS stack and IRadioIms | path present; carrier/runtime policy unknown |
| carrier aggregation | NR/LTE modem generation and opaque MCF/DRDI likely support it | platform capability only; combinations/bands unknown |
| LTE/NR bands | 5.94 MiB `md1drdi`, MCF/SBP, two FDD band-detect straps GPIO99/100 | SKU selects an RF set, but payload is opaque and strap levels were not captured: **do not publish a band list** |
| emergency calls | ECC XML (generic + OP01/02/09/12/17/18/20/236), RIL emergency path | configured; carrier/runtime behavior unknown |
| UICC secure element | `mtk_uicc_clf=1`, se1/se2 instances | two removable UICC CLF paths |
| eSIM/eUICC | prior exhaustive absence scope | absent |

The generic Dimensity 7400/MT6878 marketing band set is not evidence for this board. Exact band,
CA and NSA/SA claims require a decoded MCF/DRDI/NVRAM profile or a read-only authorized modem
capability trace; see `../runtime-test-plan.md`.
