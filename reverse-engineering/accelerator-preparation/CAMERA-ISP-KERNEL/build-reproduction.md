# Build reproduction — CAMERA-ISP-KERNEL

## One-command acceptance

From a clone of the maintained source repository:

```sh
./scripts/bootstrap.sh /absolute/path/to/workspace
./scripts/b1b2.sh /absolute/path/to/workspace /absolute/path/to/stock-modules
```

`bootstrap.sh` obtains and verifies every public input by commit **and** git tree id (or
fixed SHA-256 for the archived GKI symvers). `b1b2.sh` then performs two independent clean
runs: source extraction, patch application, kernel output preparation, provider-CRC
derivation, all nineteen module builds, full stock comparison, and B1/B2 comparison.
Nothing is reused between B1 and B2 except immutable downloaded inputs.

## Pinned environment

* kernel: AOSP common `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, Android CI
  build 12901745 KMI, release `6.1.115-android14-11-g945dff7bc1bf`;
* compiler: Android clang `clang-r487747c`, prebuilt commit `7775eb113f96`;
* source: NothingOSS kmod `5f75a3b13e81` and kdm `957dac185efe`;
* config: `gki_defconfig` merged with `mgk_64_k61_defconfig`, then `modules_prepare`;
* critical flags/shape: `KCFLAGS=-faddrsig`, `module_scmversion=`, one modpost scope per
  package, and a kbuild output mirror whose source paths resolve through `VPATH`.

The exact pins, expected trees and patch hashes live in the source repository; see
[SOURCE.md](SOURCE.md).

## Clean-checkout result

The retained transcript is
`evidence/reconstruction/build/b1b2-clean-checkout.log`. It ends in successful B1 and B2
verification for all nineteen modules.

B1 and B2 are equal for:

* 19 raw reconstructed `.ko` files and their build-ID-normalized forms;
* all **225** participating target `.o` files;
* every target-package `Module.symvers` and generated external-provider symvers;
* kernel `.config` (`config.sha256`);
* both assembled source tree ids (`SOURCE-TREE`).

Witnesses:

* `B1-SHA256SUMS.txt`, `B2-SHA256SUMS.txt` — module outputs;
* `B1-INTERMEDIATE-SHA256SUMS.txt` — all 225 object outputs;
* `config.sha256`, `SOURCE-TREE` — config and source identities;
* `provider-crc-witnesses.tsv` — provenance of all 107 vendor ABI inputs.

## Stock acceptance

`scripts/verify.py` compares functions, data objects, sections and flags/content, symbol
ordering/values, imports/exports and CRCs, KCFI ids, `.modinfo`, raw and semantic
relocations, strings and raw bytes. Build IDs are the expected nondeterministic 20-byte
residue and are normalized only after their exact location/size is identified.

The aggregate validation in
`evidence/reconstruction/manifest-validation.json` is `PASS`: 2 971 function rows,
2 474 data rows, 2 530 ABI rows, 978 section rows, 71 991 relocation rows, zero unresolved,
and B1 == B2. Of the relocations, 71 990 are raw/semantic identical and one byte load
moves within the proven equivalent function; all section headers match, with the four
non-build-ID content residues explicitly classified.

A post-build verifier audit rechecks both retained B1/B2 outputs without rebuilding:
`evidence/reconstruction/build/post-build-verifier-audit.log`. It also proves arbitrary
text mutations in both residue modules are rejected even without stock operands, while a
build-ID-only change remains accepted. The older clean-build transcript is preserved;
its section-wide relocation labels are superseded by the current row-level ledger.

## Offline preservation

Use `scripts/archive-pins.sh <workspace> <mirror>` while the public hosts are reachable.
The local GKI symvers xz fallback allows bootstrap even when ci.android.com is not.
The authoritative research pack carries a git bundle of the recipe, not downloaded source
checkouts or proprietary binaries.
