# yft_tiny2c_usb mandatory RED

## Baseline

- Stock oracle: `workspace/phase4-yft-tiny2c-usb/oracle/yft_tiny2c_usb-stock.ko`
- SHA256: `77baeee8fa7c01d9b6ad9b3a9743caa69aa61b840c3d565d5263d3e965d63eed`
- Frozen stock functions: 12
- Frozen stock undefined ELF symbols: 22
- Frozen stock `__versions` entries: 23 (22 undefined symbols plus `module_layout`)
- Frozen stock exports: 0

## Source search disposition at RED

`NO_PUBLIC_DONOR_FOUND`

No usable implementation of `yft_tiny2c_usb` was present in the local Nothing/MediaTek
source trees or prior source-candidate records. Exact-identifier public search is recorded
separately in `phase4-yft-tiny2c-usb-source-candidates.md`. The local
`mt6375-charger.c` is provider/framework evidence, not a source donor for this leaf.

## Empty-source RED

Before any reconstruction source was created, the exact-GKI reconstruction directory did
not exist and no candidate module could be built:

| Gate | Stock | Empty source baseline | RED |
|---|---:|---:|---|
| module exists | yes | no | FAIL |
| function set | 12 | 0 | FAIL |
| undefined ELF symbols | 22 | 0 | FAIL |
| `__versions` entries | 23 | 0 | FAIL |
| intermodule `yft_usb_flag` edge | present | absent | FAIL |
| DT/platform binding | present | absent | FAIL |
| GPIO/power behavior | present | absent | FAIL |
| userspace ABI | present | absent | FAIL |
| verifier | oracle available | no candidate | FAIL CLOSED |

**RED established: YES.** This file and the frozen oracle precede creation of reconstruction
source under the exact-GKI workspace.
