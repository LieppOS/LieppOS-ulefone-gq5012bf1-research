# AUDIO-BATCH-01 — MediaTek audio kernel source reconstruction (Codex)

**Result: 21 audio module identities processed; 20 newly A, 0 B, 1 C (`aw883xx_driver`).**
Independent clean-clone B1/B2 builds are byte-identical, and both pass stock acceptance.
This is a delta only. The live canonical audit was **not** modified (see `MERGE-INSTRUCTIONS.md`).

| | |
|---|---|
| Branch / worktree | `codex/audio-batch-01` in `ulefone-gq5012bf1-research-codex-audio` |
| Frozen baseline | canonical audit `548526fc` (458 identities, A219/B1/C9/D98/G131; 220 certified) |
| Scope rule | every identity in `PRESERVE:AUDIO` or `PRESERVE:AW883XX-SPEAKER-AMP`, totalling **21**. This is disjoint from PLATFORM-BATCH-04; `mtk-spmi-pmic*` was already A in Batch03 and excluded |
| Maintained source | `android_kernel_modules_audio_ulefone_gq5012bf1` @ `ec57573c`. It is not pushed and is backed up as a git bundle |
| Toolchain | GKI `6b18f0b5`, clang r487747c (`7775eb11`), KDM `957dac18` config + ALPS `5e415e05` C, Awinic `4f52a107` |
| Provisional totals after merge | **240 certified / 218 uncertified** (A239 B1 C10 D98 G110); provisional until rebased onto Batch04 |

## Per-module result

| Module | Initial | Final | Functions | Data | CRC/KCFI | Relocations | Source | Residual |
|---|---|---|---|---|---|---|---|---|
| clk-mt6878-adsp | G | **A** | 3/3 | 19 | imp 7, exp 0, KCFI 0 | 190 identical | ALPS pristine | – |
| mt6685-audclk | G | **A** | 5/5 | 16 | imp 9, exp 2, KCFI 0 | 53 identical | ALPS pristine | – |
| mt6878-mt6369 | G | **A** | 15/15 | 333 | imp 57, exp 0, KCFI 13 | 1209 identical | 0002 | – |
| mtk-afe-external | G | **A** | 15/15 | 16 | imp 7, exp 15, KCFI 0 | 105 identical | ALPS pristine | – |
| mtk-sp-spk-amp | G | **A** | 16/16 | 26 | imp 13, exp 11, KCFI 2 | 212 identical | 0003 | – |
| snd-soc-mt6878-afe | G | **A** | 204/204 | 947 | imp 129, exp 13, KCFI 29 | 13654 identical | ALPS pristine | – |
| snd-soc-mtk-common | G | **A** | 83/83 | 67 | imp 88, exp 55, KCFI 0 | 1579 identical | ALPS pristine | – |
| aw883xx_driver | G | **C** | 235/236 | 86 identical | imp 74, exp 2, KCFI identical | identical outside 1 fn | 0005+0006 | `aw883xx_dev_cfg_load` codegen |
| mt6369-accdet | G | **A** | 49/49 | 35 | imp 77, exp 4, KCFI 0 | 2107 identical | 0004 (re-derived) | – |
| mt6369-regulator | G | **A** | 14/14 | 27 | imp 35, exp 0, KCFI 11 | 291 identical | ALPS pristine | – |
| snd-soc-mt6369 | G | **A** | 83/83 | 119 | imp 59, exp 5, KCFI 6 | 4166 identical | ALPS pristine | – |
| snd-soc-tfa98xx | G | **A** | 316/316 | 111 | imp 96, exp 0, KCFI 13 | 4802 identical | ALPS pristine | – |
| adsp | G | **A** | 166/166 | 78 | imp 123, exp 54, KCFI 3 | 2882 identical | ALPS pristine | – |
| audio_ipi | G | **A** | 119/119 | 43 | imp 65, exp 9, KCFI 0 | 3704 identical | ALPS pristine | – |
| mtk-scp-audiocommon | G | **A** | 24/24 | 40 | imp 40, exp 7, KCFI 3 | 590 identical | ALPS pristine | – |
| mtk-scp-ultra | G | **A** | 7/7 | 14 | imp 6, exp 4, KCFI 0 | 72 identical | ALPS pristine | – |
| mtk-scp-vow | G | **A** | 5/5 | 14 | imp 8, exp 0, KCFI 0 | 28 identical | ALPS pristine | – |
| mtk-soc-offload-common | G | **A** | 34/34 | 43 | imp 65, exp 0, KCFI 3 | 779 identical | ALPS pristine | – |
| mtk-vow | G | **A** | 71/71 | 59 | imp 49, exp 1, KCFI 0 | 3337 identical | ALPS + audio config | – |
| snd-soc-audiodsp-common | G | **A** | 172/172 | 186 | imp 104, exp 36, KCFI 8 | 3141 identical | ALPS pristine | – |
| snd-soc-mtk-scp-ultra | G | **A** | 45/45 | 49 | imp 51, exp 2, KCFI 4 | 864 identical | ALPS pristine | – |

`BATCH-PARITY.tsv` contains exact per-axis values and `evidence/cleancheck/acceptance-B1/*.tsv` contains complete ledgers. An A module is identical to stock across the whole file after zeroing only the 20-byte GNU build-ID descriptor. That covers every function, data object, section, raw and semantic relocation, symbol table entry, import CRC, export CRC and licence, KCFI type ID, `.modinfo`, `vermagic` and `srcversion`. Stock audio modules carry neither BTF nor signatures, so there is nothing further to compare. Totals across the 20 A modules: 1,446 functions, 2,242 objects, 1,088 import CRCs, 218 export CRCs, 95 KCFI IDs and 43,765 relocations.

## What was recovered rather than reverse-engineered again

- `reverse-engineering/audio/` (Sep–Oct 2026) already held function/data/ABI-exact *development* rebuilds for 22 modules. Its sources were byte-identical to ALPS `5e415e05` except for three GQ5012BF1 deltas, which are preserved as full patches 0002–0004. Its build used a mutable historical workspace (`/tmp/ispenv.sh`, `lieppos/audio/kout`). Recovering that kout's `.config` produced the only three ODM Kconfig toggles (`reference/gq5012bf1-audio.config`).
- `Reverse Engineer - DONE/AW883XX-SPEAKER-AMP` contained the v1.6.0 → v1.7.1 delta. Applied to the public donor, it reproduced the DONE source byte-for-byte; it is kept verbatim as patch 0005.

## New findings

1. **mt6369-accdet layout (from G to A).** The historical source left 814 bytes of residue: `.bss` order, string-pool order and a lock-class `__key` counter. A falsification ledger of 10 variants (`evidence/mt6369-accdet-layout/LEDGER.md`) isolated the exact source form:
   - a real `g_gpio_accdet_fm_switch = 0` definition placed before `MODULE_DEVICE_TABLE`;
   - the ODM's `yft_parse_dts2()` helper as a deferred static function;
   - literal-name `%s` arguments in YFT style.

   The residue fell to 20 bytes, the GNU build ID only. No object was patched.
2. **aw883xx historical semantic claim corrected.** The old report said "236/236 semantically equivalent", but stock `aw883xx_dev_cfg_load` breaks the insertion search on `<=` (`b.ls`), while the reconstruction used `<`. The tie order of equal-`dev_profile` scenes therefore differed. Stock also has no `-EINVAL` early return when more than 32 DDEs match; only GKI's UBSAN traps bound it. Patch 0006 restores both behaviours. Byte identity of this single inlined function was not reached after 18 falsified variants, so the module is **C**, not B.
3. **Board audio DSP is the RISC-V SCP.** The stock DT sets `mtk-dsp-type = "RV55"`. ADSP-host modules talk to it via `scp-audio-mbox@1cbe0000`, not to a HiFi core (`AUDIO-DSP-BOUNDARIES.md`).
4. **External ABI boundary.** All 39 stock external export slots, from 14 providers (`PROVIDER-BOUNDARIES.tsv`), are reproduced by genuine compiled ALPS provider source. Each slot matches CRC, licence, namespace, symbol type and KCFI prefix. No provider classification is changed: `scp`, `ccci_*` and `mtk_slbc` remain G/D.

## Validation

- Development D2: 21/21 built; 20 passed `verify.py`; `residual-check.py` passes for aw883xx.
- Clean clone (`bwrap` tmpfs over the dev repo and dev workspace) produced fresh B1 and B2 workspaces from the immutable mirrors:
  - raw `.ko`, stripped `.ko`, all 220 `.o`, provider witnesses, `.config`, GKI symvers and normalised batch symvers are identical;
  - stock acceptance passes in both builds;
  - 24/24 ELF mutation tests behave as expected (rejected on every axis; the build-ID mutation is accepted by design);
  - the git bundle restores the identical tree.
- Safety: offline only. No phone, ADB or flashing. Claude's checkouts and branches, and the canonical audit, were untouched. Nothing was pushed.
