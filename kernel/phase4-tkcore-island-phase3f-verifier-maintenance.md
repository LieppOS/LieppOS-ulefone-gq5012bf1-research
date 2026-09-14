# Phase 3F — verifier maintenance log

§40 forbids weakening any verifier for Phase 3F, and §41 requires that an older guard which conflicts with the authorised Phase-3F state be updated **monotonically** rather than disabled. Every edit is recorded here.

## The conflict

Four tkcore verifiers carried a Phase-3E-era boundary guard asserting that `workspace/phase4-tkcore-island/acceptance/` is **empty**:

| Verifier | Original assertion |
|---|---|
| Phase 3E | `final acceptance directory untouched/empty` |
| Phase 3D | `full three-consumer acceptance still unexecuted` |
| Phase 3C-R | `three-consumer acceptance still empty` |
| Phase 3C | `three-consumer acceptance still empty` |

That guard was correct through Phase 3E, whose scope explicitly excluded consumer acceptance. Phase 3F is the separately authorised task that populates the directory, so on first run after the acceptance builds these four reported:

```
[FAIL] final acceptance directory untouched/empty
[FAIL] full three-consumer acceptance still unexecuted
[FAIL] three-consumer acceptance still empty        (×2)
```

Phase 3E and Phase 3D additionally reported a cascade failure because each invokes the previous phase's verifier as a nested check.

## The monotone replacement

A new shared module `kernel/scripts/phase4_tkcore_acceptance_gate.py` replaces "is empty" with:

> acceptance is **EMPTY** (historical pre-3F state) **OR** it is a **COMPLETE, valid Phase-3F acceptance**

`COMPLETE_PHASE3F` requires *all* of:

1. all five required artifacts present — provider `.ko`, provider `Module.symvers`, and the three consumer `.ko` files;
2. the provider inside the acceptance set hashes to exactly the frozen Phase-3E SHA `caacaf…8983` (a mutated provider means Phase 3E was silently reopened);
3. no stock ABI witness file (`stock-provider.symvers`, `tkcore-provider.symvers`) anywhere in the acceptance tree.

Anything else — partial, malformed, mutated, or witness-contaminated — still **fails**.

### Why this is monotone, not a weakening

- In the **empty** case the predicate is bit-for-bit the original one, so every pre-3F guarantee is retained unchanged.
- In the **populated** case the new predicate is strictly *stronger* than the original could ever be: the original merely demanded absence, whereas the replacement validates provider identity, completeness and witness-freedom.

### Adversarial proof

The gate was tested against synthetic states (real evidence untouched):

| State | Gate verdict | Accepted? |
|---|---|---|
| real acceptance tree | `COMPLETE_PHASE3F` | yes |
| non-existent / empty dir | `EMPTY` | yes |
| only provider + one consumer | `INCOMPLETE: missing [...]` | **no** |
| provider bytes corrupted | `PROVIDER_MUTATED: 708e1a…` | **no** |
| `stock-provider.symvers` planted | `STOCK_WITNESS_PRESENT: [...]` | **no** |

## Result

Check counts are **unchanged** — no assertion was removed, each was replaced one-for-one:

| Verifier | Before 3F | After maintenance |
|---|---|---|
| Phase 3E | 167/167 | **167/167** |
| Phase 3D | 158/158 | **158/158** |
| Phase 3C-R | 59/59 | **59/59** |
| Phase 3C | 81/81 | **81/81** |
| Phase 3B | 205/205 | 205/205 (untouched) |
| Phase 3A-R | 162/162 | 162/162 (untouched) |

## Second monotone edit: the todo-#18 state assertion

§43 requires closing todo #18 on Phase-3F success, and §48 requires updating the work-queue current status. The Phase-3E verifier asserted the literal pre-3F wording:

```python
ck("todo #18 remains open", "Todo #18 remains **OPEN**" in queue)
```

After the mandated closure this reported `[FAIL] todo #18 remains open`. It was replaced one-for-one with a monotone assertion that the work queue must carry a **recognised** todo-#18 state — either the historical `OPEN` wording, or an explicit closure naming `PHASE 3F FINAL TRUSTKERNEL ISLAND STATIC ACCEPTANCE PASS`.

Adversarial proof: replacing the closure string with arbitrary text (`WHATEVER`) makes the check fail with `UNRECOGNISED`, so a missing or vague todo state is still rejected. Check count stays 167/167.

## Non-edits

No consumer verifier required any change. `phase4_tkcore_drv_verify.py` initially reported three failures — `//lieppos/tkcore-recon Module.symvers built`, `stock-ABI module built`, `natural module built` — which were **missing build artifacts**, not regressions: those historical targets had not been built in this session. Building the three pre-existing targets restored it to 43/43 with zero edits to the verifier.

`phase4_ffa_v10_parity.py` and `phase4_spi_mt65xx_parity.py` are CLI comparison utilities requiring `stock` and `rebuilt` arguments, not standalone verifiers; their argparse usage exit is not a verification failure.

Files changed:

- `kernel/scripts/phase4_tkcore_acceptance_gate.py` (new shared gate)
- `kernel/scripts/phase4_tkcore_island_phase3e_verify.py` (one assertion replaced)
- `kernel/scripts/phase4_tkcore_island_phase3d_verify.py` (one assertion replaced)
- `kernel/scripts/phase4_tkcore_island_phase3c_r_verify.py` (one assertion replaced)
- `kernel/scripts/phase4_tkcore_island_phase3c_verify.py` (one assertion replaced)
