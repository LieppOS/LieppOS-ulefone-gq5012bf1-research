# Mutation tests

- Audit validator mutation suite `test_validate.py`: 14/14 at the f61 baseline, after stages 2–3,
  after stage 6 (`evidence/audit-mutations-final.log`) and in both replays.
- Actual-ELF mutation controls (temporary copies of rebuilt modules only): connectivity 44, CMDQ 40,
  thermal 11, DRM 34 — each in B1 and B2 = 258, all detected; only GNU20 positives accepted.
- CAS safety: `apply-canonical.py` refuses the canonical path, requires the exact expected HEAD,
  stops before writing on any identity/hash/size or expected_before mismatch, and asserts that no
  unselected row changed. The pre-state tolerance is limited to PROOF_INPUT_HASH_CHANGED inside the
  four fast-forwarded repositories.
- STOCK-INVENTORY-INTEGRITY regression suite (11/11 at 143a6db2) preserved unchanged.
