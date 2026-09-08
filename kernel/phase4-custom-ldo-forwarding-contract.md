# `custom_ldo.ko` forwarding contract

## `custom_ldo_vout`

Exact stock instruction body (`.text+0x4`, 28 bytes): PAC/stack frame,
one `R_AARCH64_CALL26 will_ldo_vout`, frame restore/AUT, return.

Equivalent C:

```c
int custom_ldo_vout(int ldo_num, int value)
{
        return will_ldo_vout(ldo_num, value);
}
```

`w0` (`ldo_num`) and `w1` (`value`) are not written before the call. The
provider's result in `w0` is not written before return. There is no channel
translation, scaling, unit conversion, clamping, validation, error mapping,
logging, branch, state access, or other side effect in this module.

## `custom_ldo_en`

Exact stock instruction body (`.text+0x24`, 28 bytes): PAC/stack frame,
one `R_AARCH64_CALL26 will_ldo_en`, frame restore/AUT, return.

Equivalent C:

```c
int custom_ldo_en(int ldo_num, int enable)
{
        return will_ldo_en(ldo_num, enable);
}
```

`w0` (`ldo_num`) and `w1` (`enable`) are not written before the call. The
provider's result in `w0` is not written before return. There is no channel or
boolean transformation, validation, error mapping, logging, branch, state
access, or other side effect in this module.

## Module-level result

The module has no `.init.text`, `.exit.text`, `.data`, `.bss`, functional
`.rodata`, functional strings, module state, hardware access, DT access, or
standalone initialization/teardown. Its only executable behavior is the two
direct forwarding calls. Generated export/module metadata is not functional
state.

| function | arguments received | arguments passed | return behavior | validation/logging/state | exact forwarding? |
|---|---|---|---|---|---|
| `custom_ldo_en` | two signed `int` | same `w0`, same `w1` | provider `w0` returned unchanged | none | YES |
| `custom_ldo_vout` | two signed `int` | same `w0`, same `w1` | provider `w0` returned unchanged | none | YES |

Evidence: `workspace/phase4-custom-ldo/stock-objdump-text.txt` and
`kernel/phase4-custom-ldo-relocations.tsv`.

Status: **PROVEN_FROM_STOCK**.
