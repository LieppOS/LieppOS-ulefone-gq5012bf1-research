# MDDP <-> CCCI/DPMAIF/CCMNI integration

`mddp.ko` (132/132 functions, 87/87 data, ABI exact) was closed in the connectivity pass at the
957dac1 tree (`3440c2c1…`). It is re-verified here (byte-identical except build-id) against
the new CCCI header, so the `mtk_ccci_common.h` update did not disturb it. Note: stock mddp is
**older** than the CCCI revision. MediaTek's fae67a9257dc mddp tree (`b8bd0037…`) is **not**
what shipped. Stock ships per-component MTK drops.

## What mddp uses from the modem stack (stock import list)

| import (provider ccci_md_all) | use |
|---|---|
| `mtk_ccci_request_port("ccci_0_200")`, `mtk_ccci_open_port`, `mtk_ccci_send_data`, `mtk_ccci_read_data`, `mtk_ccci_release_port` | kernel-only CCCI port **ccci_0_200** (CCCI_MD_DIRC_TX/RX = channels 201/200, CCIF): MDDP/WFPM IPC (enable/deactivate MD fast path, MD notify, suspend/resume tags) |
| `get_smem_start_addr(SMEM_USER_RAW_USB)` | IPC buffer in non-cache smem (`mddp_ipc.c`) |
| `get_smem_start_addr(SMEM_USER_RAW_NETD)` | offload traffic counters (`mddp_usage.c`), also exposed as `/dev/ccci_raw_netd` |
| `exec_ccci_kern_func(ID_GET_MD_STATE)` | gate filter/usage on MD READY |

mddp does **not** import anything from ccci_dpmaif or ccmni. It sees the CCMNI netdevs only by
name (`mddp_f_dev.c` ccmni0…ccmni31) through its `NF_INET_POST_ROUTING` hooks (v4/v6).

## Wi-Fi side (connectivity, already exact)

`wlan_drv_gen4m_6878` imports `mddp_drv_attach` / `mddp_drv_detach` from mddp and
`mtk_ccci_register_md_state_cb` from ccci_md_all.

## Data plane when offload is active (Wi-Fi tethering / WFPM)

```
Wi-Fi client <-> gen4m (WFPM) <-> MD fast path (MD firmware) <-> cellular
            control: netd/tethering -> mddp (/dev/mddp) -> ccci_0_200 -> MD
            stats  : MD -> SMEM RAW_NETD -> mddp_usage -> netd
```

No packet crosses DPMAIF/CCMNI on the offloaded path. Non-offloaded traffic uses
`ccmniN` ↔ DPMAIF as in `ccmni.md`.
