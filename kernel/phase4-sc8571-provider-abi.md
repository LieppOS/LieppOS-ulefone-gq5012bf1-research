# GQ5012BF1 SC8571 ↔ charger_class provider ABI

## Proven edge

The stock consumer has exactly one non-kernel module dependency:

```text
sc8571_charger.ko --charger_device_register/0x36325d38--> charger_class.ko
```

The canonical stock provider is SHA256
`0c5bd394088d109c569cf5803a82edd0f182bad53714c284f99a797c76cf4e94`
(70,616 bytes, BuildID `ac45a4f8bcae71838409efcfbccbc14b41991376`).
Its exact symbol/kcrctab evidence is frozen in
`workspace/phase4-sc8571/raw/charger-class-provider-oracle.txt`.

Evidence agrees at all layers:

- `sc8571_charger.ko` `depends=charger_class`;
- `modules.dep` names `/lib/modules/charger_class.ko`;
- consumer `__versions` records `charger_device_register` CRC `0x36325d38`;
- stock `charger_class.ko` exports that symbol from regular `__ksymtab`, empty
  namespace, with the same CRC at `__kcrctab+0x140`;
- reconstructed `__versions` is byte-identical to stock (42 records).

No CRC was edited in the ELF. The one-line
`kernel/phase4-sc8571-recon/charger_class-stock.symvers.h` is a build-time
Module.symvers-format oracle recovered from the stock provider/consumer pair.
It lets exact-GKI `modpost` validate the real external edge when the proprietary
provider is not part of the GKI source target.

## Registration prototype

Relocation-aware consumer disassembly and the MediaTek provider source/type
graph establish:

```c
struct charger_device *charger_device_register(
        const char *name,
        struct device *parent,
        void *devdata,
        const struct charger_ops *ops,
        const struct charger_properties *props);
```

The five AArch64 arguments at the stock call site are, in order, DT-selected
charger name, SC8571 device, SC8571 private state, `sc8571_chg_ops`, and
`sc8571_chg_props`. `charger_properties.alias_name` is `sc8571_chg`.

The board supplies `primary_dvchg` for the master and `secondary_dvchg` for the
slave. If `charger_name` is absent, stock falls back to `charger`.

## Consumer-visible layouts

The stock `sc8571_chg_ops` object is 648 bytes: exactly 81 64-bit callback
slots. Its fourteen non-NULL slots are:

| slot | charger_ops member | callback |
|---:|---|---|
| 4 | `enable` | `mtk_sc8571_enable_chg` |
| 5 | `is_enabled` | `mtk_sc8571_is_chg_enabled` |
| 39 | `set_ibusocp` | `mtk_sc8571_set_ibusocp` |
| 40 | `set_vbusovp` | `mtk_sc8571_set_vbusovp` |
| 41 | `set_ibatocp` | `mtk_sc8571_set_ibatocp` |
| 42 | `set_vbatovp` | `mtk_sc8571_set_vbatovp` |
| 43 | `set_vbatovp_alarm` | `mtk_sc8571_set_vbatovp_alarm` |
| 44 | `reset_vbatovp_alarm` | `mtk_sc8571_reset_vbatovp_alarm` |
| 45 | `set_vbusovp_alarm` | `mtk_sc8571_set_vbusovp_alarm` |
| 46 | `reset_vbusovp_alarm` | `mtk_sc8571_reset_vbusovp_alarm` |
| 47 | `is_vbuslowerr` | `mtk_sc8571_is_vbuslowerr` |
| 48 | `init_chip` | `mtk_sc8571_init_chip` |
| 63 | `get_adc` | `mtk_sc8571_get_adc` |
| 64 | `get_adc_accuracy` | `mtk_sc8571_get_adc_accuracy` |

All remaining slots—including normal and direct-charging watchdog kicks,
charger events/notifiers, operation-mode control and OTG—are NULL.

Every callback obtains private data from offset `0xe0` in
`struct charger_device`. The reconstruction's ABI header therefore
materializes only 0xe0 private bytes followed by `driver_data`; it does not
pretend to reimplement the provider. The callback signatures and ordering are
preserved in `kernel/phase4-sc8571-recon/charger_class_stock_abi.h`.

## KCFI and static verification

The rebuilt module has the same KCFI type word as stock for every one of the 34
functions. In particular, callbacks sharing a prototype share the same stock
KCFI type word. The 648-byte operation table and all other named PROGBITS data
objects are byte-identical before relocations; callback relocation count and
slot positions are exact.

`charger_device_register` is a direct external call, so its link contract is
the symbol name, five-argument calling convention and MODVERSION CRC. All three
match stock. No provider exports are copied into the consumer, and the module
exports zero symbols.

## Boundary

SC8571 is a provider *consumer*, not a replacement for `charger_class.ko`.
Deployment still requires the stock-compatible provider. The reconstruction
was only compiled and statically compared; it was not inserted or bound on the
phone.
