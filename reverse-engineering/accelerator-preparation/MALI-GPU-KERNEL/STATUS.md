# MALI-GPU-KERNEL status — 2026-10-08

**PARTIAL / actionable kernel RE (class A).** 8 exact stock targets located; 18 pinned donor candidates. 0 modules have existing published function/data evidence, reproduced as citations—not new measurements.

GPU runtime model/revision, OEM donor deltas, secure/protected execution and real frame performance remain unproved. No measured target source build exists for these eight modules.

Active KMD/MGM/protected allocation had no owner. GED, GPU HAL/QoS and gpufreq candidates were generic platform-source triage, not a DONE parity scope; no distinct DONE component owns them.

**Next action:** Freeze MGM/protected allocator and GPU HAL exported interfaces; compare r44p1 baseline to r44p0 only as an alternative, not an assumed match.

**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.

**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
