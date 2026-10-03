# Reverse wired charging (phone → USB-C accessory) path

Classification: **PROVEN_EXACT for the software/control path**.
**INFERRED (DT units plus silicon class) for the battery-side conversion stage.**

```
2S battery pack (~7.0–8.8 V)
   │  SC8510 forward 2:1 (autonomous, fwd-ocp code 4; no software enable)
   ▼
1S system rail (cell-equivalent, MT6375 VSYS/BAT domain)
   │  MT6375 boost, regulator "usb-otg-vbus"
   │  (/soc/i2c@11280000/mt6375@34/chg/otg, phandle 0x145/325)
   ▼
USB-C VBUS 5.25 V request, 1.8 A request
   (regulator constraints 4.85–5.50 V, 0.5–2.4 A; 0.5 A "limit-current" step)
```

**Which IC drives VBUS:** the MT6375 OTG boost. Neither SC8571 nor SC8510
does:

- **SC8571:** `OTG_EN` (0x0f bit 5) and `ACDRV*` are never written. The
  driver exposes no regulator or OTG op. The `charger_ops` set contains no
  `enable_otg`.
- **SC8510:** it has no regulator, extcon or tcpc edge, and no
  mode/direction write.

The phrase "reverse charging" in SC8510 documentation means 1S→2S
**battery** charging. It does not mean OTG.

**Source voltage and current:**

| item | value |
|---|---|
| extcon request | `vbus-voltage = 5250000` µV, `vbus-current = 1800000` µA |
| limited step | `vbus-limit-current = 500000` µA |
| regulator max | 2.4 A |

**Enable path (exact modules):**

1. `tcpc_mt6375` decides the source role and notifies (`TCP_NOTIFY_SOURCE_VBUS`).
2. `extcon-mtk-usb` sets GPIO 37 (`otg_gpio_select`).
3. `extcon-mtk-usb` calls `regulator_set_voltage`, `regulator_set_current_limit` and `regulator_enable(usb-otg-vbus)`.
4. MT6375 `mt6375_chg_regulator_enable()` runs.
5. That function performs the USB-killer ADC check and then enables the boost.

`extcon-usb` also has `mediatek,bypss-typec-sink`. The uSmart UVC gate
(GPIO 152) uses the same regulator; see
`workspace/usmart-audit/kernel/usmart-mt6375-otg-contract.md`.

**Type-C interaction:** an ordinary DRP source role (TCPC
`type_c_port0`). OTG is not a separate "reverse charging" protocol, and no
PD source-capability tuning was found in the charging modules.

**Minimum SOC and temperature restrictions:** no kernel module in the stock
power stack applies an SOC or temperature gate to OTG. The checked modules
are mtk_charger_framework, mt6375-charger, extcon-mtk-usb (exact or
contracted), tcpc and PE*. The only kernel guards are the USB-killer
detection and the regulator current limit.

**Over-current behaviour:** handled by the MT6375 boost limit (DT max
2.4 A) and its OTG fault IRQs. SC8510 `fwd-ocp` protects the pack-side converter. Shutdown
deasserts GPIO 37 and disables the regulator.

**User-facing control / HAL:** none specific. SELinux has a stale label for
`/sys/devices/platform/extcon-usb/reverse_charging_level`, but no stock
module creates that attribute. Reverse power is the ordinary Android
USB-OTG / power-role behaviour.

## Future runtime test (do NOT run without explicit approval)

Read-only, with an accessory attached:

1. `cat /sys/class/regulator/*/name` and find `usb-otg-vbus`. Read its
   `state`, `microvolts` and `microamps`.
2. `cat /sys/class/typec/port0/power_role`.
3. `cat /sys/class/power_supply/sc-cp-*/online`. Both are expected to be 0.
4. `cat /sys/kernel/debug/regmap/6-0069/registers` (if debugfs is
   permitted) and check that `FLAG*` show no RVS fault.

No register writes.
