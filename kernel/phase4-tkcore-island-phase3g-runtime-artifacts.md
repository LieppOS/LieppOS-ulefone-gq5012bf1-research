# TrustKernel Phase 3G — frozen runtime artifacts

Status: **STATIC ARTIFACT GATE PASS / DEVICE TRIAL FAILED BEFORE G1 / STOCK B RESTORED EXACTLY**

Device-trial update: the validated images were flashed to B and verified byte-exact, but the single authorized B boot never reached ADB and fell back to A. No module runtime evidence was obtained. All three B partitions were subsequently restored to their exact retained stock hashes. See `phase4-tkcore-island-phase3g-device-trial.md`.

Runtime-selection update: this file freezes the broader three-source-module static candidate. The minimized Slot-B image documented in `phase4-tkcore-island-phase3g-image-construction.md` deploys only source `tkcore` and source `tmem_ffa`; it retains stock `tkcore_drv` and stock MicroArray. The two packaged modules were rebuilt from the same accepted code with exact stock vermagic.

Starting research HEAD: `81aad9d538f67a92663ba15a73a4b6082f0815ee`.

The files below were copied immediately after a cache-cleared exact-GKI rebuild. All four build targets (the provider, the two other deployment members, and the non-deployed MicroArray control) completed with RC 0, 0 compiler warnings, 0 compiler errors, 0 modpost warnings and 0 unresolved symbols. The post-rebuild Phase-3F verifier remained **181/181**.

Authoritative frozen directory:

`workspace/phase4-tkcore-island/phase3g/artifacts/`

## Frozen broad static candidate unit

| Module | Source target / clean rebuild command | SHA-256 | Bytes | modinfo name | depends | Build ID | Expected stock placement | `modules.load` index | Runtime providers |
|---|---|---|---:|---|---|---|---|---:|---|
| `tkcore.ko` | `tools/bazel build --jobs=1 //lieppos/tkcore-island:tkcore` | `caacafd250dc2d6fbfbb1e9a0a3d129b388d31b9851b18666a33a2da90868983` | 199592 | `tkcore` | *(empty)* | `dd6133a1331bc2e5819d82e363474eb2da76690b` | vendor boot platform ramdisk `/lib/modules/tkcore.ko` | 100 | exact GKI only |
| `tkcore_drv.ko` | `tools/bazel build --jobs=1 //lieppos/tkcore-drv-phase3f:tkcore_drv_phase3f` | `5f50f77b0d47b7839d78d86baed74a790cd52e0c0654809d685ac9dd712d13a9` | 55856 | `tkcore_drv` | `ffa_v10,tkcore` | `f7b7c3497864cdf8bab887538e1064e9d6f2c79d` | vendor boot platform ramdisk `/lib/modules/tkcore_drv.ko` | 101 | source `tkcore`; installed stock `ffa_v10` |
| `tmem_ffa.ko` | `tools/bazel build --jobs=1 //lieppos/tmem-ffa-phase3f:tmem_ffa_phase3f` | `aabad7deb8041ac9c9a1ae172f6e015e22e6c75eb146ec77893dcca7a383f442` | 151448 | `tmem_ffa` | `gz_tz_system,tkcore,ffa_v10` | `26114cde7b8c67187973b232f2d483cba127c56b` | vendor_dlkm `/lib/modules/tmem_ffa.ko` | 152 | source `tkcore`; installed stock `ffa_v10` and `gz_tz_system` |

No additional module is in the deployment unit. In particular, the first boot retains stock `ffa_v10`, `gz_tz_system`, `fingerprint`, `spi-mt65xx` and `microarray_fp_tee`.

## Frozen metadata

Each `*-metadata/` directory contains:

- full `modinfo` output;
- full numeric `nm` inventory;
- complete `readelf -aW` and note/Build-ID output;
- parsed function, object, import, export, relocation, string and `__versions` maps;
- `identity.json` with SHA-256, size, name, depends, vermagic, srcversion and Build ID.

`SHA256SUMS` and `artifact-manifest.json` bind the three runtime files.

## Loader-visible identity

The final packaged copies are `phase3g/build/tkcore.stock-vermagic.ko` (`e156a9c0...`) and `phase3g/build/tmem_ffa.stock-vermagic.ko` (`073523e8...`); both carry the exact stock release token `6.1.115-android14-11-g945dff7bc1bf`. The canonical frozen acceptance artifacts below retain their original `-maybe-dirty` token and remain the source-code acceptance oracle.

All filenames and modinfo names are stock-identical. Existing `modules.load`, `modules.dep` naming and init expectations therefore require no rename and no init change.

The reconstructed files have release token `6.1.115-android14-11-maybe-dirty`, whereas stock vendor modules have `6.1.115-android14-11-g945dff7bc1bf`. This is **loader-compatible, not waived**:

- each runtime module has a populated `__versions` section (102, 66 and 77 entries respectively);
- all have the same post-release vermagic feature suffix: `SMP preempt mod_unload modversions aarch64`;
- exact Linux 6.1 `common/kernel/module/version.c:79-87` says that when the module has CRCs, `same_magic()` skips the first token of both strings and compares the remaining suffix;
- `common/kernel/module/main.c:2008-2011` invokes that check before load;
- the complete offline population audit found 0 unresolved imports and 0 version disagreements against exact-GKI `Module.symvers` plus installed module providers.

No force-load flag or vermagic alteration is required or permitted.

## Size / no-resize result

| Module | Stock bytes | Source bytes | Delta |
|---|---:|---:|---:|
| `tkcore.ko` | 221352 | 199592 | -21760 |
| `tkcore_drv.ko` | 63480 | 55856 | -7624 |
| `tmem_ffa.ko` | 151456 | 151448 | -8 |

Every replacement is smaller than its stock file. There is no module-size reason to resize super or enlarge either filesystem/image.

Runtime validation: **FAIL-CLOSED BEFORE G1**. The source module runtime behavior remains unvalidated; G2–G7 are blocked and G8–G10 are deferred.
