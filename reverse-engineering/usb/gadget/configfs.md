# Device / gadget path

```text
MTU3 UDC "11201000.usb0" (mtu3.ko, max HS)
  ▲  write /config/usb_gadget/g1/UDC ${vendor.usb.controller}
configfs gadget g1   (GKI libcomposite, USB_CONFIGFS=y)
  idVendor ${vendor.usb.vid}=0x0E8D   bcdDevice 0x0223   bcdUSB 0x0200
  strings 0x409: serial=${ro.serialno}, manufacturer=${ro.product.manufacturer} (Ulefone),
                 product=${ro.product.model} (Armor 29 Pro)
  os_desc: use=1, b_vendor_code 0x1, qw_sign "MSFT100", b.1 linked
  configs/b.1  MaxPower 500 (mA), f1..f5 symlinks per sys.usb.config
  functions (created at post-fs / post-fs-data):
    accessory.gs2 audio_source.gs3 ffs.adb ffs.mtp ffs.ptp mtk_rndis.gs4 midi.gs5 ncm.gs6
    acm.gs0..gs3 mass_storage.usb0 hid.gs0 via_modem.gs0 via_ets.gs0 via_atc.gs0
```

Kernel providers:
- **GKI built-in**: libcomposite, FunctionFS, ACM/serial, NCM, ECM, EEM, MIDI, HID, mass storage, accessory, audio source, UVC.
- **Vendor modules** (exact rebuilds): `mtk_usb_f_rndis.ko` + `mtk_u_ether.ko` (RNDIS, because GKI RNDIS is disabled) and `usb_meta.ko` (legacy `android_usb` for META).
- **Modem**: `c2k_usb*.ko` (closed in the modem research).

The function inventory, PIDs and status are in [`functions.tsv`](functions.tsv).

## What is actually configured

- Default boot: `persist.sys.usb.config` → `sys.usb.config` (AOSP `init.usb.rc` `on boot`). In the captured state it was `adb`: `0e8d:201c`, a single FunctionFS ADB interface, High-Speed.
- Charger boot (KPOC): `kpoc_midi` (PID 0x2046), or `kpoc_adb` if `ro.debuggable=1` and `ro.vendor.usb.kpoc_adb=1`. Stock sets `ro.vendor.usb.kpoc_adb=0`.
- `vendor.usb.acm_cnt`/`acm_enable`/`acm_port0/1` (MTK engineering mode) add ACM ports and select alternate PIDs.
- On `sys.usb.config=none` the vendor rc removes `f1..f5`, deletes `mtk_rndis.gs4`/`ncm.gs6`, writes UDC `saving 0` and `u3_lpm 1` (MTU3 sysfs; `u3_lpm` is a no-op on this U2 IP).

## Gadget speed

`bcdUSB 0x0200`, UDC `maximum_speed = high-speed`, and the MTU3 IP is U2-only. Gadget mode is **USB 2.0 High-Speed** only.
