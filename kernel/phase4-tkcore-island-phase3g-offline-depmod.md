# TrustKernel Phase 3G — offline dependency gate

Result: **PASS_OFFLINE_DEPMOD**.

Scope note: this is the conservative broader static candidate with source `tkcore_drv`. The final minimized first-boot image retains stock `tkcore_drv`, so it removes one substitution from this already clean population; see `phase4-tkcore-island-phase3g-image-construction.md`.

Evidence directory:

`workspace/phase4-tkcore-island/phase3g/offline-depmod/`

## Population

An ephemeral offline root was assembled from the authoritative extracted normal-boot module population:

- vendor boot platform ramdisk: 196 modules;
- vendor_dlkm: 215 modules;
- system_dlkm: 60 modules;
- total: **471 modules**.

Exactly these files were substituted in place:

- `vendor_boot/tkcore.ko`
- `vendor_boot/tkcore_drv.ko`
- `vendor_dlkm/tmem_ffa.ko`

No fourth module was substituted.

The exact ab/12901745 `modules.builtin` and `modules.builtin.modinfo` were supplied. `modules.order` contains every staged module once in partition/lexical precedence order. The pinned GKI build-tools `depmod` was run against release directory `6.1.115-android14-11-g6b18f0b574ab-ab12901745`.

## Standard depmod result

- return code: **0**
- warnings: **0**
- errors: **0**
- generated dependency metadata: frozen as `modules.*.generated`

## Full CRC resolution

Because ordinary depmod does not itself prove every modversion match, a separate dependency-free ELF pass parsed all 471 `__versions` and all module export CRC sections, with exact-GKI `bazel-bin/common/kernel_aarch64/Module.symvers` as the kernel provider map.

- exact-GKI symbol records: 8352
- ELF parse errors: **0**
- unresolved imports: **0**
- version disagreements: **0**
- duplicate **conflicting** provider symbols: **0**

The stock population contains same-CRC duplicate exports in mutually selected module files; these are pre-existing and not introduced by any replacement. No conflicting-CRC duplicate exists.

## Intended files

| Module | Modversion entries | Unresolved | Version disagreements | vermagic ABI-feature suffix equal to stock? |
|---|---:|---:|---:|---|
| `tkcore.ko` | 102 | 0 | 0 | YES |
| `tkcore_drv.ko` | 66 | 0 | 0 | YES |
| `tmem_ffa.ko` | 77 | 0 | 0 | YES |

This gate therefore does not rely on discovering an `Unknown symbol` or version disagreement on the target.
