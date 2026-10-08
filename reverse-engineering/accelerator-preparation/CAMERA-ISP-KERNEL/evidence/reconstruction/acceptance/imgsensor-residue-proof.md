# imgsensor residue proof

Operands: stock SHA-256 `9243061cec77e96e3072b19f14a4d0f893e768586585830fa86f0a5129ce3558`;
rebuilt build-ID-normalized SHA-256
`0cc1d26e6079b1db94efd7b2aa778412917f883b76f1862aaa8979fd20f25ab1`.

## Exact scope

The only differing function is the static `yft_ctrl_nightled_by_idx`, `.text+0xb0e0`,
172 bytes. Its stock function hash is
`fc311aaf2363dbf758f1df6eff04c7158e0a5ff2aa2ec4d8475f1896738a4e22`;
its rebuilt hash is
`4f633637b565ddec4ff0213c4b65a8c93067f119a50c4030739093d14fe1da19`.

Whole-file differing byte count is 70: **49 code bytes**, **one relocation byte**, and
**20 GNU build-ID bytes**. All other functions, objects and sections are byte-identical.

The single relocation difference is `R_AARCH64_LDST8_ABS_LO12_NC` (type **278**),
stock offset `.text+0xb148` → rebuild `.text+0xb144`. Its symbol index, type and addend
remain identical: section symbol `.bss`, addend **32**, the byte `nightled_is_open` at
`.bss+0x20`. It is a moved byte load, **not** an ADD relocation.

## Closed input domains

`nightled_is_open` is a local one-byte bool in zero-initialized BSS. The only relocation
references to its storage are within this function:

* `.text+0xb140`: page-address relocation to `.bss+0x20`;
* `.text+0xb148` stock / `+0xb144` rebuild: byte-load relocation;
* `.text+0xb184`: byte-store relocation.

The recovered source has no other access to that variable. It starts at zero and this
function stores the booleanized requested state, so all reachable flag values are {0,1}.

A scan of direct AArch64 `BL` targets in `.text` finds exactly two calls to `0xb0e0`:

| call offset | preceding state instruction | state |
|---|---|---:|
| `0x9878` | `0x9874: 52800021` (`mov w1, #1`) | 1 |
| `0x9fe8` | `0x9fe4: 2a1f03e1` (`mov w1, wzr`) | 0 |

These call-site instructions are byte-identical in both operands. The only relocation
addressing this function is an unwind record (`.rela.eh_frame+0x126c`, type 261), not a
callable function pointer. No function-address relocation exposes it to an indirect
caller. Thus the requested state also has the closed domain {0,1}.

## Branch equivalence

Both binaries first check sensor index == 4, with the same early return and logging. The
stock uses `cmp state, #0; ccmp flag, state, #4, ne` and the rebuild uses a zero-state
branch followed by `cmp flag, #1`. Both converge on the same callees at the same offsets:
`.text+0xb178` and `+0xb180`. Registers and branch instruction placement differ; the
callees, argument values and final flag do not.

| requested state | old flag | action in both binaries | final flag |
|---:|---:|---|---:|
| 0 | 0 | return, no hardware call | 0 |
| 0 | 1 | first callee argument 0; second callee argument 10; store 0 | 0 |
| 1 | 0 | first callee argument 1; second callee argument 11; store 1 | 1 |
| 1 | 1 | return, no hardware call | 1 |

The stock's low-bit test on the zero-state path and the rebuild's zero-byte test are equal
on the proven boolean flag domain. This is not an equivalence claim for arbitrary
out-of-contract integer inputs or corrupted BSS.

## Regression guard

The verifier pins the exact normalized rebuild hash, not merely the function name or
allowed section. It also requires the exact moved relocation pair and compares every
other raw/semantic relocation individually. An arbitrary mutation to this function fails
verification; a build-ID-only change still passes. The retained regression transcript is
`../build/post-build-verifier-audit.log`.
