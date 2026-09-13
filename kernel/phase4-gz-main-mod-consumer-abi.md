# gz_main_mod — export and consumer ABI

## 1. Exports: zero, proven

`gz_main_mod` exports **no kernel symbols at all**. This was not assumed from
the module's position in the graph; it is proven four independent ways:

| proof | result |
|---|---|
| stock `__ksymtab*` sections | absent — the stock ELF has no `__ksymtab`, `__ksymtab_gpl`, `__kcrctab` or `__kcrctab_gpl` section |
| stock export inventory | `kernel/phase4-gz-main-mod-exports.tsv` contains **0 rows** |
| stock inventory summary | `exported_symbol_count = 0` in `kernel/stock-module-inventory.csv` |
| source-built `Module.symvers` | **0 bytes** — modpost emitted no export record for the rebuilt module |

There is therefore no export CRC to reproduce, and the "natural export CRC"
metric is `0/0` by construction rather than by omission.

## 2. Consumer scan: zero consumers, proven

The scan covered **all 471 stock module placements** recorded in
`kernel/stock-module-placements.tsv` (215 `vendor_dlkm` + 60 `system_dlkm`
canonical modules plus every duplicate placement).

| check | result |
|---|---|
| modules declaring `gz_main_mod` in their `depends=` | **0** |
| entries in `vendor_dlkm/lib/modules/modules.dep` listing `gz_main_mod.ko` as a dependency of another module | **0** |
| stock modules importing any symbol defined by `gz_main_mod` | **0** (vacuous — it defines no exported symbol) |

`gz_main_mod` appears in `modules.dep` only on the **left-hand side**, as a
consumer:

```
/vendor_dlkm/lib/modules/gz_main_mod.ko: \
    /vendor_dlkm/lib/modules/mtk_sec_heap.ko \
    /vendor_dlkm/lib/modules/tmem_ffa.ko \
    /vendor_dlkm/lib/modules/gz_tz_system.ko \
    /vendor_dlkm/lib/modules/gz_ipc_mod.ko \
    /vendor_dlkm/lib/modules/gz_trusty_mod.ko
```

(`ffa_v10` is resolved from the vendor ramdisk rather than `vendor_dlkm`,
which is why it appears in `.modinfo depends=` but not in this `modules.dep`
line.)

## 3. Consequence for replacement safety

`gz_main_mod` is a **pure leaf** of the kernel-module dependency graph. No
other kernel module links against it, so replacing it cannot break any
in-kernel consumer, and no re-link of any other module is required.

Its real consumers are entirely in **userspace**, through the two character
devices — see `kernel/phase4-gz-main-mod-userspace-abi.md` and
`kernel/phase4-gz-main-mod-android-contract.md`. That userspace ABI, not a
symbol ABI, is what must be preserved, and it is preserved exactly because the
module is byte-identical in every function.

## 4. Downstream module status

| module | relationship | affected by this work? |
|---|---|---|
| `gz_tz_system` | provider (15 edges) | no — unchanged, still frozen |
| `gz_trusty_mod` | provider (5 edges) | no |
| `gz_ipc_mod` | provider (1 edge) | no |
| `ffa_v10` | provider (1 edge) | no |
| `tmem_ffa` | provider (2 edges) | no |
| `mtk_sec_heap` | provider (1 edge), stock | no |
| any consumer | **none exist** | n/a |
