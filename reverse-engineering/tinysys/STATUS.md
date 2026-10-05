# TinySys messaging status (2026-10-05)

| scope | state | basis |
|---|---|---|
| `mtk_rpmsg_mbox.ko` | **CLOSED (exact)** | byte-identical except build-id; 8/8 fn; ABI/CRC/KCFI exact; B1==B2; lineage pinned |
| `mtk_tinysys_ipi.ko` | **CLOSED (exact)** | byte-identical except build-id; 12/12 fn; ABI/CRC/KCFI exact; B1==B2; lineage pinned |
| provider/consumer boundary | **MAPPED** | 102 edges, 0 CRC mismatches, 9/9 KCFI address-taken edges equal |
| processor enablement | **RESOLVED** | SCP, VCP, GPUEB, MCUPM on TinySys IPI; SAP and ADSP are capability only (no DT node, same in the MTK reference DTS); SSPM uses SCMI; CCU/APU use other transports; CPUEB absent |
| channel map | **COMPLETE (AP side)** | DT/stock-data tables, exact offset algorithms, call-site census |
| `mtk-mbox.ko` | CLOSED earlier (`a33f4e2`), not redone | — |

Not claimed:

- Per-channel payload semantics inside proprietary firmware (SCP/VCP/GPUEB/MCUPM images). These belong to the client drivers and the firmware, not this transport.
- Runtime timing behaviour (e.g. how often POLLING sends spin). Static bounds are documented.

## Workspace classification (2026-10-05)

Recorded in `REVERSE-ENGINEERING-STATUS.md` and `COPY-MANIFEST.tsv` of the organized workspace:

- PARTIAL → DONE: `MTK-RPMSG-MBOX`, `MTK-TINYSYS-IPI`.
- Their old `source/` copies of `mtk-mbox.c` were kept as historical copies (they are exact and belong to MTK-MBOX).
