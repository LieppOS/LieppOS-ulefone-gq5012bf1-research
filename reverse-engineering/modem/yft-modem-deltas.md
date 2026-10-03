# Ulefone / YFT modem deltas

| area | upstream MediaTek behavior | GQ5012BF1 behavior | evidence / reconstructed delta | confidence |
|---|---|---|---|---|
| Linux CCCI source | MTK fae67a9257dc | identical | all 5 CCCI modules exact; 562/562 functions, 346/346 data, exact ABI. Nothing's later MODEM_DUMP_FLAG uevent is absent | exact |
| DPMAIF source | MTK fae67a9257dc | identical | 222/222 + 125/125 exact | exact |
| CCMNI/RPS | MTK 957dac1 tree | identical | 28/28 + 13/13 exact | exact |
| auxiliary MD drivers | mixed MTK component drops | no board source edits | mdpm/cooling/C2K USB exact at 957dac1; power-throttling exact at 6df320423600 | exact |
| modem DT | generic MT6878 bindings | MD1 gen6299, CCIF+DPMAIF v3 cap 0x4, named regulators/IRQs/smem | configuration-only merged DT; no source patch | high |
| SIM | generic dual-UICC support | two physical slots; only SIM1 hot-plug EINT populated; SIM GPIO map 83–88 | board DT + LK `/gpio` map | high |
| RF SKU selection | generic DRDI + MCF + RPC GPIO mechanism | FDD band-detect GPIO99/100; `md_drdi_rf_set_idx=0x0f0f0f0f`; opaque 5.94 MiB DRDI | LK-patched live DT, modem.img | high for interface; unknown profile |
| MCF | MTK SBP/operator packages | 49 OPOTA, 28 NWOTA and SAR Type0/Set1; `custom/` empty | mcf_ota ext4 inventory | exact inventory |
| MD firmware | MTK MOLY source product | Ulefone/YFT build label `TK_MD NLWCG_6878`, 2025-10-22 | CHECK_HEADER; proprietary image, no reconstruction | exact metadata |
| Android product | generic MTK telephony | DSDS, c6m_1rild, MIPC, IMS/VoLTE/WFC/ViLTE enabled, dynamic IMS/data switch | stock build properties | high |
| YFT init node | none | chmod/chown `yft_device/esim_switch` | `init.yft.rc`; does **not** establish eUICC (prior absence scope) | exact |

## Result

No Ulefone/YFT kernel C source change was found in the modem stack. Product differentiation is DT,
LK GPIO/tag data, signed MD/DRDI firmware, MCF/SBP/carrier configuration and Android properties.
The only required source reconstruction is selecting the correct per-component MTK revisions and
removing a later Nothing-only uevent hunk.
