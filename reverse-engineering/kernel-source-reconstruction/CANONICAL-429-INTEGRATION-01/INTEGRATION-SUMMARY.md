# CANONICAL-429-INTEGRATION-01

**Result:** canonical moves from **A420 B1 C11 D3 G23 = 421/458** to **A428 B1 C15 D3 E0 F0 G11 = 429/458
certified (93.7%)**, with 29 uncertified.

| Step | Input | Identities | Field changes | Classes after |
|---|---|---|---|---|
| merge | `codex/g-source-recovery-batch-02` `aa212a88` (`--no-ff`, history kept) | — | 0 (package only) | unchanged |
| 1 | Codex owner CAS (`reconcile-owner.py`, unchanged) | 12: 7 G→A, 5 G→C | 228 | A427 B1 C16 D3 G11 |
| merge | `claude/oem-source-gap-closure-01` (incl. PUBLIC-G-CLOSURE-BATCH-01) | — | 0 | unchanged |
| 2 | tmem_ffa CAS (`audit-delta.py`) | 1: C→A | 14 | **A428 B1 C15 D3 G11** |

## Changed identities

- **7 G→A:** `extdev_io_class`, `rt5133-regulator`, `spi-mt65xx`, `leds-rgb-aw2013`, `yft_gpio_keys`,
  `camera_eeprom_v4l2`, `microarray_fp_tee`.
- **5 G→C:** `aw36515`, `aw36518`, `aw36518_v2`, `fingerprint`, `tkcore_drv`. These are not promoted.
- **1 C→A:** `tmem_ffa`.
- **The other 445:** byte-identical. No A/B row was demoted, stock identity fields are unchanged, and both
  `bluetooth.ko` identities remain distinct. `tkcore` stays C.

## Validation

- Validator PASS, 0 errors.
- `test_validate.py` 14/14.
- Inventory 458/471.
- 471 stock hashes unchanged.
- All 47 A/B source repositories resolve.
- Codex's three bundles and repos were re-verified, and so were its strict results.
- `tmem_ffa` was re-verified by a new fresh-clone B3 build.

## Corrections made during integration (recorded, not hidden)

1. **Queue header:** Codex's regenerator reset the queue "Completed integration" header (the same known defect).
   It was restored from master and batch-02 appended.
2. **Anchor bug:** my tmem_ffa applier's first attempt stopped on a queue-anchor mismatch. The worktree was
   restored from git, the anchor fixed on the research branch (`86686bbc`) and the delta reapplied. The failed log
   is preserved.

## Files

| Topic | Documents |
|---|---|
| Starting state | `INITIAL-HEAD.md` |
| Identities and ownership | `CHANGED-IDENTITIES.tsv`, `SOURCE-OWNERSHIP.tsv` |
| Audit delta | `AUDIT-DELTA.tsv` (242 ALL-table field changes), `CAS-RECONCILIATION.tsv` |
| Validation | `STOCK-INVENTORY.md`, `SOURCE-PROOF-VALIDATION.md`, `MUTATION-TEST-RESULTS.md` |
| Provenance and classes | `TRUSTKERNEL-SOURCE-PROVENANCE.md`, `CLASSIFICATIONS-BEFORE-AFTER.tsv` |
| Recovery | `RECOVERY-REFERENCES.md` |
