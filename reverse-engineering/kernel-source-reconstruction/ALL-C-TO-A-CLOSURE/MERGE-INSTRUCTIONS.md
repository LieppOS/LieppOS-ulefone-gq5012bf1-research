# Safe integration — owner review required, no canonical writes performed

This package is a checkpoint, not completion of the 18/18 mission.
Eight selected identities have A evidence; ten retain C blockers. The frozen manifest
is not rewritten. `C-CLOSURE-STATE.json` and `MODULE-PARITY.tsv` are the current outcomes.

## Preconditions

1. Ensure no concurrent agent is using the destination checkout.
2. Follow STOCK-INVENTORY-INTEGRITY owner restoration instructions if canonical operands
   remain signature-stripped. Do not overwrite a shared tree opportunistically.
3. Run the unchanged inventory validator: require 458 distinct identities, 471 occurrences
   and zero errors. The isolated restored closure worktree passes, with 14/14 validator tests.
4. Reconcile pending audio, connectivity, USB closure and other agent commits against the
   **actual current HEAD**. Do not substitute this older branch's audit over a newer one.
5. Recover maintained source repos from `bundles/`, verify their hashes/trees and compare
   actual tested commits from SOURCE-CHANGES. Do not reset another agent's source checkout.

## Field-level delta

`AUDIT-DELTA.tsv` is long-form: exact identity, field, expected old value and new value.
Its expected values are from canonical `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263`.
Only eight exact identities have proposed updates. Stock hashes/sizes/paths/partitions,
component ownership, runtime observations and all unselected identities are unchanged.
The evidence supports static source A, not a new runtime status.

Five rows are canonical C→A at that baseline (four CMDQ + thermal ADC). Three vendor
connectivity BTF rows were canonical G but become C under the pending connectivity delta;
this closure proposes A for those exact identities. Do not describe the unapplied canonical
G values as already-integrated C. System_dlkm bluetooth is explicitly not targeted.

Because pending integration changes old source-owner/provenance fields, field preconditions
may intentionally conflict after an earlier delta is applied. Review/rebase each proven
identity then regenerate the delta against the actual audit; never ignore conflicts to
reach a desired count. If an identity already has valid A evidence, do not downgrade it or
overwrite a different accepted provenance automatically.

## Apply only under owner control

After reviewing field preconditions, apply the accepted source-review updates using the
canonical audit generator/review tooling. Updating only ALL-457-MODULES.tsv is insufficient:
source reviews, their input hashes, summaries, ownership/gap outputs must remain consistent.
Regenerate and run the unchanged validator and mutation tests; verify no unselected
identity or stock-definition field changed. Commit locally. Do not push.

The delta intentionally leaves ten C rows unpromoted. BLOCKERS.tsv names the next real
source experiment for each. USB-TYPEC-CLOSURE's newer functional source must be reconciled
separately; this checkpoint does not reset it to older Batch04 code.

## Counts (provisional, not a merged audit)

Canonical baseline remains A244 B1 C14 D91 E0 F0 G108 = 245/458 certified.
With pending audio/connectivity plus these eight closures: projected
A289 B1 C10 D91 E0 F0 G67 = 290 certified / 168 uncertified / 458.
Other concurrent deltas are excluded until independently reconciled. No merged classification
count is claimed by this package. No phone, flash, runtime module load or secure-world test.
