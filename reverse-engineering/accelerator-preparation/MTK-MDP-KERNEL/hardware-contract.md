# MT6878 MDP / MML hardware contract

Source of truth: the merged device tree
`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb` (22 relevant nodes,
machine-extracted into [dt-topology.tsv](dt-topology.tsv)) plus the reconstructed driver
source. **Nothing here was read from live hardware.**

## 1. The 0x1f000000 island

One contiguous 4 KiB-per-block register island holds the whole data path:

| address | node | block |
|---|---|---|
| `0x1f000000` | `/syscon@1f000000` (`mediatek,mt6878-mdpsys`, `syscon`) · `/soc/mmlsys-config@1f000000` (`mediatek,mt6878-mml`) | MDPSYS clock/config + MMLSYS top |
| `0x1f001000` | `/soc/mml-mutex0` (`mediatek,mdp_mutex0`, `mediatek,mt6878-mml_mutex`) | hardware mutex / path arbitration |
| `0x1f003000` | `/soc/mml-rdma0` | read DMA (source fetch) |
| `0x1f004000` | `/mdp-rdma1`, `/soc/mdp-rdma1` | second read DMA (legacy MDP path) |
| `0x1f005000` | `/soc/mml-hdr0` | HDR |
| `0x1f007000` | `/soc/mml-aal0` | adaptive ambient light / PQ |
| `0x1f009000` | `/soc/mml-rsz0` | resizer |
| `0x1f00a000` | `/mdp-rsz1`, `/soc/mdp-rsz1` | second resizer (legacy MDP path) |
| `0x1f00b000` | `/soc/mml-tdshp0` | sharpness |
| `0x1f00d000` | `/soc/mdp-color0` | colour (legacy MDP path) |
| `0x1f00f000` | `/soc/mml-wrot0` | write rotate (output DMA + rotation) |
| `0x1f010000` | `/mdp-wrot1` | second write rotate (legacy MDP path) |

Every node in the DTB is implicitly `okay` (no `status` property anywhere in this island).

## 2. Clocks — `clk-mt6878-mdpsys.ko`

`/syscon@1f000000` is the clock provider (`#clock-cells = 1`). The reconstructed module
registers exactly 12 gates and the DT indices line up one-for-one with the consumers above:

| id | gate | consumed by |
|---:|---|---|
| 0 | `mdp_mutex0` | `mml-mutex0` (`mutex0`) / `mdp-mutex0` (`MDP_MUTEX0`) |
| 1 | `mdp_apb_bus` | `mmlsys-config` (`apb_bus`), `mdpsys-config` (`MDP_APB_BUS`) |
| 2 | `mdp_smi0` | SMI local arbiter |
| 3 | `mdp_rdma0` | `mml-rdma0` |
| 4 | `mdp_hdr0` | `mml-hdr0` |
| 5 | `mdp_aal0` | `mml-aal0` |
| 6 | `mdp_rsz0` | `mml-rsz0` |
| 7 | `mdp_tdshp0` | `mml-tdshp0` |
| 8 | `mdp_wrot0` | `mml-wrot0` |
| 9 | `mdp_rdma1` | `mdp-rdma1` |
| 10 | `mdp_rsz1` | `mdp-rsz1` |
| 11 | `mdp_wrot1` | `mdp-wrot1` |

`/disable-unused/disable-unused-clk-mdpsys@64` references all 12 and binds them to
`power-controller@1c001000` domain **8** — i.e. the MDPSYS power domain, which is what
gates the whole island. `clk-mt6878-mdpsys` is `depends=clk-common` and is loaded at
position 30 of `modules.load`, well before its consumers.

Second clock input: `/mmdvfs-clk` (`mmdvfs_clk`) on both `/soc/mmlsys-config` (index 2)
and `/mdp` (index 1) — the MMDVFS voltage/frequency handle, owned by `mtk-mmdvfs-v3`.

## 3. Interrupts

Exactly **one** interrupt is declared in the whole island: `/soc/mml-aal0@1f007000` →
GIC **SPI 868** (`0x364`), type `0x4` (level, active high), affinity `0`. No other MML or
MDP block declares an IRQ, which is consistent with completion being signalled through
CMDQ/GCE rather than per-engine interrupt lines.

## 4. Command queue (GCE / CMDQ)

Both drivers are CMDQ clients of `/soc/gce@1e980000`:

| client | mailbox channels | priority field | atomic |
|---|---|---:|---:|
| `/soc/mmlsys-config` | 16, 17, 18, 19 | 400, 500, 400, 500 | 1 |
| `/mdp` | 20, 21 | 0, 0 | 1 |

MML additionally carries the GCE event ids used for direct-link/racing handshakes
(`event-ir-mml-ready` 0x298, `event-ir-mml-stop` 0x29a, `event-ir-disp-ready` 0x299,
`event-racing-pipe0` 0x29b, `event-racing-pipe1` 0x29c, `event-racing-pipe1-next` 0x29d,
`event-apu-start` 0x29e) and the relay/select register offsets
(`dli0-dl-relay` 0x220, `dli1-dl-relay` 0x224, `dlo0-dl-relay` 0x228,
`dlo1-dl-relay` 0x22c, `ready-sel` 0x7fc).

The GCE/CMDQ engine itself (`mtk-cmdq-drv-ext`, `cmdq-platform-mt6878`,
`cmdq_helper_inf`) is **not** owned by this component.

## 5. DMA and IOMMU

All through `/soc/iommu@1e802000` with `dma-ranges` `0x0 0x0 0x0 0x0 0x4 0x0`
(a 34-bit / 16 GB DMA window):

| master | IOMMU port |
|---|---|
| `/soc/mml-rdma0` | `0x40` |
| `/soc/mml-wrot0` | `0x42` |
| `/soc/mmlsys-config` | `0x44` |
| `/mdpsys-config` | `0x41`, `0x43` |

So only the two DMA engines (RDMA in, WROT out) plus the two sys nodes are IOMMU masters;
the PQ blocks operate on the in-island data path. SMI bandwidth/QoS is requested through
`mtk-icc-core` / `mtk-smi-dbg` (`mtk_smi_dbg_dump_for_mml` is one of the consumed exports).

## 6. MML component model

`/soc/mmlsys-config` declares `topology = "mt6878"` and `comp-count = 11`; the driver walks
ids `1 … comp-count-1`, so ids **1–10** are populated (id 0 unused):

| id | name | type | node |
|---:|---|---:|---|
| 1 | `mmlsys` | 1 | `/soc/mmlsys-config@1f000000` |
| 2 | `mutex0` | — | `/soc/mml-mutex0@1f001000` |
| 3 | `rdma0` | — | `/soc/mml-rdma0@1f003000` |
| 4 | `dli0_sel` | 2 | `/soc/mmlsys-config` (sub-component: direct-link in selector) |
| 5 | `hdr0` | — | `/soc/mml-hdr0@1f005000` |
| 6 | `aal0` | — | `/soc/mml-aal0@1f007000` |
| 7 | `rsz0` | — | `/soc/mml-rsz0@1f009000` |
| 8 | `tdshp0` | — | `/soc/mml-tdshp0@1f00b000` |
| 9 | `wrot0_sel` | 2 | `/soc/mmlsys-config` (sub-component: WROT output selector) |
| 10 | `wrot0` | — | `/soc/mml-wrot0@1f00f000` |

`mtk-mml-mt6878.ko` is exactly the topology object for this table
(`mtk-mml-tp-mt6878.o`): it registers the MT6878 IP with `mml_topology_register_ip` and
supplies the path/tile planner the core calls.

Three MML blocks carry a second `mediatek,mml-tuning-*` compatible (`hdr0`, `aal0`,
`tdshp0`) — the hook the vendor PQ service uses to push tuning data. Those algorithms are
proprietary userspace and out of scope.

## 7. Feature-to-implementation map

| feature | implementing objects |
|---|---|
| scaling / resize | `mtk-mml-rsz.o`, `mtk-mml-rsz-fw.o`, `mtk-mml-pq-birsz*.o`, `DpTileScaler.o` |
| rotation + output DMA | `mtk-mml-wrot.o`, `mtk-mml-rrot.o` |
| source fetch / crop | `mtk-mml-rdma.o`, `mtk-mml-pq-rdma.o` |
| colour conversion / PQ | `mtk-mml-color.o`, `mtk-mml-aal.o`, `mtk-mml-hdr.o`, `mtk-mml-tdshp.o`, `mtk-mml-c3d.o`, `mtk-mml-tcc.o`, `mtk-mml-fg*.o` |
| tiling / geometry | `mtk-mml-tile.o`, `tile_core.o`, `tile_mdp_func.o` |
| buffers / dma-buf | `mtk-mml-buf.o` (`dma_buf_attach` + `system_heap`), `mdp_fence.o` |
| scheduling / arbitration | `mtk-mml-core.o`, `mtk-mml-mutex.o`, `mtk-mml-sys.o`, `mtk-mml-merge.o` |
| command queues | `mtk-mml-core.o` (CMDQ pkt build), `cmdq_record.o`, `cmdq_virtual.o`, `cmdq_helper_ext.o` |
| clock / power / runtime PM | `clk-mt6878-mdpsys.o`, `mtk-mml-dpc.o`, `mdp_dpc.o` |
| DVFS / bandwidth | `mtk-mml-sys.o` + `mtk-icc-core`, `mtk-mmdvfs-v3`, `mtk_slbc` |
| error / timeout / dump | `mtk-mml-monitor.o`, `mdp_common.o`, `cmdq_mmp.o`, AEE exports |
| firmware messaging | `mtk-mml-scmi.o` (TinySys SCMI, see firmware-boundary.md) |

## 8. Confirmed vs. unverified

1. **Confirmed active hardware** — nothing. No register was read; no probe observed.
2. **Enabled in device tree** — all 22 nodes above, including both the MML path
   (rdma0/hdr0/aal0/rsz0/tdshp0/wrot0 + mutex + sys) and the legacy MDP path
   (rdma1/rsz1/wrot1/color0 + `/mdp` + `/mdpsys-config`).
3. **Shipped driver capability** — the four modules are in `modules.load` **and**
   `modules.load.recovery` at positions 30 and 71–74 (`cmdq_helper_inf`,
   `mdp_drv_mt6878`, `mtk-mml`, `mtk-mml-mt6878`, immediately before the display stack),
   so first-stage init loads them unconditionally.
4. **Reference-source-only** — `mtk-mml-test.o` and `mtk-mml-mmp.o` are NOT in the shipped
   module (`CONFIG_MTK_MML_DEBUG` unset), yet `/mml-test` and `/mml-ait` nodes exist in the
   DT; secure path (`CMDQ_SECURE_PATH_SUPPORT`) is compiled out of `mdp_drv_mt6878`; the
   other platform variants (mt6983/6985/6886/6897/6989) are compiled out.
5. **UNKNOWN** — whether either driver actually probes, whether the legacy MDP path is ever
   used by this ROM, what the real tile geometry limits are on silicon, and every
   timing/DVFS/thermal behaviour.
