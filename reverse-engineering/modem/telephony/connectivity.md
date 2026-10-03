# Telephony ↔ connectivity dependency graph

This document consumes the already-closed connectivity results; it does not reopen or rebuild them.

| interaction | modem side | connectivity side | evidence / boundary |
|---|---|---|---|
| VoWiFi/IWLAN | ImsService/RIL/MD IMS, IMS PDN; `ipsec_mon`/`libipsec_ims_shr` | Android Wi-Fi + exact MT6637 Wi-Fi/conninfra kernel | AP-assisted IWLAN properties. SIP/AKA/IPsec policy proprietary |
| tethering offload | CCCI kernel port `ccci_0_200`; RAW_USB + RAW_NETD smem | exact `mddp` + gen4m WFPM | mapped in `../data-path/mddp-integration.md` |
| Wi-Fi ↔ MD state | `mtk_ccci_register_md_state_cb` export | wlan gen4m imports callback | Wi-Fi adjusts/offloads around MD resets |
| MD ↔ CONNSYS smem | `SMEM_USER_RAW_MD_CONSYS` from ccci_util_lib | conninfra `mt6878_emi.c` calls `get_smem_phy_start_addr(MD_SYS1, ...)` | cacheable AP-MD smem region |
| cellular/Wi-Fi coexistence | MD firmware/RF policy | connsys firmware/conninfra | no open AP kernel protocol beyond state/smem; firmware side proprietary |
| AGPS / emergency location | CCCI IPC task 0 `/dev/ccci_ipc_1220_0`, ttyC2, MIPC ttyCMIPC5 | exact GNSS kernel transport; proprietary mnld/AGPS and GNSS FW | mtk_agpsd/mnld static interfaces |
| SIM-toolkit BIP | `/dev/ccci_bip` via MD | Android networking (cellular/Wi-Fi choice by policy) | bip_ap starts only when MD READY |

Kernel exactness on both sides does not make MD or CONNSYS firmware open.
