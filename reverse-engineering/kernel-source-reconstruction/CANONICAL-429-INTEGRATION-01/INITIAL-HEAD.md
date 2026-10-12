# Initial state (verified before any change)

- **Canonical:** `master` = `4e47a5b9369577751c2457da0c42ec194f56d332`. Clean, no `.git/*.lock`, no active
  make/clang/validator processes.
- **Audit:** validator PASS, 0 errors, A420 B1 C11 D3 E0 F0 G23 = 421/458 (`evidence/pre-validate.json`).
- **Inventory:** PASS, 458 identities / 471 occurrences (`evidence/pre-inventory.json`). The 471 stock `.ko`
  sha256 values equal the DISPLAY-INTEGRATION-01 operand list.
- **Branches:**
  - `codex/g-source-recovery-batch-02` = `aa212a88…`; it diverges from master at `e66cfcf7` and changes only its
    package directory (614 files).
  - The private proposal `fc4c39ed` sits on `codex/g-source02-audit-proposal`, based on `4e47a5b9`.
  - `claude/oem-source-gap-closure-01` = `e2e657e3` (master is its ancestor).
- **Codex worktree:** `aa212a88`, clean. It is not writing canonical.
