# Merging SCP-CONNECTIVITY-BATCH-01

Three independent deliverables exist:

- **PLATFORM-BATCH-04**: Claude, in progress, 30 identities.
- **AUDIO-BATCH-01**: Codex, finished, unmerged, 21 identities. Branch `codex/audio-batch-01`.
- **SCP-CONNECTIVITY-BATCH-01**: Codex, this batch, 20 identities. Branch `codex/scp-connectivity-batch-01`.

All three manifests are pairwise disjoint by `module_id` (checked by `scripts/validate-batch.py`).
**No automatic merge, and no merge while Claude is working.** The owner of the canonical checkout runs:

1. **Freeze.** Wait for Batch04 to be committed and record canonical HEAD `H`. Both Codex branches stay read only.
2. **Order.** Batch04 first, then AUDIO-BATCH-01 (its own `MERGE-INSTRUCTIONS.md`), then this batch.
   Order between the two Codex deltas does not matter: their identities are disjoint and both only
   change G rows.
3. **Identity revalidation.** For every `AUDIT-DELTA.tsv` row, `ALL-457-MODULES.tsv` at `H` must contain
   exactly one row with that `module_id`, with `source_status == old_source_status` (`G`). Abort for
   any changed identity: another batch touched it.
4. **Schema.** Map only `source_status`, `source_group`, `source_owner`, `source_repo`, `source_commit`,
   `parity_evidence`, `build_script` and `reproduction_status`. If Batch04 changed columns, map by name
   and never copy whole rows. `scripts/test-delta.py` shows the exact field-level application and is
   tested on a scratch clone (`evidence/audit-delta-test.json`).
5. **Provider drift.** If Batch04 or the audio merge reclassified a provider in `PROVIDER-BOUNDARIES.tsv`,
   nothing changes here, because certification depends only on the CRC/KCFI boundary witnessed from
   source. Two notes:
   - `scp` becomes A through this delta. That strengthens the audio and connscp boundaries without
     changing them.
   - `yft_devinfo` (C) remains the only `STOCK_PROVIDER_EXPORT` boundary, by the CAMERA-ISP-KERNEL
     precedent.
6. **Bring in research.** `git checkout codex/scp-connectivity-batch-01 -- reverse-engineering/kernel-source-reconstruction/SCP-CONNECTIVITY-BATCH-01`.
   This branch changes no other path.
7. **Re-verify before publishing.** In a scratch area, run both clean checks from the bundles
   (`scripts/cleancheck.sh <bundle> <commit> <base> <stock>` in each repo). Expect `CLEANCHECK PASS`.
8. **Apply the delta** with the canonical audit generator, then confirm 458 identities. Relative to `H`,
   this delta gives A +17, C +3 and G −20, and certifies no B.
   - On the frozen baseline alone: **237 certified / 221 uncertified** (A236 B1 C12 D98 G111).
   - With AUDIO-BATCH-01 as well: **257 / 201**.
   - Batch04's result is added on top. Do not double count: every module_id is applied once, and
     `test-delta.py` rejects a second application.
9. **Owner notes.** In SENSOR-HUB-KERNEL / CONNINFRA-KERNEL / MT6637-*-KERNEL / FM-KERNEL /
   GNSS-KERNEL-TRANSPORT / CONNFEM, record the maintained repository and commit.
   - Correct the sensors note: SCP host "Ulefone deltas" are pristine ALPS (`SCP-HOST-INTERFACES.md`).
   - Replace the historical `intree_relink.sh` `.mod.c` editing with the genuine in-tree build. It remains C because of BTF.
10. Commit in the canonical branch. Do **not** push without explicit approval.

## Re-check after Batch04 landed (canonical `f61ebf03`)

Claude committed PLATFORM-BATCH-04 during this batch: 245 certified (A244 B1 C14 D91 G108). The
canonical checkout was not touched here. In a scratch clone at `f61ebf03`, all 20 rows of this
delta and all 21 audio rows still have `old_source_status = G`, and both deltas apply cleanly
(`evidence/audit-delta-test-on-f61ebf03.json`):

- this delta: A261 B1 C17 D91 G88, **262 certified / 196 uncertified**;
- this delta + AUDIO-BATCH-01: A281 B1 C18 D91 G67, **282 certified / 176 uncertified**.

Still re-run step 3 on whatever HEAD is current when merging.
