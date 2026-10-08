# Dependencies and singleton ownership — GPU-AI-AUX-KERNEL-INTERFACES

**Prerequisites:** MTK-MBOX; MTK-RPMSG-MBOX; MTK-TINYSYS-IPI; exact GKI; preserve SCP/ADSP DONE owners.

**Owned modules:** `gpueb.ko`, `vcp_status.ko`, `vcp.ko`.

MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.

[Master dependency edges](../dependency-edges.tsv) resolve stock imports by symbol and CRC; each row carries consumer/provider/owner. The load order and legacy modinfo dependencies are recorded separately in stock-modules.tsv. `modules.dep` can be transitive and legacy modinfo can name obsolete provider identities; neither overrides the actual export/CRC graph.

Raw direct modinfo dependency sets: `mtk_tinysys_ipi,mtk-mbox; vcp_status,clk-common,mtk-smi-dbg,mtk_tinysys_ipi,irq-dbg,device-apc-common,mtk-mbox,system_heap,mrdump,aee_aed`. These names are not a list of new targets. UNKNOWN provider/type provenance must be resolved against existing stock export/KMI ledgers, not fabricated. Preserve generic platform providers and explicitly closed modules.

For cycles, freeze mutually shared headers/provider ABI, use unchanged stock provider operands during initial isolation, then verify the assembled reconstructed graph; copied stock symvers is an oracle, not source/type proof.
