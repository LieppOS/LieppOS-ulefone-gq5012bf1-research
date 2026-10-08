# Final audit corrections and validation scope

Final review: 2026-10-08, superseding `9958328`. No component reverse engineering, source rebuild, phone operation or taxonomy migration was performed.

## Corrections

- README, summary, index and A–F tables now derive counts from `components.tsv`; the old hardcoded **45 PARTIAL** reference is removed.
- Ranked targets are status-filtered and have explicit scope, source/behavior residual, evidence, closure criterion, effort, dependency and phone requirement in `NEXT-RE.md` / `next-re.tsv`. DONE VINTF/property/boot-image scopes are in the **integration queue**, not PARTIAL→DONE reconstruction recommendations. No expected 99/31 outcome is assumed.
- `CAMERA-HAL-ISP` is A while its ISP kernel parity remains actionable and unfinished, pending the approved split. Calling it B would incorrectly claim that its kernel/source work was closed. The proprietary whole HAL/3A/tuning/CCU scope cannot close statically; only the proposed kernel child is ranked. OTA and recovery acceptance are D because their remaining closure requires runtime evidence, not module parity. These are classification corrections, not status moves.
- [RT5133 correction](RT5133-CORRECTION.md): withdraw the false newer-bound-device story, mark the declared client **PRESENT-NOT-BOUND**, and reject the camera-LDO rename. The existing static two-module scope remains DONE. The first-stage `rt5133-regulator.ko` listing is taken from the actual extracted `vendor-ramdisks/platform-extracted/lib/modules/modules.load`, not inferred from the client name. Successful module load is not successful device probe.
- Three DT function labels are aligned with the established hardware-axis evidence: SH366003 is a pack fuel gauge, SC8571 is a direct-charge pump, and bound WL2864C/WL2868C is the camera-rail LDO. No ownership class is changed solely by these label corrections.
- Two GPU `.rc` configuration rows formerly had the contradictory pair **UNMAPPED / B**. They are now B under **ANDROID-INIT**, which owns init-file assembly. This does not assign the missing KMD/service implementation to init: three modules, three DT compatibles and four GPU HAL/service rows remain the ten explicit E rows. No extra component is invented.
- Dedicated closure reports and relevant canonical subsystem reports replace circular SUMMARY research links. AVB points to AVB evidence rather than TKCORE. Current workspace README links are separately included; all harvested source paths must exist.
- `SYSTEM-DLKM` is DONE for 60/60 stock GKI ELF-body parity, not a remaining F-class tracker. Boot/property/VINTF/partition/USB/thermal closures are preserved, with explicit remaining integration/runtime limitations. The original 126 figure is conditional on approved migrations, not the current registered count.

## External integration reconciled at final review

While the audit was being finalized, Claude committed research `3abc564` and device `24afa6b` without changing the 94/36/3 directory snapshot. The audit does **not** revert or repeat them. The [latest property STATUS](../../vendor-properties/STATUS.md) and [VINTF STATUS](../../vintf-hal-manifest/STATUS.md) supersede their older README gap descriptions:

- `BoardConfig.mk` now includes `TARGET_VENDOR_PROP += $(DEVICE_PATH)/vendor.prop`. The device file has **327** keys from the original **343**-key missing ledger; the canonical generator explicitly documents **16** exclusions and **one** EGL rewrite. Last-definition-wins corrects three old ledger values. Check inherited/generated keys and emitted-image behavior; do not blindly install all 343 again.
- `proprietary-files.txt` now includes `vendor/etc/vintf/manifest/bluetooth_audio.xml` without `EXTRACT_ONLY`; the vendor `Android.bp` and makefile contain the corresponding prebuilt module. The actual 199-instance ledger now counts **146 PRESENT / 48 SKU-only / 5 SOURCE-BUILT / 0 DROPPED**.
- These are verified source-tree installation facts, **not** an Android build, enforcing-SELinux result or runtime HAL test. The original mandatory integration actions remain visible as preservation/emitted-image/acceptance checks, not falsely reported as still uninstalled. No new property, VINTF or device-tree write was made by this audit.

## Synchronization scope

Unchanged stock firmware, HAL/init-service, secure-world, partition and native-library inventories are reused. Builders regenerate only corrected axes and their dependent joins/reports. If directory statuses changed during Claude's batch, the final reconciliation refreshes existing pack identity/claim metadata and affected status joins once; it does not re-investigate 457 modules or harvest proprietary payloads anew.

## Validation

`check-audit.py` checks workspace/component equality, singleton A–F assignment and reconciled totals, current index/status/path integrity, percent-encoded relative links, every axis-to-normalized row join, the exact GPU E sets, ranked target status, rejected RT5133 rename, conditional taxonomy count and absence of payload files in the audit. `test-final-audit.py` covers completed-target filtering, deterministic reports, encoded/broken links, RT5133 false-binding regression, normalized-row drift, invalid A–F classes and rejected rename consequences.

The final validation run and deterministic output hashes are recorded in [FINAL-VALIDATION.md](FINAL-VALIDATION.md). [Manifest hygiene](MANIFEST-HYGIENE.md) remains a **historical** independent baseline; it is not a current-workspace rerun and was not repaired. The audit does not overwrite `COPY-MANIFEST.tsv`, `REVERSE-ENGINEERING-STATUS.md` or component packs.
