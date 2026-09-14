# GQ5012BF1 — extcon-mtk-usb mandatory RED (Phase 4)

RED was performed **before** any behaviour was modified: the donor was built
unmodified against exact GKI ab/12901745 and compared to the stock oracle.

## 1. RED harness

```
dir     /home/armol/kernel-work/gki-12901745-workspace/lieppos/extcon-mtk-usb-donor-red/
source  extcon_mtk_usb.c   sha256 ad7a82001ff8f8820582ed2af2f02c7a7cdc9f50f6b2f990380b06e4c0fcc16f
        == byte-identical to the donor file; renamed only because kbuild
           requires the object basename to match the source basename
inc/    verbatim copy of the donor's tcpc inc/ + charger_class.h (the donor tree
        path contains spaces, which kbuild -I cannot express)
plumbing  obj-m + ccflags -DCONFIG_TCPC_CLASS=1 -DCONFIG_USB_POWER_DELIVERY=1
log     workspace/phase4-extcon-mtk-usb/oracle/build-donor-red.log
```

No driver logic was edited to obtain this build.

## 2. RED build result

```
compile   OK, 0 warnings
modpost   FAILED — 2 undefined symbols
          ERROR: modpost: "get_charger_by_name" undefined!
          ERROR: modpost: "charger_dev_enable_vac_otgovp" undefined!
```

This is itself a RED finding: the donor reaches `charger_class` through a
`dvchg1` charger-device path that the **stock Ulefone build does not contain**
(neither symbol appears in the stock import set). Comparison below is therefore
done at object level (`extcon_mtk_usb.o`), which carries the full function and
undefined-symbol inventory.

## 3. RED delta — unmodified donor vs stock

| axis | stock | donor | delta |
|---|---|---|---|
| functions | 22 | 19 | 17 shared |
| size-identical among shared | — | — | **6 / 17** |
| imports | 63 | 53 | 13 stock-only, 2 donor-only |
| exports | 0 | 0 | equal |

**In stock, absent from donor (5)** — the Ulefone/YFT delta:

```
get_otg_select_gpio   yft_parse_dts   show_uvc_insert_status
show_tiny2c_mode      store_tiny2c_mode
```

**In donor, absent from stock (2)** — present in stock only as inlined code:

```
mtk_usb_extcon_procfs_init   mtk_usb_extcon_set_vbus
```

**Imports stock has and the donor does not (13)**:

```
__class_create  class_create_file_ns  _printk  scnprintf  sscanf
gpio_request  gpio_to_desc  gpiod_direction_output_raw
gpiod_get_raw_value  gpiod_set_raw_value
of_find_compatible_node  of_get_named_gpio_flags
yft_usb_flag
```

**Imports the donor has and stock does not (2 real)**:

```
get_charger_by_name   charger_dev_enable_vac_otgovp
```

(`__this_module` also lists as donor-only; that is an artifact of comparing a
`.o` against a linked `.ko`, where the symbol is defined rather than undefined.)

## 4. Interpretation

The donor is the right code base but not the shipped source. The stock build:

1. **adds** the YFT thermal-camera plumbing (raw `of_get_named_gpio_flags` GPIO
   parsing, the `yft_extcon` class + `tiny2c_mode` attribute, `uvc_insert_status`,
   and the `yft_usb_flag` gate imported from `mt6375-charger`);
2. **removes** the donor's `charger_class`/`dvchg1` path;
3. **replaces** the donor's Nothing-specific `CONFIG_NT_USB_TS`
   `extcon_usb_mode_switch()` / `g_extcon` export — absent from the stock
   symtab — with the `tiny2c_mode` class attribute.

Only after this RED was recorded was the delta implemented.

## 5. GREEN (final reconstruction, same comparison axes)

| axis | stock | reconstruction | status |
|---|---|---|---|
| functions | 22 | 25 | **22/22 stock functions present**, 0 missing |
| imports | 63 | 63 | **exact**, 0 missing / 0 extra |
| MODVERSION symbols | 64 | 64 | **exact** |
| MODVERSION CRCs | 64 | 64 | **64/64 identical** |
| KCFI type-ids | 4 | 4 | **identical set** |
| exports | 0 | 0 | exact |
| log literals | 70 | 70 | **0 stock-only** |

The 3 extra reconstruction functions are `mtk_usb_extcon_set_vbus`,
`mtk_usb_extcon_procfs_init` and `yft_tiny2c_mode_work`: stock's clang inlined
the first two into their callers (the arithmetic closes — stock's notifier is
0x832 against 0x476 here, i.e. exactly the ~348-byte `set_vbus` body plus its
call sites, with `probe` moving −224 bytes in the opposite direction).
