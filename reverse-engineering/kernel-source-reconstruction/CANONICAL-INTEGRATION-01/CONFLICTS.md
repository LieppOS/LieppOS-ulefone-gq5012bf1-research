# Conflicts and resolutions

1. **Proof-input drift from source fast-forward.** Fast-forwarding thermal/connectivity/DRM
   maintained repos changed their SOURCE-PINS.tsv/bulk-build.sh, which are recorded proof inputs
   of 38 rows. The validator correctly failed. Resolution: all 38 (32 A + 6 promoted) passed strict
   re-verification at the new tips in both builds; Stage 5 moved the 32 A rows to the new tip with
   evidence appended and refreshed only those input hashes. No validator rule was relaxed.
2. **Stale ALL-C audit delta.** Prepared at f61ebf03; 8 of 10 rows had changed in staging. Not
   applied; replaced by a CAS derived from 437ebd57 (DRM-RECONCILIATION.md).
3. **Ownership.** ALL-C proposed new source_owner/group and `-allc` repo paths. Rejected; original
   batch ownership and maintained repositories preserved for all rows.
4. **USB-TYPEC-CLOSURE gate.** Its delta was blocked only by the damaged live stock; private and
   live operands now pass, every expected_before still matched at 437ebd57, class unchanged.
5. **Duplicate research paths.** Staged copies of four packages were byte-identical to originals
   (tree IDs equal), so history merges changed no content.
6. **Live f61 validation after restoration.** 9 thermal PROOF_INPUT_HASH_CHANGED errors (cause 1),
   recorded rather than waived.
7. **Operational slips in private worktrees (no shared effect):** a nested `workspace/workspace`
   copy (removed, recopied) and a replay assertion reading the wrong JSON key (fixed; failed replay
   worktrees removed and both replays rerun from scratch).

No row conflicted with a newer proven source class.
