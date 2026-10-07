# PARTITION-OWNERSHIP — closure (2026-10-07, static)

Workspace component `Reverse Engineer - PARTIAL/PARTITION-OWNERSHIP` → **DONE**.

## Scope

For every block partition on the device (129 by-name entries in 61
groups, taken from the read-only `slot-b-investigation` captures), this
pack records:
1. its slotting (A/B, dual copy, or single);
2. its fstab declaration;
3. which Android-side code or init scripts touch it, i.e. its owner class;
4. how AVB rollback indexes are assigned.

Out of scope:
* The *content* semantics of bootloader-private partitions. The
  preloader/lk/TEE images are not in the dump set; this is an external
  boundary.
* Destructive rollback tests.

## Result

`scripts/partition_consumers.py` writes `evidence/partition-consumers.tsv`.
A consumer is any stock file containing `by-name/<partition>`, found by a
byte scan of every stock partition tree. Mount-point strings are not used,
because they collide (for example `/misc` and `/para` appear in unrelated
binaries).

| owner class | groups |
|---|---:|
| Android code/rc consumer (named binaries/rc) | 19 |
| declared only (fstab / sepolicy label / ueventd): no Android code reads it, so the bootloader or firmware loader owns it | 29 |
| no Android-side reference at all: preloader/lk-owned | 13 |

The previously "undocumented" MediaTek reserves now have evidence-backed
owners:

| partition | Android-side owner (evidence) | class |
|---|---|---|
| `para` | `libsysenv_system.so` (sysenv), `ccci_rpcd`, `meta_tst`, `factory_init.rc` | bootloader message/env area shared with the modem RPC and factory paths |
| `proinfo` | `factory`, `meta_tst`, `factory_init.rc`/`meta_init.rc` | factory/META product-info, written only in factory/META mode |
| `expdb` | `aee_aedv64_v2` | AEE exception database |
| `mrdump` | `mrdump_tool` | MRDUMP (RAM dump) configuration |
| `otp` | `libstorage_otp.so` | storage OTP access library |
| `seccfg` | `factory_init.rc`/`meta_init.rc` only | lock-state config; normal Android never writes it |
| `boot_para`, `dram_para`, `flashinfo`, `md_sec`, `bootloader1/2` | none | preloader/lk-owned |
| `vb`, `sec1`, `pstore` | declared only | firmware-owned |

**AVB rollback ownership (static):**
* The top-level `vbmeta` uses rollback location 0. Its chain descriptors
  assign `vbmeta_system` = 2, `boot` = 3 and `vbmeta_vendor` = 4.
* Every stock image carries rollback index 0, in both slots.
* No Android component references a rollback store. Stock userspace has no
  `by-name` consumer for it, and `avbctl`/`update_engine` do not write
  indexes on MTK. The persistent indexes are therefore bootloader-owned (lk
  AVB ops) and live outside the partitions mapped here.
* Because the stock indexes are 0, any image signed with index ≥ 0 is
  accepted.
* `vbmeta_a` carries flags 3 (verification disabled), which is our
  development modification.

## Development rules (unchanged, now evidence-backed)

* Never write `seccfg`, `proinfo`, `para`, `otp`, the `nv*` partitions,
  `persist` or `protect*`. Their only writers are factory/META tools or the
  bootloader.
* `super` is shared; only explicit suffixed logical targets may be touched.
