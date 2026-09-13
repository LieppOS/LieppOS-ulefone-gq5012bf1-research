# gz_main_mod — authoritative source-closure report

**Classification: `DIRECT_SOURCE_MATCH`**
**FROZEN FOR RE: YES**

GQ5012BF1 (Ulefone Armor 29 Pro Thermal, MT6878/MT6878T), LieppOS.
Static/offline analysis only.

---

## 1. Stock oracle

| item | value |
|---|---|
| canonical path | `vendor_dlkm/lib/modules/gz_main_mod.ko` |
| SHA256 | `398ce0058798adf1d919dbd60856ed7b83e956f5d778ff6d3116e27468916fc7` |
| size | 159400 bytes |
| Build ID | `3f40ddec521d65a7dce6f240fa306e8f8da1057d` |
| compiler | Android clang 17.0.2 (10087095, +pgo +bolt +lto) |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| load index | `modules.load` line 150 (one-based) / 149 (zero-based) |
| recovery | absent from every recovery load list |
| duplicates | none — exactly one stock placement |
| parameters | none |
| exports | **0** |

Frozen at `workspace/phase4-gz-main-mod/oracle/gz_main_mod.stock.ko`.

## 2. Source lineage

Pinned MediaTek/Nothing `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`,
`drivers/misc/mediatek/geniezone/`. Object list taken verbatim from the vendor
Makefile:

```
gz_main.o  mtee_ut/gz_ut.o  mtee_ut/gz_chmem_ut.o
mtee_ut/gz_shmem_ut.o  mtee_ut/gz_vreg_ut.o  gz_ffa.o
```

Built **in the vendor directory layout** so the embedded `__FILE__` string
`../kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz_ffa.c`
reproduces byte-for-byte.

Target: `//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone:gz_main_mod`
against `//common:kernel_aarch64` (exact GKI ab/12901745).

## 3. RED

The pinned donor built **unmodified** and reproduced stock immediately.
Only build plumbing was authored. The RED build and the final build are the
same bytes (`7b7cb36b03d7749e5f7b3d53c8b0207bfc7f7e6b4bf2819c501b42d42cb5df51`),
which proves no source change was introduced afterwards.

The delta ledger contains **no functional row**.

## 4. Parity

| metric | result |
|---|---|
| stock / rebuilt functions | 42 / 42 |
| shared / missing / extra | 42 / 0 / 0 |
| size-identical | **42/42** |
| byte-identical | **42/42** |
| KCFI ids | **42/42 exact** |
| imports | 76 / 76 IDENTICAL |
| MODVERSIONs | 77 / 77 IDENTICAL |
| relocations | **2817 / 2817 IDENTICAL** |
| strings | 286 / 286, one differs (`vermagic`) |
| objects | 45 / 45, one differs in size (`__UNIQUE_ID_vermagic333`) |
| sections | 45 / 45 same names |
| exports | 0 / 0 |

## 5. Provider provenance — 76 imports

| class | count |
|---|---:|
| `GKI_NATURAL` | 51 |
| `GZ_TZ_SYSTEM_NATURAL` | 15 |
| `GZ_TRUSTY_NATURAL` | 5 |
| `TMEM_FFA_NATURAL` | 2 |
| `GZ_IPC_NATURAL` | 1 |
| `FFA_V10_NATURAL` | 1 |
| `STOCK_RUNTIME_PROVIDER` | **1** |
| `UNKNOWN` | **0** |

**75 of 76 natural.** The single non-source edge is
`dmabuf_to_secure_handle` from **`mtk_sec_heap`**, which is genuinely stock on
this device and is declared explicitly in
`stock-provider.symvers` / `stock-provider.provenance.json`. It is never
described as reconstructed.

All GenieZone provider edges resolve against REAL source-built modules,
including the **witness-free** `gz-tz-system-accept` build — no gz_tz_system,
gz_ipc_mod, gz_trusty_mod, ffa_v10 or tmem_ffa witness exists in this build.

## 6. Userspace ABI — closed

Two character devices, both owned by this module:

| node | mechanism | ioctls | compat | mmap/read/write/poll |
|---|---|---:|---|---|
| `/dev/gz_kree` | misc, `MISC_DYNAMIC_MINOR` | 9 | **yes** | none |
| `/dev/gz_ffa_dev` | dynamic chrdev + class | 8 | **no** | none |

* 17 ioctl commands total, every one named and mapped to its handler; no
  `UNKNOWN` command remains.
* All nine `/dev/gz_kree` encodings were confirmed against the stock
  disassembly of `_gz_ioctl`.
* One sysfs attribute (`gz_test`), zero module parameters, no procfs, no
  debugfs.
* Android: `/dev/gz_kree` is `0660 system:system`, labelled
  `u:object_r:gz_device:s0`, reachable by `mtk_hal_camera` and `vpud_native`;
  the userspace client library is `vendor/lib64/libgz_uree.so`.

Session, shared-memory and DT contracts are closed in their own reports.

## 7. Consumers

`gz_main_mod` exports nothing and **no stock module depends on it** (verified
across all 471 stock placements and the full `modules.dep`). It is a proven
leaf; its compatibility contract is the userspace ioctl ABI, which is
reproduced byte-exactly.

## 8. Build

| item | value |
|---|---|
| BUILD_RC | 0 |
| compiler warnings | 0 |
| modpost warnings | 0 |
| unresolved symbols | 0 (76/76 resolved) |
| forbidden techniques | none — no `KBUILD_MODPOST_WARN`, no CRC injection, no copied `__versions`, no kcrctab edit, no ELF patching |

## 9. Residuals

Exactly two, both pure build provenance, both matching the class already
accepted for `gz_trusty_mod`, `gz_ipc_mod` and `tmem_ffa`:

1. `vermagic` git-describe suffix (`g945dff7bc1bf` vs `maybe-dirty`) — the
   local exact-GKI tree is not a git checkout.
2. `.llvm_addrsig` encoding (0x58 vs 0x4e) — link-time ICF metadata, no code
   or data.

Total whole-file delta: 8 bytes. **No functional residual.**

## 10. Verdict

`gz_main_mod.ko` is **behaviourally and ABI closed**:

* complete function set closed — 42/42 byte-identical, 42/42 KCFI;
* complete import/MODVERSION set closed — 76/76 and 77/77 identical;
* every source-available provider edge is NATURAL (75/76), the one exception
  declared;
* userspace ABI, all 17 ioctls, session lifecycle, memory model, DT binding
  and Android/SELinux contract documented and unchanged;
* exact-GKI build clean;
* no kernel consumers to break;
* verifier passes fail-closed.

`FROZEN FOR RE: YES`.

Out of scope and untouched: GenieZone hypervisor, Trusty/Nebula secure world,
TA code, SMC semantics beyond Linux source, `tkcore`, `mtk_sec_heap`,
KeyMint/Gatekeeper/RPMB/Widevine.
