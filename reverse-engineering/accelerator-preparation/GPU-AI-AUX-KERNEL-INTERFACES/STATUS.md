# GPU-AI-AUX-KERNEL-INTERFACES status — 2026-10-08

**PARTIAL / actionable kernel RE (class A).** 3 exact stock targets located; 9 pinned donor candidates. 0 modules have existing published function/data evidence, reproduced as citations—not new measurements.

GPUEB/VCP target rebuild parity is not yet measured. Secure firmware internals, runtime message timing and remote algorithm behavior cannot be settled by this static preparation. MCUPM/SSPM client parity is UNKNOWN outside the owned GPU/video targets, not falsely counted as DONE.

GPUEB and VCP host/status clients were only referenced by MTK-TINYSYS-IPI. Its explicit DONE scope proves the transport module, not these client implementations. SCP and ADSP host code are already DONE elsewhere and are not duplicated.

**Next action:** Reuse DONE mailbox/RPMsg/IPI source and exact provider CRC/KCFI evidence; freeze all client-facing headers.

**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.

**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
