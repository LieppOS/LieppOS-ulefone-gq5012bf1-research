# GQ5012BF1 — extcon-mtk-usb provider / ABI analysis (Phases 8 + 12)

## 1. Summary

| axis | stock | rebuilt | result |
|---|---|---|---|
| imports (undefined symbols) | 63 | 63 | **exact**, 0 missing / 0 extra |
| MODVERSION symbols | 64 | 64 | **exact** |
| MODVERSION CRC values | 64 | 64 | **64/64 identical** |
| exports (`__ksymtab`) | 0 | 0 | exact — the module exports nothing |
| KCFI type-ids | 4 | 4 | **identical set** |

Per-symbol CRC evidence: `phase4-extcon-mtk-usb-modversion-parity.tsv`.
KCFI ids (identical in both): `__kcfi_typeid_delayed_work_timer_fn`,
`__kcfi_typeid_seq_lseek`, `__kcfi_typeid_seq_read`,
`__kcfi_typeid_single_release`.

## 2. Declared dependency edges

Stock `.modinfo` says `depends=tcpc_class,mt6375-charger`, and `modules.dep`
line 57 expands to `mt6375-charger.ko tcpc_class.ko pd_dbg_info.ko
charger_class.ko`.

| provider | symbols consumed | direction |
|---|---|---|
| `mt6375-charger` | `yft_usb_flag` | consumer-only (read) |
| `tcpc_class` | `tcpc_dev_get_by_name`, `register_tcp_dev_notifier`, `tcpm_inquire_remote_cc` | consumer-only |

`extcon-mtk-usb` exports nothing, so **every** module edge is consumer-only.

## 3. `yft_usb_flag` — the critical YFT edge

```
stock extcon __versions : 0x398e9c8b
rebuilt extcon __versions: 0x398e9c8b      MATCH
```

Ownership is unchanged and unduplicated:

- `mt6375-charger` **defines and `EXPORT_SYMBOL_GPL`s** it — the single real
  provider;
- `extcon-mtk-usb` **reads** it (gate);
- `yft_tiny2c_usb` **writes** it.

No second functional provider was created, and `yft_tiny2c_usb`'s existing
frozen reconstruction was not modified or rebuilt.

## 4. `tcpc_class` edge — finding, and how it was closed

Building the consumer against the LieppOS **tcpc-class reconstruction** embedded
that reconstruction's CRCs, which differ from stock:

```
symbol                      stock       recon-provider   verdict
tcpc_dev_get_by_name        0xa4a78f74  0x6f461bee       DIFFER
register_tcp_dev_notifier   0x796a05c1  0xb529748c       DIFFER
tcpm_inquire_remote_cc      0x199e53c1  0x0f2268f7       DIFFER
```

A module built that way would be **refused at modprobe time** by a stock
`tcpc_class.ko` ("disagrees about version of symbol"). This was a genuine ABI
blocker, not a cosmetic delta.

It was closed with a **declared, non-shippable stock-provider witness**, which
the task spec permits for consumer-only edges:

```
/home/armol/kernel-work/gki-12901745-workspace/lieppos/tcpc-class-provider-abi/
  Module.symvers      204 exports, CRCs extracted from the STOCK tcpc_class.ko
  NON-SHIPPABLE.txt   declaration + method + cross-check
```

Extraction was done **provider-side** (authoritative), not by copying the
consumer's expectations: `__ksymtab` entries are
`struct kernel_symbol {s32 value, name, namespace}`; each entry's name field
carries an `R_AARCH64_PREL32` relocation into `__ksymtab_strings`, and
`__kcrctab` holds one `u32` CRC per entry in the same order. 204 exports were
recovered from
`workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/tcpc_class.ko`.

Both directions then agree independently:

```
symbol                      provider __kcrctab   consumer __versions
tcpc_dev_get_by_name        0xa4a78f74           0xa4a78f74     MATCH
register_tcp_dev_notifier   0x796a05c1           0x796a05c1     MATCH
tcpm_inquire_remote_cc      0x199e53c1           0x199e53c1     MATCH
```

Rebuilding against the witness yields **64/64 CRC parity**.

### What this does and does not claim

- It **does** prove the reconstructed consumer is ABI-compatible with the *stock*
  `tcpc_class.ko` and would load against it.
- It does **not** claim `tcpc_class` itself is source-reconstructed. No CRC was
  injected into any ELF, no `__versions` section was copied or patched, and the
  witness ships no code. It is build evidence only and is marked as such in-tree.

## 5. The `CONFIG_TCPC_CLASS` trap (important for any future MTK consumer)

`inc/tcpm.h` selects between the real externs and `TCPC_CLASS_NA` stub inlines
on exactly the spelling `CONFIG_TCPC_CLASS`:

```c
#if IS_ENABLED(CONFIG_TCPC_CLASS)
        extern struct tcpc_device *tcpc_dev_get_by_name(const char *name);
        ...
#endif
/* Empty function if configuration not defined */
#define TCPC_CLASS_NA
static inline int register_tcp_dev_notifier(...) { return 0; }
```

An earlier iteration used a private gate name (`CONFIG_MTK_TCPC_CLASS`). It
compiled clean, emitted the procfs skeleton, and **silently bound every Type-C
call to a `return 0` stub** — producing a linkable module with zero
`tcpc_class` dependency and no Type-C behaviour. Any `-D` gate for these headers
must reuse the vendor macro name. Fixed: the module now passes
`-DCONFIG_TCPC_CLASS=1`.

## 6. `pd_dbg_info` / `charger_class`

Both appear in `modules.dep` but **not** in the stock import set, so they are
transitive dependencies of `tcpc_class` / `mt6375-charger`, not direct edges of
`extcon-mtk-usb`. The donor's direct `charger_class` path
(`get_charger_by_name`, `charger_dev_enable_vac_otgovp`) is absent from stock
and was correctly dropped — see `phase4-extcon-mtk-usb-RED.md`.
