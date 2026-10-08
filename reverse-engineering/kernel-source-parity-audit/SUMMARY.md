# Stock kernel source-parity gap audit — GQ5012BF1

## Answer and limits

**458 distinct stock binary identities, not 457.** There are 457 filenames and 471
partition occurrences. The two `bluetooth.ko` binaries have different SHA256/size:
`vendor_dlkm` is `2df021ea…`, `system_dlkm` is `d2659fb3…`. They must not share a proof
merely because their filenames match. `ALL-457-MODULES.tsv` retains the requested filename
but correctly contains **458** identity rows and every stock path.

| Source class | Count | Evidence-supported interpretation |
|---|---:|---|
| A — VERIFIED_BYTE_EXACT | 100 | 60 system_dlkm ELF bodies; 40 accelerator modules; declared nonbehavioral metadata differences |
| B — VERIFIED_SEMANTIC_EQUIVALENT | 1 | imgsensor, with bounded equivalent function/moved byte-load proof |
| C — REPRODUCIBLE_SOURCE_UNVERIFIED | 4 | FT3680, YFT devinfo, ST21NFC, tkcore source island; required stock acceptance remains incomplete |
| D — SOURCE_CANDIDATE_ONLY | 200 | Located public targets/source candidates; no accepted independent stock-compatible build |
| E — SOURCE_MISSING | 0 | No implementation is affirmatively classified missing; this is NOT a claim that every implementation is sufficient |
| F — PROVEN_NOT_REQUIRED | 0 | No production exclusion meets the requested evidential standard |
| G — UNRESOLVED | 153 | Historical source builds/parity exist, but independent recipe/input closure is not established by the reviewed records |
| **Total** | **458** | No unresolved identity dropped |

**101 A/B identities are certified. 357 identities are not certified or legitimately
excluded.** Of those, **204** are known candidate/incomplete-acceptance cases (200 D + 4 C),
and **153 remain unclassified for independent reproducibility**. Do not describe this as
357 new reverse-engineering projects: the 153 G cases include large, already reconstructed
stacks whose existing code and parity must be preserved rather than redone.

There are **181 uncertified identities required by the retained stock first-stage loader
contract** (187 first-stage identities in total). This is a conditional boot/integration
requirement, not proof that every driver controls indispensable physical hardware. For
**271 identities, production/runtime necessity remains unknown**. No authorized stripped
production configuration or removal-safety proof was supplied, so no F exclusions are made.

Source is located in some form for all 357 remaining identities: 200 public candidates and
157 reconstructed/historically built cases (153 G + 4 C). **Only four have class C's specific
incomplete stock-acceptance finding.** Availability of code is not independent reproduction;
absence of an E finding is not evidence of complete source availability.

## Inventory reconciliation

Read-only recursive hashing of the extracted stock operands gives:

| Location | Occurrences |
|---|---:|
| system_dlkm | 60 |
| vendor_dlkm | 215 |
| vendor_boot platform ramdisk | 196 |
| **Total** | **471** |

Thirteen content-identical cross-partition repeats reduce 471 occurrences to 458 identities.
All identities match `kernel/stock-module-master.csv`; all filenames match the old 457-row
coverage inventory. Every occurrence is retained in `stock_paths`. The old `214 vendor_dlkm`
figure counts filename uniqueness across partitions differently and must not replace the
215 physically shipped vendor_dlkm files.

Actual extracted load lists contain 184 normal vendor_boot entries (183 distinct listed
names), 189 recovery entries, 60 system_dlkm entries and 195 vendor_dlkm entries. All entries
resolve to shipped identities in their respective partitions; list position and hashes are
retained separately. The historical loader model resolves 187 first-stage names, including
four dependency-only modules. Listing/loading does not establish successful probing.

`runtime_status` retains name-level capture evidence separately from source class. Both
Bluetooth binary identities remain runtime-identity-unproven. Direct saved driver/module
symlinks establish binding for **23** identities; unresolved echo paths do not. Binding is
not proof of bus transactions, streaming, userspace use or production indispensability.

## Proof policy — no automatic DONE → A conversion

A/B require a pinned, preserved recipe and independent clean-build acceptance bound to the
specific stock identity. The six maintained accelerator repositories meet that bar; no
reconstruction or compilation was repeated. The public GKI stamped build has two recorded
clean builds and complete ELF-body parity.

C is used for concrete incomplete stock acceptance, not to relabel historical exact builds.
G is deliberately used for historical builds whose independent source-input closure has not
been established. Examples include `/tmp/ispenv.sh` / `/tmp/connenv.sh`, mutable vendor trees,
prepared NFC/camera output directories, generated external-provider tables and private
include operands. Some inputs may be recoverable trivially: **G does not assert that a
recipe is broken or that its driver code is missing**. `REPRODUCIBILITY-RISKS.tsv` records
actual recipe references and the exact unanswered preservation/reproduction question.

This stricter independent-reproduction audit does not revoke previous static parity proofs
or change any DONE/PARTIAL/BLOCKED classification. The 169 rows across 58 DONE owners needing
further source evidence are separately recorded: 25 D, 142 G and 2 C. Ownership often covers
additional related modules that were never the owner's reconstructed `.ko` target.

## GKI/system_dlkm

- GKI build **12901745**, common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.
- Full public manifest/build pins: `kernel/phase4-gki-effective-manifest.xml` and
  `kernel/phase4-gki-build-pins.tsv`; toolchain clang-r487747c, pinned clang
  `7775eb113f960bc69a780b621d03a715914d4bca`.
- Stamping `BUILD_NUMBER=12901745 --config=stamp`, declared `-faddrsig` handling and a
  clean release string reproduce all **60** stock ELF bodies, including build IDs.
- Appended signatures differ: Google release key versus ephemeral build key. This is
  not a code/ABI delta. LieppOS must still choose an appropriate signing/enforcement
  policy; A is not permission to load unsigned replacements into an enforcing stock boot.
- Both complete parity reports and the B1/B2 comparison are preserved in SYSTEM-DLKM.
- These 60 proofs do **not** cover vendor Bluetooth or any other vendor module.

## Dependencies and optional/reference modules

All **26,111 import records** are retained. Stock export parsing independently reproduces
all 4,875 recorded export names and their CRCs, including exported data objects. Every import
has a CRC-matching stock or exact-GKI provider: 26,039 unambiguous records and 72 with multiple
CRC-matching binary identities. These alternatives remain explicit; runtime provider choice
is not invented. CRC equality alone never proves KCFI or an independently source-built provider.

The old 15 optional/reference names were all reevaluated. MET, the Mali DMA-BUF test and
scheduler extensions may be valuable in engineering builds; generic NFC and the TFA98xx
alternative need configuration-specific removal evidence. Some are listed or loaded despite
old 'unused' labels, and TFA98xx/MET backlight have historical source parity. No one-capture
absence or negative DT alias alone supports exclusion. See `OPTIONAL-15-REVIEW.tsv`.

## Prioritized source gaps

1. **Boot clock core:** six new candidate-only targets, exact assignment in NEXT-CLAUDE-TASK.
2. **Boot/storage source preservation:** UFS/RPMB/MMC exact work exists; close immutable
   recipe/input preservation, not another driver reconstruction.
3. **PMIC/regulator/pinctrl and boot power infrastructure:** integrate located public
   sources and measure the specific modules; keep audio/charger leaf work separate.
4. **IOMMU/SMI/interconnect/CMDQ providers:** consumers depend on these unverified source
   providers; group by actual source directory and retain provider blockers separately.
5. **Connectivity:** preserve/reproduce the 21 historical connectivity targets and separately
   integrate remaining candidate platform dependencies; do not redo radio firmware.
6. **Modem/data path:** preserve the 16-source-build set and resolve external input closure;
   modem firmware/IMS algorithms stay outside scope.
7. **Normal-world security:** tkcore has a complete source island but is not a stock-ABI
   drop-in; 14/19 consumer edges change historical CRCs. Preserve the existing TEE support work.
8. **Audio:** preserve 22 exact historical modules; ADSP capability is not instantiated hardware.
9. **Sensors/touch/OEM registry:** FT3680 code/semantic residuals and YFT enum/export-CRC/KCFI
   gaps are concrete; do not reopen the closed sensor-hub algorithm/firmware boundaries.
10. **Display/camera/peripheral source packaging:** preserve existing DRM, lens, EEPROM,
    charger and support closures; independently resolve their build inputs before certification.

The complete finite map is `RECONSTRUCTION-PROJECTS.tsv` / `RECONSTRUCTION-QUEUE.md`:
156 scoped source/preservation projects, not 458 isolated projects and not one giant BSP project.

## Reproduction and validation

From the research repository:

```sh
python3 reverse-engineering/kernel-source-parity-audit/scripts/inventory.py
python3 reverse-engineering/kernel-source-parity-audit/scripts/review.py
python3 reverse-engineering/kernel-source-parity-audit/scripts/generate.py
python3 reverse-engineering/kernel-source-parity-audit/scripts/validate.py
python3 reverse-engineering/kernel-source-parity-audit/scripts/test_validate.py
```

The validator reports unsupported claims/missing operands rather than repairing them. A
passing audit means the complete ledger and its evidence references are internally validated,
**not** that all module sources are reconstructed or all G questions answered.

Workspace remains **100 DONE / 36 PARTIAL / 3 BLOCKED / 0 TODO**. Existing global manifest
drift (19 hash/size changes, 408 unregistered files, one duplicate) and the stale canonical
Mali status are documented and left untouched. Offline only; no compilation, device access,
folder moves, verified-source edits or pushes were performed.
