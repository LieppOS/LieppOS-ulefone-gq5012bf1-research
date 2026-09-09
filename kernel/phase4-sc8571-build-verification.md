# GQ5012BF1 SC8571 exact-GKI build verification

## Build

Source of record during the build:

```text
/home/armol/kernel-work/gki-12901745-workspace/lieppos/sc8571-recon/
```

Commit-contained mirror:

```text
kernel/phase4-sc8571-recon/
```

Kernel baseline:

```text
GKI build: ab/12901745
Linux: 6.1.115-android14-11
common commit: 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
common tag/describe: android14-6.1-2024-12_r4
compiler identity: Android clang 17.0.2, same .comment bytes as stock
```

Command:

```sh
cd /home/armol/kernel-work/gki-12901745-workspace
tools/bazel build //lieppos/sc8571-recon:sc8571_recon
```

Result:

```text
BUILD_RC=0
compiler warnings=0
unresolved symbols=0
check_no_remaining=empty
```

The stock-only `charger_device_register` edge is supplied to `modpost` as the
stock-proven Module.symvers record `0x36325d38`; no source or built provider is
available in the GKI target. This does not patch the module: the resulting
`__versions` section is naturally emitted and is byte-identical to stock.

Rebuilt artifact:

```text
size=49,808 bytes
sha256=73b0c46f4b3189ff26598ee188eb9e2f575c8d8977dd4b3fdddfd8b217e55d0f
name=sc8571_charger
description=SC SC8571 Driver
author=South Chip <Aiden-yu@southchip.com>
license=GPL v2
depends=charger_class
vermagic=6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64
```

The `maybe-dirty` SCM token is the local Kleaf workspace identity. Stock uses
`g945dff7bc1bf`; all remaining vermagic tokens match.

## Static parity result

Run:

```sh
python3 kernel/scripts/phase4_sc8571_verify_recon.py \
  workspace/phase4-sc8571/oracle/sc8571_charger.stock.ko \
  workspace/phase4-sc8571/recon/sc8571_charger.ko
```

Frozen output: `workspace/phase4-sc8571/verification.txt`.

Result:

```text
BINARY_IDENTITY=NO
ABI_AND_BEHAVIORAL_CONTRACT_PARITY=PASS
```

Measured parity:

- exact 34-function key set;
- exact KCFI type word for all functions;
- 20/34 functions raw-byte-identical;
- exact per-function external-call multisets;
- exact 34-object key set and sizes after excluding only the vermagic string;
- all 27 comparable named PROGBITS objects byte-identical;
- `.rodata` byte-identical (2,648 bytes), including register fields, ADC
  constants, match/property tables and compiler-generated maps;
- `.rodata.str1.1` has an exact NUL-string multiset and exact 2,657-byte size;
- `.text` has exact aggregate size 8,232 bytes;
- `__versions` byte-identical: 42 records in exact stock order;
- exact 41-symbol undefined-import set and zero exports;
- exact `.comment`, proving the compiler identity payload matches.

Two function-size residuals cancel exactly:

| function | stock | rebuilt | explanation |
|---|---:|---:|---|
| `sc8571_charger_probe` | 1,180 | 1,176 | equivalent compiler basic-block/string-address sharing |
| `mtk_sc8571_set_ibatocp` | 204 | 208 | equivalent integer-division scheduling |

There are 610 rebuilt versus 608 stock relocations. The +2 is confined to
compiler layout/address materialization in probe. Every function has the exact
same multiset of external calls, including probe, and named data/operation
objects are exact. Internal `.data` placement/padding and local BuildID differ.
No binary patching, CRC editing, fake framework implementation, or unsafe
phone-side execution was used to remove those non-behavioral differences.

## Validation boundary

This is exact-GKI build validation plus relocation-aware static oracle parity,
not runtime validation. The reconstructed module was not inserted, rebound or
used to write SC8571 registers. No charging or PD/PPS state was changed.
