# External device / gadget mode

## Sequence

1. At boot, vendor init creates configfs gadget `g1`, its strings/configuration/functions,
   mounts FunctionFS for ADB/MTP/PTP, and sets both controller properties to
   `11201000.usb0`. Gadget composition is independent of cable attachment.
2. Framework `UsbDeviceManager` and MediaTek AIDL `IUsbGadget/default` select a function
   mask. The gadget HAL sets `vendor.usb.config`/`sys.usb.config`; init owns the concrete
   symlinks, PID and UDC write.
3. For FunctionFS modes, adbd/MTP/PTP must publish descriptors/readiness first. Init then
   links functions under `configs/b.1`, writes the UDC name and finally sets
   `sys.usb.state=${sys.usb.config}`.
4. On a PC/SDP/CDP/PD sink attachment, MT6375 classification causes extcon NONE→DEVICE;
   MTU3 starts the UDC. If the gadget is bound, the host enumerates it.
5. Reconfiguration goes through `sys.usb.config=none`: UDC unbind, function links removed,
   FFS state reset, then the new composition is linked/bound.

## Base descriptors

| field | stock value |
|---|---|
| gadget / UDC | `/config/usb_gadget/g1` / `11201000.usb0` |
| VID | MediaTek `0x0e8d` for MTK compositions; AOA uses AOSP Google `0x18d1`/PIDs 0x2d00–0x2d05 |
| PID | per composition and ACM count (`gadget-functions.tsv`) |
| bcdDevice | `0x0223` |
| bcdUSB | `0x0200` |
| strings | serial `${ro.serialno}`; manufacturer `Ulefone`; product `Armor 29 Pro` |
| config | `b.1`, `MaxPower=500` mA, f1…f5 symlinks |
| Microsoft OS descriptor | enabled, vendor code 1, signature `MSFT100` |
| maximum speed | High-Speed only |

Runtime proof is the ADB-only composition: 0e8d:201c, one vendor-specific FunctionFS ADB
interface, bcdUSB 2.00 at 480 Mbit/s. Other rows are statically **CONFIGURED** by stock init,
not claimed runtime-captured.

## ADB / MTP / PTP

- ADB exists only in configurations containing `adb`. Those triggers start `adbd`; UDC
  binding waits for `sys.usb.ffs.ready=1`. Production is `user`, `ro.debuggable=0`; ADB is
  not an unconditional production default—framework/developer setting controls the
  persisted/requested composition. The captured phone had `sys.usb.config=adb`.
- MTP/PTP are FunctionFS instances managed by the gadget HAL's MTP server. Their HAL-side
  readiness properties gate endpoint use; `*,adb` also waits for adbd FFS readiness.
- Thermal or uSmart HOST takeover disconnects the gadget regardless of the requested
  composition. Thermal stop does not replay the external DEVICE role; replug recovers it.

## Networking and accessory

- RNDIS is the MediaTek function `mtk_rndis.gs4` from exact vendor modules; NCM is GKI
  `ncm.gs6`. Both have stock init compositions, with and without ADB.
- ECM/EEM are built in GKI but stock init never creates/links them; they are unavailable
  through normal stock USB selection.
- Android Open Accessory is `accessory.gs2` (optionally audio_source and/or ADB), owned by
  AOSP framework/accessory protocol + configfs. In AOA the phone remains the USB **device**
  and an external USB host initiates accessory mode. It is unrelated to the physical
  uSmart connector/GPIO path.
- HID and UVC gadget providers exist, but stock creates HID without linking it and never
  configures UVC. Kernel availability is not stock exposure.
