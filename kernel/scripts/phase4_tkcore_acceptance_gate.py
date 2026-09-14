#!/usr/bin/env python3
"""Monotone acceptance-directory gate shared by the tkcore island verifiers.

Through Phase 3E, `workspace/phase4-tkcore-island/acceptance/` was required to
be EMPTY: no consumer acceptance had been authorised yet, so anything in there
meant scope had leaked.

Phase 3F is the separately authorised task that populates it.  Simply deleting
the old assertion would weaken every earlier verifier, which is forbidden.  The
assertion is therefore made MONOTONE:

    acceptance is empty                       (historical pre-3F state)
  OR
    acceptance is a COMPLETE Phase-3F result  (stronger final state)

A partial, malformed, or witness-contaminated acceptance directory still fails,
exactly as it did before.  In the empty case the predicate is identical to the
original one, so no earlier guarantee is lost.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

PHASE3E_SHA = "caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983"

# Every artifact a complete Phase-3F acceptance must contain.
REQUIRED = (
    "provider/tkcore.phase3e.ko",
    "provider/Module.symvers",
    "tkcore_drv/tkcore_drv.phase3f.ko",
    "tmem_ffa/tmem_ffa.phase3f.ko",
    "microarray_fp_tee/microarray_fp_tee.phase3f.ko",
)

# Names that would indicate a stock ABI witness leaked into the acceptance set.
FORBIDDEN_WITNESS_NAMES = ("stock-provider.symvers", "tkcore-provider.symvers")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(acc: Path) -> str:
    """Return 'EMPTY', 'COMPLETE_PHASE3F', or a reason string explaining failure."""
    if not acc.is_dir() or not any(acc.rglob("*")):
        return "EMPTY"

    missing = [r for r in REQUIRED if not (acc / r).is_file()]
    if missing:
        return f"INCOMPLETE: missing {missing}"

    # The provider inside the acceptance set must be the exact frozen Phase-3E
    # module; a mutated provider means Phase 3E was silently reopened.
    got = _sha(acc / "provider/tkcore.phase3e.ko")
    if got != PHASE3E_SHA:
        return f"PROVIDER_MUTATED: {got}"

    # No stock ABI witness may appear anywhere in the acceptance evidence.
    leaked = sorted(
        str(p.relative_to(acc))
        for p in acc.rglob("*")
        if p.is_file() and p.name in FORBIDDEN_WITNESS_NAMES
    )
    if leaked:
        return f"STOCK_WITNESS_PRESENT: {leaked}"

    return "COMPLETE_PHASE3F"


def ok(acc: Path) -> bool:
    return state(acc) in ("EMPTY", "COMPLETE_PHASE3F")
