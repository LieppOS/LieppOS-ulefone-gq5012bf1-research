# yft_tiny2c_usb mode / state-machine contract

There is no cached mode field. The observable state is the four descriptor reads plus the
provider's independent integer flag.

| parsed value | stock meaning | raw GPIO order (io3v3, optional 5v, 3v3, 1v8) | `yft_usb_flag` | direct USB/VBUS action | return |
|---:|---|---|---:|---|---|
| 0 | power off thermal low-voltage rails | 0, 0, 0, 0 | 0 after GPIOs | none | input count |
| 1 | power on thermal low-voltage rails | 1, 1, 1, 1 | 1 after GPIOs | none | input count |
| other | unsupported | unchanged | unchanged | none | input count |
| unparsable | parser result ignored; local defaults to 0 | power-off sequence | 0 | none | input count |

The GQ5012BF1 DT populates only io3v3/3v3/1v8; the generic 5v field contains an OF error,
not a mapped GPIO. No transition delay exists. There is no old-state check, rollback,
acknowledgement, or locking, so repeated writes repeat raw GPIO stores.

`show` is not a mode name. It returns current raw values as:

```text
gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d\n
```

The friendly meanings `power on` and `power off` are stock log strings and stock app usage,
not invented aliases. USB role and VBUS state belong to the separately written extcon node
and are deliberately excluded from this module's state table.
