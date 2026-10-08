# MTK-MDP-KERNEL status — 2026-10-08

**PARTIAL / actionable kernel RE (class A).** 4 exact stock targets located; 12 pinned donor candidates. 0 modules have existing published function/data evidence, reproduced as citations—not new measurements.

No existing complete MDP/MML source-parity owner or measured rebuild was found. Public donor availability is not proof that hardware behavior or shipped module bytes match.

mdp_drv and the two MML modules are distinct from mediatek-drm. The DRM DONE scope explicitly closes DRM/panel modules, not MDP/MML; no MDP byte/semantic parity evidence was found. Keep generic CMDQ and reconstructed secure CMDQ outside this component.

**Next action:** Close clk-mt6878-mdpsys and mdp_drv object/target composition against stock.

**Blockers:** full acceptance packet and target-specific donor/config/ABI reconciliation. Signed algorithms and runtime tests are excluded, not a reason to fake static closure.

**Definition of DONE:** all owned modules satisfy the complete [parity standard](../PARITY-STANDARD.md), plus the normal-world DT/ABI contract; retained firmware and userspace boundaries remain explicit.

No ADD elsewhere, merge, removal, rename or unrelated status move is authorized by this pack.
