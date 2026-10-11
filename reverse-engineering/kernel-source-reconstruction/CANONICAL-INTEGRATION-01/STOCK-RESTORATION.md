# Stock analysis copy restoration (live canonical)

Root cause and procedure: STOCK-INVENTORY-INTEGRITY (98acd423/143a6db2). Two historical in-place
`llvm-objcopy` commands stripped the 721-byte appended signatures from 60 system_dlkm copies.

Trust anchors re-verified here:
- `system_dlkm_a.img` SHA256 `300f24c5550be110d0161583fa56d3c36ae61b8b2da4b44c128350c6e22b9f2a`
  (file mtime 2026-06-04); same digest recorded as "factory V15 exact" in canonical commit
  f037fed2 (2026-09-16, ancestor of master), predating both incidents.
- Pinned fsck.erofs (build-tools e905be25) SHA256 `3059e2f0…`.

Procedure (`restore-operands.py`, unchanged):
1. Live inventory before: FAIL, 180 errors, 60 BAD_SIGNATURE.
2. Dry run: 60 identities, 0 already intact, 60 WOULD_RESTORE. The manifest equals the preserved
   `STOCK-INVENTORY-INTEGRITY/evidence/repair/canonical-dry-run.tsv` on every column for all 60
   rows, including inode and mtime (damage unchanged since diagnosis).
3. Apply: 60 RESTORED, intact_after 60; damaged copies quarantined at
   `/home/armol/kernel-work/canonical-unsigned-stock-quarantine-canonical-integration-01/` (60 files,
   hashes in `evidence/stock-restoration/canonical-restore-manifest.tsv`).
4. Live inventory after: **PASS, 0 errors, 458 identities / 471 occurrences, 60/215/196,
   60/60 system_dlkm signed 721-byte trailers, 471/471 committed SHA+size**.

Image, expected hashes and validators were not modified. No other stock file was written.

Live validator on canonical f61ebf03 after restoration (before integration): no stock/identity
errors; exactly 9 `PROOF_INPUT_HASH_CHANGED` for thermal `SOURCE-PINS.tsv`, caused by this
integration's own verified fast-forward of the thermal repository and resolved by Stage 5. It is
recorded, not waived (`evidence/stock-restoration/canonical-f61-live-validate.json`).
