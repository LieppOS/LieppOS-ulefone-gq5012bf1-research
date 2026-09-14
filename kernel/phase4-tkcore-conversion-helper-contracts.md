# GQ5012BF1 tkcore compat conversion-helper contracts

All three helpers are GLOBAL but not exported. They convert **compat to native in place**; none is bidirectional and none copies a native result back to a separate compat object.

## `convert_compat_tee_shm_io`

```c
int convert_compat_tee_shm_io(struct tee_shm_io __user *shm);
```

Stock offset `0x1284`, size 276, KCFI `0xdaee5623`.

- NULL → `-EINVAL`.
- Writes zero to the upper 32-bit half of `buffer` at offset 4.
- Success → 0; failed user store → `-EFAULT`.
- No other field is read or written.

## `convert_compat_tee_spta_inst`

```c
int convert_compat_tee_spta_inst(struct tee_spta_inst __user *inst);
```

Stock offset `0x139c`, size 516, KCFI `0xba9dd2d9`.

- NULL → `-EINVAL`.
- Zeroes upper pointer words at offsets 4 and 0x14 in order.
- First failure stops immediately; any failed user store → `-EFAULT`; otherwise 0.
- Bytes 8–15 are never touched and their meaning is not claimed.

The sole stock call site is the compat pre-path for ioctl `0xc01874ae`; native dispatch then rejects that command. The helper is still a real stock function and is reconstructed exactly rather than omitted as dead code.

## `convert_compat_tee_cmd`

```c
int convert_compat_tee_cmd(struct tee_cmd_io __user *cmd);
```

Stock offset `0x0384`, size 3644, KCFI `0xbb8e9218`.

Exact order:

1. NULL command → `-EINVAL`.
2. Zero command pointer high words at `cmd+0x14` (UUID), `+0x1c` (data), `+0x24` (operation). Any failure → `-EFAULT`.
3. Copy the widened 8-byte operation pointer from `cmd+0x20`; NULL operation → `-EINVAL`.
4. Copy `operation->paramTypes` (4 bytes at +4).
5. Zero operation session-pointer high word at `operation+0x6c`.
6. Walk exactly four parameters, using the original type nibble:
   - 0–3: no conversion;
   - 5–7: zero high words of temporary-buffer pointer and compat size;
   - 12–15: zero high words of registered parent pointer, size and offset; copy the widened parent pointer; if non-NULL, zero that object's buffer, size and fd/pointer-union high words;
   - unsupported type: print `bad param %u` with the **parameter index**, then return `-EFAULT`.
7. Return 0.

No array count comes from userspace: the bound is the compile-time `TEEC_CONFIG_PAYLOAD_REF_COUNT == 4`. There is no output conversion phase because the widened overlay is the same total size as native and output values occupy unchanged low words.

### Mandatory direct prerequisite and Phase-3C stop

The store at `operation+0x6c` is bracketed by resolved direct branches to stock-local `uaccess_ttbr0_enable` and `uaccess_ttbr0_disable`. Both helpers are absent in Phase 3B and were explicitly excluded unless proven mandatory. That proof triggers the requested stop-before-expansion rule; this contract is recovered, but implementation is blocked pending authorization documented in `phase4-tkcore-island-phase3c-uaccess-prerequisite-blocker.md`.

## Error policy

The helpers distinguish NULL top-level/operation (`-EINVAL`) from uaccess or invalid parameter nibbles (`-EFAULT`). Both compat wrappers intentionally collapse any nonzero converter result to `-EFAULT` before native dispatch.
