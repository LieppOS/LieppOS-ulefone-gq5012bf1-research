# Mutation tests

## Audit mutation tests (`kernel-source-parity-audit/scripts/test_validate.py`, unchanged)

| Point | Result |
|---|---|
| Stage A applier (integration worktree) | 14/14 PASS |
| Stage A live canonical e66cfcf7 | 14/14 OK |
| Stage B `reconcile-owner.py --apply` (owner worktree) | 14/14 PASS (`evidence/stageB/apply/owner-g-source-mutations.log`) |
| Stage B after restoring the queue header | 14/14 OK |
| live canonical after the Stage B fast-forward | 14/14 OK (`evidence/live-post/`) |

## ELF mutation controls (committed proofs, re-read)

- Stage A: 69 per build × 2 = 138, all deliberate corruptions rejected.
- Stage B: camera_lens 91 + 91, modem_interfaces 93 + 93, secure_transport 109 + 109 = **586**, all PASS. The
  controls include the GNU build-ID flip, the only accepted difference.
