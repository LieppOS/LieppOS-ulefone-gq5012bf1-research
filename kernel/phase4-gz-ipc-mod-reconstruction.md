# GQ5012BF1 `gz_ipc_mod.ko` source closure

## Final status

- classification: **`DIRECT_SOURCE_MATCH`**
- **FROZEN FOR RE: YES**
- stock: `87d8a2a1eb8cb55bbf3bd372fc76e59fecfa8d8479bd931f714252cac60b6a19`, 78,648 bytes
- stock Build ID: `a430fe26d6e355bf7264af682787afc9a5bda3df`
- placement/load: `vendor_dlkm`, index 146 one-based / 145 zero-based
- lineage: `device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`
- source: `drivers/misc/mediatek/geniezone/gz-trusty/trusty-ipc.c`
- final target: `//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport`

## Why this classification

The pinned source/config/header set itself reproduces stock. The upper-provider mandatory RED used the real source-built Trusty module and was immediately 43/43 byte-identical with 15/15 natural export CRCs. No C delta was required; matching vendor source/header paths closed the only line-provenance strings.

## Final parity

| Property | Result |
|---|---|
| build | RC 0; 0 compiler warnings; 0 modpost warnings; 0 unresolved |
| functions | 43 stock / 43 rebuilt / 43 shared / 0 missing / 0 extra |
| function sizes | 43/43 identical |
| function bytes | **43/43 identical** |
| KCFI | **43/43 exact** |
| imports | **81/81 identical**: 78 GKI + 3 natural Trusty |
| MODVERSIONs | **82/82 identical** |
| exports | **15/15**, all natural CRCs exact |
| objects | 19 exact PROGBITS + 14 exact NOBITS; 3 `.modinfo` layout-only |
| relocations | **1003/1003 semantic records exact** |
| strings | **88/88 inventory rows**, 84/84 unique values exact |
| metadata | name/depends/license/description/aliases/params/import-ns exact |
| section names/order | exact |

Machine tables: `phase4-gz-ipc-mod-function-parity.tsv` and `phase4-gz-ipc-mod-object-parity.tsv`.

## Provider/consumer closure

`gz_ipc_mod` depends on source-built `gz_trusty_mod` through exactly three natural edges. Stock direct consumers are `gz_tz_system` (five exports) and `gz_main_mod` (`tipc_set_default_cpumask`), for 6/6 accepted edges. All 15 exports are reproduced naturally; nine channel-level exports have no committed stock-module consumer but remain byte/CRC exact.

## Linux behavior closure

The four-state channel machine, virtio device lifecycle, routing by first service token, TEE mapping, blocking/nonblocking whole-message read/write, connect completion, `-ERESTARTSYS`, buffer ownership, CPU affinity, character-device ioctl/read/write/poll ABI, and all 15 exports are closed in the contract/state/type/DT/userspace reports.

## Nonfunctional residuals

Whole-ELF identity is not claimed. Rebuilt size is 78,640 bytes and Build ID `cb3844b9416fc58c6fb6bf89843b4022cd265297`; local vermagic contains `maybe-dirty` instead of stock `g945dff7bc1bf`. `.llvm_addrsig` has eight fewer non-runtime references. These are build provenance only and account for the 8-byte file residual.

Verifier: `python3 kernel/scripts/phase4_gz_ipc_mod_verify.py` → **269/269 CHECKS PASSED**.
