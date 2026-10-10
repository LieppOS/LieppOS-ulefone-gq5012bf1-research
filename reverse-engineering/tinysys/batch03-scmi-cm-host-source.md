# Batch03 SCMI/CM host source acceptance

`tinysys-scmi.ko` now has full stock acceptance from maintained mailbox-tinysys
commit `e4d3683f3a35bea970f48968320d9ed4330ce7ad`.
`mtk_cm_ipi`, `mtk_cm_mgr` and `mtk_cm_mgr_mt6878` are independently accepted from
power-policy commit `de4756ceb05c882be10bb8096d581d114dc2837a`.
These normal-world host targets use pinned ALPS5e415e0 and genuine provider/header
witnesses; imports, exports, licenses, CRCs, KCFI and every relocation are checked.

Complete ledgers: ../kernel-source-reconstruction/PLATFORM-BATCH-03/MAILBOX-TINYSYS/,
POWER-POLICY/ and evidence/PROVIDER-GRAPH.tsv. Existing MTK-TINYSYS-IPI ownership
and previously accepted components are unchanged. Actual compiled-unit interfaces
and saved mailbox/shared-memory/reserved-memory DT properties are preserved separately
in source/hardware contracts, with contextual nodes explicitly not claimed as binding.

Source-exact send/configuration behavior is not firmware source closure or proof of
SSPM startup/communication. No message, DMA, firmware command or secure-world request
was sent. Retain the existing processor/firmware and runtime test boundaries.
