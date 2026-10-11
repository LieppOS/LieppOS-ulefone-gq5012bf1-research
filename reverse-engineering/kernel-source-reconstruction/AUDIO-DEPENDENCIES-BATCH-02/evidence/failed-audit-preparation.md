# Preserved isolated audit preparation failures

No live canonical table, assertion or expected hash was changed to obtain the final PASS.

1. `audit-scratch/`: first execution raised FileNotFoundError on `kernel/nothing-module-index.csv`. That preexisting git-ignored input is absent from a fresh Git worktree; its canonical original exists. Subsequent setup aliases only missing original files after checking their already-frozen workspace-input SHA256. The first proposed snapshot is preserved, not reused as final proof.
2. `audit-scratch-v2/`: validator returned46 errors:23 INVALID_EVIDENCE_PATH and23 MISSING_PROOF_INPUT, all referring to the same prior saved `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt`. The actual returned FAIL JSON is preserved as isolated-audit-validation-v2-missing-snapshot.json. The saved offline capture was checked against its preexisting review-input hashes and aliased into this worktree; no new phone/ADB capture was made.
3. `audit-scratch-v3/`: unchanged validator PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES with zero errors; all14 unchanged audit mutation tests PASS. Both original failures remain available. All proposed stock bytes independently match458 frozen identities/471 occurrences through private immutable raw aliases.

The fresh-build failures are separate: independent-proof/failure.json records the killed Git toolchain pin-check process; independent-proof-low-cpu/failure.json records26 genuinely differing intermediate preparation/tool objects with embedded workspace paths. The final shared engine fixes those source compiler flags and fresh B1/B2 objects are exact, without postprocessing or filtering the object gate.

Canonical shared stock-identity drift is a different unresolved integration prerequisite. No shared signature-stripped stock file was repaired by this task.
