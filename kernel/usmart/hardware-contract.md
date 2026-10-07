# uSmart hardware contract

## What it is

uSmart is Ulefone's proprietary **mechanical expansion connector** for its E01/E02/E03
endoscopes and C01 microscope. The GQ5012BF1 phone-side electrical/software contract is a
standard USB2 host path behind board controls—not a separate serial bus or second USB
controller.

| software-visible conductor/function | evidence | result |
|---|---|---|
| accessory ID | DT `id-gpios=<gpio 28, flags 0>` + exact driver | digital active-low insertion input |
| accessory power/VBUS enable | DT `uvc_vbus_gpio=<gpio 152, flags 0>` + exact driver | active-high board power gate |
| USB D+/D− | DT `uvc_switch_gpio=<gpio 55, flags 0>` + shared USB captures | alternate USB2 pair selected by GPIO55 |
| ground/return | required by powered USB function, not named in software | board-only |
| additional pins/functions | no DT, driver, APK or native-daemon control found | not proven |

Connector contact count, pin numbering, mating part, pull resistor and analog switch/load
switch silicon are not present in local static artifacts. Software does not depend on
those identities.

## Functional topology

```text
external Type-C D+/D− ─┐
                        ├─ board USB2 route (GPIO55) ─→ usb2-phy0 ─→ MTU3 ─→ xHCI
uSmart D+/D− ──────────┘

GPIO28 LOW → GPIO152 HIGH (accessory power) → GPIO55 HIGH (uSmart pair)
             → physical-status 1 → HOST
```

GPIO55 LOW is the boot/default external-Type-C route; GPIO55 HIGH selects uSmart. The
proof is the exact transition code plus functioning external USB with probe-initialized
LOW and the dedicated `uvc_switch_gpio` DT assignment. No Type-C SS, DP, analog-audio,
I2C, UART or display-output path reaches uSmart.
