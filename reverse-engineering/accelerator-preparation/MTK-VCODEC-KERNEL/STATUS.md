# MTK-VCODEC-KERNEL status — 2026-10-08

**PARTIAL / actionable kernel RE (class A).** 5 exact stock targets located; 15 pinned donor candidates. 0 modules have existing published function/data evidence, reproduced as citations—not new measurements.

Unchanged-donor binary equivalence and actually functioning exposed codecs are UNKNOWN. XML/config/source capabilities are static declarations only; runtime encode/decode and signed firmware internals are excluded.

Four codec/VCU normal-world drivers and their dedicated clock provider have donor targets but no complete module-level source/parity owner. Generic coverage was not a measured reconstruction.

**Next action:** Close dedicated vcodec clock module and common IRQ/DMA/power/provider helpers.

**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.

**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
