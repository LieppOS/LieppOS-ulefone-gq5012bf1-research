# PLATFORM-BATCH-03 — independent offline source reproduction

## Frozen scope

Research freeze `7ab3c16`; manifest SHA256
`07940aeefe13a9c3fa50a2ba2e8fb9cee75ce1e057942b0d5da34215896246d5`.
All 34 unchanged Batch02 proposal identities (28 D / 6 G) were processed. See
SOURCE-REPOSITORIES.tsv for the five exact maintained commits and owned targets.
Each committed engine builds the joint batch; ownership is not expanded to external providers.

## Public inputs

- ALPS implementations: `5e415e059253ce0d2e61c97108e5f5785d71f06f`, tree `9c61acc3cb0d9bb7f5dbabb51adc2b3fd993810c`.
- NothingOSS Kconfig/defconfig: `957dac185efe46cbf6336b0fff9516d84c8cd78f`.
- GKI common: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.
- Android Clang17.0.2/r487747c: `7775eb113f960bc69a780b621d03a715914d4bca`.
- Native common BTF tools/pahole1.23: `e905be252a53d20c52bd9e59df3ff8fdd46b9eab`.
- Public GKI CI12901745 vmlinux SHA256: `27abab46089851dd9c25910074b8cd2ca04db8578aa887fc0d074baba7f8c030`.

The CI vmlinux is a documented public ABI/BTF base, not an OEM/stock object transplant,
and does **not** reproduce the OEM split-BTF references. Native ADC remains C.
Verified offline source mirrors live at `/home/armol/kernel-work/interconnect-pin-mirror`
and `/home/armol/kernel-work/platform-batch-03-native-inputs` (public vmlinux and
kernel-build-tools.git). Immutable URL/commit/tree/hash records and input checks are
in every recipe's SOURCE-PINS.tsv and reference/native-public-artifact.json.

## Full source and deltas

All 6619 C/H files in the assembled vendor tree were checked:
6614 immutable ALPS blobs; three complete implementation patches; one witness
containing genuine preserved historical charger declarations; one immutable common ADC.
No selected body is reconstructed from stock executable bytes.

1. `mt6375.c`: recovered historical IRQ acknowledgement behavior.
2. `mtk_peak_power_budget.c`: source-level removal of the stock-absent callback/registration.
3. `charger_cooling.c`: stock-equivalent cooling policy and source-level warning locations.

The three source patches are independently reapplied to genuine public files by
scripts/verify-preservation.py. Witness declaration lines and full historical source
hashes are verified there; declaration-only witnesses do not close whole charger providers.
Kbuild changes scope target/provider compilation and preserve the real common in-tree
native ADC path. Configs and compiler commands are recorded in evidence/build;
evidence/host-config-drift.md documents the host's legacy defconfig regeneration drift.
The accepted config derives from preserved verified vendor preparation, not unrecorded
host defaults. Generated headers and preparation are reproducibly obtained by the recipes.

## Reproduce offline

From a clean clone of any SOURCE-REPOSITORIES.tsv repository:

```sh
export TMPDIR=/tmp TMP=/tmp TEMP=/tmp PYTHONDONTWRITEBYTECODE=1
export LIEPPOS_IOMMU_MIRROR=/home/armol/kernel-work/interconnect-pin-mirror
export LIEPPOS_BATCH03_NATIVE_MIRROR=/home/armol/kernel-work/platform-batch-03-native-inputs
export JOBS=12
bash scripts/bootstrap.sh /home/armol/kernel-work/my-batch03
bash scripts/native-bootstrap.sh /home/armol/kernel-work/my-batch03
bash scripts/bulk-build.sh /home/armol/kernel-work/my-batch03 B1
bash scripts/bulk-build.sh /home/armol/kernel-work/my-batch03 B2
LIEPPOS_VERIFY_JOINT=1 python3 scripts/verify.py /home/armol/kernel-work/my-batch03/out/B1
```

The final verification intentionally rejects ADC whole-ELF acceptance. Run the research
scripts/compare-batch.py with LIEPPOS_BATCH_RECIPE pointing to that source clone for
per-module ledgers, and scripts/diagnose-native.py for explicit incomplete ADC evidence.
Only a structurally parsed GNU 20-byte build-ID descriptor may be normalized.
No CRC, symbol, relocation, BTF or executable/data patch is allowed.

## Independent proof already performed

`scripts/cleancheck.sh` cloned all five committed recipes without hardlinks, renamed the
original recipes and development workspace `.unavailable`, bootstrapped a separate
workspace, then freshly assembled/compiled all 34 through each engine as B1 and B2.
EXIT-trap restoration completed; the originals are available again.

Evidence: `evidence/cleancheck-result.json`, full logs in evidence/build and per-family
acceptance ledgers. Ten complete compilations, each with 34 raw/stripped modules,
130 vendor target/provider intermediate objects plus two native objects. B1/B2 and
cross-family source identities, config, symvers and all outputs are identical. Target
and witness objects were not reused; verified common preparation/public header inputs
were reused explicitly. 33 modules pass complete stock acceptance in every run;
ADC consistently fails only the 21 split-BTF reference bytes (261-byte .BTF section).
All ADC functions/data/ABI/relocations/metadata/layout otherwise match. Determinism is
not used to certify that incorrect ELF.

16 actual ELF mutation cases pass, including code/data/relocation/symbol/metadata/BTF,
structural build-ID checks, signatures, and import/export licensing/KCFI guards.
Five Git recovery bundles were verified and freshly cloned back to exact source heads
and tree hashes. See evidence/source-preservation-result.json. Per-module compiled
source units, hashes and real resource/API calls are in SOURCE-TO-HARDWARE-CONTRACTS.json.

## Boundaries

Core symvers/public BTF are scoped ABI inputs, not new whole-kernel certification.
89 non-core source boundaries were checked; 31 external slots have natural source
witnesses. Whole external providers are not promoted. Secure-world RNG/SiP services,
SSPM/SCMI firmware and thermal/MMIO/voltage behavior remain untested. No phone access,
register writes, experimental loading, firmware calls or Git push occurred.
