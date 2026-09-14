# GQ5012BF1 tkcore island Phase 3A-R — tkcore_drv static core trace

**Result: PASS_STATIC**

This is an offline trace of the frozen stock provider consumer. No module was loaded and no full three-consumer acceptance build was attempted.

## Consumer oracle

- Module: `workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko`
- SHA-256: `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d`
- Size: `63480` bytes
- Disassembly capture: `workspace/phase4-tkcore-island/phase3a-r/tkcore_drv.objdump.txt`

## Provider pointer handoff

The frozen probes establish their transport pointer in standard device driver data before entering the common constructor:

- `tkcore_smc_probe`: store at platform-device `+0xa8`, which is embedded `dev + 0x98` (`dev->driver_data`).
- `tkcore_ffa_probe`: store at FF-A device `+0xb8`, likewise embedded `dev + 0x98`.

This matches `tee_tz_new` and the closed core allocation path's expectation that the provider is associated with the parent device.

## Direct core call graph

| Consumer function | Direct closed API | Role/order |
|---|---|---|
| `tee_tz_new` | `tee_core_alloc` | Allocate and initialize the core object using the parent device, name, id, ops, and private tail size. |
| `tee_tz_new` | `tee_core_add` | Register the three misc records and lifecycle surfaces after provider-private initialization. |
| `tee_tz_new` | `__tee_get` | Take the initial module/device/backend reference after successful registration. |
| `tee_tz_new` | `tee_core_del` | Unwind a failed add/get path. |
| `tkcore_ffa_remove` | `tee_core_del` | Remove the FF-A-backed core object. |
| `tkcore_smc_remove` | `tee_core_del` | Remove the platform/SMC-backed core object. |
| none | `tee_core_free` | No relocation exists in this frozen consumer; stock uses `tee_core_del` after an allocated object enters the constructor's teardown domain. |

The successful constructor ordering is:

```text
tee_core_alloc
  → provider-private initialization
  → tee_core_add
  → __tee_get
  → publish returned tee pointer
```

The post-registration failure edge calls `tee_core_del`; both transport remove functions also call `tee_core_del`.

`tee_core_free` is nevertheless closed and exported, but has no natural call edge in frozen `tkcore_drv`. Its absence is recorded as **NOT_CALLED**, not fabricated into a false consumer trace and not treated as a failure.

## ABI checks

All five target KCFI ids exactly match stock:

| API | KCFI | Phase-3A-R state |
|---|---|---|
| `tee_core_alloc` | `0x89819660` | `CFG_EQUIVALENT` |
| `tee_core_add` | `0xa1200a70` | `CFG_EQUIVALENT` |
| `__tee_get` | `0xa1200a70` | `CFG_EQUIVALENT` |
| `tee_core_del` | `0xa1200a70` | `EXACT_BYTE` |
| `tee_core_free` | `0xa1200a70` | `EXACT_BYTE`, not called by this consumer |

Every naturally called API is present in Phase-3A-R exports. Export CRCs are not yet claimed natural because the island uses private reconstructed type names; this remains static compatibility evidence only.

## Scope boundary

This report does not require or claim final-natural `tkcore_drv` acceptance. It does not build `tkcore_drv`, `tmem_ffa`, or microarray against the island. Those gates belong after the remaining tkcore subsystems are reconstructed.

## Verdict

All actual frozen `tkcore_drv` core-lifecycle edges resolve to APIs with exact KCFI and closed stock semantics; allocation/add/get ordering and deletion unwind/removal ordering are coherent. The unreferenced `tee_core_free` API is accurately accounted rather than invented.

**PASS_STATIC**
