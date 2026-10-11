# Stale or unsupported source-completeness claims

Existing records are preserved. This audit changes no component status or generated provenance.

| Earlier claim / shorthand | Current evidence and correction |
|---|---|
| “457 distinct shipped modules” | 457 filenames, **458 binary identities**, 471 occurrences. Vendor and system Bluetooth have different SHA256/size and require separate proof. |
| “214 vendor_dlkm modules” as a physical count | The extracted partition contains **215** `.ko` files. The old name-based coverage total must not replace actual partition occurrences. |
| “E=0 / no unmapped modules” means source complete | The older coverage A–E classes describe ownership, not this audit's source A–G classes. Zero unowned modules does not prove any clean source build. |
| Every DONE owner proves every module assigned to it | 158 uncertified identities are associated with 56 DONE owners: 24 D, 132 G, 2 C. Often only named leaf modules were source-closed, not all umbrella/platform dependencies. No owner is downgraded here. |
| Historical exact module artifacts automatically establish preserved independent reproduction | Real parity is retained, but recipes use temporary environment shims, prepared outputs, mutable vendor trees/provider inputs or private includes. 143 historical-build identities remain G until exact independent input closure is established. This is not a claim that their source code is absent. |
| GKI 60-module source closure proves vendor modules | All 60 system_dlkm ELF bodies match, including build IDs; signatures differ. Vendor Bluetooth has a distinct baseline, and the other vendor modules are not covered by these proofs. |
| Signature delta is a code delta — or can be ignored for deployment | Appended signing data differs without changing ELF code/ABI. Stock signature enforcement can still reject a replacement; LieppOS signing policy is a separate integration decision. |
| 15 old optional/reference modules are automatically production-excludable | No F exclusion is certified. Actual lists/captures, reverse imports, declared DT aliases, engineering use and unknown userspace/removal evidence are recorded per identity in OPTIONAL-15-REVIEW.tsv. |
| The Mali DMA-BUF test has no source because the old index does not resolve its name | Relevant r44p1 `dma-buf-test-exporter.c` exists at pinned public GPU revision `580d08eac018657a993e56b1806407e41a3b9545`. It is D, not missing source, and not one of the eight already closed GPU targets. |
| “scheduler_ext is MET baggage” is a removal proof | A source candidate exists in `sched_cus`; the old grouping does not establish scheduler extension necessity, consumers or removal safety. Keep it unexcluded. |
| Normal-world tkcore source island means stock-compatible drop-in | Phase 3F documents a statically complete provider but only 5/19 historical CRC-compatible consumer edges; 14 private-type CRC edges differ. The normal-world source island is C for stock-compatible acceptance. No proprietary TA work is required by this audit. |
| A module in modules.load is successfully initialized | Load-list membership is separate from name-level runtime loading, confirmed driver/module symlinks, actual hardware transactions and subsystem execution. RT5133's documented failed initial probe is an explicit counterexample. |
| Existing global workspace audit is clean | Pre-existing 19 hash/size drifts in five components, 408 unregistered files in nine components and one duplicate remain. No unrelated records are changed to conceal them. |
| Mali is still an unfinished accelerator reconstruction | Its organized workspace/source package is DONE; the older canonical component ledger still says PARTIAL. This pre-existing drift is recorded, not repaired. |
| BOOT-CLOCK-CORE is D: public candidate likely sufficient, "no demonstrated missing implementation or required OEM patch" | Measured 2026-10-09: four of six were exact from public ALPS `5e415e059253`; `clk-mt6878`/`clk-mt6878-peri` needed the GQ5012BF1 display-PWM clock delta (mux ID 282, gates 31/32) that upstream `591991d44aad` removed. All six are now A. |
| PRESERVE:STORAGE is G: historical exact storage rebuilds without independent input closure | Measured 2026-10-09: the historical artifacts were exact, but the recipe depended on a since-modified shared kout, stock-harvested `stock-all.symvers`, a hand-edited `-ise` symvers and copied headers. All replaced by pinned/regenerated inputs; all ten are now A (`../kernel-source-reconstruction/STORAGE/STALE-CLAIMS.md`). |
| PINCTRL remains four public-candidate-only D rows | Measured unchanged ALPS 5e41 C reproduces all four full stripped ELFs except GNU build ID; independent clean B1/B2 and all ABI/data/table/relocation proof now permits four A rows (`../kernel-source-reconstruction/PINCTRL/`). |
| REGULATORS are still four public candidates D; RT6160 load_order133 is current | Unchanged ALPS C now reproduces all four complete ELFs except GNU ID, with independent clean B1/B2 and real provider CRC witnesses; all four A. Actual hashed stock lists prove RT6160 normal124/recovery122; only its target metadata corrected, no list changes (`../kernel-source-reconstruction/REGULATORS/`). |
| MMQoS/EMI are three public candidates only; audit load67/68/47 is current | Unchanged ALPS C is complete stock-exact except GNU IDs, with independent B1/B2 and33 real provider CRC/licence/KCFI boundaries. Exactly three A; actual stock normal61/62/51 (recovery59/60/50), no list edits. mtk-emi is the ICC vote wrapper, not the separate EMI controller (`../kernel-source-reconstruction/INTERCONNECT-EMI/`). |
| Original four IOMMU names authorize a four-module closure; main load71 is current | Only current drivers/iommu target mtk_iommu moved D→A via unchanged ALPS C, independent B1/B2 and complete ELF parity. Normal65/recovery63; debug/secure/test remain separate D. No taxonomy promotion or runtime-DMA proof (`../kernel-source-reconstruction/IOMMU/`). |

| Batch03 deterministic all34 means A/B all34 | Five committed engines independently build all34 B1/B2;33 have full whole-ELF acceptance. Native ADC remains C:21 .BTF reference bytes differ although all functions/data/CRC/KCFI/relocations/layout match. Determinism does not waive metadata acceptance. |
| The public CI BTF base is the OEM source lineage | Public CI12901745 is a pinned source-derived provider input, not OEM g945dff7bc1bf BTF. Authentic matching declaration/tool/base lineage remains to be found; no stock BTF transplantation or field editing is permitted. |
| Reused maintained recipe HEAD must equal every previous batch's accepted commit | A later scoped recipe commit does not invalidate an immutable accepted ancestor. Batch02 acceptance/ownership/reference records are checked at its exact preserved Git commit, not the advanced Batch03 HEAD. No previous audit identity is reclassified. |

| Batch04 old DONE/code-exact history makes all30 certified | Three committed engines freshly build all30 six times,25 whole-accepted A;five remain strict C for source-token/counter metadata and TCPC behavior/data/layout. A bounded separate TCPC experiment improves701→702/709 bodies but is not accepted or substituted into the six-build proof. |
| Legacy uvc_switch/vbus GPIO names identify thermal-camera controls | GPIO55/152 belong to uSmart route/power. Thermal usesGPIO149/191/192 and tiny2c_mode; same USB0 role/fabric, physical default-route sharing remains UNKNOWN. Existing USB topology corrected from actual earlier uSmart/thermal evidence; no new hardware test. |
| Unsigned local copies may replace frozen signed stock inventory | After interruption,60 local system_dlkm operands lacked721-byte signatures. Original local GQ5012BF1 system_dlkm_a image independently yielded60 exact frozen SHA/size matches; original signed analysis copies restored, drift quarantined, no audit hash or compilation output changed. |

## What the current counts do not claim

- **213 uncertified/unexcluded identities after Batch04 (238 after Batch03,271 after Batch02,298 after Batch01) are not missing implementations.** Earlier checkpoint counts remain historical, not current totals.
- **0 class E is not proof that every candidate is sufficient.** The 108 G source claims
  remain unresolved for independent input/recipe closure.
- **108 G is not a reversal of measured byte/semantic parity.** Preserve that work and
  resolve its reproduction evidence; do not reverse-engineer it again.
- **74 boot-contract gaps after Batch04 are conditional on retaining the stock first-stage load model**,
  not an assertion that all74 drivers control essential fitted hardware.
- **271 unknown necessity results must not be turned into F just to shrink the queue.**
