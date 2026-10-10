# Corrections and non-claims

| Stale/unsafe claim | Evidence-backed correction |
|---|---|
| mtk-emi is the physical EMI/MPU/monitoring driver | It is the Linux ICC bandwidth-to-DVFSRC vote driver; separate emi.ko/DRAMC/EMI-MPU/monitor modules own those functions. mtk-emi exports no API and maps no EMI register resource. |
| MT6878 requires a newly authored EMI node table | Its exact stock OF match selects the compiled mt6873_icc descriptor:38 onecell entries; xlate indices are not always internal IDs. |
| MMQoS uses the generic ICC provider registry end-to-end | Private mtk-icc-core handles encoded MMQoS IDs/#mtk-interconnect-cells. Common then uses Linux of_icc_get/icc_set_bw for EMI votes. Both parsers use the same interconnects property with different cell rules. |
| All GPU/NPU/storage routes traverse MMQoS larbs | Those clients have no board ICC property here. EMI table entries alone prove implementation, not device wiring or request execution. |
| All IOMMU port IDs are MMQoS master nodes |112 exact leaf matches,5 larb-only matches and16 outside the compiled MMQoS/SMI mapping. Table/domain bits must remain separate from larb/port bits. |
| MMQoS source has166 physical larbs |166 total records:1 common,9 common ports,24 logical larbs,132 master ports;21 larbs and1 common have explicit board supplier links. Logical5/8 and virtual39 lack physical supplier nodes. |
| Audit load positions67/68/47 are current | Actual hashed normal lists: common61/platform62/EMI51; recovery59/60/50. No load files changed. |
| A source builds, therefore it matches stock | First build's functions/data code matched, but depends metadata differed because provider filenames were wrongly underscore-normalized. Correct source-derived producer basename gives full ELF equality. |
| Trace include errors need C edits or private headers | Only external-tree Kbuild -I$(src) fixes were needed for local define_trace.h includes. No C changes. |
| Newer957dac mmqos C is automatically stock | Candidate blob differs at record_idx; older5e415e is measured stock-exact. No newer compiled acceptance is claimed. |
| Export CRCs can be paired with function relocations positionally | CRC/function order need not agree. Authoritative ledgers read each __crc_name symbol at its own kcrctab offset and licence section; full CRC-slot count is checked. Historical generic positional parser is not used for final values. |
| Source CRC equality certifies all other providers |33 source CRC/licence/CFI boundaries do not certify full provider modules or firmware. Existing classifications/owners stay unchanged. |
| HRT constants prove measured DRAM bandwidth/channel count | Probe queries DRAMC/emi dynamically and can overwrite fallback HRT totals. No frequency, channel count, DDR type or throughput measured offline. |
| DT mmqos-state proves current module parameter state |0xc8d is the initial DT declaration; privileged module parameters can change it later. No parameter read/write or VCP firmware execution was performed. |
| Exact source means fault handling is safe | Existing error/unwind behavior is preserved, not repaired or runtime-qualified. V2 setup proceeds after probe_ret, removal omits some persistent resource cleanup; controlled failure testing remains necessary. |

Source certification and workspace component statuses are separate. No PARTIAL→DONE
promotion, source-owner duplication, optional omission, loader rewrite or hardware tuning.
