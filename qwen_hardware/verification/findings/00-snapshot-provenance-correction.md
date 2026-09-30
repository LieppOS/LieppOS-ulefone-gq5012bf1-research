# Cross-cutting correction: the "live-stock" snapshot is a GSI, not stock system

**Current claim (original audit):** framework-level observations in the 2026-08-31 capture describe what *stock Ulefone software* does.

**Previous confidence:** implicit PROVEN throughout the original reports ("stock framework policy", "stock lists 4K30", "500-nit policy cap").

**New evidence**
* `identity.txt`: `[ro.lineage.display.version]: [LieppOS-23-20260830-VANILLA-EROFS-GSI]`
* `identity.txt` first line: `uid=0(root) ... context=u:r:ksu:s0` -> KernelSU-rooted
* `[ro.build.display.id]: [BP4A.251205.006 release-keys]` while `[ro.build.fingerprint]` still carries the stock vendor fingerprint `Ulefone/GQ5012BF1_EEA/GQ5012BF1:15/AP3A.240905.015.A2/...` - the classic GSI signature (stock vendor + replaced system)
* `packages.txt` contains `org.lineageos.setupwizard`, `LineageSettingsProvider`, `SimpleSettingsConfig` and **zero** Ulefone/YFT/thermal packages, while the extracted stock images do contain `YftSystemUI`, `YftSettings`, `YftSmartTouch`, `YftFmRadio`, `M170infisens`, `M170infDlp`

**Contradicting evidence:** none. The snapshot directory name (`live-stock-adb-...`) is simply mislabelled.

**Internet sources:** none — this finding rests entirely on local artefacts, so no `VI` id applies.

**Local evidence:** VL25 (`identity.txt`, `packages.txt`) and VL16 (the stock `M170infisens`/`M170infDlp` APKs that are absent from the GSI); normalised in `../evidence/live-runtime-extracts.md` (Snapshot provenance section).

**Read-only live evidence:** the snapshot itself; no new device queries were possible.

**Final conclusion**
Kernel-, driver-, device-tree-, bus- and vendor-partition-derived facts in the capture remain fully valid: the vendor/kernel side was untouched. But every *Android framework* observation must be re-labelled **"observed under LieppOS GSI"**, not "stock uses". Specifically these original statements are no longer supportable as stock behaviour:
* the 500-nit brightness policy and absence of AOD/CABC (GSI display config; the panel is rated 2200 nits peak by the OEM, and the GSI reports `mNits=[2.0, 490.0]`),
* "stock lists 4K30 / 1080p30" video policy (that was the GSI camera app, not Ulefone's),
* the enabled `bluetooth.profile.bap.*` LE-Audio properties (AOSP/Lineage defaults),
* "no thermal camera application" (the Ulefone apps exist in the stock images; they were simply absent from the GSI).

**Final confidence:** PROVEN.

**Remaining uncertainty:** what the genuine Ulefone stock framework exposes (brightness curve, camera video menu, LE Audio toggles) is now **unmeasured**; it needs a capture taken on the untouched stock system.

**Impact on final inventory:** MASTER-HARDWARE-INVENTORY, HARDWARE-CAPABILITY-MATRIX, UNUSED-HIDDEN-CAPABILITIES and FINAL-REPORT all had "STOCK USES" cells populated from GSI observations; they are corrected and re-labelled.
