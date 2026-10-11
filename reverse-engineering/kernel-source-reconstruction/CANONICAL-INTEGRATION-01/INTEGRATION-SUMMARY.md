# CANONICAL-INTEGRATION-01 — summary

**Result: A333 / B1 / C10 / D60 / E0 / F0 / G54 = 334 certified / 124 uncertified of 458.**
Matches the documented consistency target exactly; it was computed from identity-keyed rows,
not forced. Status: see "Canonical status" at the end.

| Step | A | B | C | D | E | F | G | Certified | Uncertified |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| f61ebf03 canonical baseline (validated) | 244 | 1 | 14 | 91 | 0 | 0 | 108 | 245 | 213 |
| + COMPLETED-BATCHES-INTEGRATION-01 (55dab18a) | 301 | 1 | 20 | 82 | 0 | 0 | 54 | 302 | 156 |
| + NEXT-DG-BATCH-01 (437ebd57) + original history merges | 323 | 1 | 20 | 60 | 0 | 0 | 54 | 324 | 134 |
| + 4+5-ALL-C-AND-SOURCE-SUPERSEDE | 333 | 1 | 10 | 60 | 0 | 0 | 54 | 334 | 124 |
| + 6-USB-TYPEC-CLOSURE | 333 | 1 | 10 | 60 | 0 | 0 | 54 | 334 | 124 |

Every count row is an actual unchanged-validator PASS (0 errors) with 14/14 audit mutation tests.

## What was integrated, in order

1. Baseline f61ebf03 re-validated in a private worktree against independently verified operands.
2. Fast-forward to NEXT-DG 437ebd57, which contains COMPLETED-BATCHES-INTEGRATION-01 55dab18a
   (63 identities: 57 A, 6 C) and NEXT-DG (22 D→A). Canonical had not advanced, so this is the
   validated staging output on its own base, not an old snapshot over newer work.
3. Original package histories merged with commit identity preserved and **tree unchanged** (the
   staged copies are byte-identical): AUDIO-BATCH-01 f00bd8af, SCP-CONNECTIVITY-BATCH-01 40bfedda,
   AUDIO-DEPENDENCIES-BATCH-02 fb558640, STOCK-INVENTORY-INTEGRITY 143a6db2.
4. Research-only merges: USB-TYPEC-CLOSURE 7e196c32 (977 files), ALL-C-TO-A-CLOSURE 652e4195
   (489 files, includes daef94c6, 6b52a800, cef3bafa).
5. Stage 4: ALL-C 10 C→A after **re-verifying** acceptance in the combined environment.
6. Stage 5: 32 already-A rows of the thermal/connectivity/DRM repositories moved to the verified
   superseding recipe tips (status unchanged).
7. Stage 6: USB-TYPEC-CLOSURE 22-field C evidence (no class change).

173 field CAS changes over 47 identities in stages 4–6; 103 identities differ from f61ebf03 in
total ({('G', 'A'): 53, ('D', 'A'): 31, ('G', 'C'): 1, ('A', 'A'): 8, ('C', 'C'): 5, ('C', 'A'): 5}). Unselected rows, identity set, stock hash/size/path/partition fields and all
ownership fields (source_owner/source_group/source_repo/build_script/component_owner) are unchanged.

## Verification

- Inventory (unchanged STOCK-INVENTORY-INTEGRITY checker): private 458/471, 60/60 signed; live
  canonical after restoration PASS 458/471, 60/60 signed. Both bluetooth.ko identities separate.
- Whole-ELF re-verification: 196 strict acceptances (CMDQ 35, thermal 34, connectivity 17, DRM 12,
  each in B1 and B2) against flat operands derived from the verified worktree, GNU20 only.
- Actual-ELF mutation controls: 258 (connectivity 44, CMDQ 40, thermal 11, DRM 34, ×2 builds).
- Audit mutation tests 14/14 at every stage. Source bundles 48/48 `git bundle verify`.
- 35 source locations, all referenced commits present; 4 maintained repos fast-forwarded only.
- Two independent owner replays from f61ebf03: all 28 audit files, CAS plan, application log and
  class table byte-identical to fc31148e and to each other.

## Canonical status

The shared canonical stock copies were restored (60/60) through the authenticated owner procedure
while the checkout was idle. The integrated branch is applied to canonical master by fast-forward
only after the live inventory passes; the resulting canonical SHA is recorded in the final commit
message and MERGE-INSTRUCTIONS.md section 5 (no self-referential hash inside this file). No push.

## Executed canonical application

- Pre-integration reference: annotated tag `pre-canonical-integration-01` → f61ebf03 and verified
  bundle `/home/armol/kernel-work/canonical-integration-01/pre-integration-canonical-f61ebf03.bundle`.
- Idle check repeated immediately before applying: no new writes, HEAD/refs unchanged.
- `git merge --ff-only 88ccded8c9c685e2c1493e44fca31a95fabebc84` on canonical master (no history
  rewritten). Live, in the canonical checkout with the restored shared stock:
  inventory PASS 0 errors 458/471, 60/60 signed; validator PASS 0 errors A333/B1/C10/D60/E0/F0/G54;
  audit mutation tests 14/14 (`evidence/canonical-live/`).
- This evidence commit follows on master; its SHA is the final canonical commit. No push.
