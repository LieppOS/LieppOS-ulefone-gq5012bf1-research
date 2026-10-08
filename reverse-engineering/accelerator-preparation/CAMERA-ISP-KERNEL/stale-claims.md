# Stale-claim audit — CAMERA-ISP-KERNEL

Use this file when older preparation notes conflict with the completed reconstruction.
The newer machine evidence and [RECONSTRUCTION-REPORT.md](RECONSTRUCTION-REPORT.md) win.

## 1. “CAMERA-ISP-KERNEL is PARTIAL”

**Stale.** The explicitly registered nineteen-module normal-world kernel scope is DONE.
The proprietary parent `CAMERA-HAL-ISP` remains PARTIAL; that does not reopen the child.
Global component/coverage ledgers are updated with this scoped distinction.

## 2. “Only sixteen modules have function/data evidence; PDA/VMM are open”

**Stale.** All nineteen modules now have new whole-module acceptance. Function parity is
2 970/2 971 exact with the one declared semantic-equivalence residue; data parity is
2 474/2 474 exact. PDA and both VMM modules build from unmodified public source and are
byte-identical after build-ID normalization.

## 3. “The old grafted `133c6c1` tree is the source of truth”

**Stale as a build prescription, retained as historical evidence.** The maintained recipe
starts from pristine public pins (`5f75a3b` kmod, `957dac1` kdm) and applies three explicit
GQ5012BF1 patches whose result trees are asserted. The old graft workspace helped recover
changes, but it is not needed to reproduce the result and is not an accepted source pin.

Several patches that look cosmetic are parity requirements: placement relative to
`pr_info`/`module_param` changes `.rodata`, and source line numbers change `__bug_table`.
They are retained because stock proves them, not because style requires them.

## 4. “Stock `.modinfo` dependencies prove `mtk_ccu.ko` and `mtk_ccu_mssv.ko` exist”

**False.** Those filenames are absent from the 457-module inventory. CRC-resolved exports
come from `mtk_ccuv.ko`; selected package-scoped modpost inputs preserve historical stock
`depends=` strings. Do not invent missing provider modules.

## 5. “Every shipped camera module binds to a DT node”

**False.** The merged board DT has no compatible for DPE, IPESYS-ME, VMM ISP71 or C2PS.
Helper/software-created devices can be valid without direct DT ownership; DPE/IPESYS-ME
may remain unbound. A stock filename or `status = "okay"` is not runtime proof.

## 6. “All nineteen modules are raw byte-identical”

**Too broad.** Seventeen differ only in the 20-byte build ID. `mtk_imgsys_cmdq` additionally
has a proven COMPILER_ONLY local symbol/string-table suffix residue; `imgsensor` has one
70-byte PROVEN_SEMANTIC_EQUIVALENT function residue. Both are accepted and fully scoped;
claiming literal whole-file identity would erase the evidence.

## 7. “Static DONE proves camera works”

**False.** No hardware command, probe, firmware boot, ioctl or stream was executed in this
closure. Runtime and image-quality acceptance remain explicitly NOT TESTED.

## 8. “Every section content and raw relocation is identical”

**Too broad.** All 978 headers match, but content rows are 955 identical, 19 build-ID-only,
two COMPILER_ONLY and two PROVEN_SEMANTIC_EQUIVALENT. There are 71,990 exact raw/semantic
relocations and one moved `R_AARCH64_LDST8_ABS_LO12_NC` byte load (type 278), not an ADD
relocation. The earlier verifier conservatively labeled all 13,515 `imgsensor .rela.text`
rows with the function's residue class; the current ledger checks each entry individually.
Both B1/B2 artifacts reverify with identical outputs and the exact moved pair enforced.

## 9. Pre-existing unrelated canonical drift

Mali is already DONE in the organized workspace but remains PARTIAL in older canonical
coverage records. This camera task does not reopen or modify its module ownership/status
rows. After camera promotion the actual workspace totals are 100 DONE / 36 PARTIAL /
3 BLOCKED / 0 TODO; the canonical component ledger remains 99 / 37 / 3 / 0 because of
that one pre-existing discrepancy. Do not treat the stale Mali row as new work.

## 10. Historical preparation files

`CLAUDE-HANDOFF.md`, `RE-PLAN.md`, old source-candidate rows and the external organized
`Reverse Engineer - PARTIAL/…` path describe the 2026-10-08 starting state. They are
retained or rewritten as historical handoff material; they do not override current status.
