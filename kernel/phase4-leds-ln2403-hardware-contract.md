# LN2403 hardware topology

| signal/property | MT6878 GPIO | direction/state | polarity | probe state | function |
|---|---:|---|---|---|---|
| `ln2403-power-gpio` | 74 | direction preconfigured; module writes raw value | active-high | 0 | LN2403/current-stage power |
| `ln2403-en-gpio` | 91 | direction preconfigured; module writes raw value | active-high | 0 | LN2403 enable; timer-gated in BLINK/SOS |
| `leds-power-gpio` | 153 | direction preconfigured; module writes raw value | active-high | 0 | common red/blue warning-light power |
| `leds-red-gpio` | 20 | direction preconfigured; module writes raw value | active-high | 0 | red warning LED selection |
| `leds-blue-gpio` | 21 | direction preconfigured; module writes raw value | active-high | 0 | blue warning LED selection |
| PWM output | 22 | GPIO output or mux-1 PWM_3 | active-high waveform | `ln2403_pwmoff_low` | LN2403 dimming input |

The module never calls a GPIO direction API; it assumes board/pinctrl setup and
uses `gpiod_{get,set}_raw_value` without active-low translation. The SoC drives
the LN2403 as a power/current stage: GPIO74/91 gate the stage and
SoC legacy PWM channel 3 reaches it on GPIO22. Red/blue LEDs use a separate
common-power GPIO and two selection GPIOs; they do not use the PWM provider.

PWM modes first stop any GPIO timer, disable PWM, force GPIO22 high then drive
GPIO91/74 low. LOW/NORMAL/HIGH select PWM and program it, assert GPIO91, then
GPIO74. BLINK/SOS select GPIO22 low, start GPIO91 gating, then assert GPIO74.
OFF ends with GPIO91=0, GPIO74=0 and GPIO22 low. Brightness writes use the stock
alternate on-order: program PWM, assert GPIO74, then GPIO91.
