# Regression tests

`scripts/test_stock_operand_integrity.py` (11 tests, 25 s; log: `evidence/regression/regression-tests.log`).

```sh
cd reverse-engineering/kernel-source-reconstruction/STOCK-INVENTORY-INTEGRITY/scripts
PYTHONDONTWRITEBYTECODE=1 python3 test_stock_operand_integrity.py -v
# OPERAND_ROOT=<checkout with intact operands>  IMAGE=<system_dlkm_a.img>  FSCK_EROFS=<pinned fsck.erofs>  SCRATCH=<btrfs dir>
```

Each test reflinks the three stock roots into a private temporary tree and points the **unchanged** canonical
`inventory.scan()` at it, through `inventory.ROOT`/`STOCK_ROOTS`. The validator logic is not modified or
mocked. No test writes outside the temporary tree.

| Test | What it proves |
|---|---|
| `test_intact_operands_pass` | authentic operands: 0 errors, 458/471 |
| `test_in_place_objcopy_strips_signature_and_is_rejected` | the **actual command** (`llvm-objcopy --dump-section .BTF=/dev/stdout IN`) deterministically produces the incident bytes `6d239276…` (−721 B), and the validator rejects them with the exact MISSING/UNEXPECTED pair |
| `test_full_incident_reproduces_exact_60_60_failure` | rerunning the incident loop over all 458 first paths reproduces the **byte-identical error list** of the captured canonical failure; the 11 unsigned vendor `.BTF` modules stay authentic |
| `test_vendor_bluetooth_not_confused_with_system_bluetooth` | stripping system `bluetooth.ko` reports only the system identity, never the vendor one |
| `test_truncation_only_rejected` | plain 721-byte truncation is rejected |
| `test_same_size_signature_corruption_rejected` | a 1-bit flip inside the PKCS#7 blob at unchanged size is rejected |
| `test_rebuilt_module_substitution_rejected` | other bytes under the same filename (vendor bluetooth at the system path) are rejected, including the duplicated-path error |
| `test_verifier_passes_intact_and_rejects_stripped` | `verify-inventory.py` passes intact and reports exactly SIZE+SHA256+SIGNATURE_TRAILER for a strip |
| `test_restore_repairs_only_stripped_and_quarantines` | the restoration tool repairs a stripped file, quarantines the damaged bytes, writes a manifest and the validator passes |
| `test_restore_refuses_non_signature_damage_without_writing` | any non-strip damage aborts the **whole** run before any write, even for files that could otherwise be repaired; no quarantine is created |
| `test_restore_refuses_unauthenticated_image` | a 1-bit-different image is refused |

None of the tests normalizes altered stock evidence. Every altered operand must be rejected.

Existing canonical audit mutation tests (`test_validate.py`, unchanged) pass 14/14 against the repaired
isolated operands (`evidence/after/mutation-tests.stderr.txt`). Before repair they were 10/14 on canonical.
