# GQ5012BF1 uSmart full contract

**Canonical status: EFFECTIVELY COMPLETE (offline static closure, 2026-10-07).**

Detailed closure: [`kernel/usmart/README.md`](usmart/README.md). This file supersedes the
older combined thermal/uSmart diagram and the false YftSuperScreen/tiny2c attribution.

## Contract in one diagram

```text
uSmart proprietary expansion connector (E01/E02/E03 endoscopes, C01 microscope)

physical insert drives/asserts ID LOW
  → GPIO28 LOW, both-edge ONESHOT IRQ, zero-delay work
  → GPIO152 HIGH                  accessory power gate
  → GPIO55 HIGH                   single USB2 D+/D− route: Type-C → uSmart
  → uvc_insert_status = 1         physical status only
  → if yft_usb_flag == 0: queue HOST
  → shared usb2-phy0 / MTU3 11201000 / xHCI 11200000
  → standard usbcore enumeration
  → optional com.endoscope.otgcamera app (usbfs/libusb/libuvc or vendor device path)

remove: GPIO152 LOW → GPIO55 LOW → status 0 → (unless thermal flag) role NONE
```

No userspace process powers or routes uSmart. `extcon-mtk-usb.ko` owns GPIO28/55/152,
the IRQ, status and role request; it is already byte-level closed. There is no dedicated
uSmart driver/HAL/daemon.

## Key findings

- GPIO28 is active-low insertion detect. Probe initializes GPIO55/152 LOW, registers both
  IRQ edges, then samples the current level; boot-attached operation is autonomous.
- GPIO152 is the uSmart accessory power/VBUS gate. The exact board rail voltage/current
  is unknown. The MT6375 5.25-V/1.8-A boost and GPIO37 belong to external Type-C; the
  uSmart ID worker does not call them.
- GPIO55 LOW selects the external/default USB2 route; HIGH selects uSmart. There is one
  USB2 controller/PHY, no second `11211000.usb1` controller and no simultaneous data.
- `uvc_insert_status` mirrors GPIO28 physical state; it is set before role/enumeration and
  is not UVC-success status. Kernel mode 0444, init chmod 0777, no store handler.
- Genuine userspace clients are YftSystemUI (missing-app prompt), FactoryMode (physical +
  any-device test/launcher), and the downloadable `com.endoscope.otgcamera` camera app.
  YftSuperScreen and ThermoVue apps are not uSmart clients.
- The connector/kernel layer has no proprietary protocol beyond detect/power/route/USB.
  The optional camera app supports standard UVC over usbfs plus Sonix, NS108x and
  U-Storage accessory-specific protocols.
- uSmart provides camera input/local preview and recording, not display output or analog
  audio. Generic digital USB Audio remains a standard host capability.
- No uSmart ownership gate exists. Type-C can override its role while GPIO55 stays HIGH;
  removal forces NONE without restoring the external cable state.
- During thermal operation, `yft_usb_flag` suppresses only the final uSmart role request:
  GPIO152/55/status still change. uSmart can therefore steal the route while thermal HOST
  remains active; removal restores the route without clearing HOST.

## Boundaries

Unknown but non-blocking: connector pin numbers/contact count, analog switch/load-switch
identity and netlist, GPIO152 electrical rating, captured E01/E02/E03/C01 descriptors and
which app-specific vendor protocol each revision uses. Reverse charging through uSmart is
not supported by stock software.

Files under [`kernel/usmart/`](usmart/) provide the exact GPIO table, state machine,
power/routing/role contracts, app filter inventory, clients/sysfs, Type-C/thermal races,
failures, stale-claim ledger and LieppOS requirements.
