# ffa_v10 lineage

**Verdict: a MediaTek vendor *copy* (not a fork) of the in-tree Linux FF-A
transport, snapshotted from android14-6.1 between 6.1.34 and 6.1.56, shipped
as an out-of-tree vendor module.**

It is *not* a rewrite, not a compatibility wrapper and not a vendor protocol
stack. Every function, string, constant and ABI in the shipped binary is
upstream Arm FF-A code by Sudeep Holla.

## Evidence

| signal | finding |
|---|---|
| function names | all 34 are upstream `bus.c` / `driver.c` / `smccc.c` symbols |
| strings | verbatim upstream (`ARM FF-A: Driver version %d.%d`, `Firmware version higher than driver version, downgrading`, `Incompatible v%d.%d! Earliest supported v%d.%d`, `MODALIAS=arm_ffa:%04x:%pUb`) |
| modinfo | `author=Sudeep Holla`, `description=Arm FF-A interface driver`, `alias=arm-ffa`, `license=GPL v2` - all upstream |
| exports | the exact upstream `bus.c` export set, all five GPL-only |
| file paths | `device_modules/drivers/misc/mediatek/trusted_mem/ffa_v10/` |
| vendor delta | one `Copyright (c) 2023 MediaTek Inc.` line per file + one line reflow in `driver.c`. **Zero logic changes.** |

## Exact snapshot dating

Building the current GKI 6.1.115 copy unchanged leaves exactly four functions
differing from stock. Each difference maps to one stable commit that the
vendor snapshot predates:

| function | delta | commit the vendor snapshot lacks |
|---|---|---|
| `ffa_memory_ops` (+24 B) | stock always writes attributes `0x2f`; 6.1.115 computes `0` for `MEM_LEND` | `e578a26084eb` "firmware: arm_ffa: Don't set the memory region attributes for MEM_LEND" (6.1.56, upstream `9dda1178479a`) |
| `ffa_mode_32bit_set` (-20 B) | stock keeps the `if (drv_info->version > FFA_VERSION_1_0) return;` guard and the `_ffa_mode_32bit_set()` helper | `d43c3e49744c` "firmware: arm_ffa: Allow the FF-A drivers to use 32bit mode of messaging" (6.1.63, upstream `2d698e8b4fd2`) |
| `ffa_device_register` (1 instruction) | stock stores only `vm_id`; 6.1.115 also stores the IDA `id` (`stp w24, w21` vs `str w21`) | `5429ecbb1b8b` "firmware: arm_ffa: Assign the missing IDR allocation ID to the FFA device" (upstream `7d0bc6360f17`) |
| `ffa_partition_info_get` | consequential codegen shift only | (same set) |

Reverting those three commits from the GKI copy reproduces stock **34/34
byte-identical** - which is what first proved the dating, before the vendor
source itself was located and confirmed it.

So the vendor snapshot sits in the window **after 6.1.34** (`410689432880`
"Set handle field to zero in memory descriptor" is present) and **before
6.1.56**.

## Why it is called `ffa_v10`

Not a marketing name and not the module version: the driver hard-codes

```c
#define FFA_DRIVER_VERSION	FFA_VERSION_1_0
#define FFA_MIN_VERSION		FFA_VERSION_1_0
```

so it advertises and requires **FF-A v1.0**. MediaTek named the directory and
the module after the protocol version it implements. See
`phase4-ffa-v10-version-contract.md`.

## Security note on the snapshot

Because the vendor snapshot predates `e578a26084eb`, the shipped module sets
memory-region attributes on `FFA_MEM_LEND`, which the FF-A spec says a relayer
may reject with `INVALID_PARAMETERS`. This is stock behaviour, reproduced
faithfully; the newer GKI variant (kept as `//lieppos/ffa-v10-red`) fixes it
and has **identical export CRCs and an identical import set**, so it is a
drop-in if that behaviour is ever wanted.
