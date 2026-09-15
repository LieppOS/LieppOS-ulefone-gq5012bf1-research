# GQ5012BF1 TrustKernel Phase 3G-R — superseding diagnosis

Status: **DIAGNOSTIC PLAN ACTIVE / NO PHASE-3G-R DEVICE WRITE YET**

Starting research HEAD: `8e53f501e14b6e391ac4758deed6a4a064595b91`.

This report supersedes the *interpretation* of Phase 3G without altering or erasing its historical reports or evidence.

## What Phase 3G established

The 2026-09-15 Phase-3G trial wrote and byte-verified its three Slot-B candidate partitions, then made exactly one B boot attempt. B never reached ADB, fell back to A after approximately 124 seconds, and was marked unbootable. No B-side kernel, module or userspace evidence existed. The device was subsequently returned to A and all three B partitions were restored byte-exactly to stock.

Therefore Phase 3G failed **before G1**. Source `tkcore`, source `tkcore_drv`, and source `tmem_ffa` runtime behavior were **not validated**. The failure must not be attributed to source `tkcore` or any TrustKernel runtime function without module/runtime evidence.

## Retired Phase-3G deployment unit

The booted candidate contained:

- source `tkcore.ko`;
- **stock `tkcore_drv.ko`**;
- source `tmem_ffa.ko`.

That was not the final Phase-3F deployment unit. Phase 3F proved only **5/19** stock-consumer edges directly compatible with final source `tkcore`; `tkcore.ko`, `tkcore_drv.ko`, and `tmem_ffa.ko` must move together.

For stock `tkcore_drv`, only 4/11 relevant edges retain the historical stock CRC:

- `tee_map_cached_shm`;
- `tee_clkmgr_handle`;
- `tee_wait_queue_init`;
- `tee_wait_queue_exit`.

The other 7/11 stock-consumer edges are incompatible with final source `tkcore` and require the source-island consumer ABI:

- `tee_core_alloc`;
- `tee_core_add`;
- `tee_core_del`;
- `__tee_get`;
- `tee_supp_cmd`;
- `tee_wait_queue_sleep`;
- `tee_wait_queue_wakeup`.

This is a real static module-ABI defect in the previous candidate. It does **not** prove that the defect caused the observed pre-ADB failure. The previous Phase-3G image set is permanently retired and must not be retried.

## Independently unresolved boot-chain question

The previous top-level `vbmeta_b` was structurally coherent on the host and signed with the local AOSP RSA-2048 test key, but acceptance of that key by the real Slot-B boot chain was never independently proven.

Observed state remains contradictory:

- bootloader Fastboot: `unlocked=yes`, `secure=no`;
- running Android: `ro.boot.flash.locked=1`, `ro.boot.vbmeta.device_state=locked`, `ro.boot.verifiedbootstate=green`.

Fastboot's reported unlock state must not be treated as proof that an arbitrarily signed top-level vbmeta will execute.

## Mandatory diagnostic order

### C0 — top-level vbmeta acceptance control

Use exact stock B payloads and regenerate only top-level `vbmeta_b` with the same local test key. All descriptor semantics must remain stock-identical. C0 contains zero module replacements and answers only whether the local top-level key is accepted for a B boot.

### C1 — corrected TrustKernel island

C1 is forbidden unless C0 boots B and proves authoritative `_b` identity. C1 must deploy exactly:

- source `tkcore.ko`;
- source `tkcore_drv.ko`;
- source `tmem_ffa.ko`.

Stock `microarray_fp_tee.ko` and the already proven compatible non-tkcore providers remain installed. C1 stops after G1 module-load identity and absence of unknown-symbol/modversion failures.

## Stop discipline

Every device-write stage requires fresh explicit authorization. C0 failure stops Phase 3G-R and forbids C1. C1 failure permits no second B boot. Verification/verity disabling, bootloader relocking, Slot-A writes, super resize, shared-state mutation, secure-world probing and TrustKernel ioctl tests are out of scope.
