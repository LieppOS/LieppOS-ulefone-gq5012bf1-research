# Safe local integration — currently blocked

**Do not apply this delta now.** The live canonical validator rejects60 missing/60 unexpected unrelated stock SHA identities and frozen-inventory/ownership drift. Existing live mutation baseline also FAILs. All five scoped stock identities still match and the canonical audit TSV remains unchanged. Four independent source-build proofs,23 ELF mutation tests and14 frozen-fixture audit tests do not override this live gate.

No push, phone access or runtime deployment is authorized.

## Preconditions

1. Other agents' work must have finished; reconcile audio/SCP/connectivity or any newer audit/source changes without overwriting their worktrees.
2. Reconcile the actual frozen-stock identity drift legitimately outside this scoped task. Do not replace audit SHA rows merely to accept changed files, normalize raw inventory hashes, repair unrelated stock files here or waive validator failures.
3. Obtain a clean integration worktree at the current canonical head; preserve that head and all current audit/ownership/component/runtime tables. This research is based on `f61ebf03275ba2d3f6aa4f9d5aebe18e12922263`, not an instruction to reset canonical to it.
4. The unchanged live inventory validator and mutation tests must PASS before editing audit fields. If they do not, stop and preserve the failure.

## Source integration

Maintained local tips:

| Repository | Baseline | Closure tip |
|---|---|---|
| Type-C | `d41a2436c15fc53c25061dd9cd19d0e08f11ffbb` | `758f9edc78c7a50d07b8629126438a3674845911` |
| Charging/shared | `44ce4ff57556bba462772f4b164c2650b9caa0e3` | `b2a343a9d8664b77a63dc16835b5af0fd0e55cf1` |

Review each baseline-to-tip diff in a separate integration worktree. Preserve original `0001`/`0002` patches and failed experiments. Reconcile the identical shared `0003-stock-observed-tcpc-code-and-timers.patch` and assembled-tree pin consistently across both engines. Retain standard debug-only prefix maps and complete source lineage. Do not transplant compiled operands or apply a stock fingerprint/counter/diagnostic patch. The new algorithms are selected-stock reconstructions, not a new original OEM textual release or an assertion of equivalence to different PD behavior.

Verified bundles and source hashes are under `evidence/bundles/` and `evidence/fresh-clones/source-commits.json`. Recover into temporary clones, verify bundle ancestry/full `git fsck`, then rebuild using pinned inputs. Never merge by copying source-only target `.ko`, `.o` or comparison archives into build inputs. Rebase/cherry-pick/merge conflicts must be reviewed; original closure hashes cannot identify a changed merge tree. Any changed engine/source configuration needs new independent build evidence.

## Research integration

Use a reviewed local merge/cherry-pick of the research preservation commit, confined to `reverse-engineering/kernel-source-reconstruction/USB-TYPEC-CLOSURE/`. It intentionally contains no canonical audit, ownership, runtime or unrelated Batch04 edits. Preserve its failed proofs and complete ledgers, not just the summary. Do not overwrite historical Batch04 results with current counts.

## Field-level audit proposal

`AUDIT-DELTA.tsv` is an **unapplied compare-and-swap proposal**, not a replacement audit table. For each of22 entries:

- Match the exact `module_id`, filename and field in the latest current audit.
- Require current field equality to `expected_before`; if changed, stop and reconcile with the newer owner/evidence. Do not silently overwrite or force the proposal.
- Check `proposed_after` references exist in the integrated research/source layout and identify the reviewed source commit. Rebased/merged sources need their real reviewed commit and regenerated proof, not the old commit string.
- Synchronize corresponding gap/ownership/project copies only as required by the unchanged validator and only for these five identities. Do not change runtime/component ownership.
- Keep all five `source_status` values **C**. No whole-module A/B evidence exists. TCPC class instruction count701→709 and instruction mismatch count8→0 are scoped improvements; metadata/relocation blockers remain.

Validate all five selected rows and prove all453 unselected identities/fields remain unchanged by this proposal. The delta contributes **zero certifications**, independently of any other agent's count changes. Do not hardcode245/213 if the integration baseline has advanced; those are this task's frozen baseline counts, not a reason to overwrite newer counts.

## Post-integration gates

Run the unchanged canonical validator and mutation tests, strict complete five-module acceptance, source-build preservation checks and genuinely independent committed-source B1/B2 builds. Expect25 prior acceptances/five strict C rejections from the current unchanged source; if merging changes source, inspect all new discrepancies rather than accepting an expected count alone. Keep ABI/export licenses/KCFI, raw and semantic relocations, sections/symbols, natural srcversion, BTF and real raw-byte ledgers.

If any gate FAILs, do not claim integration/closure complete. Preserve the blocker and stop. Full module promotion still requires authentic original OEM token/counter/diagnostic lineage and complete existing A/B evidence. Do not push.
