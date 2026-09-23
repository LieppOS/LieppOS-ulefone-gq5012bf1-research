# Stock USB runtime forensics

## Safety gate

All initial captures were read-only and began only after:

```text
ro.boot.slot_suffix=_a
sys.boot_completed=1
```

See `evidence/stock-safe-state.txt`. No boot slot, partition, RPMB, calibration, NVRAM or persist state was changed.

## Normal external gadget state

Evidence: `evidence/stock-udc-gadget.txt`, `evidence/stock-runtime-lowlevel.txt`, `evidence/host-external-usb-enumeration.txt`, and `evidence/host-external-usb-descriptor.txt`.

| Item | Runtime result | Classification |
|---|---|---|
| UDC | `11201000.usb0` | PROVEN |
| bound platform driver | `mtu3` | PROVEN |
| USB role switch | `11201000.usb0-role-switch=device` | PROVEN |
| extcon | `USB=1`, `USB-HOST=0` | PROVEN |
| configfs function | `ffs.adb` in the captured state | PROVEN |
| UDC current speed | `high-speed` | PROVEN |
| UDC maximum speed | `high-speed` | PROVEN |
| UDC state | `configured` | PROVEN |
| host-negotiated speed | `480M` | PROVEN |
| descriptor | `0e8d:201c`, `bcdUSB 2.00`, Ulefone Armor 29 Pro | PROVEN for ADB configuration |

The Linux host had SuperSpeed-capable xHCI root hubs and a paired 5000-Mbit/s hub, but the phone appeared only on the 480-Mbit/s USB2 bus. This proves that the tested connection negotiated High-Speed. The cable was not independently certified during this capture, so this runtime test alone does not prove missing SS board lanes. The DT and UDC maximum-speed evidence independently show that stock software caps this instance at High-Speed.

## Controller, PHY and interrupt bindings

Normal gadget state:

```text
11201000.usb0       driver=mtu3
11f40000.usb-phy0   driver=mtk-xsphy
11200000.xhci0      unbound
```

`/proc/iomem` records:

- `11201000-11203dff`: MTU3 `mac`;
- `11203e00-11203eff`: MTU3 `ippc`;
- `11f40000-11f403ff`: `usb2-phy0@11f40000`.

The live interrupt table records GIC interrupt 416 for `11201000.usb0`, MT6375 TCPC interrupt 120, MT6375 charger interrupts, and GPIO 28 `extcon-usb` detection. See `evidence/stock-runtime-lowlevel.txt`.

## Type-C state while attached to the host

Evidence: `evidence/stock-typec-state.txt`.

The port reported:

```text
data_role=host [device]
power_role=source [sink]
port_type=[dual] source sink
power_operation_mode=default
preferred_role=sink
usb_power_delivery_revision=3.1
usb_typec_revision=1.2
vconn_source=no
```

Square brackets mark the active choice, so the captured state was **device + sink**, with a dual-role port and sink preference. The revision files describe supported protocol revisions, not proof that the PC connection had negotiated a PD contract.

## Idle host-device topology

With the external cable in gadget mode and the thermal camera off, `/sys/bus/usb/devices` was empty because xHCI was not bound. This is expected for the dual-role controller in device mode and is recorded in `evidence/stock-usb-device-topology-idle.txt`.

## Internal thermal-camera transition

The controlled test is documented fully in `USB-INTERNAL-THERMAL-CAMERA.md`.

During thermal operation:

```text
UDC current_speed=UNKNOWN
UDC maximum_speed=high-speed
UDC state=not attached
11200000.xhci0 driver=xhci-mtk
usb1 root hub serial=11200000.xhci0, speed=480
1-1 3474:4321 Thermal Cam Co.,Ltd Camera, speed=480
```

The internal camera exposed UVC VideoControl and VideoStreaming interfaces and streamed through the stock AC020 userspace stack. External wired ADB disappeared during this state. Returning Home removed the USB device and unbound xHCI; replugging the external cable restored normal gadget enumeration.

## What runtime proves and does not prove

### Proven

- stock external gadget operation is USB 2.0 High-Speed;
- the stock DT/UDC ceiling is High-Speed;
- MTU3 switches between gadget and xHCI-host operation;
- the internal thermal camera is direct High-Speed UVC on `11200000.xhci0` port 1;
- internal thermal operation and external wired ADB are mutually exclusive in observed stock behavior;
- MT6375 provides active Type-C/role/charger integration.

### Not proven by runtime

- absence of dormant USB3 capability inside MT6878T silicon;
- absence of SS traces on the mainboard or daughterboard;
- connector contact population;
- behavior with a separately certified SS cable in both orientations;
- whether board modifications could expose dormant capability.
