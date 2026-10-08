# Stale or unsupported source-completeness claims

Existing records are preserved. This audit changes no component status or generated provenance.

| Earlier claim / shorthand | Current evidence and correction |
|---|---|
| “457 distinct shipped modules” | 457 filenames, **458 binary identities**, 471 occurrences. Vendor and system Bluetooth have different SHA256/size and require separate proof. |
| “214 vendor_dlkm modules” as a physical count | The extracted partition contains **215** `.ko` files. The old name-based coverage total must not replace actual partition occurrences. |
| “E=0 / no unmapped modules” means source complete | The older coverage A–E classes describe ownership, not this audit's source A–G classes. Zero unowned modules does not prove any clean source build. |
| Every DONE owner proves every module assigned to it | 169 uncertified identities are associated with 58 DONE owners: 25 D, 142 G, 2 C. Often only named leaf modules were source-closed, not all umbrella/platform dependencies. No owner is downgraded here. |
| Historical exact module artifacts automatically establish preserved independent reproduction | Real parity is retained, but recipes use temporary environment shims, prepared outputs, mutable vendor trees/provider inputs or private includes. 153 historical-build identities remain G until exact independent input closure is established. This is not a claim that their source code is absent. |
| GKI 60-module source closure proves vendor modules | All 60 system_dlkm ELF bodies match, including build IDs; signatures differ. Vendor Bluetooth has a distinct baseline, and the other vendor modules are not covered by these proofs. |
| Signature delta is a code delta — or can be ignored for deployment | Appended signing data differs without changing ELF code/ABI. Stock signature enforcement can still reject a replacement; LieppOS signing policy is a separate integration decision. |
| 15 old optional/reference modules are automatically production-excludable | No F exclusion is certified. Actual lists/captures, reverse imports, declared DT aliases, engineering use and unknown userspace/removal evidence are recorded per identity in OPTIONAL-15-REVIEW.tsv. |
| The Mali DMA-BUF test has no source because the old index does not resolve its name | Relevant r44p1 `dma-buf-test-exporter.c` exists at pinned public GPU revision `580d08eac018657a993e56b1806407e41a3b9545`. It is D, not missing source, and not one of the eight already closed GPU targets. |
| “scheduler_ext is MET baggage” is a removal proof | A source candidate exists in `sched_cus`; the old grouping does not establish scheduler extension necessity, consumers or removal safety. Keep it unexcluded. |
| Normal-world tkcore source island means stock-compatible drop-in | Phase 3F documents a statically complete provider but only 5/19 historical CRC-compatible consumer edges; 14 private-type CRC edges differ. The normal-world source island is C for stock-compatible acceptance. No proprietary TA work is required by this audit. |
| A module in modules.load is successfully initialized | Load-list membership is separate from name-level runtime loading, confirmed driver/module symlinks, actual hardware transactions and subsystem execution. RT5133's documented failed initial probe is an explicit counterexample. |
| Existing global workspace audit is clean | Pre-existing 19 hash/size drifts in five components, 408 unregistered files in nine components and one duplicate remain. No unrelated records are changed to conceal them. |
| Mali is still an unfinished accelerator reconstruction | Its organized workspace/source package is DONE; the older canonical component ledger still says PARTIAL. This pre-existing drift is recorded, not repaired. |

## What the new counts do not claim

- **357 uncertified/unexcluded identities are not 357 missing implementations.**
- **0 class E is not proof that every candidate is sufficient.** The 153 G source claims
  remain unresolved for independent input/recipe closure.
- **153 G is not a reversal of measured byte/semantic parity.** Preserve that work and
  resolve its reproduction evidence; do not reverse-engineer it again.
- **181 boot-contract gaps are conditional on retaining the stock first-stage load model**,
  not an assertion that all 181 drivers control essential fitted hardware.
- **271 unknown necessity results must not be turned into F just to shrink the queue.**
