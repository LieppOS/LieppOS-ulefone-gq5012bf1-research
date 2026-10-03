# DPMAIF (modem data HIF) — kernel scope DONE

| module | functions | data | ABI | whole file |
|---|---:|---:|---|---|
| ccci_dpmaif | 222/222 | 125/125 | exact (imports 139/139, modversions 140/140, 20/20 sections) | identical except build-id |

Source: MediaTek `fae67a9257dc` (`drivers/misc/mediatek/eccci/hif`, `ccci_dpmaif-y`), the
same tree as CCCI. `CONFIG_PAGE_POOL=y` adds `-DRX_PAGE_POOL` and `ccci_dpmaif_page_pool.o`.

## GQ5012BF1 configuration (DT `dpmaif@10014000` + source)

| item | value | source |
|---|---|---|
| HW version | `mediatek,dpmaif-ver = 3` → `ccci_dpmaif_drv_v3.c`, `ccci_dpmaif_reg_v3.h` | DT |
| capability | `mediatek,dpmaif-cap = 0x4` = `DPMAIF_CAP_USE_RESV_MEM` only. **LRO and 2-RXQ disabled**, so `real_rxq_num = 1` and `max_pit_seq = 0xFE`. `USE_MAX_BAT` is not set | DT, `dpmaif_init_cap()` |
| RX | **1 RX queue** (rxq0); IRQ GIC 0xee. The second DT IRQ 0x103 is for rxq1 and stays unused. RX runs in a hi-priority tasklet (`dpmaif_rxq_tasklet`); the software GRO helper (`dpmaif_skb_gro_receive`) is only used on the LRO path, which is off | DT + source; live dmesg shows only `dpmaif-rxq0`, budget 16383 |
| BAT | `DPMAIF_DL_BAT_ENTRY_SIZE 16384` (v3), PIT = 2×BAT; normal buffer 1664 B (`DPMAIF_PKT_SIZE 128*13`), fragment buffer 1920 B | `ccci_dpmaif_reg_v3.h`, `ccci_dpmaif_com.h` |
| TX | **4 TX queues × 2048 DRB** (`DPMAIF_TXQ_NUM 4`, `DPMAIF_UL_DRB_ENTRY_SIZE 2048`) | source; live dmesg `dpmaif-txq: 0-3 ... [2048]` |
| HW MTU | `DPMAIF_HW_MTU_SIZE 3*1024+8`; packet align 64 | `ccci_dpmaif_com.h` |
| memory | reserved `ccci-dpmaif-cache-memory` 0x190000 + `ccci-dpmaif-nocache-memory` 0x50000 (no-map) | DT reserved-memory |
| clocks/bus | infra dpmaif / blk / rg-mmw clocks; `icc-mdspd-bw` interconnect + `required-opps` → DVFSRC (`dvfsrc_get_required_opp_peak_bw`) | DT, imports |
| speed/DVFS | `net-spd-ver 5` → `net_speed.c`, `md_spd_dvfs_*`. Throughput tiers drive CPU/DRAM boost and the ccmni RPS mask (`set_ccmni_rps`, `ccmni_set_init_rps`) | DT, imports from ccmni |
| HW reset | `hw-reset-ver 1` (infracfg 0x40) | DT |
| debug | `/proc/dpmaif_debug`; `ccci_set_dpmaif_debug_cb` | source |

## Flow

```
MD DL -> DPMAIF HW (PIT/BAT in resv mem) -> IRQ 0xee -> rxq0 tasklet
      -> ccci_port_recv_skb() (ccci_md_all port_net) -> ccmni_ops.rx_callback -> ccmniN netdev
      -> NAPI/WQ-GRO (ccmni) -> RPS (init.modem.rc 0x0D) -> Linux stack
Linux TX -> ccmniN ndo_start_xmit -> port_net -> ccci_dpmaif txq (0..3 by priority) -> DRB -> MD UL
```

* TX queue priority follows `enum QUEUE_PRIORITY` in `mtk_ccci_common.h`: Q0 normal, Q1 high,
  Q2 medium (QoS VRB), Q3 IMS.
* Exception handling: DPMAIF dumps its registers and rings on MD EE via `ccci_md_force_assert`,
  `mrdump_mini_add_extra_file` and `/proc/ccci_dump`. The HW reset follows the FSM
  stop/start.
* Suspend/resume: the dpmaif syscore and pm ops save/restore the queue state; the MD wake-up
  source is logged per channel.

## Boundary

Linux DPMAIF is complete and exact. The MD-side DPMAIF firmware (L2/PDCP, the HPC/LRO engine)
is part of the signed MD1 image.
