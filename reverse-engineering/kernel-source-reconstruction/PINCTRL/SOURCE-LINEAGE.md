# Source lineage — measured, not assumed

The audit candidate was NothingOSS MT6878 device modules `957dac185efe…`.
ALPS `5e415e059253…` was already valuable for storage/clock source work but was tested
independently here. Initial four-module build from unchanged ALPS C produced complete
stripped ELF identity except GNU IDs, not only matching functions or module sizes.

`evidence/source/source-blobs.tsv` records both revisions' immutable blobs for all eleven
relevant files (C, headers and vendor Makefile), plus assembled byte hashes. MT6878,
MT6363, common-v2 and Paris implementation blobs are identical across these candidates.
`mtk-eint.c` differs only in executable file mode (100644 → 100755), not bytes.

The debug source differs by this later hunk in `957dac…`:

```diff
- if (pin - hw->chip.base >= hw->soc->npins) {
+ pin -= hw->chip.base;
+ if (pin >= hw->soc->npins) {
```

It is not accepted as stock source. A separately measured build with that candidate debug
file compiles successfully but changes `gpio_get_tristate_input` from **820 to 824 bytes**
and fails full normalized-file acceptance (`evidence/source/candidate-957dac-result.json`).
Same overall module length (30528) does not establish equivalence. The older ALPS implementation
passes; there is no reason to apply a semantic patch or normalize its code differences away.

This proves a **stock-compatible source lineage**, not recovery of the ODM's original Git
commit, authoring history or proprietary build paths. No C-level GQ5012BF1 delta was needed.
The phone-specific contract lives in stock DT and consumer drivers, not a new pin table.
The source-only Kbuild scope patch is completely committed in the maintained repository.
No prebuilt stock instruction, data or CRC slot is injected into a rebuild.
