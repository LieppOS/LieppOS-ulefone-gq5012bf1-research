# Canonical baseline

- Canonical checkout `ulefone-gq5012bf1-research`, branch master, HEAD
  `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263` (2026-10-11 03:33, platform-batch04), clean.
- No newer canonical commit, no PLATFORM-BATCH-05 branch/package/workspace found
  (refs, all worktrees' kernel-source-reconstruction directories and /home/armol/kernel-work).
- Baseline audit: A244 B1 C14 D91 E0 F0 G108 = 245/458 (validated, `evidence/stage1-f61-validate.json`,
  14/14 `evidence/stage1-f61-mutations.log`) on private verified operands.
- Live canonical **before** restoration: inventory FAIL 180 errors, exactly the 60 signature-stripped
  system_dlkm copies (`evidence/stock-restoration/canonical-inventory-before.json`).
- Branch topology: every package branch forks from f61ebf03 except AUDIO-BATCH-01 and
  SCP-CONNECTIVITY-BATCH-01 (from bb370374); 55dab18a is an ancestor of 437ebd57; ALL-C,
  USB-TYPEC-CLOSURE and STOCK-INVENTORY-INTEGRITY are independent forks of f61ebf03.
- Only the two staging commits change the audit; every other package touches only its own
  research directory.
