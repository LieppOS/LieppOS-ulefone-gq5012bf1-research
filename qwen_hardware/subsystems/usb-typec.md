> **Superseded in part (2026-09-08).** This file is first-pass working material. Where it disagrees with `../final/` or `../verification/findings/`, the verification pass wins.
>
> Two corrections apply to every subsystem file: (a) the 2026-08-31 capture was taken under a **LieppOS GSI**, so its framework-level observations are **not** stock Ulefone behaviour; and (b) `vendor/etc/init/hw/init.yft.rc` is a **platform-wide ODM option catalogue**, not this device's bill of materials.
>
> Charging protocols are **PD + PPS only - UFCS is positively absent**; reverse output is **10 W wired** via the SC8510. See `charging-capabilities.md` and `wireless-charging.md`.

# USB Type-C, PD and accessory connector

## Hardware found

* MT6375 Type-C Port Controller/PD path at I2C `5-0034` (`mtk_tcpc 1-0034` in the kernel contract).
* Stock Android/vendor paths include `usbd`, `usb_gadget`, TCPC/PD debug and `tiny2c_usb` (the latter is the thermal module's private tunnel, not the phone's external USB PHY).
* OEM/independent database identifies a USB Type-C port, USB OTG and a separate pogo-pin/magnetic accessory connector.

## Capability layer

* Board-level PD/PPS source/role paths are present. **CORRECTED 2026-09-08:** the OEM claims **120 W (20 V/6 A) over PD/PPS**; **UFCS is positively absent** (`POWER_SUPPLY_USB_TYPE = SDP DCP CDP PD PD_PPS`).
* MediaTek platform can support USB 3.x-class interfaces, but the exact phone's public specification says **USB 2.0**. Therefore SuperSpeed and DisplayPort Alt Mode are **not proven and likely not populated**.
* OTG/host mode is a product claim; VBUS current limit and accessory negotiation are UNKNOWN.

## Board configuration / stock use

* Snapshot was USB powered at 5 V / 1 A reporting state; no high-power PDO/APDO capture.
* TCPC manages source/sink/role and PD/PPS; standard Android USB gadget service is present. The magnetic/pogo connector likely carries accessory power/data, but pinout and protocol are UNKNOWN.
* Thermal HAL has a USB-port temperature sensor, with current snapshot around 43 °C and no static hot threshold exposed.

## Hidden / unused

1. USB-C **PD/PPS** higher-power modes require a compatible source, cable and charge-pump state. There is no UFCS mode to reach.
2. OTG can be used for UVC accessories and may be the external route analogous to the private thermal `tiny2c_usb` transport.
3. No stock evidence exposes DP Alt Mode or USB 3 SuperSpeed; a custom kernel cannot create missing PHY/wiring.

## Verification

Capture `/sys/class/typec`, `usbmon`, PD debug and partner PDO/APDO data under several chargers; test OTG/UVC and SuperSpeed negotiation with a certified cable; continuity-test the pogo connector only with the device disassembled.

Sources: S01–S05; `kernel/phase4-tcpc-mt6375-*`, live thermal/power; S05.
