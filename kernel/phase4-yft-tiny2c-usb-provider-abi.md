# yft_tiny2c_usb MT6375 provider ABI

## Exact edge

| field | stock fact |
|---|---|
| consumer | `yft_tiny2c_usb.ko` |
| provider | `mt6375-charger.ko` (module name `mt6375_charger`) |
| symbol | `yft_usb_flag` |
| kind | writable data object, not a function |
| prototype | `extern int yft_usb_flag;` |
| size | 4 bytes |
| initial value | zero-initialized (`.bss+0x4` in stock provider) |
| export | `EXPORT_SYMBOL_GPL(yft_usb_flag)` (`__ksymtab_gpl+yft_usb_flag`) |
| stock CRC | `0x398e9c8b` |
| KCFI | not applicable to an object |
| consumer sites | `.text+0x214/+0x218` writes 1; `.text+0x28c/+0x290` writes 0 |
| arguments/return | none: direct 32-bit stores; no call and no return value |

The consumer writes the flag only after writing all available rail GPIOs. It neither looks up
nor calls a charger API. No error can be returned by this edge.

## Exact provider readers

Stock `mt6375-charger.ko` SHA256:
`201628cd5b5aff2129901fcf555049afa7fdc3ce80f7ff1502b6b095806384d4`.
Relocation-aware provider disassembly finds exactly two reader pairs:

1. `mt6375_chg_bc12_work_func`, provider `.text+0x1094/+0x1098`: compares the
   flag to 1. When 1 it branches to `.text+0x11e4`, logs, and bypasses the normal
   `phy_get` / `phy_set_mode_ext(..., PHY_MODE_USB_DEVICE, ...)` / `phy_put` sequence
   before continuing the BC1.2 field/update tail.
2. `mt6375_tcp_notifier_call`, provider `.text+0x1904/+0x190c`: on the relevant
   TCP attach-state jump-table arm it marks the port attached; when the flag is 1 it
   queues the charger's BC1.2 work on CPU 32. It does not enable an OTG regulator there.

## Physical meaning

`yft_usb_flag` is a **thermal-camera USB-path/BC1.2 exclusion handshake**. It tells the
MT6375 charger logic that the internal tiny2c USB camera route is active, so charger attach
processing must not perform the ordinary USB-PHY/DPDM BC1.2 mode transition that would
conflict with that route. It also ensures the charger BC1.2 work is queued for the relevant
TCP notification.

It is **not** an OTG/VBUS-enable API, reverse-charging API, charger power-path API, or
thermal supply output. The consumer's stores do not directly change MT6375 regulator,
VBUS, or charger registers.

## Source provenance

The exact local MediaTek/Nothing framework source is:

`/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules/drivers/power/supply/mt6375-charger.c`

It contains the matching `mt6375_chg_bc12_work_func` framework and stock charger control
flow, but it predates/omits Ulefone's small `yft_usb_flag` board delta and does not define
that identifier. Therefore it is exact framework/provider source evidence, not byte-exact
source provenance for the Ulefone-added flag. The Ulefone delta is closed from the exact
stock provider ELF at the two reader sites above.

For the consumer build, the CRC must be produced naturally from the exact declaration and a
real GPL export build dependency. No stock CRC is injected into `Module.symvers`, no ELF is
patched, and no warning-mode modpost is permitted.
