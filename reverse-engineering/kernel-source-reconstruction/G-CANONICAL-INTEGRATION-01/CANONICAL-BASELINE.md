# Canonical baseline

- **Starting canonical:** `0390534d91d96f4607787efb380c23b4cd0fc304` (KDM-INTEGRATION-01), clean, no index lock,
  no agent build processes. The unchanged validator passed with 0 errors at **A385 B1 C10 D8 E0 F0 G54 = 386/458**
  (`evidence/stageA/validate-pre-A.json`).
- **Recovery:**
  - tag `pre-g-canonical-integration-01` → 0390534d;
  - bundle `kernel-work/g-canonical-integration-01/pre-integration-master-0390534d.bundle`, sha256
    `88bc19de9aeab49c2140195d12054c7f67f7922122b45e1ffd7e78575a1d3ef7`, verified.
- **Stock operands:** the sha256 list of all 471 stock `.ko` equals the list recorded at KDM-INTEGRATION-01.

## Worktrees and owners at start

| Worktree | State | Treatment |
|---|---|---|
| canonical (`master`) | 0390534d, clean | fast-forward only, after re-checking idle |
| `-boot-lowpower-integration` | clean, reused for Stage A (branch `integration/g-canonical-01`) | — |
| `-codex-g-source` | `codex/g-source-recovery-batch-01` @ 468a226e, clean, no files touched in 3 h | merged as history (package directory only) |
| `-codex-g-source-audit` | `codex/g-source-audit-proposal` @ 6c12da0e (based on ee1803b7), clean | **not merged**; it holds a stale full-audit snapshot |
| `-codex-g-source-replay` | detached ee1803b7 with 11 uncommitted Codex scratch files | untouched |
| `-owner-g-source` | new, created for Stage B from e66cfcf7 (branch `owner/g-source-final`) | the only worktree name `reconcile-owner.py` accepts |

## Codex history merged

`codex/g-source-recovery-batch-01` is based on 63f12972. Its three commits (59ee0113, 2a1bd515, 468a226e) add
only `reverse-engineering/kernel-source-reconstruction/G-SOURCE-RECOVERY-BATCH-01/`. The merge left the audit tree
byte-identical; the audit change was then applied separately by the identity-keyed CAS.
