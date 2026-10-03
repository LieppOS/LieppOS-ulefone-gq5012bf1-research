# CCMNI (modem netdevs) — kernel scope DONE

| module | functions | data | ABI | whole file |
|---|---:|---:|---|---|
| ccmni | 27/27 | 12/12 | exact (exports 5/5 incl. `ccmni_ops`) | identical except build-id |
| rps_perf | 1/1 | 1/1 | exact (`set_rps_map`) | identical except build-id |

Source: `drivers/misc/mediatek/ccmni/` and `drivers/misc/mediatek/rps/`. Both are unchanged
since the 957dac1 baseline: the same tree ids appear at fae67a9257dc and 6df320423600.

## Interfaces

* `eccci_ccmni_ops` (port_net.c): `ccmni_ver = CCMNI_DRV_V0`, **`ccmni_num = 21`**, name
  `ccmni`, `md_ability = MODEM_CAP_DATA_ACK_DVD | MODEM_CAP_CCMNI_MQ`. The modem capability
  bits are added at port init.
* The stock port table creates **20 CCMNI net ports: ccmni0–ccmni7 and ccmni9–ccmni20**.
  ccmni8 (CCCI_CCMNI9 channel) has no port entry. All 20 are on HIF **DPMAIF**,
  `txq 0 / rxq 0`, ack queue `0xF1`.
* netdev setup (`ccmni_dev_init`):
  * pure IP: `ARPHRD_NONE`, `IFF_NOARP`, no broadcast/multicast, no header ops
  * `tx_queue_len 1000`
  * `NETIF_F_VLAN_CHALLENGED | NETIF_F_GRO_FRAGLIST`
  * `NETIF_F_HW_CSUM` only if the MD reports `MODEM_CAP_HWTXCSUM`
  * `NETIF_F_SG` only if `MODEM_CAP_SGIO`
  * GRO via `ENABLE_WQ_GRO` (flush timer 2 ms) when NAPI is not reported
  * `MAX_MTU 3000`
* RPS:
  * driver default on open: `0x0F`, or the DPMAIF-supplied init value
  * stock `init.modem.rc` writes `rps_cpus = 0D` (CPU0, 2, 3) on ccmni0–7 and 9–20 at
    early-init, which matches the port table exactly
  * it also sets `netdev_max_backlog 50000` and `ipfrag_high_thresh 20 MiB`
* Users:
  * RIL `setupDataCall` returns `ccmniN` as the interface name; netd/ConnectivityService
    configure it
  * `ipsec_mon` references `ccmni4` (IMS PDN interface in the stock config)
  * `mddp` filters `ccmni0…31` in its netfilter postrouting hook
  * `mtk_u_ether` (RNDIS) also uses `rps_perf.set_rps_map`

## Boundary

Kernel complete. The mapping of PDN/APN to ccmni index is chosen at runtime by the MD and RIL.
