# LN2403 device-tree contract

Exact merged vendor-boot DT path: `/yft_camplight`.

```dts
yft_camplight {
    compatible = "mediatek,yft_camplight";
    ln2403-power-gpio = <&pio 74 0>;
    ln2403-en-gpio = <&pio 91 0>;
    leds-power-gpio = <&pio 153 0>;
    leds-red-gpio = <&pio 20 0>;
    leds-blue-gpio = <&pio 21 0>;
    pinctrl-names = "default", "ln2403_pwmoff_high",
                    "ln2403_pwmoff_low", "ln2403_pwmon";
    pinctrl-0 = <&ln2403_default>;
    pinctrl-1 = <&ln2403_high>;
    pinctrl-2 = <&ln2403_low>;
    pinctrl-3 = <&ln2403_pwm>;
    status = "okay";
};
```

All GPIO flags are zero: active-high/no inversion. Stock deliberately uses raw
GPIO descriptor access, so values below are electrical raw values.

The module consumes all five named GPIO properties, compatible, status through
platform matching, and three explicit state names. It does not parse a PWM
phandle, channel, period, brightness/default-mode scalar, or any other YFT
property. Channel/configuration are hard-coded. `default` is not looked up by
the module; the pinctrl core may select `pinctrl-0`, whose board group is empty.

Resolved pinctrl groups: `ln2403_high` is GPIO22/mux 0/output-high;
`ln2403_low` is GPIO22/mux 0/output-low; `ln2403_pwm` is GPIO22/mux 1
`PWM_3`, output-high. All set `slew-rate = <1>`.
