# Actual integration baseline

Canonical checkout: `/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research`. Actual branch master, HEAD **f61ebf03275ba2d3f6aa4f9d5aebe18e12922263**, clean when inspected. Counts A244/B1/C14/D91/E0/F0/G108,245 certified/213 remaining. Neither the three Codex source deltas nor PLATFORM-BATCH-05 was integrated at this recorded start; this was measured, not assumed from the request.

Dedicated staging worktree: `ulefone-gq5012bf1-research-codex-integration`; branch `codex/completed-batches-integration`, created at that exact commit. Additional private replay worktree `ulefone-gq5012bf1-research-codex-integration-replay` demonstrates the owner CAS procedure from the same baseline; it is not canonical or another agent's workspace.

Recorded concurrent Category-C worktree: `ulefone-gq5012bf1-research-codex-all-c-closure`, branch `codex/all-c-to-a-closure`, starting HEAD e0c1754e52b834356ab952bd60ff1bed0bcce71a, five untracked research changes at inspection. User identifies Claude as the concurrent Category-C owner. That branch, its files, source work and build outputs were not edited/reset/rebased. Later activity is allowed; this snapshot does not freeze another agent.

Original research tips preserved verbatim:

| Batch | Research commit | Distinct targets | A/C |
|---|---|---:|---|
| AUDIO-BATCH-01 | f00bd8af7e6bd4fde4355ae67e8392feab596a80 |21|20/1|
| SCP-CONNECTIVITY-BATCH-01 |40bfedda097cc33d05eba145fa0c51d6ceb0a07e|20|17/3|
| AUDIO-DEPENDENCIES-BATCH-02 |fb558640b3227eb57b4172e129c6048b46d07ed6|22|20/2|
| STOCK-INVENTORY-INTEGRITY |143a6db22434216e815e4a16c5da41a255efed2b (includes98acd423)|—|no promotions|

`evidence/baseline-first.json` and `baseline.json` contain actual branch/ref/worktree/owner activity, canonical audit SHA and resource limits. Do not assume this baseline remains current when the owner integrates. Inspect then-current HEAD and reconcile every identity/field; never reset newer totals or copy this audit wholesale over new work.

All continuing commands were capped to four CPUs60–63 and nice10; no reconstruction builds were repeated. No phone/ADB/image/firmware changes or push.
