# DRM helper reconciliation

| Step | drm_display_helper / drm_dma_helper | Source |
|---|---|---|
| f61ebf03 | D (public candidates) | candidate source rows recorded in the f61ebf03 audit |
| AUDIO-DEPENDENCIES-BATCH-02 → 55dab18a/437ebd57 | C: all non-BTF bytes exact, public-base split-BTF residual | audio_shared_infrastructure 425ffd72; owner `AUDIO-DEPENDENCIES-BATCH-02:TRANSITIVE-SHARED-INFRASTRUCTURE` |
| ALL-C (652e4195) | A in its own checkpoint | recipe 4697eac3 on `-allc` clone |
| This integration | **A** | maintained repo fast-forwarded 425ffd72→4697eac3 |

Conflict: ALL-C's `AUDIT-DELTA.tsv` was prepared against f61ebf03 (where both were D) and proposed
`source_owner/source_group = ALL-C-TO-A-CLOSURE:BTF-DRM` and `source_repo = …-allc`. Applying it
to the staged audit would have failed CAS and overwritten Codex ownership. It was **not applied**.
`plan-canonical.py` instead derived a fresh CAS from the committed staged values at 437ebd57:
only source_status, source_commit, source_pin, parity_evidence, abi/crc/kcfi_status,
exact/unresolved functions, verified_difference_classification, blocker and preservation_risk.
Codex's source_owner, source_group, source_repo and build_script are preserved.

Re-verification under the combined environment: the 4697eac3 recipe's preserved B1/B2 outputs pass
the unchanged strict verifier for all 12 modules (10 previously A + 2 DRM) against independently
verified operands; 34 ELF mutation controls per build. The other ten Codex modules moved to
4697eac3 by Stage 5 with their original evidence plus the reverify reports; none was dropped.
