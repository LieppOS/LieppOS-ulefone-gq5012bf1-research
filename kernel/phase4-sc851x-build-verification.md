# SC851x exact-GKI build and oracle verification

## Build

```text
workspace: /home/armol/kernel-work/gki-12901745-workspace
target: //lieppos/sc851x-recon:sc851x_recon
kernel: 6.1.115-android14-11, GKI ab/12901745
commit: 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
BUILD_RC=0
compiler warnings=0
unresolved symbols=0
```

No fake `Module.symvers`, CRC patch, symbol shim, or binary edit was used. The
Kleaf `check_no_remaining` output is an empty file. The signing-key SSL notices
in `recon-build.log` are the workspace's expected unsigned-module notice and do
not fail the build.

## Static comparison

Oracle:
`workspace/phase4-sc851x/stock/sc851x_charger.ko`

Rebuild:
`workspace/phase4-sc851x/recon/sc851x_charger.ko`

Verifier:
`workspace/phase4-sc851x/verify_recon.py`

Result:
`workspace/phase4-sc851x/verify-recon-vs-stock.txt`

| metric | stock | reconstruction | result |
|---|---:|---:|---|
| file size | 28,488 | 28,480 | 8-byte local vermagic-length delta |
| defined functions | 11 | 11 | exact keys/sizes |
| `.text` | 3,228 | 3,228 | size exact |
| `.init.text` | 48 | 48 | byte-identical |
| `.exit.text` | 40 | 40 | byte-identical |
| `.rodata` | 1,520 | 1,520 | byte-identical |
| `.data` | 1,112 | 1,112 | byte-identical |
| `.rodata.str1.1` | 1,509 | 1,509 | byte-identical |
| `__versions` | 1,920 | 1,920 | byte-identical, 30 entries |
| `.comment` | 185 | 185 | byte-identical |
| total relocations | 254 | 254 | target/type sequence exact |
| `.rela.text` | 215 | 215 | target/type sequence exact |
| exports | 0 | 0 | exact |
| KCFI type words | 11 | 11 | all exact |

Eight of nine behavioral `.text` functions are byte-identical. The 1924-byte
probe has compiler-local stack/register scheduling differences after inlining
large on-stack property/init tables, while retaining exact size and exact
relocation target/type order. IRQ registration differs only in equivalent
unsigned bounds-check encodings. These are reported residuals, not claimed as
byte identity.

## Safety

No reconstructed module was loaded and no live register, GPIO, regulator,
reverse-power, bind/unbind, flash, or slot operation was performed.
