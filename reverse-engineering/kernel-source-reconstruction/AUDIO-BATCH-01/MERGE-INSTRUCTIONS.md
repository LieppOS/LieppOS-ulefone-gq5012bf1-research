# Merging AUDIO-BATCH-01 after PLATFORM-BATCH-04

**Do not merge while Claude is working. No automatic merge.** The owner of the canonical checkout
performs these steps after Batch04 is committed.

1. **Freeze.** Record the new canonical HEAD `H`. Branch `codex/audio-batch-01` stays read only.
2. **Identity revalidation.** For each `AUDIT-DELTA.tsv` row, the new
   `kernel-source-parity-audit/ALL-457-MODULES.tsv` must contain exactly one row with the same
   `module_id`, where module ID = filename@stock sha256. Its `source_status` must still equal
   `old_source_status` (`G`). Abort for any audio identity whose status changed: someone else
   touched it.
3. **Schema check.** If Batch04 changed the audit columns, map only these fields:
   `source_status`, `source_group`, `source_owner`, `parity_evidence`, `build_script`, the
   reproduction status and the verified A/B flag. Never copy whole rows from this branch.
4. **Disjointness.** Assert that the module IDs in `AUDIO-BATCH-01/BATCH-MANIFEST.tsv` do not intersect
   with `PLATFORM-BATCH-04/BATCH-MANIFEST.tsv`. This holds at freeze time: 0 overlap.
5. **Provider drift.** If Batch04 reclassified a provider listed in `PROVIDER-BOUNDARIES.tsv`, nothing
   changes for audio. Audio certification does not depend on provider class, only on the CRC/KCFI
   boundary witnessed from source.
6. **Bring in research.** `git checkout codex/audio-batch-01 -- reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01`
   (new directory only; this branch changes no other path).
7. **Re-verify before publishing.** In a scratch copy, re-run the clean check from the bundle:
   `scripts/cleancheck.sh <bundle> ec57573c… <base> <stock>`. Expect `CLEANCHECK PASS`.
8. **Apply the delta** with the canonical audit generator, then confirm 458 identities. Starting
   from Batch04's result, A rises by 20 and C by 1, while G falls by 21. On the frozen baseline
   that is 240 certified / 218 uncertified; these numbers stay provisional until applied to Batch04.
9. **Owner notes.** Mark component `AW883XX-SPEAKER-AMP` with the corrected semantic note: the
   historical `<` tie order and D10 have been replaced by patch 0006. `MT6369-AUDIO-CODEC` keeps DONE.
10. Commit in the canonical branch. Do **not** push without explicit approval.
