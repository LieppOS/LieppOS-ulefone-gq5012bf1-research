# `custom_ldo.ko` export contract

## Result

Both consumer-visible prototypes are recovered exactly at the C type level:

```c
int custom_ldo_en(int ldo_num, int enable);
int custom_ldo_vout(int ldo_num, int value);
```

Parameter identifiers are not encoded in ELF and do not participate in
genksyms CRCs; `ldo_num`, `enable`, and `value` are reconstructed semantic
names. The return type, parameter count, parameter types, signedness, order,
and absence of enum/typedef wrappers are proved by the combined evidence
below.

| export | stock offset | stock size | KCFI ID | stock CRC | consumer |
|---|---:|---:|---:|---:|---|
| `custom_ldo_vout` | `.text+0x4` | 28 | `0x56e5b5a5` | `0xfda530e0` | `imgsensor` |
| `custom_ldo_en` | `.text+0x24` | 28 | `0x56e5b5a5` | `0x239d3df2` | `imgsensor` |

## Prototype proof

1. Both stock wrappers have KCFI type ID `0x56e5b5a5`.
2. The called stock provider exports `will_ldo_vout` and `will_ldo_en` with
   the same KCFI ID and with independently reproduced declarations:

   ```c
   int will_ldo_vout(int ldo_num, int value);
   int will_ldo_en(int ldo_num, int enable);
   ```

3. Each wrapper passes incoming `w0` and `w1` untouched to its corresponding
   provider and returns the provider's `w0` untouched. AArch64 therefore
   proves exactly two 32-bit scalar arguments and a 32-bit scalar result.
4. Stock `imgsensor.ko` calls both exports with 32-bit `w0`/`w1` values.
5. The reconstructed plain-`int` declarations reproduce both stock genksyms
   CRCs naturally (see the build/structural verification evidence). This
   excludes unsigned and enum/typedef declaration alternatives visible to
   genksyms.

## ABI records

* `kernel/phase4-custom-ldo-functions.tsv`
* `kernel/phase4-custom-ldo-exports.tsv`
* `kernel/phase4-custom-ldo-modversions.tsv`
* `workspace/phase4-custom-ldo/stock-objdump-text.txt`

Status: **PROVEN_FROM_STOCK**, with generated-build CRC confirmation.
