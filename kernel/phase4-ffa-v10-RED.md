# ffa_v10 RED (Reconstruction Evidence Delta)

Per mandatory-RED policy: the donor is frozen and built **completely
unmodified** first, against exact GKI, before any delta is considered.

## Donor A: pristine current-GKI arm_ffa (RED baseline)

`//lieppos/ffa-v10-red` - `common/drivers/firmware/arm_ffa/{bus.c,driver.c,
smccc.c,common.h}` copied verbatim from this workspace's pinned common commit
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`, zero edits.

Build flags proven necessary by the stock ELF (not invented):
`-DCONFIG_ARM_FFA_TRANSPORT_MODULE=1` (else `arm_ffa.h` hides the real
prototypes behind `!IS_REACHABLE()` stubs and every export CRC changes),
`-DCONFIG_ARM_FFA_SMCCC=1` (stock contains the real, non-stub
`ffa_transport_init` and both `__arm_ffa_fn_{smc,hvc}`).

### RED mismatch (proves the donor needed dating, not blind reuse)

| metric | result |
|---|---|
| BUILD_RC | 0, 0 warnings |
| **export CRCs** | **5/5 match stock exactly**, including both hard gates |
| functions | 34/34 present, 0 missing/extra |
| size-identical | 32/34 |
| byte-identical | **30/34** |
| kCFI-identical | **34/34** |
| imports | 40/40, `__versions` 41/41, all CRCs identical |
| object counters | 12 `__UNIQUE_ID_*`/`.modinfo` names differ (build-provenance counter offset only) |

Four functions differ in bytes despite identical kCFI (i.e. identical
prototypes - only the function *bodies* differ):
`ffa_memory_ops` (+24 B), `ffa_mode_32bit_set` (-20 B), `ffa_device_register`
(1 instruction), `ffa_partition_info_get` (consequential codegen shift).

**This is the RED: exact export-ABI match, imperfect byte match.** It proves
donor A is the right driver family and even the right export ABI, but not the
exact snapshot MediaTek shipped.

## Root-causing the RED (before touching anything)

Each of the four mismatches was independently traced to one specific stable
commit in `common`'s own git history for
`drivers/firmware/arm_ffa/{driver.c,bus.c}` (see
`phase4-ffa-v10-lineage.md` for the commit-by-commit mapping). All three are
post-6.1.34, pre-6.1.56 android14-6.1-lts backports.

## Donor B: exact vendor source (found after RED, see source-candidates.md)

Once dated, the exact vendor snapshot was located verbatim in the pinned
Nothing MT6878 tree
(`device_modules/drivers/misc/mediatek/trusted_mem/ffa_v10/`,
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`). Built completely
unmodified (only a `Kconfig`-driven `CONFIG_ARM_FFA_TRANSPORT_MODULE`/
`CONFIG_ARM_FFA_SMCCC` build define, same as donor A):

| metric | result |
|---|---|
| BUILD_RC | 0, 0 warnings, 0 modpost warnings |
| export CRCs | **5/5 match stock exactly** |
| functions | **34/34 byte-identical** |
| kCFI | 34/34 identical |
| imports | 40/40 identical, `__versions` 41/41 identical CRCs |
| relocations | 346/346 identical |
| strings | identical (only `vermagic` differs, `-maybe-dirty` vs
  `-g945dff7bc1bf`, a documented project-wide scmversion artefact - see
  `module-replacement-plan.md`) |

**Donor B closes the RED completely: full byte identity, not just ABI
identity.**

## Disposition

* `//lieppos/ffa-v10` (final target) = donor B, exact vendor source, unmodified.
* `//lieppos/ffa-v10-red` = donor A, pristine current-GKI source, kept as the
  documented RED baseline and as a forward-looking drop-in (it fixes the
  MEM_LEND attributes issue - see lineage doc - with identical export ABI).

No clean-room reconstruction was needed anywhere in this task: both A and B
are unmodified, evidence-dated real source.
