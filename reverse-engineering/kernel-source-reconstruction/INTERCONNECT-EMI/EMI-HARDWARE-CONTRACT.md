# What mtk-emi.ko actually owns

**Linux interconnect vote provider**, not the physical EMI controller driver.
Stock and rebuilt code/data are exact; source is unchanged public mtk-emi.c.
Eight function symbols,88 data objects,22 imports,zero exports. No custom char device,
proc/sysfs/debugfs implementation, memory-protection policy, channel/rank query, latency
monitor or performance-counter register access is implemented in this module.

## Platform registration and selected descriptor

Driver name:mediatek-emi-icc. Probe matches **the parent** DVFSRC node, not a child OF
alias invented from the driver name. The parent is /soc/dvfsrc@1c00f000, compatible
mediatek,mt6878-dvfsrc, phandle0x16, #interconnect-cells1. Public DVFSRC MFD setup creates
the platform child; provider->dev points to that parent. This source boundary/ABI is
verified, but the entire DVFSRC provider module and successful child probing are not
newly certified or runtime-proven here.

MT6878 match selects **mt6873_icc**:38 onecell entries decoded from actual stock pointers
and node structures. See EMI-NODES.tsv. A onecell index need not equal internal ID:
index24 dbgif→ID27;25 hrt_ddr_emi→28;26 hrt_mmsys→29;34 wifi→24;35 bt→25;
36 netsys→26;37 hrt_adsp→36. mmsys index8→ddr0; HRT mmsys26→HRT DDR25.
GPU7, VPU16-18, MDLA19-20, UFS21, PCIe22, USB23 and connectivity entries are compiled
capability only unless a board consumer/API path is separately established.

## Vote semantics, not measurements

emi_icc_aggregate sums average kB/s and takes the maximum peak kB/s, storing them in
node software state. Destination endpoint1 forwards peak and average to
mtk_dvfsrc_send_request using PEAK_BW_REQUEST/BW_REQUEST. Endpoint2 forwards summed
average through HRTBW_REQUEST. DVFSRC owns register programming/firmware interactions;
this driver does not directly map or write EMI register resources.

Trace events report requested values (converted by /1000) and selected dbgif consumers,
not measured memory throughput. **emi_icc_get_bw always returns zero** for average/peak;
zero is not a hardware performance reading. Source struct comment mentions buswidth,
but no such field exists in the actual40-byte structure. No bus width is inferred.

Provider uses Linux ICC add/create/link/xlate APIs and sync_state=icc_sync_state. Node
creation failure removes nodes/provider; remove performs that teardown. Link-create
return values are not checked in the source. It has no explicit suspend/resume or
runtime-PM ops; lifecycle is coordinated by clients and generic parent/provider state.
Core ICC debugfs may expose framework state when configured; that belongs to the
framework, not a private mtk-emi monitoring ABI.

## Separate actual owners

- **emi.ko / emi-cen.c** exports mtk_emicen_get_ch_cnt and owns central EMI/channel state.
- **mtk_dramc.ko / dramc.c** owns DDR type and step-frequency queries.
- EMI MPU/monitor/debug modules, where shipped, remain separately owned/unverified.
- **mtk-dvfsrc.ko** performs the actual BW/HRTBW request handling and platform policy.
- **mtk-icc-core.ko** is the separate private MMQoS provider registry.

Source-derived CRC/licence/CFI boundaries agree, but these are not full-provider source
certifications. No active DRAM type, channel/rank count, frequency, bus width, latency,
throughput or memory-protection state was measured or changed. Future runtime proof
must establish probe, vote propagation, zero-vote release, parent power/clock readiness,
suspend/recovery and observability under separately authorized controlled conditions.
