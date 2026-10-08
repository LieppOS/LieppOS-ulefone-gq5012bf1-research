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
