# LN2403 mandatory RED

## RED condition

`NO_PUBLIC_DONOR_FOUND`.

The pre-reconstruction baseline was empty source: no public or local target
driver could be built. It therefore necessarily produced:

- no `leds_ln2403.ko`;
- 0/16 stock functions;
- 0/32 imports and MODVERSION entries;
- neither required `mt-pwm` provider edge;
- no `mediatek,yft_camplight` binding;
- no five-GPIO/pinctrl/PWM behavior;
- no camping-light, brightness, red/blue, timer, wake-lock or sysfs ABI.

This is the mandatory fail/RED recorded before accepting reconstructed behavior.
Generic PWM LED drivers were rejected as donors because they do not implement
the stock ABI or state machines.

## Provider distinction

A genuine MT6878 `mtk-pwm` source provider exists and was source-built. It is a
dependency, not a donor for `leds_ln2403`; it does not alter the target RED.
