# Root cause: 60 missing / 60 unexpected stock identities

**Confirmed.** The failure is real damage to 60 local analysis copies, not a validator, baseline or
checkout problem. The 60 signed `system_dlkm` GKI modules in the shared canonical analysis tree
`ulefone-gq5012bf1-research/workspace/gq5012bf1/stock/partitions/system_dlkm/lib/modules/` lost their
721-byte appended module signatures. The canonical audit was correct and the validator correctly rejected the files.

**The damage was caused by Codex's own tool calls during SCP-CONNECTIVITY-BATCH-01, not by another agent.**

## Mechanism

```sh
llvm-objcopy --dump-section .BTF=/dev/stdout <stock .ko>         # incident 2
llvm-objcopy --dump-section=.modinfo=/dev/stdout <stock .ko>     # incident 1
```

Both commands were meant as read-only section dumps, but neither gave an output operand. In that case
`llvm-objcopy` (LLVM 23, `/usr/lib/llvm/23/bin/llvm-objcopy`) writes the re-serialised object **back over
its input**, through a temporary file and a rename, so the file gets a new inode. Its ELF writer keeps only
bytes covered by headers and sections. The kernel module signature (PKCS#7 + `struct module_signature` +
`~Module signature appended~\n`) is appended after all ELF content and belongs to no section, so it is dropped.

- Signed module: rewritten as exactly the unsigned prefix, 721 bytes shorter.
- Unsigned module (all vendor_dlkm / vendor_boot): rewritten to byte-identical content, so nothing is detected.
- Module without the requested section (`.BTF`): `llvm-objcopy` exits 1 and writes nothing.

Reproduced on private copies (`scripts/reproduce-mechanism.sh`, `evidence/root-cause/mechanism-reproduction.log`).
Both forms turn stock `6lowpan.ko` `114382f9…` (59 329 B) into `6d239276…` (58 608 B), the exact
bytes on canonical disk. The safe form with an explicit output operand leaves the input untouched.

## Timeline (`evidence/root-cause/tool-call-timeline.json`, from the agent session log)

| Local time (+0300) | Event |
|---|---|
| 2026-10-11 01:38:12–01:38:19 | **Incident 1.** A Codex connectivity-survey loop over all 458 audit rows ran `llvm-objcopy --dump-section=.modinfo=/dev/stdout` on each first stock path that had `.BTF` (absolute canonical paths). 71 files were rewritten; the 60 signed ones lost their signatures. |
| ≈ 03:22 | PLATFORM-BATCH-04 (Claude) found the 60 unsigned copies ("across interruption, cause unknown"), quarantined them and restored them from `system_dlkm_a.img` (`PLATFORM-BATCH-04/evidence/stock-operand-drift/`). |
| 03:33 | Batch04 committed `f61ebf03` with a passing live validator. |
| 12:38:52.536 | **Incident 2.** The Codex "OEM split-BTF base census" (SCP-CONNECTIVITY-BATCH-01, `cwd` = canonical checkout) ran `llvm-objcopy --dump-section .BTF=/dev/stdout` on the first stock path of all 458 rows. The 71 `.BTF` files were rewritten again (mtimes 12:38:52.60 → 12:38:58.80; tool result 12:38:58.84). |
| 13:40 | USB-TYPEC-CLOSURE (`7e196c32`) recorded the live validator FAIL 60/60 as "unrelated drift" and correctly refused to integrate. |

Filesystem evidence (`evidence/root-cause/canonical-rewritten-files.tsv`): the rewritten files are exactly **71**
(60 system_dlkm + 6 vendor_dlkm + 5 vendor_boot) and have fresh sequential inodes. They are exactly the 71 first-path
stock modules that contain `.BTF`, which is precisely the set the command could rewrite. The other 400 occurrences
keep their 2009/1970 image timestamps. For `reboot-mode` and `syscon-reboot-mode` only the first path was touched,
matching the `stock_paths.split(';')[0]` loop. The 11 vendor files are unsigned and remain byte-identical to stock.

## Same 60 files as Batch04?

**Yes.** For all 60 the current bytes equal Batch04's recorded `before_sha256/size` and its quarantined copies.
The validator identity lists are identical to `validator-before-restoration.json`
(`EXPECTED-VS-OBSERVED.tsv`: `same_as_batch04_before`, `same_as_batch04_quarantine`,
`*_in_batch04_validator_failure`, all true). The re-damage is deterministic, so the previous incident has the
same origin (incident 1 above), even though Batch04 recorded the cause as unknown.

## What the validator codes mean

`validate.py` reports `MISSING_IDENTITY` for an identity **observed on disk but absent from the audit**, and
`UNEXPECTED_IDENTITY` for an **audit identity not found on disk**. The 60 "missing" are the stripped on-disk
hashes. The 60 "unexpected" are the true stock identities. `STALE_FROZEN_INVENTORY` and `OWNERSHIP_IDENTITY_SET`
follow from the same 60 substitutions. Pairing is one-to-one by path (`MISSING-IDENTITIES.tsv`,
`UNEXPECTED-IDENTITIES.tsv`).

## Alternative causes, excluded

| Hypothesis | Verdict | Evidence |
|---|---|---|
| A. Signatures missing from local copies | **Confirmed** | Observed = image member minus its exact 721-byte trailer, for all 60; ELF content ends at that offset |
| B. Stale validator baseline | Excluded | The 60 expected hashes and sizes equal the authenticated image members. `stock-module-master.csv` is unchanged since 2026-09-07. The system_dlkm rows are identical since the first audit commit `ac3a839a`. The closure baseline equals `f61ebf03` |
| C. Incorrect checkout | Excluded | Closure ran the canonical scripts on canonical `f61ebf03` (trace paths in its log). A fresh worktree at `f61ebf03` with a reflinked workspace gives a byte-identical result |
| D. Path/partition confusion | Excluded | One-to-one pairing by path, all `system_dlkm`. `bluetooth.ko`: the vendor identity is intact and unreported; only the system identity changed |
| E. Overwritten by a fresh build | Excluded | The bytes are the exact stock prefix, not a compiled artifact. The tool calls that wrote them are identified |
| F. Symlink/mount/cache | Excluded | Regular files on btrfs `@home`, no symlinks in the stock module trees. The isolated reflinked copy reproduces the failure |
| G. Validator regression | Excluded | Validator unchanged since `2bef0ac6`/`ac3a839a` (2026-10-09). It PASSES with 0 errors on authentic operands and rejects every stripped, truncated or substituted variant (`REGRESSION-TESTS.md`) |

## Other consequences checked

- Every private stock copy used by the Codex AUDIO-BATCH-01 and SCP-CONNECTIVITY-BATCH-01 acceptances
  (`/home/armol/kernel-work/codex-*/stock*`) still matches a canonical identity. Those copies are vendor modules,
  so their in-place rewrites were byte-identical. Their acceptance results are unaffected.
- SCP-CONNECTIVITY-BATCH-01's `evidence/btf-residual/oem-base-census.txt` values are correct, because reading
  `.BTF` was unaffected. The procedure that produced them is the incident-2 command, which is a hazard. That branch is not modified here.
- No PLATFORM-BATCH-04 or USB-TYPEC-CLOSURE target is in `system_dlkm` (30/30 vendor_boot/vendor_dlkm).

## Prevention

- Never call `llvm-objcopy`/`objcopy`/`strip` on a stock operand without an explicit output operand.
  Use `llvm-objcopy --dump-section S=out.bin IN /dev/null` or `llvm-readelf -x S`, and prefer running on private reflinked copies.
- Do not run census loops with `cwd` or paths in the canonical stock tree.
- Before and after any batch, run `scripts/verify-inventory.py <checkout>` to detect signature-stripped operands immediately.
