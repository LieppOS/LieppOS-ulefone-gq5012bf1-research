# GPU-AI-AUX-KERNEL-INTERFACES — DONE

Status: DONE — all three owned modules rebuild from unmodified public ALPS source
(`5e415e059253`) and match stock byte-for-byte except their 20-byte GNU build IDs.
Start at [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) and [SOURCE.md](SOURCE.md).

- **Subsystem:** Accelerators / GPU/AI auxiliary processors
- **Hardware identity:** GPUEB and VCP are the unfinished GPU/video host clients. SCP sensor/audio/CHRE host is already reconstructed; ADSP source is closed but the board has no instantiated ADSP DT node. MCUPM/SSPM are CPU/system-power dependencies, not silently bundled as GPU firmware projects. SAP/CPUEB capability names are not proof of instantiated processors.
- **Stock artifact:** `gpueb.ko`, `vcp_status.ko`, `vcp.ko`
- **Interfaces:** GPUEB shared-memory/mailbox/11 IPI channel setup and GPU-frequency consumer callbacks; VCP/status readiness, feature reference counts, reserved/shared memory, IPI/mailboxes, loader/boot, suspend, reset and recovery. SCP/ADSP contracts are reused, not reconstructed. Each channel has distinct client-visible payload and ownership; no single universal co-processor protocol is inferred. See processors.tsv and existing tinysys protocol ledgers.
- **Still required:** nothing static. Runtime-only: probe, firmware boot, IPI round trip, mailbox interrupts, feature votes, suspend and watchdog/recovery (see [source-to-userspace-contract.md](source-to-userspace-contract.md) §4). GPUEB/VCP firmware images remain proprietary and excluded.

**Purpose:** GPU/AI auxiliary processors normal-world kernel source/parity closure, not firmware reconstruction.

**Decision:** DONE. The GPUEB and VCP host/status clients are now reconstructed from exact public source with full static parity, clean-checkout B1/B2 determinism and 67 verified cross-component ABI edges; see [parity-gaps.tsv](parity-gaps.tsv), [cross-component-abi.tsv](cross-component-abi.tsv) and [stale-claims.md](stale-claims.md). MTK-TINYSYS-IPI keeps the transport module; SCP and ADSP host code were not duplicated.

**Entry point:** [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) (the original [CLAUDE-HANDOFF.md](CLAUDE-HANDOFF.md) is preserved as the preparation record). Canonical research: `reverse-engineering/accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/`. Workspace pack: `Reverse Engineer - DONE/GPU-AI-AUX-KERNEL-INTERFACES/`.

**Exclusive primary kernel modules (3):** `gpueb.ko`, `vcp_status.ko`, `vcp.ko`. Dependencies are references, not additional ownership.

[stock modules](stock-modules.tsv), [DT nodes](dt-nodes.tsv), [source candidates](source-candidates.tsv), [parity gaps](parity-gaps.tsv), [function parity](function-parity.tsv), [data parity](data-parity.tsv), [cross-component ABI](cross-component-abi.tsv), [imports](imports.tsv), [exports](exports.tsv), [functions](functions.tsv), [data symbols](data-symbols.tsv), [donor ABI witnesses](abi-source-witnesses.tsv).

MTK-MBOX, MTK-RPMSG-MBOX and MTK-TINYSYS-IPI remain DONE for their exact transport modules. SENSOR-HUB-KERNEL keeps scp/hf_manager/sensorhub; AUDIO-DSP-KERNEL keeps adsp/audio host modules. CCU belongs to CAMERA-ISP-KERNEL and APUSYS to APUSYS-NPU-KERNEL. Firmware algorithms, signing, secure-boot loader internals and per-channel remote implementations are excluded.

The original preparation created no rebuild or parity result; every parity statement in this pack now comes from the measured reconstruction recorded in `evidence/reconstruction/`. No hardware command was executed at any stage.
