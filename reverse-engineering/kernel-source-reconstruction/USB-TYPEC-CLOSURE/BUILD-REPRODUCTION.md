# Independent source reproduction — passed, stock closure still incomplete

## Committed inputs

Type-C engine: `758f9edc78c7a50d07b8629126438a3674845911`.
Charging/shared engine: `b2a343a9d8664b77a63dc16835b5af0fd0e55cf1`.
See [source lineage](SOURCE-LINEAGE.md), complete source bundles and their SHA256 records. Source C/header tree is `2f08a85f28379aff76414c01ec8b6d3fc6ba5af1`; public/common/config/compiler/GKI pins are unchanged. Debug-only prefix maps are explicitly recorded.

## Actual clean builds

`evidence/fresh-clones/result.json` records **four complete builds**: two separately recovered source engines, each in independently bootstrapped B1/B2 workspaces. Source bundles were verified, recovered clones passed `git fsck --full`, and no Git alternates or original target objects were used. The task's own original recipe/development paths were unavailable during all four builds and restored afterwards. Canonical/other-agent checkouts were never moved or edited.

- All 30 existing Batch04 targets source-built in each run. This is preservation/reproduction of the existing batch, not a new reconstruction batch.
- All **30 raw modules and 30 stripped modules are byte-identical across four runs**, including their GNU build IDs.
- All **157 actual intermediate objects** are byte-identical; SHA manifests were checked against real files, not merely compared to each other.
- Configurations, core GKI symvers, natural external provider symvers, source-tree hash and provider witnesses/errors are byte-identical. No provider-generation errors.
- All **437 joint export records** have identical CRC, name, license, namespace and source-tree-relative producer identity. Raw joint `Module.symvers` text contains different absolute workspace prefixes in its producer column; those original files and hashes remain preserved. Resolving this explicit build-location column is not an ELF/CRC/source-metadata acceptance exemption.
- All **25 previously certified modules retain complete strict stock acceptance** in each run. All **five selected targets still reject**, as expected from their documented real ELF residues.
- **23 real verifier mutation/rejection tests pass**: positive original/GNU20 cases, instruction/data/relocation/symbol/CRC/KCFI/metadata/layout/signature corruption rejections, and all five unchanged incomplete-target rejections.

All ledgers for the five targets report every code/data object, section layout/content, raw and semantic relocation record, imported/exported CRC/license, KCFI ID, symbol table, `.modinfo`, BTF presence, raw difference range and structural build-ID bounds. Both `.BTF` and `.BTF.ext` are absent in all five operands; this is recorded, not treated as an untested split-BTF waiver.

## Preserved failed attempts

The first four fresh workspace builds exposed actual DWARF-path nondeterminism. Their source bundles, build workspaces and failure diagnosis are retained. Standard `-fdebug-prefix-map` compilation flags fixed that without changing macro/source strings, source fingerprints, instructions or acceptance criteria.

The debug-mapped four-build checker initially compared `SHA256SUMS` wholesale; that manifest also hashes path-bearing joint `Module.symvers` text. Although all raw/stripped module/object bytes already matched, the overbroad text comparison failed. The failure log is retained. The corrected checker directly hashes all actual module/object bytes and compares all precise export fields, including the same relative source producer. No ELF artifact is altered and no acceptance mismatch is waived.

## Separate canonical audit gate

The unchanged live canonical audit validator currently FAILs on60 unrelated missing/60 unexpected stock SHA identities plus frozen-inventory/ownership drift. Its live mutation tests also reject the drift. No canonical audit/source/stock input was repaired or overwritten. The unchanged14 audit mutation tests PASS against the preserved frozen-inventory fixture, explicitly labeled as fixture validation rather than live acceptance. Five selected stock identities remain SHA-verified. Integration is blocked until this separate drift is reconciled; source-build/ELF-mutation PASS does not override it.

## Commands

After setting the desired new, unused proof root and preserving the source worktrees/bundles:

```sh
export PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp
export LIEPPOS_CLOSURE_PROOF_DIR=/home/armol/kernel-work/usb-typec-closure-proof-new
python3 scripts/cleancheck.py
```

`cleancheck.py` recovers committed sources and uses only the dedicated nonwritable local mirror. It must run from this isolated research context with its two owned source worktrees present; it does not operate on the canonical recipes. `validate-cleancheck.py PROOF_ROOT` revalidates existing complete runs without compiling/reusing them as new source-build proofs.

Actual final workspaces are `/home/armol/kernel-work/usb-typec-closure-proof-debugmapped/F{0,1}-B{1,2}/`. Copied proof logs/manifests/config/provider records reside under `evidence/fresh-clones/`; complete five-target ledgers under `evidence/final/full-acceptance/`. Sixty compressed raw/stripped stage operands (baseline through final) are verified by `evidence/compiled-operands/manifest.json`; they are comparison evidence, never build inputs.
