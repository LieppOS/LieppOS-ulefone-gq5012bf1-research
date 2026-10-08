# MALI-GPU-KERNEL status — 2026-10-08

**DONE (static, normal-world kernel scope).**

* All 8 owned modules are rebuilt from pinned public MediaTek sources: NothingOSS
  kernel_modules 580d08e (+4 files from c3d070e), NothingOSS device_modules 957dac, and
  ALPS 5e415e059253.
* Clean B1 == B2.
* Against stock: 2748/2748 function symbols byte-identical, all data objects and
  relocations identical, and imports/exports/KCFI/modversions identical (CRCs natural,
  including the 30 external-provider CRCs).
* Residue: the 20-byte build-id in each module, plus kbase `srcversion` (source-text hash,
  code-invisible).
* DT binding, userspace ABI, firmware and GPUEB boundaries are mapped. All 8 modules are
  live and bound in the existing read-only runtime capture.

**Remaining (runtime-only, not static):**
* GPU_ID, revision and core mask;
* actual DVFS and thermal behaviour;
* protected-mode execution;
* behaviour of the rebuilt modules when loaded on the device (not done: no device interaction).

## Workspace move (2026-10-08)

Moved `Reverse Engineer - PARTIAL/MALI-GPU-KERNEL` -> `Reverse Engineer - DONE/MALI-GPU-KERNEL` via `reverse-engineering/scripts/promote-to-done.py` (research commit cf0a994); 93 COPY-MANIFEST rows, 0 drift / 0 unregistered for this component. Totals: 95 DONE / 41 PARTIAL / 3 BLOCKED / 0 TODO.

## Accelerator-preparation validator after closure

* `validate.py --scope MALI-GPU-KERNEL --inputs-only` **PASS**: stock operands and donor
  input fingerprints are unchanged, and the canonical .md files have no forbidden links.
* Full mode stops at `non-singleton status MALI-GPU-KERNEL`. That mode asserts the
  *preparation* snapshot (scope pack under `Reverse Engineer - PARTIAL`, PARTIAL
  registration, `workspace-sync.json` pack hashes), which this closure supersedes by
  design.
* `validate.py` is left unmodified because it is shared by all six accelerator scopes.
  Making it closure-aware is a separate tooling change.
