# GQ5012BF1 — tkcore_drv static clock trace

`tkcore_drv` is **FROZEN FOR RE** and was read only. Nothing in it was modified.

## Call site

Exactly one import and one direct call, inside `call_tee`:

```text
1310: mov  w9, #0x30000000
1314: cmp  x8, x9
1318: b.eq 0x143c                  ; a different RPC class
131c: mov  w9, #-0x7fffffff        ; 0x80000001 = the clkmgr RPC class
1320: cmp  x8, x9
1324: b.ne 0x1470                  ; not ours
1328: ldr  x9, [x25, #0x28]
132c: mov  w8, #-0xfffa            ; TEEC_ERROR_BAD_PARAMETERS (0xFFFF0006)
1330: cbz  x9, 0x1468              ; reject: null payload
1334: ldr  x8, [x25, #0x30]
1338: and  x9, x8, #0x7
133c: mov  w8, #-0xfffa
1340: cmp  x9, #0x1
1344: b.ne 0x1468                  ; reject: payload class != 1
1348: ldr  w0, [x25, #0x38]        ; arg0 -> cmd
134c: ldr  w1, [x25, #0x40]        ; arg1 -> val
1350: bl   tee_clkmgr_handle
1354: sxtw x8, w0                  ; sign-extend the int result
1358: b    0x1468                  ; publish to the secure world
```

## Recovered contract

| Question | Answer |
|---|---|
| caller | `call_tee` |
| trigger | secure-world RPC class `0x80000001` |
| argument values | `cmd = rpc[0x38]` (u32), `val = rpc[0x40]` (u32) |
| token construction | performed by the **secure world**, not by tkcore_drv |
| enable/disable use | carried in `val` bit 0; tkcore_drv does not interpret it |
| expected return | `int`; sign-extended to 64-bit and returned as the RPC result |
| error handling | tkcore_drv pre-rejects malformed payloads with `TEEC_ERROR_BAD_PARAMETERS`; it does **not** inspect `tee_clkmgr_handle`'s own error codes |
| call timing | synchronously on the RPC return path from a secure-world call |
| SMC/RPC relationship | normal-world service of a secure-world request; no SMC is issued by this path |

## Compatibility with the Phase-3D reconstruction

- The consumer needs a **direct** `int(uint32_t, uint32_t)` symbol. The island
  provides exactly that, with stock KCFI `0x06da45e1`.
- Imported CRC `0x6913f6b2` == island provider CRC `0x6913f6b2`.
- The island returns `int` values that sign-extend correctly: `0`, `-65528`
  (`TEEC_ERROR_ITEM_NOT_FOUND`) and `-65526` (`TEEC_ERROR_NOT_SUPPORTED`) — the
  same `0xFFFF00xx` family tkcore_drv itself uses one instruction earlier.
- No behaviour change is required in `tkcore_drv`.

## Result

```text
PASS_STATIC_CLOCK
```

No runtime testing was performed, no clock was toggled, and no module was loaded.
