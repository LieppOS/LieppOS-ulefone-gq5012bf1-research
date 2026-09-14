# GQ5012BF1 tkcore — `tee_spi_cfg_padsel` recovered contract

Stock: `0x90c8`, 332 bytes, KCFI `0xab53c5c9`, historical export CRC `0x56729869`.

| Question | Answer |
|---|---|
| exact prototype | `int tee_spi_cfg_padsel(uint32_t spi_padsel)` |
| KCFI | `0xab53c5c9` |
| export CRC | `0x56729869` (reproduced naturally) |
| configuration object layout | none — a single `uint32_t` is passed by value |
| config-size validation | **none** |
| pad-select value/range | **not validated**; forwarded verbatim |
| SPI instance selection | not performed in the normal world |
| controller interaction | **none** |
| global state mutation | **none** |
| locking | **none** |
| return convention | `TEEC_Result` from the TA, or the failing `TEEC_*` result |
| error paths | the three-step TEEC ladder (see the state document) |
| logging | one `pr_info("tkcore: padsel=0x%x\n", padsel)` at entry |

## Which of the four candidate behaviours is it?

The task asked whether this function only caches configuration, directly changes
SPI controller state, calls MediaTek SPI provider APIs, or mixes those.

**None of them.** The complete callee set is
`memset`, `_printk`, the five `TEEC_*` entry points and `__stack_chk_fail`.
There is no pinctrl call, no controller write, no MediaTek SPI API, and no
retained state. The function is a pure secure-world RPC: it asks the proxy TA
to apply the pad selection and returns the TA's result.

## Operation construction

```text
operation.paramTypes   = 0x1     ; TEEC_VALUE_INPUT, NONE, NONE, NONE
operation.params[0].value.a = spi_padsel
TEEC_InvokeCommand(&session, 2, &operation, &return_origin)
```

Encoded in stock as a single `stp w8, w20, [sp, #0x1c]` writing `paramTypes`
and `params[0].value.a` together.

## Reconstruction result

Size 332 == 332, KCFI exact, call multiset exact, string set exact,
relocation multiset exact. Classification **SIZE_EXACT_SEMANTIC_EXACT**.
No hardware or pinctrl was touched at any point.
