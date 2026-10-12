# Audit mutation tests

- After step 1 (Codex CAS): `test_validate.py` OK, 14/14 (`evidence/step1-codex/after-codex-mut.log`).
- After step 2 (tmem_ffa CAS): OK, 14/14 (applier).
- Final integration tree: `test_validate.py -v`, 14 tests, all `... ok` (`evidence/final/int-mut.log`).
- Live canonical after fast-forward: see `evidence/live-post/`.
