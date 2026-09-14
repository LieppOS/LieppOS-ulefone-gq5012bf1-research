# GQ5012BF1 tkcore island Phase 3D — regression report

Three-way: stock oracle, Phase 3C-R, Phase 3D.

## Module identity

| | Phase 3C-R | Phase 3D |
|---|---|---|
| SHA-256 | `7d9d7979521853c8d5a4412bb08c534870cd977a2f1efebe363f172ef067aeee` | `c34a16e78a385a995e626c922bbc02dc756217cca9ef403253dd37999f4031b5` |
| size | 190784 | 196904 |
| Build ID | `316c670d516f9fb7f823c0b588ce586a186c3549` | `65bcfb2d5e7fb386c8ecf0a0356295d382835787` |
| srcversion | `8AFF88A87FBB74AB1FCB2D7` | `3E2810D195047DBD1697163` |
| vermagic | `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64` | same |
| depends | empty | **empty** |
| import_ns | DMA_BUF | DMA_BUF |

## Coverage

| Metric | Stock | Phase 3C-R | Phase 3D |
|---|---:|---:|---:|
| stock functions | 122 | — | — |
| present | — | 113 | **117** |
| missing | — | 9 | **5** |
| byte-identical | — | 47 | 47 |
| island-only | — | 0 | **0** |
| exports | 25 | 21 | **25** |
| undefined imports | 100 | 97 | 97 |

Newly present, exactly the four Phase-3D targets and nothing else:

```text
tee_clkmgr_handle
tee_spi_cfg_padsel
tee_spi_transfer
tee_spi_transfer_disable
```

Exact remaining missing set — all five belong to Phase 3E:

```text
big_core_affinity_get_candidate_cpu
big_core_affinity_match_cpu
big_core_affinity_need_bind_cpu
plat_cpu_is_big
plat_tee_init
```

Byte-identical stayed at 47: none was lost, and none of the four new functions
reached byte identity (each has exactly one benign residual, below).

## Per-target quality

| Function | Stock size | Phase 3D size | Δ | KCFI | Export CRC | Classification |
|---|---:|---:|---:|---|---|---|
| `tee_clkmgr_handle` | 308 | 308 | 0 | `0x06da45e1` exact | `0x6913f6b2` natural | SIZE_EXACT_SEMANTIC_EXACT |
| `tee_spi_cfg_padsel` | 332 | 332 | 0 | `0xab53c5c9` exact | `0x56729869` natural | SIZE_EXACT_SEMANTIC_EXACT |
| `tee_spi_transfer` | 452 | 452 | 0 | `0xffeb18b3` exact | `0x184ce7da` natural | SIZE_EXACT_SEMANTIC_EXACT |
| `tee_spi_transfer_disable` | 300 | 300 | 0 | `0x36b1c5a6` exact | `0xadb9b21c` natural | SIZE_EXACT_SEMANTIC_EXACT |

None is `INCOMPLETE` and none is `STRUCTURAL_ONLY`.

### Residual differences, fully attributed

The three SPI functions differ from stock in exactly **one** instruction each:

```text
stock : str wzr, [sp, #0x10]     ; 32-bit zero of the session identifier
island: str xzr, [sp, #0x10]     ; 64-bit zero of the same 8-byte slot
```

`TEEC_Session` is a union whose largest member is 8 bytes, so Clang widens the
store to the whole object. Stock leaves the upper 4 bytes indeterminate; the
island zeroes them. `TEEC_OpenSession` overwrites the field on success either
way, so there is no behavioural difference — the island is marginally safer.
The `TEEC_Session` layout is PROVEN_EXACT and was deliberately **not**
re-spelled to chase this one instruction.

`tee_clkmgr_handle` matches stock's size and semantics exactly; its differences
are instruction scheduling and block ordering only. Two worth naming because
they look like changes but are not:

- `cmp x23, #0x4 ; b.hs` versus stock `cmp x23, #0x3 ; b.hi` — identical
  unsigned predicate (`x > 3` ⟺ `x >= 4`).
- stock has four `mov w0, wzr` (one per switch case); the island tail-merges
  them into one shared exit. All four cases still return literal `0`.

Its `csel x9, x10, x9, eq` with `x9 = -0x30` / `x10 = -0x28` is the **same
selector polarity as stock**, which is the load-bearing detail of the function.

## Whole-module audits — all clean

| Audit | Result |
|---|---|
| callgraph (32 edges over the four) | **0 anomalies** — no stock-only, no island-only edge |
| strings (14 over the four) | **0 anomalies** — every stock string reproduced, none added |
| relocations (46 classes over the four) | **0 anomalies** — multisets equal |
| imports | **0 added, 0 removed**; still 97, all present in stock |
| objects | one new symbol: `tee_spi_ta_uuid`, 16 bytes, `.data` — the TA UUID |
| KCFI | 4/4 targets exact, plus 3 already-closed controls still exact |
| export parity | 25/25 present; the four are `NATURAL_STOCK_CRC` |

The 16 exports carrying `ISLAND_NATURAL_PROVIDER_CRC` are the **pre-existing**
private-spelling limitation documented in earlier phases. Their Phase-3C-R and
Phase-3D CRCs are identical, so Phase 3D changed none of them.

Independent corroboration of the `(void)` prototype for
`tee_spi_transfer_disable`: the already-closed `int(void)` functions
`tee_peridev_init` and `plat_register_spi_clk` carry KCFI `0x36b1c5a6` in both
stock and the island — the same id, because it is the id of the type `int(void)`.

## Clock foundation not regressed

`tee_clkmgr_register`, `tee_peridev_init`, `tee_peridev_exit`,
`plat_register_spi_clk`, `mtk_enable_clk` and `mtk_disable_clk` were not
modified. The 72-byte record layout and all six of its `static_assert`s are
unchanged, and `tee_clkmgr_register` retains KCFI `0xe70e59df` and its stock CRC.

## Verifier results

| Verifier | Before | After | Note |
|---|---:|---:|---|
| Phase 3D | — | **158/158 PASS** | new |
| Phase 3C-R | 63/63 | **59/59** | see below |
| Phase 3C | 85/85 | **81/81** | see below |
| Phase 3B | 203/203 | **205/205** | +2, see below |
| Phase 3A-R | 162/162 | **162/162** | untouched |

Zero `[FAIL]` lines anywhere.

### Why two check counts dropped, and why that is not a weakening

The 3C and 3C-R verifiers each contained a loop asserting that all nine
then-missing functions **stay** missing. That is a scope guard for their own
phase, but taken literally it asserts that no later phase may ever make
progress — a correct Phase 3D would be reported as a regression.

Following the precedent already set for the Phase-3A-R verifier and co-owned
files, those guards were made **monotone** rather than removed:

- `coverage still 113/122` → `coverage never regressed below 113/122`
- `missing set is exactly ...` → `nothing outside the declared out-of-scope set is missing`
- `exports still 21` → `exports never regressed below 21` **plus** a new check
  that no export present at Phase 3C-R was lost
- `no function added` → `no function added outside a later phase's declared scope`
- the boundary loop now covers the **five** still-deferred Phase-3E functions

The 4 + 4 removed assertions are precisely the four clock/SPI symbols, and the
Phase-3D verifier replaces them with **strictly stronger** obligations: those
four must now be present, exported, CRC-matched and KCFI-matched. Every
behavioural assertion of Phase 3C and Phase 3C-R was left untouched, including
the `_update_client_tee_cmd` residual and the `tee_context_copy_from_client`
byte-identity check.

### Why the Phase-3B count rose from 203 to 205

The Phase-3B verifier pinned the **live, shared** Phase-3 work queue to the
literal string `"104 of the 122 stock functions"`. That document is updated by
every later phase, so the assertion meant "no later phase may record progress".

It was replaced by three checks that are collectively stronger:

1. the work queue still records a stock-function coverage figure at all;
2. that figure never regressed below the 104/122 Phase 3B achieved;
3. the queue still credits the Phase-3B shared-memory closure
   (`Phase 3B added 13` and `closed in Phase 3B`).

No Phase-3B behavioural assertion was altered; all 203 original subject-matter
checks still run and pass.

## Build

```text
BUILD_RC=0  warnings=0  errors=0  modpost=0  unresolved=0
depends=(empty)   layout probe: built
```

## Scope

Final five platform/affinity functions: untouched and still absent.
`workspace/phase4-tkcore-island/acceptance/`: still empty.
todo #18: still OPEN.
