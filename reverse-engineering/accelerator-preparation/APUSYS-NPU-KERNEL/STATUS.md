# APUSYS-NPU-KERNEL status — 2026-10-08

**PARTIAL / actionable kernel RE (class A).** 2 exact stock targets located; 6 pinned donor candidates. 0 modules have existing published function/data evidence, reproduced as citations—not new measurements.

Dedicated NPU model execution, actual exposed inference throughput, signed payload algorithms and secure internals are UNKNOWN. DT enablement, loaded apusys and runtime library presence are not inference-execution proof.

apusys and apu_top are normal-world source-actionable kernel code, not proprietary algorithms. Prior class-C blob-inventory ownership did not establish source parity; APU/MDLA RPMsg nodes were incorrectly attributed to camera consumers.

**Next action:** Close apu_top power initialization, OPP/DVFS/thermal callbacks, unwind and suspend/reset state machine.

**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.

**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
