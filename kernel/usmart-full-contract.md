# GQ5012BF1 uSmart full hardware/software contract

Device: **Ulefone Armor 29 Pro Thermal**  
Model: **GQ5012BF1**  
SoC: **MediaTek MT6878 / MT6878T**  
Stock kernel family: **6.1.115-android14-11**  
Audit method: **static/read-only only**

## 1. Executive result

The GQ5012BF1 uSmart subsystem is not one controller and does not use a separate USB
controller. It is a coordinated path across:

1. `extcon-mtk-usb.ko` — central uSmart detect, external switch/power GPIOs, USB role
   requests and Type-C coexistence;
2. `yft_tiny2c_usb.ko` — FM78100 thermal-camera logic rails and I2C identity;
3. `mt6375-charger.ko` — OTG boost regulator, charger/BC1.2 behavior and the exported
   `yft_usb_flag` coordination variable;
4. MT6375 TCPC / `tcpc_class` — Type-C notifications;
5. the single MTU3/xHCI/USB2-PHY fabric described by USB0 in DT;
6. YFT SystemUI/SuperScreen/thermal-camera applications performing split sysfs
   coordination.

`yft_tiny2c_usb` is **not** the uSmart controller. SC851x is not on the proven uSmart
path. The legacy `11211000.usb1` userspace path has no live DT controller.

## 2. Confidence summary

| Conclusion | Classification |
|---|---|
| central owner is `extcon-mtk-usb.ko` | **PROVEN_EXACT** |
| FM78100 rail/ID glue is `yft_tiny2c_usb.ko` | **PROVEN_EXACT** |
| MT6375 supplies `usb-otg-vbus` and exports `yft_usb_flag` | **PROVEN_EXACT** |
| one shared USB0/MTU3/xHCI stack exists | **PROVEN_EXACT** |
| uSmart and Type-C share/arbitrate the USB2 fabric | **PROVEN_HIGH_LEVEL** |
| GPIO and DT numeric contract below | **PROVEN_EXACT** |
| reverse-charging-level sysfs implementation | **NO_STOCK_SUPPORT** |
| independent USB1 controller | **NO_STOCK_SUPPORT** |
| SC851x as uSmart power/controller | **NO_STOCK_SUPPORT** |
| connector pinout, load-switch circuitry and accessory limits | **UNKNOWN** |
| complete USB VID/PID/interface/endpoint matrix | **BLOCKED_WITH_MISSING_EVIDENCE** |

## 3. Proven topology

```text
                    stock userspace
 YftSystemUI ---------- reads ----------> uvc_insert_status / sensor_id
 YftSuperScreen -------- writes --------> tiny2c_usb_mode + tiny2c_mode
 uSmartCamera (com.endoscope.otgcamera) -> native OTG/UVC handling

          FM78100 thermal/uSmart module
          | I2C identity @ 0x3c, ID 0x4c59
          | logic rails: GPIO 149 / 191 / 192
          | insertion ID: GPIO 28
          | accessory VBUS: GPIO 152
          | USB path switch: GPIO 55
          v
       shared USB2 fabric / usb2-phy0@11f40000
          |
       MTU3 usb0@11201000 (dr_mode=otg, usb-role-switch)
          `-- xhci0@11200000 host side

 External Type-C port
          |
       MT6375 TCPC type_c_port0
          |
       extcon notifier -> GPIO 37 + MT6375 usb-otg-vbus regulator
```

There is no live `11211000.usb1` and no live `compatible = "mediatek,usb3"` node.

## 4. Exact device-tree contract

### 4.1 `/extcon-usb`

| Property | Stock value |
|---|---:|
| `compatible` | `mediatek,extcon-usb` |
| `charger` | phandle `0xe4`, MT6375 charger |
| `id-gpios` | GPIO 28 |
| `otg_gpio_select` | GPIO 37 |
| `uvc_switch_gpio` | GPIO 55 |
| `uvc_vbus_gpio` | GPIO 152 |
| `vbus-supply` | phandle `0x145`, `usb-otg-vbus` |
| `vbus-voltage` | 5,250,000 µV |
| `vbus-current` | 1,800,000 µA |
| `vbus-limit-current` | 500,000 µA |
| `tcpc` | `type_c_port0` |
| `mediatek,u2` | present |
| `mediatek,bypss-typec-sink` | present/value 1 |
| status | `okay` |

The misspelling `bypss` is the stock ABI.

### 4.2 MT6375 OTG regulator

| Constraint | Stock value |
|---|---:|
| name | `usb-otg-vbus` |
| minimum voltage | 4,850,000 µV |
| maximum voltage | 5,500,000 µV |
| minimum current | 500,000 µA |
| maximum current | 2,400,000 µA |

No wider limit is claimed from generic MT6375 documentation.

### 4.3 Thermal-camera nodes

```dts
yft_tiny2c_usb {
    compatible = "mediatek,yft_tiny2c_usb";
    tiny2c_usb_vddio_3v3 = <... 149 0>;
    tiny2c_usb_vdd_1v8   = <... 192 0>;
    tiny2c_usb_vdd_3v3   = <... 191 0>;
};

fm78100@0x3c {
    compatible = "mediatek,tiny2c_usb";
    status = "okay";
    reg = <0x3c>;
};
```

The FM78100 child is under `soc/i2c@11e03000`.

## 5. Exact GPIO contract

| GPIO | Software name | Proven behavior |
|---:|---|---|
| 28 | `id-gpios` | input/IRQ; LOW inserted, HIGH removed |
| 37 | `otg_gpio_select` | initialized LOW; follows Type-C source VBUS |
| 55 | `uvc_switch_gpio` | HIGH for inserted uSmart path, LOW removed |
| 152 | `uvc_vbus_gpio` | HIGH for inserted accessory power, LOW removed |
| 149 | `tiny2c_usb_vddio_3v3` | camera I/O-rail command |
| 191 | `tiny2c_usb_vdd_3v3` | camera 3.3-V-rail command |
| 192 | `tiny2c_usb_vdd_1v8` | camera 1.8-V-rail command |

The main controller exposes a 1:1 GPIO range of 196 pins. Exact PCB net names,
external switch polarity circuitry and current limits are not proven.

## 6. Kernel ownership and module ABI

| Module | Stock location | Depends on |
|---|---|---|
| `extcon_mtk_usb` | vendor ramdisk | `tcpc_class,mt6375-charger` |
| `yft_tiny2c_usb` | vendor_dlkm | `mt6375-charger` |
| `mt6375_charger` | vendor ramdisk | `charger_class,tcpc_class` |

All carry stock vermagic `6.1.115-android14-11-g945dff7bc1bf ... aarch64`.

The exact symbol edge is:

```text
mt6375-charger.ko  DEFINE + EXPORT_SYMBOL_GPL(yft_usb_flag)
yft_tiny2c_usb.ko IMPORT + WRITE yft_usb_flag
extcon-mtk-usb.ko IMPORT + READ  yft_usb_flag
mt6375-charger.ko LOCAL READ     yft_usb_flag
```

Only `yft_usb_flag` is YFT-exported by the analyzed charger module. It is not a
userspace property; it is an in-kernel ownership gate.

## 7. Accessory state machine

### 7.1 Extcon insertion detection

The probe-time ID sample and delayed ID work apply the same transition:

| GPIO 28 | GPIO 152 | GPIO 55 | `uvc_insert_status` | queued role |
|---:|---:|---:|---:|---|
| 0 | 1 | 1 | 1 | HOST |
| 1 | 0 | 0 | 0 | NONE |

The ID IRQ handler queues delayed work on `system_power_efficient_wq`. An accessory
already present at probe is immediately applied.

When `yft_usb_flag == 1`, the detect work logs that the YFT driver ignores ordinary USB
function processing and returns. A physical removal whose work executes while the flag
is still 1 can therefore leave cached insertion/GPIO/role state stale until another
coordinated action or detect event occurs. This is a stock fault window.

### 7.2 Thermal rail command

`/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode` accepts:

- `1`: drive I/O 3.3 V, optional 5-V slot, 3.3 V and 1.8 V HIGH; then set
  `yft_usb_flag=1`;
- `0`: drive the same slots LOW; then set `yft_usb_flag=0`;
- any other value: reject/log failure.

The live DT omits the optional 5-V property. Show returns four raw slot states.

At platform probe the driver briefly powers these rails, registers the I2C driver and
then powers them off.

### 7.3 USB role command

`/sys/class/yft_extcon/tiny2c_mode`:

- write 1 -> asynchronously request HOST;
- other parsed value -> asynchronously request NONE;
- read -> always `0\n`;
- does not manipulate accessory power, switch or Type-C VBUS.

The complete camera transition is therefore split across independent interfaces and is
not atomic.

### 7.4 FM78100 identity

The I2C driver binds address `0x3c`, waits 400 ms at probe, reads a 16-bit value with
retries and accepts ID `0x4c59`. `sensor_id` publishes that value in hexadecimal.
This proves that `yft_tiny2c_usb` is FM78100 thermal-camera glue.

## 8. Type-C and charger coexistence

### 8.1 Extcon Type-C notifier

The exact module handles numeric TCPM events 8, 13 and 17, correlated with matching MTK
headers as source VBUS, Type-C state and DR swap.

The source-VBUS path performs:

1. GPIO 37 HIGH/LOW;
2. on enable, request 5.25 V and 1.8 A then enable `usb-otg-vbus`;
3. on disable, disable the regulator;
4. update cached VBUS state.

Thus GPIO 37 is consumed in lockstep with the ordinary Type-C OTG source path. It is not
the uSmart GPIO-152 accessory-VBUS output.

The flag gate suppresses YFT-added ordinary Type-C role/VBUS handling while the thermal
camera owns the path.

### 8.2 Power-supply detector

`usb_is_online()` reads `POWER_SUPPLY_PROP_ONLINE` and
`POWER_SUPPLY_PROP_TYPE`, not `USB_TYPE`. Online is accepted for power-supply types 4
(USB) and 6 (USB_DCP). The detector is gated by `yft_usb_flag`.

### 8.3 MT6375 BC1.2 gate

`mt6375_chg_bc12_work_func()` reads the flag. In thermal-camera mode it takes the
YFT-specific path and skips the ordinary `phy_get("usb2-phy")`,
`phy_set_mode_ext()` and `phy_put()` programming sequence. The charger TCPC notifier
also requeues BC1.2 work for selected states while the flag is 1.

This is coordinated mutual exclusion around the shared USB2/BC1.2 fabric.

### 8.4 MT6375 USBID is not uSmart detect

The module contains USBID charger-device operations and DT lists `usbid_evt`, but the
exact stock `mt6375_usbid_evt_handler()` is an 8-byte stub returning 1. uSmart detection
is GPIO 28 in extcon, not this IRQ.

## 9. VBUS, current limiting and reverse power

`vbus_limit_cur` accepts only 0 or 1. While Type-C VBUS is active:

- 1 requests the DT limit of 500,000 µA;
- 0 restores the normal DT request of 1,800,000 µA.

MT6375 regulator enable includes boost programming and a stock USB-killer protection
check using charger ADC state. Extcon shutdown drives GPIO 37 LOW, disables the
regulator and clears cached source/current-limit state.

### Reverse-power result

- Ordinary Type-C OTG source capability through MT6375 is **PROVEN_EXACT**.
- Accessory-facing reverse-power acceptance or a controllable uSmart reverse-charge
  level is **NOT PROVEN**.
- SELinux labels a historical
  `/sys/devices/platform/extcon-usb/reverse_charging_level`, but no stock module creates
  or even contains that attribute: **NO_STOCK_SUPPORT**.

Do not expose reverse charging in LieppOS on the basis of this stale label.

## 10. Userspace and SELinux contract

### 10.1 Consumers

- `YftSystemUI.apk` reads `uvc_insert_status` and `sensor_id` and references
  `com.endoscope.otgcamera`.
- `YftSuperScreen.apk` contains both mode endpoints.
- `M170infDlp.apk` and `M170infisens.apk` contain the tiny2c paths/mode names.
- `uSmartCamera.apk` contains OTG camera activities and JNI handling under package
  `com.endoscope.otgcamera`.

### 10.2 Stock init permissions

`init.yft.rc` applies mode 0666 to the two mode nodes and `sensor_id`, mode 0777 to
`uvc_insert_status`, and also tries the dead USB1 path. These are exact stock facts but
are insecure design choices.

### 10.3 SELinux

- mode endpoints: `sysfs_yft_file`;
- status and sensor ID: `yft_fmt_device`;
- platform/system app domains can write `sysfs_yft_file` and read `yft_fmt_device`.

No property or service was found that makes the transition atomic. Stock applications
write sysfs directly.

## 11. Fault and power-management behavior

| Condition | Exact behavior / risk |
|---|---|
| ID transition while flag=1 | detect work returns; stale state is possible |
| `tiny2c_mode` readback | always 0; cannot confirm actual role |
| process dies between two mode writes | rails/flag and role can diverge |
| regulator programming fails | error logged/returned; not every external GPIO action is transactionally rolled back |
| USB-killer suspicion | MT6375 source enable can be rejected |
| shutdown with Type-C VBUS on | GPIO 37 LOW and regulator disable |
| tiny2c module suspend/resume | no module-specific callbacks found |
| extcon module suspend/resume | no YFT-specific PM callbacks found |
| charger USBID interrupt | no-op handler |
| unexpected accessory removal | no proven atomic recovery across userspace and kernel state |

No live fault injection, cable event, GPIO toggle, charger write or power test was
performed.

## 12. LieppOS-safe integration requirements

Exact target workspace was verified at
`/home/armol/kernel-work/gki-12901745-workspace/common`:

- Linux 6.1.115;
- common commit `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`.

Existing reconstruction work includes `lieppos/yft-tiny2c-usb-recon/` and a
`mt6375-charger-provider-abi/` witness. The latter is not a functional charger and must
not ship as one. No completed extcon reconstruction was present at audit time.

### Required kernel work

1. Retain exact stock charger/TCPC providers only if symbol CRC and vermagic are truly
   compatible; never force-load mismatched modules.
2. Complete `extcon-mtk-usb` reconstruction from the exact call/state contract here.
3. Keep one and only one `yft_usb_flag` provider.
4. Preserve all GPIO numbers, polarities, graph links, regulator constraints and the
   `bypss` property spelling.
5. Preserve charger BC1.2 and Type-C flag gates.
6. Do not add USB1, SC851x ownership or reverse-charge controls.

### Required userspace/security work

Replace direct world-writable sysfs access with one privileged serialized service. It
must own enable/disable, timeouts and rollback. Applications receive read-only state or
a narrow Binder API. Use dedicated SELinux types rather than broad `sysfs_yft_file`.

A safe policy-level disable sequence is: stop camera userspace, request role NONE, wait
for quiescence, remove UVC switch/accessory power, clear rail/flag state, then return
arbitration to TCPC. This is an improved LieppOS policy, not a claim that stock is
transactional.

### Static release gates

- module build/modpost against exact target workspace;
- no unresolved or duplicate `yft_usb_flag`;
- exact DT diff review;
- call-graph comparison for role/VBUS/GPIO order;
- sysfs/procfs ABI comparison where retained;
- SELinux denial review and no app-domain raw writes;
- no hardware testing until a separate bounded validation plan is approved.

## 13. Unclosed evidence

| Question | Result |
|---|---|
| connector/contact pinout | **BLOCKED_WITH_MISSING_EVIDENCE** |
| external mux/load-switch part and schematic | **BLOCKED_WITH_MISSING_EVIDENCE** |
| exact USB descriptors for each accessory | **BLOCKED_WITH_MISSING_EVIDENCE** |
| safe accessory inrush/current envelope | **BLOCKED_WITH_MISSING_EVIDENCE** |
| reverse-power electrical directionality | **BLOCKED_WITH_MISSING_EVIDENCE** |
| PCB/pinctrl human-readable net names | **UNKNOWN** |

These gaps do not change the proven software topology but prevent claims about unknown
accessories or reverse power.

## 14. Evidence index

Authoritative evidence tree:

`workspace/usmart-audit/`

Key reports:

- `README.md`
- `dt/usmart-dt-contract.md`
- `kernel/usmart-extcon-analysis.md`
- `kernel/usmart-yft-tiny2c-analysis.md`
- `kernel/usmart-mt6375-otg-contract.md`
- `kernel/usmart-kernel-{owners,dependencies}.md`
- `kernel/usmart-lieppos-plan.md`
- `usb/usmart-usb-controller-topology.md`
- `gpio/usmart-gpio-mux-contract.md`
- `charger/usmart-typec-coexistence.md`
- `userspace/usmart-userspace-dependencies.md`
- `accessories/usmart-accessory-matrix.md`
- exact annotated disassembly, DT extracts and identifier inventories alongside them.

## Final disposition

The static uSmart contract is closed at controller, DT, role, VBUS, charger, GPIO,
Type-C, thermal-camera, init and userspace layers. Unknown connector/electrical and USB
descriptor details are explicitly isolated rather than inferred. LieppOS can preserve
uSmart safely only by porting the exact extcon/charger flag contract and replacing the
stock split, world-writable userspace control with a serialized privileged service.
