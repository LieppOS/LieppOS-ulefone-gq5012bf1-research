# GQ5012BF1 `gz_trusty_mod.ko` source closure

## Final status

- classification: **`DIRECT_SOURCE_MATCH`**
- **FROZEN FOR RE: YES**
- stock: `83e7e3d89b192ea6258db2cb6e5071492caf3badc289e03575661a03341bb5eb`, 53,848 bytes
- stock Build ID: `c06e791cf6e3de51ce75e986230da4461e0778ec`
- placement/load: `vendor_dlkm`, index 145 one-based / 144 zero-based
- lineage: `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`
- source: `drivers/misc/mediatek/geniezone/gz-trusty/{trusty.c,smcnr-table.c}`
- final target: `//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`

## Why this classification

The pinned source/config/header set itself reproduces stock. No C change, forward port, compatibility shim, CRC witness, or generated ABI substitution is present. The mandatory unmodified RED was already 33/33 byte-identical and 14/14 natural CRC exact; reproducing the vendor source path then closed the line strings.

## Final parity

| Property | Result |
|---|---|
| build | RC 0; 0 compiler warnings; 0 modpost warnings; 0 unresolved |
| functions | 33 stock / 33 rebuilt / 33 shared / 0 missing / 0 extra |
| function sizes | 33/33 identical |
| function bytes | **33/33 identical** |
| KCFI | **33/33 exact** |
| imports | **59/59 identical**, all GKI |
| MODVERSIONs | **60/60 identical** |
| exports | **14/14**, all natural CRCs exact |
| objects | 14 exact PROGBITS + 5 exact NOBITS; 3 `.modinfo` layout-only |
| relocations | **553/553 semantic records exact** |
| strings | **63/63 inventory rows**, 59/59 unique values exact |
| metadata | name/depends/license/description/aliases/params/import-ns exact |
| section names/order | exact |

Machine tables: `phase4-gz-trusty-mod-function-parity.tsv` and `phase4-gz-trusty-mod-object-parity.tsv`.

## Provider/consumer closure

This is the lowest GenieZone transport provider. Its 59 imports are all exact-GKI. Seven stock modules consume it over 34 edges:

`gz_ipc_mod`, `gz_irq_mod`, `gz_log_mod`, `gz_main_mod`, `gz_tz_system`, `gz_virtio_mod`, `sapu`.

All 14 exports are consumed and all 34 natural rebuilt CRCs satisfy stock consumers. The three `gz_ipc_mod` edges are `get_smcnr_dev`, `trusty_fast_call32`, and `trusty_get_api_version`.

## Linux behavior closure

The two platform instances (`android,trusty-smc-v1`, `android,nebula-smc-v1`), SMC call serialization/retry behavior, atomic/blocking notifiers, per-CPU NOP queues/threads, completions, sysfs version attribute, probe/remove unwinding, and all 14 public functions are closed in the contract/call-path/type/DT/userspace reports.

## Nonfunctional residuals

Whole-ELF identity is not claimed. Rebuilt size is 53,840 bytes and Build ID `075c74a64545526e299d07a90c8d8e46756f3496`; local vermagic contains `maybe-dirty` instead of stock `g945dff7bc1bf`. `.llvm_addrsig` has eight fewer non-runtime symbol references. These account for the 8-byte whole-file residual; no functional section, function, ABI edge, relocation, string, or consumer mismatch remains.

Verifier: `python3 kernel/scripts/phase4_gz_trusty_mod_verify.py` → **239/239 CHECKS PASSED**.
