# `ffa_v10.ko` — authoritative source closure report

**Device:** Ulefone Armor 29 Pro Thermal, GQ5012BF1, MediaTek MT6878/MT6878T
**Baseline:** Linux 6.1.115-android14-11, Android CI `ab/12901745`, common commit
`6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
**Exact-GKI workspace:** `/home/armol/kernel-work/gki-12901745-workspace`
**Verifier:** `kernel/scripts/phase4_ffa_v10_verify.py` — **49/49 checks passed**

---

## Final classification

**`DIRECT_SOURCE_MATCH`.**

The shipped module is built from source that exists verbatim in the pinned
Nothing MT6878 vendor tree
(`device_modules/drivers/misc/mediatek/trusted_mem/ffa_v10/`,
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`). Building those
four files unmodified against exact GKI 12901745 reproduces the stock module
**34/34 byte-identical**, with **all 5 export CRCs regenerated naturally by
genksyms** — no witness, no CRC injection, no ELF patch, no
`KBUILD_MODPOST_WARN` anywhere in the closure.

## FROZEN status

**FROZEN FOR RE: YES.**

| criterion | status |
|---|---|
| complete stock function set accounted | ✅ 34/34 by name |
| exact import ABI | ✅ 40/40 imports, 41/41 MODVERSION CRCs identical |
| complete stock export set accounted | ✅ 5/5 (`ffa_bus_type`, `ffa_device_register`, `ffa_device_unregister`, `ffa_driver_register`, `ffa_driver_unregister`) |
| ALL export CRCs naturally reproduced | ✅ 5/5, including both hard gates |
| KCFI exact where applicable | ✅ 34/34 |
| exact FF-A bus/device behaviour | ✅ byte-identical `bus.c` |
| exact registration/unregistration behaviour | ✅ byte-identical, see registration contract |
| exact message-ops contract | ✅ byte-identical `ffa_sync_send_receive`/`ffa_msg_send_direct_req` |
| exact memory-ops contract | ✅ present, byte-identical, unused by any consumer on this device |
| exact lifecycle | ✅ byte-identical `init_module`/`cleanup_module` |
| all known stock consumers accept rebuilt provider | ✅ 3/3 (`tkcore_drv`, `tmem_ffa`, `gz_main_mod`) |
| exact-GKI build clean | ✅ `BUILD_RC=0`, 0 compiler warnings, 0 modpost warnings |
| verifier PASS | ✅ 49/49 |
| no unexplained Linux-visible residual | ✅ only the documented scmversion stamp |

## Stock oracle

| | |
|---|---|
| canonical path | `workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/ffa_v10.ko` |
| sha256 | `2f8341d3f920418f3d9f4b8f64299acf97e591ad232a6bbbf6298b63231eebde` |
| size | 38688 B |
| all copies (3 found) | byte-identical |
| vermagic | `6.1.115-android14-11-g945dff7bc1bf SMP preempt mod_unload modversions aarch64` |
| name / alias / license / author / description | `ffa_v10` / `arm-ffa` / `GPL v2` / `Sudeep Holla <sudeep.holla@arm.com>` / `Arm FF-A interface driver` |
| depends | *(empty — provider leaf)* |
| placement | `vendor_boot` platform ramdisk, `P:97` / `R:95` (load order `ffa_v10 → teeperf → tkcore → tkcore_drv` preserved) |

Full ELF inventory: `kernel/phase4-ffa-v10-{functions,objects,imports,
modversions,exports,relocations,strings}.tsv`. Freeze notes:
`kernel/phase4-ffa-v10-stock-oracle.txt`.

## Source provenance

`kernel/phase4-ffa-v10-source-candidates.md` (search), `kernel/
phase4-ffa-v10-lineage.md` (dating + delta analysis), `kernel/
phase4-ffa-v10-RED.md` (mandatory unmodified-donor evidence).

**Donor:** exact MediaTek vendor copy of the upstream Linux FF-A transport
(Sudeep Holla, ARM Ltd.), snapshotted between android14-6.1 v6.1.34 and
v6.1.56, shipped unmodified apart from a copyright line and one line-wrap.
Not a rewrite. Not a protocol reimplementation.

```
bus.c      3cda7cc57a774e1b0c138acd8a5fc8fb12e4255fd81b0e96675a290be40bf8a6
driver.c   6b14f18ee44e4966810d55b00eaa3d32163da1c82b8290e78cd30f3fb66306c5
smccc.c    3701a267eaad251847e25fefa80ba1a6495e57c3af3bc095ac73e50288cd49a3
common.h   84883f2fefa4d64c51f5491e37388ac29e75925e138acc1a3fac51d3baf196f5
Kconfig    c47ebe5ba1b43a6e1225c59ea48812a5a0821f2b2e2b87afc04fb8f913e8c78c
```

## RED

Two donors were built unmodified, in order, before any delta was considered
(full detail: `phase4-ffa-v10-RED.md`):

1. **Donor A** — pristine current-GKI `arm_ffa` (common commit
   `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`). RED result: **5/5 export CRCs
   match** (proving the driver family/ABI), but only **30/34 byte-identical**
   functions. The 4 mismatches were root-caused to three specific stable
   commits the vendor snapshot predates (`e578a26084eb`, `d43c3e49744c`,
   `5429ecbb1b8b`) — dating the snapshot to the v6.1.34–v6.1.56 window.
2. **Donor B** — the exact vendor source located afterward using that dating.
   RED result: **34/34 byte-identical**, closing the RED completely.

Donor A is retained as `//lieppos/ffa-v10-red` (documented drop-in that also
fixes the MEM_LEND attributes issue — see lineage.md). Donor B is the shipped
`//lieppos/ffa-v10` target. No clean-room reconstruction was required.

## Full stock export ABI

`kernel/phase4-ffa-v10-export-abi.tsv`. All five, all `EXPORT_SYMBOL_GPL`,
all **NATURAL**:

| symbol | stock CRC | status |
|---|---|---|
| `ffa_bus_type` | `0x82c0ded3` | NATURAL |
| `ffa_device_register` | `0xa400c46e` | NATURAL |
| `ffa_device_unregister` | `0x85b1f074` | NATURAL |
| `ffa_driver_register` | `0x0d53cde9` | **NATURAL (hard gate)** |
| `ffa_driver_unregister` | `0x3c660e4c` | **NATURAL (hard gate)** |

## Complete stock consumer search

`kernel/phase4-ffa-v10-consumer-abi.md`. All 471 stock `.ko` files scanned;
**three** consumers found (one beyond the two named in the task brief):

| consumer | edge(s) | result |
|---|---|---|
| `tkcore_drv.ko` | `ffa_driver_register`, `ffa_driver_unregister` | MATCH |
| `tmem_ffa.ko` | `ffa_driver_register` | MATCH |
| `gz_main_mod.ko` (new discovery) | `ffa_driver_register` | MATCH |

No consumer on this device uses `ffa_bus_type`, `ffa_device_register` or
`ffa_device_unregister`.

## FF-A type graph

`kernel/phase4-ffa-v10-type-graph.md`. Every type feeding an export CRC is
public upstream `include/linux/arm_ffa.h` API — `struct ffa_driver`,
`struct ffa_device`, `struct ffa_device_id`, the `ffa_info_ops`/`ffa_msg_ops`/
`ffa_mem_ops`/`ffa_ops` tables, `struct ffa_partition_info`,
`struct ffa_send_direct_data`, `struct ffa_mem_ops_args`. Nothing is a private
vendor type, which is structurally why all five CRCs are natural (contrast
with tkcore's private `struct tee`). Function-pointer prototypes are
cross-verified independently via Clang kCFI type ids, not just genksyms.

## Driver registration contract

`kernel/phase4-ffa-v10-registration-contract.md`. `ffa_driver_register()`
stores `.bus/.name/.owner/.mod_name` into the embedded `struct device_driver`
and calls `driver_register()` verbatim; `ffa_driver_unregister()` calls
`driver_unregister()` verbatim. `tkcore_drv`'s exact call —
`ffa_driver_register(&tkcore_ffa_driver, THIS_MODULE, KBUILD_MODNAME)` —
is a direct, unmodified match to this contract, proven by the acceptance
rebuild.

## FF-A bus/device contract

`kernel/phase4-ffa-v10-bus-contract.md`. `ffa_bus_type` (match/uevent/probe/
remove), `ffa_device_register`/`_unregister`, UUID matching, and the
`partition_id`/`uuid` sysfs `DEVICE_ATTR_RO` pair — all live entirely inside
`ffa_v10.ko` since GKI builds none of `CONFIG_ARM_FFA_TRANSPORT` on this
device.

## Message transport ABI

`kernel/phase4-ffa-v10-message-contract.md`. `ffa_dev->ops->msg_ops->
sync_send_receive()` → `ffa_msg_send_direct_req()`, packing
`struct ffa_send_direct_data`'s five `unsigned long` fields into `x3–x7`,
selecting `FFA_MSG_SEND_DIRECT_REQ` (32-bit) vs `FFA_FN64_...` (64-bit) by
`dev->mode_32bit`, transparently resuming `FFA_INTERRUPT` responses with
`FFA_RUN`, and translating `FFA_ERROR` codes to negative `errno` before the
caller ever sees them.

## Memory-ops ABI

`kernel/phase4-ffa-v10-memory-contract.md`. Share/lend/reclaim/fragment
machinery present and byte-identical, but **unused by every consumer on this
device** — `tkcore_drv` builds its own SHM window via SMC fast-call
`0xf2005704`, not FF-A memory-share.

## Protocol version

`kernel/phase4-ffa-v10-version-contract.md`. `FFA_DRIVER_VERSION` and
`FFA_MIN_VERSION` are both hard-coded `FFA_VERSION_1_0` — the entire reason
for the `ffa_v10` name. The driver downgrades even a higher-versioned
firmware's response to v1.0 semantics; consequently `ffa_mode_32bit_set()`'s
`version > FFA_VERSION_1_0` guard never passes, so every registered partition
on this device always gets 32-bit direct-message mode.

## Module init/exit

`kernel/phase4-ffa-v10-lifecycle.md`. `ffa_init()`/`ffa_exit()`, byte-identical
to stock, are what `subsys_initcall`/`module_exit` resolve to under `MODULE`
(confirmed: `include/linux/module.h` maps `subsys_initcall(fn)` to
`module_init(fn)` when building out-of-tree). No lifecycle quirks to preserve
— the teardown is the clean symmetric inverse of init.

## Config/build contract

`kernel/phase4-ffa-v10-build-contract.md`. `CONFIG_ARM_FFA_TRANSPORT` is unset
in GKI's `gki_defconfig` (confirmed by grep), which is exactly why this ships
as a vendor module rather than in `system_dlkm`. Two defines are required and
both are proven necessary by stock ELF evidence, not guessed:
`CONFIG_ARM_FFA_TRANSPORT_MODULE=1` (else `arm_ffa.h`'s `IS_REACHABLE()` guard
substitutes stub prototypes and every export CRC changes) and
`CONFIG_ARM_FFA_SMCCC=1` (else `ffa_transport_init` is a stub and `smccc.o` is
not even compiled). No vendor include paths, generated headers or namespace
imports are required.

## Exact-GKI build

```
tools/bazel build //lieppos/ffa-v10:ffa_v10          # final target, donor B
tools/bazel build //lieppos/ffa-v10-red:ffa_v10_red  # RED baseline, donor A
```

Both build against `//common:kernel_aarch64`, the correct exact-GKI target
(not the historical broken prebuilt `kernel_filegroup` path). `BUILD_RC=0`,
0 compiler warnings, 0 modpost warnings for the final target. No
`KBUILD_MODPOST_WARN` anywhere in `//lieppos/ffa-v10`.

## Kernel import parity

**100% edge parity.** All 40 kernel imports and all 41 `__versions` entries
(40 imports + `module_layout`) are identical, byte-for-byte CRC, between
stock and rebuilt. Zero missing, zero extra.

## Natural export CRC gate — HARD GATE PASSED

| symbol | stock | rebuilt | status |
|---|---|---|---|
| `ffa_bus_type` | `0x82c0ded3` | `0x82c0ded3` | ✅ |
| `ffa_device_register` | `0xa400c46e` | `0xa400c46e` | ✅ |
| `ffa_device_unregister` | `0x85b1f074` | `0x85b1f074` | ✅ |
| **`ffa_driver_register`** | **`0x0d53cde9`** | **`0x0d53cde9`** | ✅ **HARD GATE** |
| **`ffa_driver_unregister`** | **`0x3c660e4c`** | **`0x3c660e4c`** | ✅ **HARD GATE** |

No provider witness of any kind is used anywhere in `//lieppos/ffa-v10`;
verified by check 7 of the verifier (no `.symvers`/witness/patch files in the
package, no `KBUILD_EXTRA_SYMBOLS`, no `KBUILD_MODPOST_WARN`).

## KCFI parity

**34/34 identical**, including every exported function
(`ffa_driver_register` `0xa23dba3c`, `ffa_driver_unregister` `0xb0ac9bfc`,
`ffa_device_register` `0xeeea6c98`, `ffa_device_unregister` `0xa30d19cc`),
every bus callback (`ffa_device_match/probe/remove/uevent`), and both
init/exit entry points.

## Function parity

`kernel/phase4-ffa-v10-function-parity.tsv`.

| metric | value |
|---|---|
| stock functions | 34 |
| rebuilt functions | 34 |
| shared | 34 |
| missing | 0 |
| extra | 0 |
| size-identical | 34/34 |
| **byte-identical** | **34/34** |
| kCFI exact | 34/34 |

## Object parity

`kernel/phase4-ffa-v10-object-parity.tsv`. 28/28 objects, all
`BYTE_IDENTICAL` except the module-metadata `vermagic` string
(`BUILD_PROVENANCE_ONLY` — see residuals).

## Behavioral verifier

`python3 kernel/scripts/phase4_ffa_v10_verify.py` → **49/49 CHECKS PASSED**,
`RESULT: ffa_v10 SOURCE-CLOSED - all 5 export CRCs NATURAL, no provider
witnesses`. Covers: stock oracle hash/size, all copies identical, module
metadata, donor provenance hashes, export surface, the natural CRC gate
(including both hard gates), that the CRCs really originate from this build's
own `__kcrctab_gpl` (not injected), absence of any witness/patch/
`KBUILD_MODPOST_WARN` artefact, function/import parity, all three discovered
stock consumer edges, and the `tkcore_drv` acceptance rebuild.

## Secure-world / opaque items

None applicable in the sense tkcore_drv had them — `ffa_v10` is entirely
Linux-side transport code; the only opacity is the secure firmware's actual
FF-A implementation behind each SMC/HVC call, which is out of scope by
project charter for every module in this stack.

## Residuals

Exactly one, cosmetic and explained:

* **`vermagic` scmversion stamp** — rebuilt carries `-maybe-dirty`, stock
  carries `-g945dff7bc1bf`. Documented project-wide artefact: GKI commit
  `945dff7bc1bf` is absent from this local mirror, so kleaf's scmversion
  stamp differs identically for every module rebuilt in this workspace (see
  `module-replacement-plan.md`). Not a source or ABI difference — every byte
  of code, every export CRC, and every import CRC is unaffected.

## Runtime-validation status

**NOT RUNTIME-VALIDATED.** Static/offline only, per task charter: nothing was
loaded, unloaded, probed, or SMC'd on the device. Every claim here is
reproducible from the frozen stock oracle plus the exact-GKI build.

## Safety

No FF-A calls, no TrustKernel invocations, no SMCs, no TEE device opens, no DT
edits, no reserved-memory or secure-memory touches, no flashing, no reboot, no
slot switch, no driver bind/unbind were performed. Load order
`ffa_v10 → teeperf → tkcore → tkcore_drv` (P:97–P:100, R:95–R:98) is
unchanged and must be preserved by any future flashing work.

## Evidence index

| artefact | contents |
|---|---|
| `kernel/phase4-ffa-v10-reconstruction.md` | this report |
| `kernel/scripts/phase4_ffa_v10_verify.py` | fail-closed verifier (49 checks) |
| `kernel/scripts/phase4_elf_inventory.py` | generic 7-TSV ELF inventory dumper (new, reused from this task on) |
| `kernel/scripts/phase4_ffa_v10_parity.py` | stock-vs-rebuilt function/object parity analyser |
| `kernel/phase4-ffa-v10-stock-oracle.txt` | frozen oracle facts |
| `kernel/phase4-ffa-v10-{functions,objects,imports,modversions,exports,relocations,strings}.tsv` | full ELF inventory |
| `kernel/phase4-ffa-v10-source-candidates.md` | source search |
| `kernel/phase4-ffa-v10-lineage.md` | driver lineage + exact dating |
| `kernel/phase4-ffa-v10-RED.md` | mandatory unmodified-donor evidence |
| `kernel/phase4-ffa-v10-export-abi.tsv` | full export ABI table |
| `kernel/phase4-ffa-v10-consumer-abi.md` | all 3 discovered stock consumers |
| `kernel/phase4-ffa-v10-type-graph.md` | type graph behind every export CRC |
| `kernel/phase4-ffa-v10-registration-contract.md` | register/unregister contract |
| `kernel/phase4-ffa-v10-bus-contract.md` | bus/device contract |
| `kernel/phase4-ffa-v10-message-contract.md` | message transport ABI |
| `kernel/phase4-ffa-v10-memory-contract.md` | memory-ops ABI |
| `kernel/phase4-ffa-v10-version-contract.md` | protocol version contract |
| `kernel/phase4-ffa-v10-lifecycle.md` | init/exit |
| `kernel/phase4-ffa-v10-build-contract.md` | Kconfig/Makefile/defines |
| `kernel/phase4-ffa-v10-function-parity.tsv` | per-function parity |
| `kernel/phase4-ffa-v10-object-parity.tsv` | per-object parity |
| `//lieppos/ffa-v10` | final target (donor B, exact vendor source) |
| `//lieppos/ffa-v10-red` | RED baseline (donor A, pristine current-GKI) |
| `workspace/phase4-ffa-v10/{oracle,build,raw}/` | frozen artefacts and disassembly |

## Final verdict

`ffa_v10.ko` is **`DIRECT_SOURCE_MATCH`**, **FROZEN FOR RE**. All five export
CRCs are produced naturally by genksyms from real, unmodified, exactly-dated
vendor C — including both hard-gate symbols `ffa_driver_register` and
`ffa_driver_unregister`. 34/34 functions byte-identical, 40/40 kernel imports
identical, all three discovered stock consumers (`tkcore_drv`, `tmem_ffa`,
`gz_main_mod`) accept the rebuilt provider without modification.

`tkcore_drv`'s stock-ABI target was rebuilt against this real provider and is
**behaviourally unchanged** (byte-identical `.ko`, 50/50 functions, 0
exports, 37 pre-existing checks still pass) — only its ABI *provenance*
improved:

| edge class | before | after |
|---|---|---|
| NATURAL | 6 | **8** (+`ffa_driver_register`, +`ffa_driver_unregister`) |
| STOCK_PROVIDER_WITNESS | 7 | **5** |

The remaining 5 witnesses are exactly the tkcore private-type blockers
(`tee_core_alloc/add/del`, `__tee_get`, `tee_supp_cmd`) and are untouched.
**`tkcore` remains `PROVIDER_ABI_PARTIAL` / `NOT RECONSTRUCTED` / stock
runtime provider, blocked on original TrustKernel private headers — not
reopened by this task.**
