# Post-`ffa_v10`-closure documentation consistency audit

> **Historical snapshot:** this audit records repository state immediately
> after `ffa_v10` closure. Its statements that `spi-mt65xx` closure remained
> open or that MicroArray was stock-held are superseded by
> `phase4-spi-mt65xx-post-closure-consistency-audit.md`. Current status is
> source-built/frozen `fingerprint` + `spi-mt65xx` + `microarray_fp_tee`, with
> unreconstructed stock-runtime `tkcore`.

**Scope:** documentation-only synchronization after the `ffa_v10` source
closure (`kernel/phase4-ffa-v10-reconstruction.md`, commit `8457d10`). No
reverse engineering, no source/Kbuild/BUILD.bazel/Module.symvers edits, no
device interaction. Verifiers were re-run read-only to confirm no textual
claim drifted from the actual (unmodified) build artefacts.

## Authoritative current state (restated for reference)

| module | classification | key numbers |
|---|---|---|
| `ffa_v10` | `DIRECT_SOURCE_MATCH` / `SOURCE_NOW` / `FROZEN FOR RE` | 34/34 functions byte-identical, 34/34 kCFI exact, 40/40 kernel imports, 41/41 MODVERSION entries, **5/5 exports NATURAL**, 49/49 verifier |
| `tkcore_drv` | `SOURCE_RECONSTRUCTED` / `SOURCE_NOW_WITH_PROVIDER_WITNESSES` / `PROVIDER_ABI_PARTIAL` / `FROZEN FOR RE` | **8 NATURAL / 5 STOCK_PROVIDER_WITNESS** (was 6/7), **43/43 verifier** (was 37/37), rebuilt `.ko` byte-identical to pre-closure build, behavior not reopened |
| `tkcore` | `NO_PUBLIC_SOURCE_FOUND` / `PROVIDER_ABI_PARTIAL` / `NOT RECONSTRUCTED` / `STOCK RUNTIME PROVIDER` | unchanged: 14/25 natural, 11/25 `PROVIDER_ABI_BLOCKED` on TrustKernel private headers/member names |

`tkcore_drv`'s 5 remaining `STOCK_PROVIDER_WITNESS` edges are exactly:
`tee_core_alloc`, `tee_core_add`, `tee_core_del`, `__tee_get`,
`tee_supp_cmd` — all tkcore, all blocked on TrustKernel private struct member
names. Neither `ffa_driver_register` nor `ffa_driver_unregister` is a
witness of any kind in current documentation; both are `NATURAL_FFA`.

Stock load order, unchanged and re-confirmed nowhere reordered:
`ffa_v10 → teeperf → tkcore → tkcore_drv` (P:97–P:100, R:95–R:98).

## 1. Files audited

Explicitly named in the task, all read and checked:

- `kernel/zero-blob-queue.md`
- `kernel/phase4-tkcore-drv-reconstruction.md`
- `kernel/module-replacement-plan.md`
- `kernel/phase4-slot-b-minimum-source-stack.md`
- `kernel/phase4-remaining-module-triage.md`
- `kernel/phase4-remaining-module-dependency-graph.md`
- `kernel/phase4-buildability-plan.md`
- `kernel/unknown-exact-audit.md`
- `kernel/phase4-ffa-v10-reconstruction.md`

Additionally located and audited by the repo-wide grep sweep (per "do not
limit the cleanup to the currently uploaded docs"):

- `kernel/phase4-fingerprint-reconstruction.md` (found one genuine
  `CURRENT_STALE` hit — `tkcore_drv` listed as "stock-held")
- `kernel/phase4-remaining-module-triage.tsv` (raw evidence — left untouched,
  see policy note below)
- `kernel/phase4-tkcore-verify.txt` (raw verifier log, unrelated module —
  false positive, left untouched)
- `kernel/kmi-comparison.md`, `kernel/phase2-local-findings.md`,
  `kernel/phase4-tkcore-stock-inventory.md` (factual/structural mentions of
  `tkcore_drv`'s import counts and stock ELF layout — not status claims, no
  change needed)
- `kernel/phase4-microarray-fp-tee-abi-provenance.md`,
  `kernel/phase4-microarray-fp-tee-reconstruction.md`,
  `kernel/phase4-tkcore-provider-abi.md` (no `ffa_v10`/`tkcore_drv` mentions
  at all — nothing to fix)
- Repo root `README.md`, `docs/README.md`, `docs/build-status.md`,
  `TODO/kernel-enhancement-roadmap.md`, `kernel/ulefone-only-kmi-status.csv`,
  `kernel/phase4-first-batch-matrix.csv` (no mentions of `ffa_v10`, `tkcore`,
  or `tkcore_drv` — nothing to fix)

Search patterns run (all six specified, plus the ad-hoc broader sweeps
described above):

```
rg -n '6 NATURAL|6/13|7 STOCK_PROVIDER_WITNESS|7/13' kernel
rg -n '37/37' kernel
rg -n 'tkcore.*tkcore_drv.*stock|tkcore_drv.*stock' kernel
rg -n 'stock ffa_v10|ffa_v10.*STOCK_PROVIDER_WITNESS' kernel
rg -n 'ffa_driver_register.*STOCK_PROVIDER_WITNESS|ffa_driver_unregister.*STOCK_PROVIDER_WITNESS' kernel
rg -n 'two TEE modules|two entries.*tkcore.*tkcore_drv' kernel
rg -n 'ffa_v10 \[port\]|ffa_v10 \[stock\]|ffa_v10 has not been analysed|ffa_v10 not reconstructed|ffa_v10 witness' kernel
rg -n 'stock tkcore \+ stock ffa_v10|needs stock tkcore \+ ffa_v10|tkcore and tkcore_drv remain stock|tkcore_drv remains stock' kernel
```

## 2. Files changed

| file | what changed |
|---|---|
| `kernel/zero-blob-queue.md` | Main `tkcore_drv` bullet under "Frozen/source-ready" was describing the pre-closure 6/7-split, 37/37-verifier state as current with no label. Rewritten to 8/5, 43/43, with the closure summary sentence and `ffa_v10` bullet retained as-is (already correct). |
| `kernel/phase4-tkcore-drv-reconstruction.md` | Full normalization pass: header verifier count, "Final classification" prose, "ffa_v10 provider edges" section (both edges reclassified `STOCK_PROVIDER_WITNESS` → `NATURAL_FFA`, with an explicit labeled historical callout), "ABI provenance split" table (6/7/7 → 8/5/5 with a `NATURAL_FFA` row and a labeled historical table), "Source provenance" table row (7 witness CRCs → 5), "Behavioral verifier" section (rewrote the 9-item check list to match the live 43-check script, including check 3b and the updated check 2/6 wording, with a labeled historical callout for the pre-closure 37-check version), evidence-index table row (37 checks → 43), "Final verdict" section (rewrote the summary paragraph and the per-symbol split, added the `ffa_v10` current-status line). No behavioral/reconstruction claims were altered. |
| `kernel/module-replacement-plan.md` | The "Priority 8" summary paragraph after the already-correct closure bullets still said "the completed `fingerprint`... consumer can both be source-built while `tkcore` and `tkcore_drv` remain stock." Corrected to name only `tkcore` as stock, and added a clarifying note that `ffa_v10` is not a direct `microarray_fp_tee` provider and that `spi-mt65xx` provider closure remains a separate open item. |
| `kernel/phase4-slot-b-minimum-source-stack.md` | Level C table: added an explicit `ffa_v10` row (previously absent from this table) and updated the `tkcore_drv` row with its current 8/5, 43/43 numbers. Replaced the stale "Two entries (`tkcore`, `tkcore_drv`) may reasonably remain stock indefinitely" paragraph with wording that isolates `tkcore` as the only remaining genuinely-stock entry, and added an explicit paragraph distinguishing the Level-A "retain stock binaries for first boot" **strategy** from source-reconstruction **status**, so the two are never conflated again. |
| `kernel/phase4-remaining-module-triage.md` | (a) Triage table (§6): fixed the `tkcore_drv` disposition cell from "6 NATURAL + 7 STOCK_PROVIDER_WITNESS; 37/37 verifier" to "8 NATURAL + 5 STOCK_PROVIDER_WITNESS; 43/43 verifier" with an inline before/after note; added a new `ffa_v10` row (marked as a cross-reference, not one of the original 23 `§5.3` entries) with its current classification. (b) §16 "Safe to keep temporarily as stock transition blobs": removed `tkcore_drv` from the "keep stock" list (it no longer is) and added a note that both `tkcore_drv` and `ffa_v10` have graduated, leaving only `tkcore` in this TEE pair. |
| `kernel/phase4-remaining-module-dependency-graph.md` | §5 TEE/SECURITY cluster diagram redrawn to show `ffa_v10` and `tkcore` as two separate root providers (previously merged into one ASCII block that obscured which edges belong to which provider), explicitly listing all three `ffa_v10` consumers (`tkcore_drv`, `tmem_ffa`, and the newly discovered `gz_main_mod`) with a caption explaining `gz_main_mod`'s provenance and scope boundary. Labels changed from `[port]`/`[stock]` to `[SOURCE / FROZEN]` for `ffa_v10` and an explicit "blocked on original TrustKernel private headers" annotation for `tkcore`. Stock load order line (`ffa_v10 → teeperf → tkcore → tkcore_drv`) was not touched — already correct and unchanged. |
| `kernel/phase4-buildability-plan.md` | The "tkcore_drv closure update" section's "Results: ..." paragraph stated 37/37 with no indication it had been superseded two paragraphs later. Added an explicit "at the time of this closure" / "Current status (post-`ffa_v10` closure)" framing so the two adjacent sections no longer contradict each other on a casual read. |
| `kernel/unknown-exact-audit.md` | No change required — its current-resolution note for `tkcore_drv` already correctly stated 8 NATURAL/5 STOCK_PROVIDER_WITNESS and 43/43 (was 37/37, explicitly labeled) from the prior closure task. Historical exact-source-scan entries for `tkcore`/`tkcore_drv` were left untouched per policy. |
| `kernel/phase4-fingerprint-reconstruction.md` | Not in the original file list, found by the repo-wide sweep. "Final classification" section stated "`tkcore_drv` remain[s] separate unresolved/stock-held" as a blanket, unlabeled current claim. Corrected to name only `tkcore` as stock-held and added a note that `tkcore_drv`/`ffa_v10` were later source-closed by a separate task, unaffected by and not affecting this fingerprint closure. |
| `kernel/phase4-ffa-v10-reconstruction.md` | Inspected, no change required — already internally consistent (its own "Final verdict" table already states the before/after 6→8 / 7→5 split correctly labeled). |

## 3. Stale current-state statements fixed

1. `zero-blob-queue.md` — `tkcore_drv` primary entry: 6/13, 7/13, 37/37 stated as current → 8/13, 5/13, 43/43.
2. `phase4-tkcore-drv-reconstruction.md` header — "37 checks, 0 failures" stated as the current verifier count → 43/0, with historical count noted.
3. `phase4-tkcore-drv-reconstruction.md` "Final classification" — "7 of its 13 provider ABI edges are `STOCK_PROVIDER_WITNESS`" stated as current → corrected to 5 witness / 8 natural, historical split noted separately.
4. `phase4-tkcore-drv-reconstruction.md` "ffa_v10 provider edges" — both `ffa_driver_*` edges classified `STOCK_PROVIDER_WITNESS` with "GKI... cannot regenerate them... `ffa_v10` itself was not analysed" stated as current → reclassified `NATURAL_FFA`, historical callout added.
5. `phase4-tkcore-drv-reconstruction.md` "ABI provenance split" table — `NATURAL` 6 / `STOCK_PROVIDER_WITNESS` 7 / `PROVIDER_ABI_GAP` 7 stated as current → `NATURAL` 6 + `NATURAL_FFA` 2 (total 8) / `STOCK_PROVIDER_WITNESS` 5 / `PROVIDER_ABI_GAP` 5, historical table added.
6. `phase4-tkcore-drv-reconstruction.md` "Source provenance" table — "only the 7 declared `STOCK_PROVIDER_WITNESS` CRCs" → 5.
7. `phase4-tkcore-drv-reconstruction.md` "Behavioral verifier" — 9-check, 37-check description stated as current → rewritten to match the live 43-check/10-item script output, historical version noted.
8. `phase4-tkcore-drv-reconstruction.md` evidence index — "fail-closed verifier (37 checks)" → 43 checks (current), 37 (historical) noted.
9. `phase4-tkcore-drv-reconstruction.md` "Final verdict" — "37/37 verifier checks", "6 provider edges are NATURAL, 7 are STOCK_PROVIDER_WITNESS", "`tkcore` and `ffa_v10` are not source-pure... remain stock runtime providers" (false for `ffa_v10`) → 43/43, 8 NATURAL/5 STOCK_PROVIDER_WITNESS, `ffa_v10` current status stated separately from `tkcore`.
10. `module-replacement-plan.md` — "can both be source-built while `tkcore` and `tkcore_drv` remain stock" → `tkcore` only, with `ffa_v10`/`microarray_fp_tee` scope clarification.
11. `phase4-slot-b-minimum-source-stack.md` — "Two entries (`tkcore`, `tkcore_drv`) may reasonably remain stock indefinitely" → only `tkcore`; `ffa_v10` added to the Level C table (previously absent, an omission rather than a wrong value, but corrected as part of this sweep); explicit boot-strategy-vs-source-status disambiguation paragraph added.
12. `phase4-remaining-module-triage.md` §6 — `tkcore_drv` disposition cell "6 NATURAL + 7 STOCK_PROVIDER_WITNESS; 37/37 verifier" stated as current → 8/5, 43/43; `ffa_v10` row added.
13. `phase4-remaining-module-triage.md` §16 — `tkcore_drv` listed among modules where "keep stock" is the current recommended disposition → removed, with a note that it (and `ffa_v10`) have graduated.
14. `phase4-remaining-module-dependency-graph.md` §5 — the merged ASCII diagram gave the visual impression that `ffa_v10`'s only consumer was `tkcore_drv`; redrawn to show all three known consumers, and `gz_main_mod` (a real finding from the `ffa_v10` closure) was entirely undocumented in this graph.
15. `phase4-buildability-plan.md` "tkcore_drv closure update" — "37/37 fail-closed verifier" presented as an unqualified current result immediately above a section that supersedes it → explicit "at the time of this closure" / "current status" framing added.
16. `phase4-fingerprint-reconstruction.md` — "`tkcore` and `tkcore_drv` remain separate unresolved/stock-held modules" stated as current in the Final classification header → `tkcore_drv` removed from that list, with a note pointing to its later closure.

## 4. Historical statements intentionally retained (with rationale)

| location | text (abbreviated) | why retained |
|---|---|---|
| `zero-blob-queue.md:111-113` | "provenance split moved from 6 NATURAL/7 STOCK_PROVIDER_WITNESS to 8 NATURAL/5..." | explicit before→after transition sentence inside the `ffa_v10` closure bullet — describes the delta, not a current-state claim in isolation |
| `phase4-tkcore-drv-reconstruction.md` (multiple, all new in this pass) | "Historical, pre-`ffa_v10`-closure result (superseded above): ..." blocks | added by this cleanup specifically so the historical numbers stay visible without being mistaken for current ones |
| `phase4-buildability-plan.md:1274-1281` | "Results **at the time of this closure** (2026-09-13, pre-`ffa_v10`...): ... 37/37 ..." | now explicitly time-boxed; the chronological build-history narrative (tkcore_drv closure happened before ffa_v10 closure) is preserved per the "do not rewrite old chronological build-history sections" instruction |
| `phase4-buildability-plan.md:1311-1313` | "...verifier 43/43 (was 37/37)..." | correctly labeled before/after, part of the immediately-following "ffa_v10 closure update" section |
| `unknown-exact-audit.md:461` | "43/43 verifier checks (was 37/37 before the..." | already correctly labeled from the prior closure task; this is a historical-audit file by design and its exact-source-scan entries were not touched |
| `phase4-remaining-module-triage.md:179` | "...43/43 verifier — was 6/7 and 37/37 before the 2026-09-13 `ffa_v10` closure" | current value stated first, historical value explicitly labeled and dated |
| `phase4-remaining-module-triage.tsv` rows 7-8 | `NO_USEFUL_SOURCE`, `STOCK_TRANSITION_BLOB`, "Retain stock tkcore_drv.ko; keep ffa_v10 on stock too, or prove ffa_v10's 2 consumed export CRCs before rebuilding it" | raw historical baseline data from the original triage population/subtraction methodology (§5 of the .md companion); the .md document's own table (§6) carries the maintained current-status annotation, and per task policy raw TSV evidence is not rewritten to change prose |
| `phase4-tkcore-verify.txt:27` | "[PASS] tkcore_drv edge CRCs match stock provider" | raw verifier log from the **`tkcore`** analysis task (checking that stock `tkcore.ko`'s exports satisfy what the stock `tkcore_drv.ko` binary imports) — this is about `tkcore`'s own export classification, not a claim about `tkcore_drv`'s reconstruction status; false-positive match on the search pattern, left untouched as raw evidence |
| `phase4-ffa-v10-reconstruction.md:350-351` | "NATURAL \| 6 \| **8**", "STOCK_PROVIDER_WITNESS \| 7 \| **5**" | already-correct before/after table in the `ffa_v10` report's own Final Verdict section |
| `phase4-fingerprint-reconstruction.md:360` | "`microarray_fp_tee`, `tkcore`, and `tkcore_drv` are not reconstructed or marked complete **by this work**" | scoped to what the fingerprint task itself accomplished (true then and still true now — that task did not reconstruct them), not a claim about present-day global status |
| `phase4-tkcore-drv-recon/Makefile.{stockabi,natural}` comments | "the FF-A bus provider is a module on this platform (stock ffa_v10.ko)" | build-rationale comment explaining why `CONFIG_ARM_FFA_TRANSPORT_MODULE` is needed; describes the platform's module packaging fact (FF-A ships as a `.ko`), not a provenance claim; per task policy, Makefiles are not edited for prose reasons |

## 5. Consistency invariants — result

| # | invariant | result |
|---|---|---|
| 1 | ffa_v10 is source-closed | ✅ |
| 2 | ffa_v10 is DIRECT_SOURCE_MATCH | ✅ |
| 3 | ffa_v10 is FROZEN FOR RE | ✅ |
| 4 | ffa_v10 has 5/5 naturally reproduced export CRCs | ✅ |
| 5 | ffa_v10 verifier is 49/49 | ✅ |
| 6 | tkcore_drv is source-reconstructed | ✅ |
| 7 | tkcore_drv is FROZEN FOR RE | ✅ |
| 8 | tkcore_drv current provider split is 8 NATURAL / 5 STOCK_PROVIDER_WITNESS | ✅ |
| 9 | tkcore_drv current verifier is 43/43 | ✅ |
| 10 | the remaining five tkcore_drv witnesses are only `tee_core_alloc`, `tee_core_add`, `tee_core_del`, `__tee_get`, `tee_supp_cmd` | ✅ |
| 11 | no current statement calls either `ffa_driver_*` edge a stock witness | ✅ (zero live hits; all matches are historical/labeled or raw-evidence false positives) |
| 12 | tkcore remains NOT RECONSTRUCTED | ✅ |
| 13 | tkcore remains the stock runtime provider | ✅ |
| 14 | tkcore remains blocked on original TrustKernel private headers/type member names | ✅ |
| 15 | ffa_v10 closure does not promote tkcore | ✅ (explicit non-promotion statements present in every touched file) |
| 16 | source status and Level-A "use stock for minimal boot" policy are not conflated | ✅ (explicit disambiguation paragraph added to `phase4-slot-b-minimum-source-stack.md`) |
| 17 | stock load order remains ffa_v10 → teeperf → tkcore → tkcore_drv | ✅ (unchanged everywhere; re-confirmed, not reordered) |

## 6. Repo-wide stale-hit scan (post-cleanup)

All six mandated patterns plus two supplementary ones (`ffa_v10 [port]`/`[stock]`/witness phrasing; `stock tkcore + stock ffa_v10`) were re-run after every edit. Final result: **zero `CURRENT_STALE` hits.** Every remaining match is `HISTORICAL_VALID` (explicitly labeled) or `FALSE_POSITIVE` (raw evidence, unrelated module, or build-rationale comment), enumerated in §4 above.

## Verification performed

- `python3 kernel/scripts/phase4_tkcore_drv_verify.py` → 43/43, unchanged by this task
- `python3 kernel/scripts/phase4_ffa_v10_verify.py` → 49/49, unchanged by this task
- No `.c`/`.h`/`Makefile`/`BUILD.bazel`/`Module.symvers`/oracle/raw-TSV file was modified
- No module was loaded, unloaded, probed, flashed, or otherwise touched on the device

## Not started (per task boundary)

`tmem_ffa` reverse engineering, `gz_main_mod` reverse engineering,
`spi-mt65xx` provider closure, connectivity work, panel/provider work,
`yft_devinfo`, `uSmart`.

## Result

**DOCUMENTATION CONSISTENCY: PASS**
