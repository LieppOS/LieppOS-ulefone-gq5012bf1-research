# GPU-AI-AUX-KERNEL-INTERFACES — PARTIAL preparation

**Purpose:** GPU/AI auxiliary processors normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** REGISTER PARTIAL. GPUEB and VCP host/status clients were only referenced by MTK-TINYSYS-IPI. Its explicit DONE scope proves the transport module, not these client implementations. SCP and ADSP host code are already DONE elsewhere and are not duplicated.

**Entry point:** [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md). Canonical research: `reverse-engineering/accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/`. Workspace pack: `Reverse Engineer - PARTIAL/GPU-AI-AUX-KERNEL-INTERFACES/`.

**Exclusive primary kernel modules (3):** `gpueb.ko`, `vcp_status.ko`, `vcp.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.

No module rebuilt, hardware command executed or parity result created by this preparation. Published proof rows are preserved and labeled by axis; the component starts PARTIAL, never DONE.
