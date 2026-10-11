# Owner replay / merge instructions

1. Confirm canonical is still at the recorded base and idle (`git status`, `git worktree list`,
   process cwd scan). If canonical advanced, do not fast-forward: rerun `owner-replay.sh` on the new
   base after adapting the expected base, and resolve any CAS stop explicitly.
2. Stock: if `verify-inventory.py <canonical>` fails, follow STOCK-INVENTORY-INTEGRITY
   MERGE-INSTRUCTIONS (dry-run must equal the preserved plan; apply with a new quarantine).
3. Source: maintained repos cmdq/connectivity/thermal_cooling/audio_shared_infrastructure must be at
   0b4b07f3/40bf4296/ff6e97b3/4697eac3 (fast-forward from bundles in ALL-C-TO-A-CLOSURE/bundles if
   not). Never reset an active repository.
4. Independent replay (no master writes):
   `bash scripts/owner-replay.sh <new-worktree> <integration-commit> <verified-operand-root> <report-dir>`
   must report zero differing files, 0 validator errors and 14/14 mutations.
5. Apply: `git -C ulefone-gq5012bf1-research merge --ff-only integration/canonical-01`, then run
   `verify-inventory.py`, `validate.py` and `test_validate.py` live. The executed canonical result
   and SHA are recorded in the final integration commit message.
6. Do not push.
