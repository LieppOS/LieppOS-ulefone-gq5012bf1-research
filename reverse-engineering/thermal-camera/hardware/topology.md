# Thermal camera — hardware / DT topology (GQ5012BF1, stock)

Source DT: `workspace/usmart-audit/dt/live-merged.dts` (live `/sys/firmware/devicetree`
of the stock unit), cross-checked with the frozen FDT under
`qwen_hardware/qwen-thermal/evidence/local/dt/`.

## Result in one line

`8-003c` is **not a separate companion chip**. It is the I2C-slave control port of the
thermal module's own ASIC (Raytron/InfiRay **Tiny2-C / TC2-C**, LY-series ASIC), the same
silicon that enumerates on USB as `3474:4321`. Stock uses that port for exactly one thing:
a boot-time two-byte chip-ID read (`0x4c59`). Power, USB role and USB routing are separate
software paths.

```
                         MT6878 AP
 ┌────────────────────────────────────────────────────────────────────┐
 │ I2C8 /soc/i2c@11e03000 (SCL GPIO141, SDA GPIO142)                  │
 │   └─ fm78100@0x3c  compatible "mediatek,tiny2c_usb"  reg 0x3c      │──I2C──┐
 │        driver tiny2c_usb-sensor (yft_tiny2c_usb.ko)                │       │
 │ /yft_tiny2c_usb  compatible "mediatek,yft_tiny2c_usb" (phandle 0x1d1)      │
 │   tiny2c_usb_vddio_3v3 = <&pio 149 0>  ── raw GPIO ─► VDDIO (3.3 V) │       │
 │   tiny2c_usb_vdd_3v3   = <&pio 191 0>  ── raw GPIO ─► VDD33         │       │
 │   tiny2c_usb_vdd_1v8   = <&pio 192 0>  ── raw GPIO ─► VDD18         │       │
 │   (tiny2c_usb_vdd_5v   absent)                    VDD50: board     │       │
 │ USB0 / MTU3 / xHCI 11200000 / mtk-xsphy (USB2, single root port) ──┼─USB2─┐│
 │ /extcon-usb (extcon-mtk-usb.ko)                                    │      ││
 │   tiny2c_mode (class yft_extcon) → role HOST/NONE                  │      ││
 │   id-gpios 28, uvc_switch_gpio 55, uvc_vbus_gpio 152,              │      ││
 │   otg_gpio_select 37  ── uSmart accessory / OTG only, not thermal  │      ││
 └────────────────────────────────────────────────────────────────────┘      ││
                                                                             ▼▼
                         Tiny2-C / TC2-C module (256×192, 12 µm, LWIR)
                         one ASIC: USB2 device 3474:4321 (UVC 1.10)
                                   + IIC slave @0x3c (ID regs 0x0000/0x0001)
                                   + internal shutter, flash (fw + calibration)
```

## Node table

| item | value | source | confidence |
|---|---|---|---|
| I2C controller | `/soc/i2c@11e03000`, alias `i2c8`, `mediatek,mt6989-i2c`, IRQ GIC SPI 0x198, `clock-div=1`, SCL/SDA GPIO IDs 141/142, phandle 0x255 | DT | PROVEN |
| other clients on i2c8 | `aw36518@63` (flash LED driver; unrelated) | DT | PROVEN |
| client node | `fm78100@0x3c`: `compatible="mediatek,tiny2c_usb"`, `reg=<0x3c>`, `status="okay"`; **no** interrupts, reset/power GPIOs, regulators, clocks, pinctrl or phandle | DT | PROVEN |
| bound driver | `8-003c -> /sys/bus/i2c/drivers/tiny2c_usb-sensor` (modalias `of:Nfm78100T(null)Cmediatek,tiny2c_usb`) | runtime bus capture `evidence/hw-tests/build14-touch-usb/of-live-input-buses.txt:111` | PROVEN |
| platform node | `/yft_tiny2c_usb`, `compatible="mediatek,yft_tiny2c_usb"`, phandle 0x1d1, three GPIO properties above, flags 0, no pinctrl | DT | PROVEN |
| pio phandle | 0x89 | DT | PROVEN |
| extcon node | `/extcon-usb` `mediatek,extcon-usb`, `id-gpios=<&pio 28 0>`, `otg_gpio_select=<&pio 37 0>`, `uvc_switch_gpio=<&pio 55 0>`, `uvc_vbus_gpio=<&pio 152 0>`, `tcpc="type_c_port0"`, `mediatek,u2`, `mediatek,bypss-typec-sink=1`, vbus-supply → MT6375 OTG | DT | PROVEN |
| chip ID register | 16-bit addr 0x0000 (=0x59) and 0x0001 (=0x4c) | driver + FactoryMode | PROVEN |
| IRQ / reset / clock / regulator for 0x3c | none | DT + driver | PROVEN none |

## GPIO55 / GPIO152 correction

Earlier summaries (and the task brief) stated "GPIO55 switches D+/D- between external
Type-C and the internal thermal camera" and "GPIO152 powers the camera". Static evidence
contradicts that:

1. `extcon-mtk-usb` (exact rebuild) parses GPIO 55/152 with `gpio_direction_output(…, 0)`
   at probe and writes them **only** from `mtk_usb_extcon_detect_cable()` /
   `mtk_usb_extcon_id_pin_init()`, i.e. the GPIO 28 ID pin = uSmart pogo accessory.
   Each write also sets `uvc_insert_status`.
2. The thermal path writes `/sys/class/yft_extcon/tiny2c_mode`, whose store only queues
   `mtk_usb_extcon_set_role(HOST|NONE)`; it touches no GPIO.
3. The controlled stock thermal capture (`usb-research/evidence/thermal-camera-transition-sysfs.txt`)
   shows the camera enumerated at `1-1` (480 Mbit/s) with `uvc_insert_status=0`,
   so GPIO 55/152 stayed at their probe-time LOW during the whole thermal session.
4. Thermal power comes from GPIO 149/191/192 (`tiny2c_usb_mode=…gpio_1v8=1,gpio_3v3=1,gpio_5v=0,gpio_io3v3:1`).

So GPIO 55/152 are the uSmart accessory switch/VBUS (matching `kernel/usmart-full-contract.md`),
and the thermal D+/D- connection does not depend on any GPIO driven by thermal software.
Whether the thermal D+/D- share the Type-C pair passively or go through a mux whose idle
state (GPIO 55 low) selects the thermal/Type-C side is board wiring and cannot be resolved
statically. **PROVEN**: no thermal software toggles a mux. **UNKNOWN**: physical routing.

## Identity classification

| claim | class |
|---|---|
| 8-003c is the thermal module's own I2C slave (not an independent IC) | STRONGLY SUPPORTED (Tiny2-C/TC2-C pinout has IIC_SLV_SCL/SDA + USB_DP/DM + VDD50/VDD33/VDD18/VDDIO, exactly the driver's rails; stock never addresses it for anything but the module ID) |
| module = Raytron/InfiRay Tiny2-C (TC2-C) 256×192 | PROVEN at software/firmware level: M170infDlp ships `RS300_TC2C_…whole_package` with `"device_name":"TINY2-C"`; IR_SENSOR_WIDTH 256 / HEIGHT 386 (=2×192+2); USB identity equals the public Tiny2-C/TC001 descriptor |
| chip-ID value 0x4c59 | PROVEN |
| 0x4c59 = ASCII "LY" = LY300 ASIC tag | STRONGLY SUPPORTED (inference) |
| FM78100 fitted on this board | **RETRACTED** — FM78100/FM78102 is a separate single-point IR thermometer family (fm78100-sensor driver surface, `libthermometerTemp78102.so`); no driver ships, the FactoryMode test is hidden, the node name is inherited |
| FM78100 vendor | UNKNOWN (not needed: part not fitted) |
| 640×512 | marketing output figure; native detector is 256×192 and the stock app runs `MNN_SR_TINY2C` super-resolution (×2) — see `../ac020/README.md` |
