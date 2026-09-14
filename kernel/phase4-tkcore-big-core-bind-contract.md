# `big_core_affinity_need_bind_cpu` contract

| Property | Proven value |
|---|---|
| stock offset / size | `0x2c0c` / 8 bytes |
| binding / export | LOCAL / not exported |
| prototype | `bool (void *context)` |
| KCFI | `0x98d3ad02` = `_ZTSFbPvE` |
| rebuilt size/KCFI | 8 / `0x98d3ad02` |
| classification | **EXACT_BYTE** |

The complete body is `mov w0,#1; ret`. It ignores context and always requests binding in the abstract policy sense. It does not inspect current CPU, candidate CPU, task/thread state, affinity masks, secure command class, or any global. It has no callee, error path, log, or side effect.

This function is **policy-only**. It does not change affinity. Its address is stored in ops slot 0, but stock contains no executable callsite of this KCFI type, so on GQ5012BF1 even the constant policy callback is dormant. Raw rebuilt bytes are identical to stock.
